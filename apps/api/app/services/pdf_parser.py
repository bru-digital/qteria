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
- OCR support (pytesseract for scanned PDFs)
- Table extraction (tabula-py for structured data)
- Parallel page processing (asyncio for performance)
- Configurable section patterns (custom regex per workflow)
"""
import re
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
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

# Optional table extraction (graceful degradation if Java not available)
try:
    import tabula
    TABLE_EXTRACTION_AVAILABLE = True
except ImportError:
    TABLE_EXTRACTION_AVAILABLE = False
    logger.warning(
        "Table extraction dependencies not available (tabula-py missing). "
        "Table extraction will be disabled."
    )


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
        enable_tables: bool = True,
        enable_parallel: bool = True,
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
            enable_tables: Enable table extraction (default: True)
            enable_parallel: Enable parallel page processing (default: True)

        Returns:
            Dict with:
                - document_id: UUID of the document
                - pages: List of {page_number, section, text}
                - tables: List of extracted tables (if enable_tables=True)
                - method: Parsing method used ('pypdf2', 'pdfplumber', 'ocr')
                - cached: Whether result came from cache

        Raises:
            EncryptedPDFError: If PDF is password-protected
            CorruptPDFError: If PDF is corrupt or malformed
            PDFParsingError: For other parsing failures
        """
        # Validate boolean parameters
        if not isinstance(enable_ocr, bool):
            raise PDFParsingError(f"enable_ocr must be a boolean, got {type(enable_ocr).__name__}")
        if not isinstance(enable_tables, bool):
            raise PDFParsingError(f"enable_tables must be a boolean, got {type(enable_tables).__name__}")
        if not isinstance(enable_parallel, bool):
            raise PDFParsingError(f"enable_parallel must be a boolean, got {type(enable_parallel).__name__}")

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
                "tables": cached_result["tables"],
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
                "enable_ocr": enable_ocr,
                "enable_tables": enable_tables,
                "enable_parallel": enable_parallel,
            },
        )

        # 3. Extract text with PyPDF2 (primary) or parallel extraction
        pages = []
        parsing_method = "pypdf2"

        try:
            if enable_parallel:
                # Use asyncio for parallel page processing
                pages = asyncio.run(self._parse_pdf_parallel(file_path))
                parsing_method = "pypdf2_parallel"
            else:
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
        if enable_ocr and self._is_scanned_pdf(pages):
            logger.info(
                "Scanned PDF detected, falling back to OCR",
                extra={
                    "event": "ocr_fallback",
                    "document_id": str(document_id),
                    "organization_id": str(organization_id),
                },
            )
            try:
                pages = self._extract_with_ocr(file_path)
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

        # 6. Extract tables if enabled
        tables = []
        if enable_tables:
            try:
                tables = self._extract_tables(file_path)
            except Exception as table_error:
                logger.warning(
                    "Table extraction failed",
                    extra={
                        "event": "table_extraction_failed",
                        "document_id": str(document_id),
                        "organization_id": str(organization_id),
                        "error": str(table_error),
                    },
                )
                # Continue without tables (graceful degradation)

        # 7. Detect sections across pages (with custom patterns if provided)
        structured_pages = self._detect_sections(pages, custom_patterns)

        # 8. Cache parsed result (including tables)
        result_data = {
            "pages": structured_pages,
            "tables": tables,
        }
        self._cache_parse(document_id, organization_id, result_data, parsing_method)

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
            Dict with pages, tables and method, or None if not cached
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
            # Handle both old format (pages only) and new format (pages + tables)
            if isinstance(cached.parsed_data, dict):
                # New format: {pages: [...], tables: [...]}
                return {
                    "pages": cached.parsed_data.get("pages", []),
                    "tables": cached.parsed_data.get("tables", []),
                    "method": cached.parsing_method,
                }
            else:
                # Old format: just list of pages
                return {
                    "pages": cached.parsed_data,
                    "tables": [],
                    "method": cached.parsing_method,
                }

        return None

    def _is_scanned_pdf(self, pages: List[Dict]) -> bool:
        """
        Detect if PDF contains scanned images (no extractable text).

        Checks if total extractable text across all pages is below a threshold,
        indicating the PDF is likely scanned/image-based.

        Args:
            pages: List of page dictionaries with extracted text

        Returns:
            True if PDF appears to be scanned, False otherwise
        """
        # Calculate total text length across all pages
        total_text = "".join(page.get("text", "") for page in pages)
        total_chars = len(total_text.strip())

        # Threshold: < 100 characters for entire document = likely scanned
        # This accounts for PDFs with only metadata/headers but no body text
        if total_chars < 100:
            return True

        # Additional check: If most pages have very little text, likely scanned
        pages_with_text = sum(
            1 for page in pages if len(page.get("text", "").strip()) > 20
        )
        if pages_with_text < len(pages) * 0.5:  # Less than 50% of pages have text
            return True

        return False

    def _extract_with_ocr(self, file_path: str) -> List[Dict]:
        """
        Extract text from scanned PDF using OCR (pytesseract).

        Converts PDF pages to images and runs OCR on each image.
        Processes pages one at a time to avoid memory issues.

        Args:
            file_path: Path to PDF file

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

        try:
            # Get page count first to avoid loading all pages into memory
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)

            # Process pages one at a time to avoid memory issues
            # Converting 50 pages at 300 DPI = ~2.5GB memory
            pages = []
            for page_num in range(1, page_count + 1):
                try:
                    # Convert single page to image
                    images = convert_from_path(
                        file_path,
                        dpi=300,
                        first_page=page_num,
                        last_page=page_num
                    )

                    # Run OCR on the single page image
                    text = pytesseract.image_to_string(images[0], lang="eng")
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
                            "text": f"[OCR error on page {page_num}]",
                            "section": None,
                        }
                    )

            return pages

        except Exception as e:
            raise PDFParsingError(f"OCR extraction failed: {str(e)}")

    def _extract_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF using tabula-py.

        Returns tables as list of dictionaries (one per table found).

        Args:
            file_path: Path to PDF file

        Returns:
            List of table dictionaries: [{"page": 1, "table_index": 0, "data": [...]}, ...]
            Each table's data is a list of dictionaries (rows with column headers as keys)

        Raises:
            PDFParsingError: If table extraction dependencies unavailable or Java missing
        """
        if not TABLE_EXTRACTION_AVAILABLE:
            raise PDFParsingError(
                "Table extraction dependencies not available (tabula-py missing). "
                "Install with: pip install tabula-py"
            )

        # Check if Java is available (required by tabula-py)
        if not self._check_java_available():
            logger.warning(
                "Java runtime not available - table extraction disabled",
                extra={"event": "java_missing"},
            )
            return []

        try:
            # Extract all tables from PDF (all pages)
            # read_pdf returns list of DataFrames (one per table)
            dfs = tabula.read_pdf(file_path, pages="all", multiple_tables=True)

            tables = []
            for idx, df in enumerate(dfs):
                # Convert DataFrame to list of dictionaries (rows)
                table_data = df.to_dict(orient="records")

                tables.append(
                    {
                        "table_index": idx,
                        "data": table_data,
                        "columns": list(df.columns),
                        "row_count": len(df),
                    }
                )

            return tables

        except Exception as e:
            logger.warning(
                "Table extraction failed",
                extra={"event": "table_extraction_error", "error": str(e)},
            )
            return []

    def _check_java_available(self) -> bool:
        """
        Check if Java runtime is available and version is 8+ (required for tabula-py).

        Returns:
            True if Java 8+ is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return False

            # Java prints version to stderr
            version_output = result.stderr

            # Parse Java version from output
            # Examples:
            # - Java 8: 'java version "1.8.0_XXX"'
            # - Java 11+: 'openjdk version "11.0.XX"' or 'java version "17.0.XX"'
            import re
            version_match = re.search(r'version "(\d+)\.(\d+)', version_output)

            if not version_match:
                # If we can't parse version, warn but allow (graceful degradation)
                logger.warning(
                    "Could not parse Java version, assuming compatible",
                    extra={"event": "java_version_unknown", "output": version_output}
                )
                return True

            major_version = int(version_match.group(1))
            minor_version = int(version_match.group(2))

            # Java 8 is reported as "1.8", Java 9+ as "9", "11", "17", etc.
            if major_version == 1 and minor_version >= 8:
                return True  # Java 8 (reported as 1.8)
            elif major_version >= 9:
                return True  # Java 9+

            # Java version too old
            logger.warning(
                f"Java version {major_version}.{minor_version} is too old (need 8+)",
                extra={"event": "java_version_too_old", "version": f"{major_version}.{minor_version}"}
            )
            return False

        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def _parse_pdf_parallel(self, file_path: str) -> List[Dict]:
        """
        Parse PDF pages in parallel using asyncio.

        Extracts text from all pages concurrently for faster processing.

        Args:
            file_path: Path to PDF file

        Returns:
            List of page dictionaries with text (order preserved)

        Raises:
            CorruptPDFError: If PDF parsing fails
        """
        try:
            # Read all pages while file is open to avoid file handle issues
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                if reader.is_encrypted:
                    raise EncryptedPDFError("PDF is encrypted")

                # Extract page objects while file is open
                # Store tuples of (page_num, page_object) for processing
                page_objects = [
                    (page_num, page)
                    for page_num, page in enumerate(reader.pages, start=1)
                ]

            # Now create async tasks with the extracted page objects
            # File is safely closed, but page objects remain valid
            tasks = [
                self._parse_page_async(page_num, page)
                for page_num, page in page_objects
            ]

            # Execute all tasks concurrently
            page_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and return valid pages
            pages = []
            for idx, result in enumerate(page_results, start=1):
                if isinstance(result, Exception):
                    logger.warning(
                        "Parallel page parsing failed",
                        extra={"event": "parallel_page_error", "error": str(result), "page": idx},
                    )
                    # Continue with error placeholder (use correct page number from iteration)
                    pages.append(
                        {
                            "page": idx,
                            "text": f"[Error: {str(result)}]",
                            "section": None,
                        }
                    )
                else:
                    pages.append(result)

            return pages

        except PyPDF2.errors.PdfReadError as e:
            raise CorruptPDFError(f"PyPDF2 failed to read PDF: {str(e)}")
        except Exception as e:
            raise CorruptPDFError(f"Unexpected error in parallel parsing: {str(e)}")

    async def _parse_page_async(
        self, page_num: int, page: PyPDF2.PageObject
    ) -> Dict:
        """
        Extract text from a single PDF page asynchronously.

        Args:
            page_num: Page number (1-indexed)
            page: PyPDF2 page object

        Returns:
            Dictionary with page number and extracted text
        """
        # Run blocking I/O in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, page.extract_text)

        return {
            "page": page_num,
            "text": text if text else "",
            "section": None,
        }

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
        compiled_patterns = []

        for pattern_str in patterns:
            # Validate pattern length (prevent ReDoS)
            if len(pattern_str) > 1000:
                raise PDFParsingError(
                    f"Pattern too long (max 1000 chars): {pattern_str[:50]}..."
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
        nested_quantifiers = re.compile(
            r'\([^()]*[+*?]\)[+*?]'  # Simple case: (a+)+
            r'|\([^()]*\{[0-9]+,[0-9]*\}\)[+*?]'  # With counted: (a{2,5})+
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
            # Further validate: check if alternations overlap
            # Extract the alternation group
            import warnings
            warnings.warn(
                f"Pattern contains alternation with quantifier - verify no overlapping branches: {pattern_str[:100]}",
                UserWarning
            )
            # Note: Full overlap detection is complex, so we just warn
            # For production, consider using re2 library for guaranteed linear time

    def _cache_parse(
        self, document_id: UUID, organization_id: UUID, parsed_data: Dict[str, Any], method: str
    ) -> None:
        """
        Store parsed text and tables in database cache.

        Note: This method uses flush() instead of commit() to allow the caller
        to manage the transaction. The caller should commit after all operations
        are complete.

        Args:
            document_id: UUID of the document
            organization_id: UUID of the organization (for multi-tenancy)
            parsed_data: Dictionary with 'pages' and 'tables' keys
            method: Parsing method used ('pypdf2', 'pdfplumber', 'ocr', 'pypdf2_parallel')

        Raises:
            PDFParsingError: If database operation fails
        """
        parsed_doc = ParsedDocument(
            document_id=document_id,
            organization_id=organization_id,
            parsed_data=parsed_data,
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
