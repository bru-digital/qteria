"""
PDF Parsing Service with caching and section detection.

This service extracts structured text from PDF documents using PyPDF2 (primary)
and pdfplumber (fallback). Parsed results are cached in the database to avoid
re-parsing the same document multiple times.

Features:
- Page boundary preservation (track which text is on which page)
- Section detection (numbered sections like "1.", "2.3", "3.2.1")
- Fallback extraction (pdfplumber if PyPDF2 fails)
- Database caching (stores parsed data in parsed_documents table)
- Error handling (corrupt PDFs, encrypted PDFs)
- Configurable section patterns (custom regex per workflow)
- OCR support (pytesseract for scanned PDFs)
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime

import PyPDF2
import pdfplumber
from sqlalchemy.orm import Session

from app.models.models import ParsedDocument

logger = logging.getLogger(__name__)

# Optional OCR dependencies (graceful degradation if not available)
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning(
        "OCR dependencies not available (pytesseract or pdf2image missing). "
        "Scanned PDF support will be disabled."
    )

# Optional memory monitoring (graceful degradation if not available)
try:
    import psutil
    MEMORY_MONITORING_AVAILABLE = True
except ImportError:
    MEMORY_MONITORING_AVAILABLE = False
    logger.info("psutil not available, OCR DPI optimization disabled")

# Helper function for Java availability check (must be defined before use)
def _check_java_availability() -> bool:
    """
    Check if Java Runtime Environment is available.

    Required for tabula-py table extraction.

    Returns:
        True if Java is available, False otherwise
    """
    import subprocess
    try:
        # Run 'java -version' to check if Java is installed
        result = subprocess.run(
            ['java', '-version'],
            capture_output=True,
            timeout=5,
            check=False
        )
        # Java prints version to stderr (not stdout)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception as e:
        logger.warning(
            f"Failed to check Java availability: {e}",
            extra={"event": "java_check_failed", "error": str(e)}
        )
        return False


# Optional table extraction dependencies (graceful degradation if not available)
try:
    import tabula
    JAVA_AVAILABLE = _check_java_availability()
    TABLE_EXTRACTION_AVAILABLE = JAVA_AVAILABLE
    if not JAVA_AVAILABLE:
        logger.warning(
            "Java Runtime Environment not available. "
            "Table extraction will be disabled. "
            "Install with: apt-get install default-jre (Linux) or brew install openjdk (macOS)"
        )
except ImportError:
    TABLE_EXTRACTION_AVAILABLE = False
    logger.warning(
        "tabula-py not available. Table extraction will be disabled. "
        "Install with: pip install tabula-py"
    )

# Configuration constants
# OCR configuration
SCANNED_PDF_CHAR_THRESHOLD = 100  # Min chars to consider PDF as having text
SCANNED_PDF_PAGE_TEXT_THRESHOLD = 20  # Min chars per page for text-based PDF
OCR_DEFAULT_DPI = 300  # Standard DPI for OCR (balances quality vs memory)
OCR_LOW_MEMORY_DPI = 150  # DPI for memory-constrained environments
OCR_MEMORY_MB_PER_PAGE_AT_300DPI = 5  # Estimated memory usage per page at 300 DPI
OCR_TIMEOUT_SECONDS = 60  # Timeout per page for OCR processing (prevents hung processes)
OCR_BYTES_PER_PIXEL_RGBA = 4  # RGBA color format uses 4 bytes per pixel
OCR_MEMORY_SAFETY_MARGIN = 1.2  # 20% safety margin for temporary buffers and processing overhead

# Pattern validation
MAX_PATTERN_LENGTH = 1000  # Maximum allowed regex pattern length
MAX_CUSTOM_PATTERNS = 100  # Maximum number of custom patterns allowed
REDOS_NESTED_QUANTIFIER_MAX_LENGTH = 50  # Max chars inside nested quantifiers to prevent ReDoS

# Page count validation
MAX_PAGE_COUNT = 10000  # Maximum allowed page count (prevents integer overflow attacks)


class PDFParsingError(Exception):
    """Base exception for PDF parsing failures."""

    pass


class EncryptedPDFError(PDFParsingError):
    """Raised when PDF is password-protected or encrypted."""

    pass


class CorruptPDFError(PDFParsingError):
    """Raised when PDF is corrupt or malformed."""

    pass


class PDFParserService:
    """
    PDF parsing service with caching and multi-library fallback.

    Extracts structured text from PDFs with page boundaries and section detection.
    Results are cached in the database to avoid re-parsing.
    """

    def __init__(self, db: Session):
        """
        Initialize PDF parser service.

        Args:
            db: SQLAlchemy database session for caching operations
        """
        self.db = db

    def parse_document(
        self,
        document_id: UUID,
        file_path: str,
        organization_id: UUID,
        custom_patterns: Optional[List[str]] = None,
        enable_ocr: bool = True,
        ocr_language: str = "eng",
        enable_tables: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse PDF document and return structured text with page/section info.

        This is the main entry point. It checks the cache first, then parses
        if needed, and stores the result in the database.

        Note: This method is synchronous. For background processing, wrap in
        a Celery task (see STORY-021).

        Args:
            document_id: UUID of the document being parsed
            file_path: Absolute path to the PDF file
            organization_id: UUID of the organization (for multi-tenancy)
            custom_patterns: Optional custom regex patterns for section detection
            enable_ocr: Enable OCR fallback for scanned PDFs (default: True)
            ocr_language: Tesseract language code for OCR (default: "eng", e.g., "deu" for German, "fra" for French)
            enable_tables: Enable table extraction (default: True)

        Returns:
            Dict with:
                - document_id: UUID of the document
                - pages: List of {page_number, section, text}
                - tables: List of {page, columns, data} (empty if enable_tables=False or extraction fails)
                - method: Parsing method used ('pypdf2', 'pdfplumber', or 'ocr')
                - cached: Whether result came from cache

        Raises:
            EncryptedPDFError: If PDF is password-protected
            CorruptPDFError: If PDF is corrupt or malformed
            PDFParsingError: For other parsing failures (including invalid OCR language code)
        """
        # 0. Validate OCR language early (fail fast principle)
        # Even if OCR might not be used, validate input immediately for consistency
        if enable_ocr:
            self._validate_ocr_language(ocr_language)

        # 1. Check cache first
        cached_result = self._get_cached_parse(document_id, organization_id)
        if cached_result:
            logger.info(
                "PDF parsing cache hit",
                extra={
                    "event": "cache_hit",
                    "document_id": str(document_id),
                    "organization_id": str(organization_id),
                    "method": cached_result["method"],
                },
            )
            return {
                "document_id": document_id,
                "pages": cached_result["pages"],
                "tables": cached_result.get("tables", []),  # Backward compatible
                "method": cached_result["method"],
                "cached": True,
            }

        # 2. Validate PDF file
        self._validate_pdf(file_path)

        # Log parsing start (cache miss)
        logger.info(
            "Parsing PDF document",
            extra={
                "event": "pdf_parsing_start",
                "document_id": str(document_id),
                "organization_id": str(organization_id),
                "file_path": file_path,
            },
        )

        # 3. Extract text with PyPDF2 (primary)
        try:
            pages = self._extract_with_pypdf2(file_path)
            parsing_method = "pypdf2"
        except Exception as e:
            # 4. Fallback to pdfplumber
            logger.warning(
                "PyPDF2 failed, falling back to pdfplumber",
                extra={
                    "event": "parser_fallback",
                    "document_id": str(document_id),
                    "organization_id": str(organization_id),
                    "pypdf2_error": str(e),
                },
            )
            try:
                pages = self._extract_with_pdfplumber(file_path)
                parsing_method = "pdfplumber"
            except Exception as fallback_error:
                logger.error(
                    "Both PyPDF2 and pdfplumber failed",
                    extra={
                        "event": "pdf_parsing_failed",
                        "document_id": str(document_id),
                        "organization_id": str(organization_id),
                        "pypdf2_error": str(e),
                        "pdfplumber_error": str(fallback_error),
                    },
                )
                raise PDFParsingError(
                    f"Both PyPDF2 and pdfplumber failed. PyPDF2: {str(e)}, pdfplumber: {str(fallback_error)}"
                )

        # 5. Check if PDF is scanned (no extractable text) and use OCR if enabled
        is_scanned, detection_reason = self._is_scanned_pdf(pages)
        if enable_ocr and is_scanned:
            logger.info(
                "Scanned PDF detected, falling back to OCR",
                extra={
                    "event": "ocr_fallback",
                    "document_id": str(document_id),
                    "organization_id": str(organization_id),
                    "ocr_language": ocr_language,
                    "detection_reason": detection_reason,
                },
            )
            try:
                pages = self._extract_with_ocr(file_path, language=ocr_language)
                parsing_method = "ocr"
            except Exception as ocr_error:
                logger.warning(
                    "OCR extraction failed",
                    extra={
                        "event": "ocr_failed",
                        "document_id": str(document_id),
                        "organization_id": str(organization_id),
                        "error": str(ocr_error),
                    },
                )
                # Continue with empty text (graceful degradation)

        # 6. Detect sections across pages
        structured_pages = self._detect_sections(pages, custom_patterns)

        # 7. Extract tables if enabled
        tables = []
        if enable_tables:
            tables = self._extract_tables(file_path)

        # 8. Cache parsed result (including tables)
        self._cache_parse(document_id, organization_id, structured_pages, parsing_method, tables)

        return {
            "document_id": document_id,
            "pages": structured_pages,
            "tables": tables,
            "method": parsing_method,
            "cached": False,
        }

    def _validate_pdf(self, file_path: str) -> None:
        """
        Validate that PDF file exists, is readable, and not encrypted.

        Args:
            file_path: Path to PDF file (should be from Vercel Blob download,
                      not user-controlled input)

        Raises:
            CorruptPDFError: If file doesn't exist, isn't readable, or path traversal detected
            EncryptedPDFError: If PDF is password-protected
        """
        # Resolve path to absolute path (prevents symlink/relative path attacks)
        try:
            path = Path(file_path).resolve(strict=True)
        except (OSError, RuntimeError) as e:
            raise CorruptPDFError(f"Invalid file path: {file_path} - {str(e)}")

        # Additional security: Ensure path doesn't contain suspicious patterns
        # This prevents path traversal attacks if file_path is ever user-controlled
        path_str = str(path)
        if ".." in file_path or path_str.startswith(("/etc", "/sys", "/proc")):
            logger.warning(
                "Suspicious file path detected",
                extra={
                    "event": "path_traversal_attempt",
                    "file_path": file_path,
                    "resolved_path": path_str,
                },
            )
            raise CorruptPDFError(f"Invalid file path: {file_path}")

        # Check file exists (should already be true if resolve(strict=True) succeeded)
        if not path.exists():
            raise CorruptPDFError(f"PDF file not found: {file_path}")

        # Check file is readable
        if not path.is_file():
            raise CorruptPDFError(f"Path is not a file: {file_path}")

        # Check if encrypted
        if self._is_encrypted(str(path)):
            raise EncryptedPDFError(
                f"PDF is password-protected or encrypted: {file_path}"
            )

    def _is_encrypted(self, file_path: str) -> bool:
        """
        Check if PDF is password-protected or encrypted.

        Args:
            file_path: Path to PDF file

        Returns:
            True if encrypted, False otherwise
        """
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                return reader.is_encrypted
        except Exception:
            # If we can't determine encryption status, assume not encrypted
            # The actual parsing will fail with CorruptPDFError if it's really broken
            return False

    def _extract_with_pypdf2(self, file_path: str) -> List[Dict]:
        """
        Extract text from PDF using PyPDF2.

        Args:
            file_path: Path to PDF file

        Returns:
            List of page dictionaries: [{"page": 1, "text": "...", "section": None}, ...]

        Raises:
            CorruptPDFError: If PDF is corrupt or cannot be read
        """
        pages = []

        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                # Check if encrypted (should have been caught earlier, but double-check)
                if reader.is_encrypted:
                    raise EncryptedPDFError("PDF is encrypted")

                # Extract text from each page
                for page_num, page in enumerate(reader.pages, start=1):
                    try:
                        text = page.extract_text()
                        pages.append(
                            {
                                "page": page_num,
                                "text": text if text else "",
                                "section": None,  # Will be detected later
                            }
                        )
                    except Exception as page_error:
                        # If one page fails, log but continue with others
                        pages.append(
                            {
                                "page": page_num,
                                "text": f"[Error extracting page {page_num}: {str(page_error)}]",
                                "section": None,
                            }
                        )

        except PyPDF2.errors.PdfReadError as e:
            raise CorruptPDFError(f"PyPDF2 failed to read PDF: {str(e)}")
        except Exception as e:
            raise CorruptPDFError(f"Unexpected error reading PDF: {str(e)}")

        return pages

    def _extract_with_pdfplumber(self, file_path: str) -> List[Dict]:
        """
        Extract text from PDF using pdfplumber (fallback method).

        pdfplumber is more robust for complex PDFs with tables and multi-column layouts.

        Args:
            file_path: Path to PDF file

        Returns:
            List of page dictionaries: [{"page": 1, "text": "...", "section": None}, ...]

        Raises:
            CorruptPDFError: If PDF is corrupt or cannot be read
        """
        pages = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text()
                        pages.append(
                            {
                                "page": page_num,
                                "text": text if text else "",
                                "section": None,
                            }
                        )
                    except Exception as page_error:
                        pages.append(
                            {
                                "page": page_num,
                                "text": f"[Error extracting page {page_num}: {str(page_error)}]",
                                "section": None,
                            }
                        )

        except Exception as e:
            raise CorruptPDFError(f"pdfplumber failed to read PDF: {str(e)}")

        return pages

    def _detect_sections(
        self, pages: List[Dict], custom_patterns: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Detect section headings across pages using regex patterns.

        Looks for numbered sections like:
        - "1. Introduction" or "1. introduction" (case-insensitive)
        - "2.3 Test Results" or "2.3 test results"
        - "3.2.1 Details"
        - "SECTION 1 - OVERVIEW" (uppercase headings)

        The detected section name persists across pages until a new section is found.

        Args:
            pages: List of page dictionaries with text
            custom_patterns: Optional custom regex patterns (overrides defaults if provided)

        Returns:
            Same list with "section" field populated
        """
        current_section = None

        # Use custom patterns if provided, otherwise use default patterns
        if custom_patterns:
            # Validate and compile custom patterns
            section_patterns = self._compile_section_patterns(custom_patterns)
        else:
            # Default regex patterns for section detection (in priority order)
            section_patterns = [
                # Numbered sections: "1.", "2.3", "3.2.1" (case-insensitive)
                # Matches: "1. Introduction", "2.3 test results", "3.2.1 Details"
                re.compile(r"^(\d+(?:\.\d+)*\.?\s+[a-zA-Z][^\n]{0,100})", re.MULTILINE),
                # Uppercase headings: "SECTION 1", "CHAPTER 2", "PART A"
                re.compile(r"^([A-Z][A-Z\s]{5,50})\n", re.MULTILINE),
                # Underlined headings (text followed by ===== or -----)
                re.compile(
                    r"^([A-Z][^\n]{5,100})\n[=\-]{5,}$", re.MULTILINE
                ),
            ]

        for page in pages:
            text = page["text"]

            # Try each pattern in order
            section_found = False
            for pattern in section_patterns:
                match = pattern.search(text)
                if match:
                    # Extract and clean section name
                    section_name = match.group(1).strip()
                    # Remove trailing punctuation
                    section_name = section_name.rstrip(".:- ")
                    current_section = section_name
                    section_found = True
                    break

            # Assign current section to this page
            page["section"] = current_section

        return pages

    def _get_cached_parse(
        self, document_id: UUID, organization_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached parsed text from database.

        Args:
            document_id: UUID of the document
            organization_id: UUID of the organization (for multi-tenancy)

        Returns:
            Dict with pages, tables (if available), and method, or None if not cached
        """
        cached = (
            self.db.query(ParsedDocument)
            .filter(
                ParsedDocument.document_id == document_id,
                ParsedDocument.organization_id == organization_id,
            )
            .first()
        )

        if cached:
            # parsed_data can be either:
            # - Old format: List[Dict] (just pages)
            # - New format: Dict with "pages" and "tables" keys
            parsed_data = cached.parsed_data

            # Handle backward compatibility
            if isinstance(parsed_data, list):
                # Old format: just pages
                return {
                    "pages": parsed_data,
                    "tables": [],
                    "method": cached.parsing_method,
                }
            elif isinstance(parsed_data, dict):
                # New format: includes pages and tables
                return {
                    "pages": parsed_data.get("pages", []),
                    "tables": parsed_data.get("tables", []),
                    "method": cached.parsing_method,
                }

        return None

    def _cache_parse(
        self,
        document_id: UUID,
        organization_id: UUID,
        parsed_data: List[Dict],
        method: str,
        tables: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Store parsed text in database cache.

        Note: This method uses flush() instead of commit() to allow the caller
        to manage the transaction. The caller should commit after all operations
        are complete.

        Args:
            document_id: UUID of the document
            organization_id: UUID of the organization (for multi-tenancy)
            parsed_data: List of page dictionaries
            method: Parsing method used ('pypdf2', 'pdfplumber', or 'ocr')
            tables: Optional list of table dictionaries (default: None)

        Raises:
            PDFParsingError: If database operation fails
        """
        # Store in new format: Dict with pages and tables
        cache_data = {
            "pages": parsed_data,
            "tables": tables if tables is not None else []
        }

        parsed_doc = ParsedDocument(
            document_id=document_id,
            organization_id=organization_id,
            parsed_data=cache_data,
            parsing_method=method,
            parsed_at=datetime.utcnow(),
        )

        try:
            self.db.add(parsed_doc)
            self.db.flush()  # Flush to DB but don't commit
            self.db.refresh(parsed_doc)
        except Exception as e:
            # Don't rollback - let caller manage transaction
            logger.error(
                "Failed to cache parsed document",
                extra={
                    "event": "cache_write_failed",
                    "document_id": str(document_id),
                    "organization_id": str(organization_id),
                    "error": str(e),
                },
            )
            raise PDFParsingError(f"Failed to cache parsed document: {str(e)}")

    def _compile_section_patterns(
        self, patterns: List[str]
    ) -> List[re.Pattern]:
        """
        Compile and validate custom section detection patterns.

        Validates patterns to prevent ReDoS (Regular Expression Denial of Service).

        Args:
            patterns: List of regex pattern strings

        Returns:
            List of compiled regex patterns

        Raises:
            PDFParsingError: If pattern is invalid or too long
        """
        if len(patterns) > MAX_CUSTOM_PATTERNS:
            raise PDFParsingError(
                f"Too many custom patterns (max {MAX_CUSTOM_PATTERNS}): {len(patterns)}"
            )

        compiled_patterns = []

        for pattern_str in patterns:
            # Validate pattern length (prevent ReDoS)
            if len(pattern_str) > MAX_PATTERN_LENGTH:
                raise PDFParsingError(
                    f"Pattern too long (max {MAX_PATTERN_LENGTH} chars): {pattern_str[:50]}..."
                )

            # Check for dangerous ReDoS patterns (nested quantifiers)
            self._validate_redos_safety(pattern_str)

            # Try to compile pattern
            try:
                pattern = re.compile(pattern_str, re.MULTILINE)
                compiled_patterns.append(pattern)
            except re.error as e:
                raise PDFParsingError(
                    f"Invalid regex pattern '{pattern_str}': {str(e)}"
                )

        return compiled_patterns

    def _validate_redos_safety(self, pattern_str: str) -> None:
        """
        Validate regex pattern for ReDoS vulnerabilities.

        Checks for dangerous patterns that can cause exponential backtracking:
        - Nested quantifiers: (a+)+, (a*)*
        - Overlapping alternations: (a|a)*
        - Multiple quantifiers in sequence: a+*

        Args:
            pattern_str: Regex pattern string to validate

        Raises:
            PDFParsingError: If pattern contains dangerous constructs
        """
        # Check for nested quantifiers: (...)+ with quantifiers inside
        # Matches patterns like (a+)+, (x*)+, (y{2,5})*
        # Use [^)] instead of . to prevent catastrophic backtracking
        nested_quantifiers = re.compile(
            rf'\([^)]{{0,{REDOS_NESTED_QUANTIFIER_MAX_LENGTH}}}[+*?]\)[+*?]'
        )
        if nested_quantifiers.search(pattern_str):
            raise PDFParsingError(
                f"Pattern contains nested quantifiers (ReDoS risk): {pattern_str[:100]}..."
            )

        # Check for multiple quantifiers in sequence: a++, a**, a+*
        multiple_quantifiers = re.compile(r'[+*?]{2,}')
        if multiple_quantifiers.search(pattern_str):
            raise PDFParsingError(
                f"Pattern contains multiple consecutive quantifiers (ReDoS risk): {pattern_str[:100]}..."
            )

        # Check for overlapping alternations with quantifiers: (a|a)*, (ab|a)*
        # This is a simplified check - catches obvious cases
        alternation_pattern = re.compile(r'\([^()]*\|[^()]*\)[+*]')
        if alternation_pattern.search(pattern_str):
            # For production, consider using re2 library for guaranteed linear time
            logger.warning(
                "Pattern contains alternation with quantifier (potential ReDoS risk)",
                extra={
                    "event": "redos_warning_alternation",
                    "pattern": pattern_str[:100],
                },
            )
            # Note: We log a warning but don't block, as not all such patterns are dangerous
            # A full overlap analysis would require more complex logic

    def _validate_ocr_language(self, language: str) -> None:
        """
        Validate OCR language code to prevent command injection.

        Tesseract language codes must be 3-letter ISO 639-2 codes (e.g., "eng", "deu", "fra")
        or combined languages (e.g., "eng+deu"). This validation prevents command injection
        attacks via the language parameter.

        Args:
            language: OCR language code to validate

        Raises:
            PDFParsingError: If language code format is invalid

        Examples:
            >>> _validate_ocr_language("eng")  # Valid
            >>> _validate_ocr_language("eng+deu")  # Valid (combined)
            >>> _validate_ocr_language("eng; rm -rf /")  # Raises PDFParsingError
        """
        if not re.match(r'^[a-z]{3}(\+[a-z]{3})*$', language):
            raise PDFParsingError(
                f"Invalid OCR language code: {language}. "
                "Must be 3-letter ISO 639-2 code (e.g., 'eng', 'deu', 'fra') or combined (e.g., 'eng+deu')"
            )

    def _is_scanned_pdf(self, pages: List[Dict]) -> Tuple[bool, str]:
        """
        Detect if PDF contains scanned images (no extractable text).

        Checks if total extractable text across all pages is below a threshold,
        indicating the PDF is likely scanned/image-based.

        Args:
            pages: List of page dictionaries with extracted text

        Returns:
            Tuple of (is_scanned: bool, reason: str) for better debugging and observability
        """
        # Calculate total text length across all pages
        total_text = "".join(page.get("text", "") for page in pages)
        total_chars = len(total_text.strip())

        # Threshold: < SCANNED_PDF_CHAR_THRESHOLD characters for entire document = likely scanned
        # This accounts for PDFs with only metadata/headers but no body text
        if total_chars < SCANNED_PDF_CHAR_THRESHOLD:
            return True, f"total_chars={total_chars} < {SCANNED_PDF_CHAR_THRESHOLD}"

        # Additional check: If most pages have very little text, likely scanned
        pages_with_text = sum(
            1 for page in pages if len(page.get("text", "").strip()) > SCANNED_PDF_PAGE_TEXT_THRESHOLD
        )
        if pages_with_text < len(pages) * 0.5:  # Less than 50% of pages have text
            return True, f"only {pages_with_text}/{len(pages)} pages have text (>50% threshold)"

        return False, "sufficient_text"

    def _get_optimal_dpi(self, file_path: str, page_count: int) -> int:
        """
        Calculate optimal DPI for OCR based on available memory and page dimensions.

        Memory varies by page size:
        - A4 at 300 DPI: ~25 MB uncompressed
        - Legal at 300 DPI: ~30 MB
        - A3 at 300 DPI: ~50 MB

        Args:
            file_path: Path to PDF file (to read page dimensions)
            page_count: Number of pages to process

        Returns:
            Optimal DPI value (either OCR_DEFAULT_DPI or OCR_LOW_MEMORY_DPI)
        """
        if not MEMORY_MONITORING_AVAILABLE:
            # If psutil not available, use default DPI
            return OCR_DEFAULT_DPI

        try:
            # Read first page dimensions to estimate memory accurately
            # Note: PyPDF2 loads page metadata eagerly but page content lazily,
            # so accessing .pages[0].mediabox is fast and doesn't load full content
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                if len(reader.pages) == 0:
                    return OCR_DEFAULT_DPI

                first_page = reader.pages[0]
                # Get page dimensions in points (1/72 inch)
                # Access all page properties inside context manager for proper semantics
                width = float(first_page.mediabox.width)
                height = float(first_page.mediabox.height)

            # Convert to inches (PDF units are points: 1/72 inch)
            width_inches = width / 72
            height_inches = height / 72

            # Calculate memory per page: width * height * DPI² * bytes_per_pixel / 1MB
            # Use RGBA (4 bytes) instead of RGB (3 bytes) as pytesseract may use alpha channel
            # Add 20% safety margin for temporary buffers and processing overhead
            memory_mb_per_page = (
                width_inches * height_inches * OCR_DEFAULT_DPI * OCR_DEFAULT_DPI * OCR_BYTES_PER_PIXEL_RGBA
            ) / (1024 * 1024) * OCR_MEMORY_SAFETY_MARGIN

            # Get available memory in MB
            available_mb = psutil.virtual_memory().available / (1024 * 1024)

            # Calculate estimated memory usage at 300 DPI
            estimated_memory_mb = page_count * memory_mb_per_page

            # If estimated usage exceeds available memory, use lower DPI
            if estimated_memory_mb > available_mb:
                logger.info(
                    "Using low DPI for OCR due to memory constraints",
                    extra={
                        "event": "ocr_dpi_lowered",
                        "page_count": page_count,
                        "page_size_inches": f"{width_inches:.1f}x{height_inches:.1f}",
                        "memory_per_page_mb": round(memory_mb_per_page, 1),
                        "available_mb": int(available_mb),
                        "estimated_mb": int(estimated_memory_mb),
                        "dpi": OCR_LOW_MEMORY_DPI,
                    }
                )
                return OCR_LOW_MEMORY_DPI

            return OCR_DEFAULT_DPI

        except Exception as e:
            logger.warning(
                f"Failed to calculate optimal DPI, using default: {e}",
                extra={"event": "ocr_dpi_calculation_failed", "error": str(e)}
            )
            return OCR_DEFAULT_DPI

    def _extract_with_ocr(self, file_path: str, language: str = "eng") -> List[Dict]:
        """
        Extract text from scanned PDF using OCR (pytesseract).

        Converts PDF pages to images and runs OCR on each image.
        Processes pages one at a time to avoid memory issues.

        Args:
            file_path: Path to PDF file
            language: Tesseract language code (default: "eng", e.g., "deu", "fra")

        Returns:
            List of page dictionaries with OCR-extracted text

        Raises:
            PDFParsingError: If OCR dependencies unavailable or extraction fails
        """
        if not OCR_AVAILABLE:
            raise PDFParsingError(
                "OCR dependencies not available (pytesseract or pdf2image missing). "
                "Install with: pip install pytesseract pdf2image"
            )

        # Validate language parameter to prevent command injection
        self._validate_ocr_language(language)

        try:
            # Get page count first to avoid loading all pages into memory
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)

            # Validate page count to prevent integer overflow attacks
            if page_count > MAX_PAGE_COUNT:
                raise PDFParsingError(
                    f"PDF too large: {page_count} pages (max {MAX_PAGE_COUNT}). "
                    "This may be a malicious PDF attempting to cause resource exhaustion."
                )

            # Calculate optimal DPI based on available memory and page dimensions
            optimal_dpi = self._get_optimal_dpi(file_path, page_count)

            # Process pages one at a time to avoid memory issues
            # Converting 50 pages at 300 DPI = ~2.5GB memory
            pages = []
            for page_num in range(1, page_count + 1):
                try:
                    # Convert single page to image with optimal DPI
                    # DPI choice: 300 DPI (default) balances quality (readable text) vs memory (~5-25MB/page)
                    # Automatically lowered to 150 DPI in memory-constrained environments (Railway/Render 512MB tier)
                    # Lower DPI reduces quality but prevents OOM errors on large PDFs
                    images = convert_from_path(
                        file_path,
                        dpi=optimal_dpi,
                        first_page=page_num,
                        last_page=page_num
                    )

                    # Run OCR on the single page image with specified language
                    # Defense in depth: Use explicit config to prevent arbitrary options
                    # Add timeout to prevent hung OCR processes on malformed images
                    try:
                        text = pytesseract.image_to_string(
                            images[0],
                            lang=language,
                            config='--psm 1',  # Automatic page segmentation with OSD (Orientation and Script Detection)
                            timeout=OCR_TIMEOUT_SECONDS
                        )
                    except RuntimeError as timeout_error:
                        # pytesseract raises RuntimeError for timeouts (not a specific exception type)
                        # We use string matching as pytesseract doesn't provide a dedicated timeout exception
                        # This is the recommended approach from pytesseract documentation
                        error_msg = str(timeout_error).lower()
                        # Check for known timeout message patterns from pytesseract
                        is_timeout = (
                            "timeout" in error_msg
                            or "timed out" in error_msg
                            or "tesseract process timeout" in error_msg
                        )

                        if is_timeout:
                            logger.warning(
                                f"OCR timeout on page {page_num}",
                                extra={
                                    "event": "ocr_timeout",
                                    "page": page_num,
                                    "timeout_seconds": OCR_TIMEOUT_SECONDS,
                                    "error_message": str(timeout_error),
                                },
                            )
                            text = f"[OCR timeout on page {page_num}]"
                        else:
                            # Re-raise non-timeout RuntimeErrors (e.g., tesseract not installed, corrupt image)
                            # This ensures we don't silently swallow serious errors
                            raise

                    pages.append(
                        {
                            "page": page_num,
                            "text": text if text else "",
                            "section": None,
                        }
                    )
                    # Image is automatically freed after each iteration

                except Exception as page_error:
                    logger.warning(
                        f"OCR failed for page {page_num}",
                        extra={
                            "event": "ocr_page_failed",
                            "page": page_num,
                            "error": str(page_error),
                        },
                    )
                    pages.append(
                        {
                            "page": page_num,
                            "text": f"[Error parsing page {page_num}: {str(page_error)}]",
                            "section": None,
                        }
                    )

            return pages

        except Exception as e:
            raise PDFParsingError(f"OCR extraction failed: {str(e)}")

    def _extract_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF using tabula-py.

        Returns structured table data with columns, rows, and page numbers.

        Args:
            file_path: Path to PDF file

        Returns:
            List of table dictionaries:
            [
                {
                    "page": 1,
                    "columns": ["Column1", "Column2"],
                    "data": [{"Column1": "value1", "Column2": "value2"}, ...]
                },
                ...
            ]

        Raises:
            PDFParsingError: If table extraction is unavailable or fails
        """
        if not TABLE_EXTRACTION_AVAILABLE:
            logger.warning(
                "Table extraction unavailable",
                extra={
                    "event": "table_extraction_unavailable",
                    "file_path": file_path,
                }
            )
            return []

        try:
            # Extract tables from all pages
            # pages='all' extracts from every page
            # pandas_options={'header': 'infer'} tries to detect column headers
            tables_df = tabula.read_pdf(
                file_path,
                pages='all',
                multiple_tables=True,
                pandas_options={'header': 'infer'}
            )

            # Convert pandas DataFrames to structured dictionaries
            structured_tables = []
            for i, df in enumerate(tables_df):
                if df.empty:
                    continue

                # Get page number from tabula metadata (if available)
                # Note: tabula doesn't always provide page numbers reliably,
                # so we track by index
                page_num = i + 1  # Simple sequential numbering

                # Convert DataFrame to list of dictionaries
                columns = df.columns.tolist()
                data = df.to_dict('records')

                structured_tables.append({
                    "page": page_num,
                    "columns": columns,
                    "data": data
                })

            logger.info(
                "Table extraction completed",
                extra={
                    "event": "table_extraction_success",
                    "file_path": file_path,
                    "table_count": len(structured_tables),
                }
            )

            return structured_tables

        except Exception as e:
            # Don't raise - gracefully degrade
            logger.warning(
                "Table extraction failed",
                extra={
                    "event": "table_extraction_failed",
                    "file_path": file_path,
                    "error": str(e),
                }
            )
            return []
