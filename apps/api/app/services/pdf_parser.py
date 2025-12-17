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
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime

import PyPDF2
import pdfplumber
from sqlalchemy.orm import Session

from app.models.models import ParsedDocument

logger = logging.getLogger(__name__)

# Configuration constants
MAX_PATTERN_LENGTH = 1000  # Maximum allowed regex pattern length
MAX_CUSTOM_PATTERNS = 100  # Maximum number of custom patterns allowed
REDOS_NESTED_QUANTIFIER_MAX_LENGTH = 50  # Max chars inside nested quantifiers to prevent ReDoS


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

        Returns:
            Dict with:
                - document_id: UUID of the document
                - pages: List of {page_number, section, text}
                - method: Parsing method used ('pypdf2' or 'pdfplumber')
                - cached: Whether result came from cache

        Raises:
            EncryptedPDFError: If PDF is password-protected
            CorruptPDFError: If PDF is corrupt or malformed
            PDFParsingError: For other parsing failures
        """
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

        # 5. Detect sections across pages
        structured_pages = self._detect_sections(pages, custom_patterns)

        # 6. Cache parsed result
        self._cache_parse(document_id, organization_id, structured_pages, parsing_method)

        return {
            "document_id": document_id,
            "pages": structured_pages,
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
            Dict with pages and method, or None if not cached
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
            return {
                "pages": cached.parsed_data,
                "method": cached.parsing_method,
            }

        return None

    def _cache_parse(
        self, document_id: UUID, organization_id: UUID, parsed_data: List[Dict], method: str
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
            method: Parsing method used ('pypdf2' or 'pdfplumber')

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
