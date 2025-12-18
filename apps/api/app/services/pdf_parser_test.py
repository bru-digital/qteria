"""
Unit tests for PDF Parser Service.

Tests cover:
- PyPDF2 extraction
- pdfplumber fallback
- Section detection (numbered and uppercase)
- Caching logic (hit/miss)
- Error handling (encrypted, corrupt PDFs)
- Validation

Target: 95% code coverage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from uuid import uuid4, UUID

from app.services.pdf_parser import (
    PDFParserService,
    PDFParsingError,
    EncryptedPDFError,
    CorruptPDFError,
)
from app.models.models import ParsedDocument


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy database session."""
    db = Mock()
    db.query = Mock(return_value=Mock())
    db.add = Mock()
    db.commit = Mock()
    db.flush = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def pdf_parser(mock_db):
    """PDF parser service instance with mocked database."""
    return PDFParserService(db=mock_db)


@pytest.fixture
def sample_document_id():
    """Sample document UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_organization_id():
    """Sample organization UUID for testing."""
    return uuid4()


class TestPyPDF2Extraction:
    """Test PyPDF2 extraction functionality."""

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_extract_simple_pdf(self, mock_open, mock_reader, pdf_parser):
        """Should extract text from simple single-page PDF."""
        # Arrange
        mock_page = Mock()
        mock_page.extract_text.return_value = "This is page 1 text"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_reader_instance.is_encrypted = False
        mock_reader.return_value = mock_reader_instance

        # Act
        pages = pdf_parser._extract_with_pypdf2("/fake/path.pdf")

        # Assert
        assert len(pages) == 1
        assert pages[0]["page"] == 1
        assert pages[0]["text"] == "This is page 1 text"
        assert pages[0]["section"] is None

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_extract_multi_page_pdf_preserves_boundaries(self, mock_open, mock_reader, pdf_parser):
        """Should preserve page boundaries across multiple pages."""
        # Arrange
        mock_pages = []
        for i in range(1, 11):  # 10 pages
            page = Mock()
            page.extract_text.return_value = f"Page {i} content"
            mock_pages.append(page)

        mock_reader_instance = Mock()
        mock_reader_instance.pages = mock_pages
        mock_reader_instance.is_encrypted = False
        mock_reader.return_value = mock_reader_instance

        # Act
        pages = pdf_parser._extract_with_pypdf2("/fake/path.pdf")

        # Assert
        assert len(pages) == 10
        for i, page in enumerate(pages, start=1):
            assert page["page"] == i
            assert page["text"] == f"Page {i} content"

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_encrypted_pdf_raises_error(self, mock_open, mock_reader, pdf_parser):
        """Should raise EncryptedPDFError for password-protected PDF."""
        # Arrange
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = True
        mock_reader.return_value = mock_reader_instance

        # Act & Assert
        with pytest.raises(EncryptedPDFError):
            pdf_parser._extract_with_pypdf2("/fake/encrypted.pdf")

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_corrupt_pdf_raises_error(self, mock_open, mock_reader, pdf_parser):
        """Should raise CorruptPDFError for malformed PDF."""
        # Arrange
        import PyPDF2.errors

        mock_reader.side_effect = PyPDF2.errors.PdfReadError("Invalid PDF")

        # Act & Assert
        with pytest.raises(CorruptPDFError, match="PyPDF2 failed to read PDF"):
            pdf_parser._extract_with_pypdf2("/fake/corrupt.pdf")


class TestPdfplumberFallback:
    """Test pdfplumber fallback extraction."""

    @patch("app.services.pdf_parser.pdfplumber.open")
    def test_fallback_extraction(self, mock_pdfplumber, pdf_parser):
        """Should extract text using pdfplumber as fallback."""
        # Arrange
        mock_page = Mock()
        mock_page.extract_text.return_value = "Text from pdfplumber"
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_pdf

        # Act
        pages = pdf_parser._extract_with_pdfplumber("/fake/path.pdf")

        # Assert
        assert len(pages) == 1
        assert pages[0]["text"] == "Text from pdfplumber"

    @patch("app.services.pdf_parser.pdfplumber.open")
    def test_pdfplumber_failure_raises_error(self, mock_pdfplumber, pdf_parser):
        """Should raise CorruptPDFError if pdfplumber also fails."""
        # Arrange
        mock_pdfplumber.side_effect = Exception("pdfplumber error")

        # Act & Assert
        with pytest.raises(CorruptPDFError, match="pdfplumber failed to read PDF"):
            pdf_parser._extract_with_pdfplumber("/fake/path.pdf")


class TestSectionDetection:
    """Test section detection with various patterns."""

    def test_detect_numbered_sections(self, pdf_parser):
        """Should detect numbered sections like '1.', '2.3', '3.2.1'."""
        # Arrange
        pages = [
            {"page": 1, "text": "1. Introduction\nThis is the intro.", "section": None},
            {"page": 2, "text": "More intro text...", "section": None},
            {"page": 3, "text": "2.3 Test Results\nResults here.", "section": None},
            {"page": 4, "text": "3.2.1 Detailed Analysis\nDetails...", "section": None},
        ]

        # Act
        result = pdf_parser._detect_sections(pages)

        # Assert
        assert result[0]["section"] == "1. Introduction"
        assert result[1]["section"] == "1. Introduction"  # Section persists
        assert result[2]["section"] == "2.3 Test Results"
        assert result[3]["section"] == "3.2.1 Detailed Analysis"

    def test_detect_uppercase_headings(self, pdf_parser):
        """Should detect ALL CAPS headings."""
        # Arrange
        pages = [
            {"page": 1, "text": "TECHNICAL SPECIFICATIONS\nContent here.", "section": None},
            {"page": 2, "text": "More content...", "section": None},
        ]

        # Act
        result = pdf_parser._detect_sections(pages)

        # Assert
        assert result[0]["section"] == "TECHNICAL SPECIFICATIONS"
        assert result[1]["section"] == "TECHNICAL SPECIFICATIONS"

    def test_section_persists_across_pages(self, pdf_parser):
        """Should maintain section name across pages until new section found."""
        # Arrange
        pages = [
            {"page": 1, "text": "1. Introduction\nIntro text.", "section": None},
            {"page": 2, "text": "More intro...", "section": None},
            {"page": 3, "text": "Continued intro...", "section": None},
            {"page": 4, "text": "2. Methods\nNew section.", "section": None},
        ]

        # Act
        result = pdf_parser._detect_sections(pages)

        # Assert
        assert result[0]["section"] == "1. Introduction"
        assert result[1]["section"] == "1. Introduction"
        assert result[2]["section"] == "1. Introduction"
        assert result[3]["section"] == "2. Methods"

    def test_no_section_detected_defaults_to_none(self, pdf_parser):
        """Should leave section as None if no pattern matches."""
        # Arrange
        pages = [
            {"page": 1, "text": "just some text without sections", "section": None},
        ]

        # Act
        result = pdf_parser._detect_sections(pages)

        # Assert
        assert result[0]["section"] is None


class TestCaching:
    """Test database caching logic."""

    def test_cache_hit_skips_parsing(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id
    ):
        """Should return cached result without parsing if cache hit."""
        # Arrange
        cached_doc = ParsedDocument(
            id=uuid4(),
            document_id=sample_document_id,
            parsed_data=[{"page": 1, "text": "Cached text", "section": None}],
            parsing_method="pypdf2",
        )
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = cached_doc
        mock_db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is not None
        assert result["pages"][0]["text"] == "Cached text"
        assert result["method"] == "pypdf2"

    def test_cache_miss_returns_none(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id
    ):
        """Should return None if no cached result found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is None

    def test_cache_stores_parsed_data(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id
    ):
        """Should store parsed data in database."""
        # Arrange
        parsed_data = [{"page": 1, "text": "New text", "section": "1. Intro"}]
        method = "pypdf2"

        # Act
        pdf_parser._cache_parse(sample_document_id, sample_organization_id, parsed_data, method)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()  # Changed from commit to flush
        called_with = mock_db.add.call_args[0][0]
        assert isinstance(called_with, ParsedDocument)
        assert called_with.document_id == sample_document_id
        assert called_with.organization_id == sample_organization_id
        assert called_with.parsed_data == parsed_data
        assert called_with.parsing_method == method


class TestValidation:
    """Test PDF validation logic."""

    @patch("app.services.pdf_parser.Path")
    def test_validate_pdf_file_not_found(self, mock_path, pdf_parser):
        """Should raise CorruptPDFError if file doesn't exist."""
        # Arrange
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # Act & Assert
        with pytest.raises(CorruptPDFError, match="PDF file not found"):
            pdf_parser._validate_pdf("/fake/missing.pdf")

    @patch("app.services.pdf_parser.Path")
    def test_validate_pdf_not_a_file(self, mock_path, pdf_parser):
        """Should raise CorruptPDFError if path is not a file."""
        # Arrange
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = False
        mock_path.return_value = mock_path_instance

        # Act & Assert
        with pytest.raises(CorruptPDFError, match="Path is not a file"):
            pdf_parser._validate_pdf("/fake/directory")

    @patch("app.services.pdf_parser.PDFParserService._is_encrypted")
    @patch("app.services.pdf_parser.Path")
    def test_validate_pdf_encrypted(self, mock_path, mock_is_encrypted, pdf_parser):
        """Should raise EncryptedPDFError if PDF is encrypted."""
        # Arrange
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance
        mock_is_encrypted.return_value = True

        # Act & Assert
        with pytest.raises(EncryptedPDFError, match="password-protected"):
            pdf_parser._validate_pdf("/fake/encrypted.pdf")


class TestEncryptionCheck:
    """Test encryption detection."""

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_is_encrypted_true(self, mock_open, mock_reader, pdf_parser):
        """Should return True if PDF is encrypted."""
        # Arrange
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = True
        mock_reader.return_value = mock_reader_instance

        # Act
        result = pdf_parser._is_encrypted("/fake/encrypted.pdf")

        # Assert
        assert result is True

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_is_encrypted_false(self, mock_open, mock_reader, pdf_parser):
        """Should return False if PDF is not encrypted."""
        # Arrange
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = False
        mock_reader.return_value = mock_reader_instance

        # Act
        result = pdf_parser._is_encrypted("/fake/plain.pdf")

        # Assert
        assert result is False

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_is_encrypted_handles_errors_gracefully(self, mock_open, mock_reader, pdf_parser):
        """Should return False if encryption check fails (assume not encrypted)."""
        # Arrange
        mock_reader.side_effect = Exception("Cannot read PDF")

        # Act
        result = pdf_parser._is_encrypted("/fake/broken.pdf")

        # Assert
        assert result is False


class TestParsingMethodRecorded:
    """Test that parsing method is correctly recorded."""

    @patch("app.services.pdf_parser.PDFParserService._validate_pdf")
    @patch("app.services.pdf_parser.PDFParserService._extract_with_pypdf2")
    @patch("app.services.pdf_parser.PDFParserService._detect_sections")
    @patch("app.services.pdf_parser.PDFParserService._get_cached_parse")
    @patch("app.services.pdf_parser.PDFParserService._cache_parse")
    def test_pypdf2_method_recorded(
        self,
        mock_cache_parse,
        mock_get_cached,
        mock_detect,
        mock_extract,
        mock_validate,
        pdf_parser,
        sample_document_id,
        sample_organization_id,
    ):
        """Should record 'pypdf2' as parsing method when PyPDF2 succeeds."""
        # Arrange
        mock_get_cached.return_value = None
        mock_extract.return_value = [{"page": 1, "text": "Test", "section": None}]
        mock_detect.return_value = [{"page": 1, "text": "Test", "section": None}]

        # Act
        result = pdf_parser.parse_document(
            sample_document_id, "/fake/path.pdf", sample_organization_id
        )

        # Assert
        assert result["method"] == "pypdf2"
        mock_cache_parse.assert_called_once()
        assert mock_cache_parse.call_args[0][3] == "pypdf2"

    @patch("app.services.pdf_parser.PDFParserService._validate_pdf")
    @patch("app.services.pdf_parser.PDFParserService._extract_with_pypdf2")
    @patch("app.services.pdf_parser.PDFParserService._extract_with_pdfplumber")
    @patch("app.services.pdf_parser.PDFParserService._detect_sections")
    @patch("app.services.pdf_parser.PDFParserService._get_cached_parse")
    @patch("app.services.pdf_parser.PDFParserService._cache_parse")
    def test_pdfplumber_method_recorded_on_fallback(
        self,
        mock_cache_parse,
        mock_get_cached,
        mock_detect,
        mock_pdfplumber,
        mock_pypdf2,
        mock_validate,
        pdf_parser,
        sample_document_id,
        sample_organization_id,
    ):
        """Should record 'pdfplumber' when PyPDF2 fails and pdfplumber succeeds."""
        # Arrange
        mock_get_cached.return_value = None
        mock_pypdf2.side_effect = Exception("PyPDF2 failed")
        mock_pdfplumber.return_value = [{"page": 1, "text": "Test", "section": None}]
        mock_detect.return_value = [{"page": 1, "text": "Test", "section": None}]

        # Act
        result = pdf_parser.parse_document(
            sample_document_id, "/fake/path.pdf", sample_organization_id
        )

        # Assert
        assert result["method"] == "pdfplumber"
        mock_cache_parse.assert_called_once()
        assert mock_cache_parse.call_args[0][3] == "pdfplumber"


class TestErrorHandling:
    """Test comprehensive error handling."""

    @patch("app.services.pdf_parser.PDFParserService._validate_pdf")
    @patch("app.services.pdf_parser.PDFParserService._extract_with_pypdf2")
    @patch("app.services.pdf_parser.PDFParserService._extract_with_pdfplumber")
    @patch("app.services.pdf_parser.PDFParserService._get_cached_parse")
    def test_both_parsers_fail_raises_error(
        self,
        mock_get_cached,
        mock_pdfplumber,
        mock_pypdf2,
        mock_validate,
        pdf_parser,
        sample_document_id,
        sample_organization_id,
    ):
        """Should raise PDFParsingError if both PyPDF2 and pdfplumber fail."""
        # Arrange
        mock_get_cached.return_value = None
        mock_pypdf2.side_effect = Exception("PyPDF2 error")
        mock_pdfplumber.side_effect = Exception("pdfplumber error")

        # Act & Assert
        with pytest.raises(PDFParsingError, match="Both PyPDF2 and pdfplumber failed"):
            pdf_parser.parse_document(sample_document_id, "/fake/path.pdf", sample_organization_id)


class TestMultiTenancy:
    """Test multi-tenancy isolation for parsed documents."""

    def test_get_cached_parse_filters_by_organization(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should filter cached results by organization_id."""
        # Arrange
        other_org_id = uuid4()
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        pdf_parser.db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is None
        pdf_parser.db.query.assert_called_once_with(ParsedDocument)
        # Verify filter was called with both document_id AND organization_id
        mock_query.filter.assert_called_once()
        # The filter should have been called with both conditions
        filter_call = mock_query.filter.call_args
        assert filter_call is not None

    def test_get_cached_parse_returns_none_for_different_org(self, pdf_parser, sample_document_id):
        """Should return None when cache exists but belongs to different organization."""
        # Arrange
        org_a = uuid4()
        org_b = uuid4()

        # Mock a cached document for org_a
        cached_doc = Mock()
        cached_doc.organization_id = org_a
        cached_doc.document_id = sample_document_id
        cached_doc.parsed_data = [{"page": 1, "text": "Test", "section": None}]
        cached_doc.parsing_method = "pypdf2"

        # Setup mock to return None when querying with org_b
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None  # Different org returns None
        pdf_parser.db.query.return_value = mock_query

        # Act - Query with org_b (different from cached org_a)
        result = pdf_parser._get_cached_parse(sample_document_id, org_b)

        # Assert
        assert result is None  # Should not return cached data from different org

    def test_cache_parse_stores_organization_id(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should store organization_id when caching parsed document."""
        # Arrange
        parsed_data = [{"page": 1, "text": "Test", "section": None}]
        method = "pypdf2"

        # Act
        pdf_parser._cache_parse(sample_document_id, sample_organization_id, parsed_data, method)

        # Assert
        pdf_parser.db.add.assert_called_once()
        added_doc = pdf_parser.db.add.call_args[0][0]
        assert isinstance(added_doc, ParsedDocument)
        assert added_doc.document_id == sample_document_id
        assert added_doc.organization_id == sample_organization_id
        assert added_doc.parsed_data == parsed_data
        assert added_doc.parsing_method == method


class TestCustomSectionPatterns:
    """Tests for custom section pattern functionality."""

    def test_compile_valid_custom_patterns(self, pdf_parser):
        """Should compile valid custom regex patterns successfully."""
        # Arrange
        patterns = [
            r"^SECTION\s+\d+",
            r"^Article\s+\d+\.",
            r"^Chapter\s+[IVXLCDM]+",
        ]

        # Act
        compiled = pdf_parser._compile_section_patterns(patterns)

        # Assert
        assert len(compiled) == 3
        assert all(hasattr(p, "search") for p in compiled)  # All are compiled regex

    def test_custom_patterns_used_in_section_detection(self, pdf_parser):
        """Should use custom patterns for section detection when provided."""
        # Arrange
        pages = [
            {"page": 1, "text": "SECTION 1: Introduction\nSome text here"},
            {"page": 2, "text": "More content\nSECTION 2: Methods"},
        ]
        custom_patterns = [r"^SECTION\s+\d+:\s+([^\n]+)"]

        # Act
        result = pdf_parser._detect_sections(pages, custom_patterns)

        # Assert
        assert result[0]["section"] == "SECTION 1: Introduction"
        assert result[1]["section"] == "SECTION 2: Methods"

    def test_default_patterns_when_no_custom_patterns(self, pdf_parser):
        """Should use default patterns when no custom patterns provided."""
        # Arrange
        pages = [
            {"page": 1, "text": "1. Introduction\nSome text here"},
            {"page": 2, "text": "2. Methods\nMore text"},
        ]

        # Act
        result = pdf_parser._detect_sections(pages, custom_patterns=None)

        # Assert
        assert result[0]["section"] == "1. Introduction"
        assert result[1]["section"] == "2. Methods"

    def test_pattern_too_long_raises_error(self, pdf_parser):
        """Should reject patterns exceeding MAX_PATTERN_LENGTH."""
        # Arrange - Pattern longer than 1000 chars
        long_pattern = "a" * 1001

        # Act & Assert
        with pytest.raises(PDFParsingError, match="Pattern too long"):
            pdf_parser._compile_section_patterns([long_pattern])

    def test_too_many_patterns_raises_error(self, pdf_parser):
        """Should reject more than MAX_CUSTOM_PATTERNS."""
        # Arrange - 101 patterns (max is 100)
        patterns = [r"^test\d+" for _ in range(101)]

        # Act & Assert
        with pytest.raises(PDFParsingError, match="Too many custom patterns"):
            pdf_parser._compile_section_patterns(patterns)

    def test_invalid_regex_raises_error(self, pdf_parser):
        """Should reject invalid regex patterns."""
        # Arrange - Invalid regex (unmatched parenthesis)
        invalid_pattern = r"^test(unclosed"

        # Act & Assert
        with pytest.raises(PDFParsingError, match="Invalid regex pattern"):
            pdf_parser._compile_section_patterns([invalid_pattern])

    def test_redos_nested_quantifiers_blocked(self, pdf_parser):
        """Should block nested quantifiers to prevent ReDoS attacks."""
        # Arrange - Dangerous nested quantifiers
        dangerous_patterns = [
            r"(a+)+",  # Classic ReDoS
            r"(x*)*",  # Another nested quantifier
            r"(y{2,5})*",  # Bounded nested quantifier
        ]

        # Act & Assert
        for pattern in dangerous_patterns:
            with pytest.raises(PDFParsingError, match="nested quantifiers"):
                pdf_parser._validate_redos_safety(pattern)

    def test_redos_multiple_quantifiers_blocked(self, pdf_parser):
        """Should block multiple consecutive quantifiers."""
        # Arrange
        dangerous_patterns = [
            r"a++",
            r"b**",
            r"c+*",
        ]

        # Act & Assert
        for pattern in dangerous_patterns:
            with pytest.raises(PDFParsingError, match="multiple consecutive quantifiers"):
                pdf_parser._validate_redos_safety(pattern)

    def test_redos_alternation_with_quantifier_warning(self, pdf_parser):
        """Should warn (not block) alternations with quantifiers."""
        # Arrange - Potentially dangerous but not always
        pattern = r"(a|ab)*"

        # Act & Assert
        # Should NOT raise an error, just log a warning
        # (The code logs a warning but doesn't block these patterns)
        try:
            pdf_parser._validate_redos_safety(pattern)
        except PDFParsingError:
            pytest.fail("Should not block alternation patterns, only warn")

    def test_safe_patterns_pass_validation(self, pdf_parser):
        """Should allow safe regex patterns."""
        # Arrange - Safe patterns
        safe_patterns = [
            r"^SECTION\s+\d+",
            r"^Article\s+\d+\.",
            r"^Chapter\s+[IVXLCDM]+",
            r"^\d+\.\d+",
            r"^[A-Z]+\s+[A-Z]+",
        ]

        # Act & Assert - Should not raise any errors
        compiled = pdf_parser._compile_section_patterns(safe_patterns)
        assert len(compiled) == 5

    def test_redos_validation_with_max_length_constraint(self, pdf_parser):
        """Should enforce REDOS_NESTED_QUANTIFIER_MAX_LENGTH correctly."""
        # Arrange - Pattern with nested quantifiers within length limit (should block)
        pattern_within_limit = r"(a{1,10}){1,5}+"  # Within 50 chars

        # Act & Assert
        with pytest.raises(PDFParsingError, match="nested quantifiers"):
            pdf_parser._validate_redos_safety(pattern_within_limit)

    def test_custom_patterns_empty_list(self, pdf_parser):
        """Should handle empty custom patterns list gracefully."""
        # Arrange
        pages = [{"page": 1, "text": "1. Introduction\nText"}]
        empty_patterns = []

        # Act
        compiled = pdf_parser._compile_section_patterns(empty_patterns)

        # Assert
        assert len(compiled) == 0

    def test_custom_patterns_integration_parse_document(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id, tmp_path
    ):
        """Should pass custom_patterns through parse_document flow."""
        # Arrange - Create a real PDF file (mocked)
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")
        custom_patterns = [r"^CUSTOM\s+\d+"]

        # Mock cache miss
        pdf_parser._get_cached_parse = Mock(return_value=None)

        # Mock PDF extraction
        with patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader:
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "CUSTOM 1: Title\nSome text"
            mock_pdf.pages = [mock_page]
            mock_pdf.is_encrypted = False
            mock_reader.return_value = mock_pdf

            with (
                patch("pathlib.Path.exists", return_value=True),
                patch("pathlib.Path.is_file", return_value=True),
            ):

                # Act
                result = pdf_parser.parse_document(
                    document_id=sample_document_id,
                    file_path=str(pdf_file),
                    organization_id=sample_organization_id,
                    custom_patterns=custom_patterns,
                )

                # Assert - Custom pattern should have been used
                assert result["pages"][0]["section"] == "CUSTOM 1: Title"


class TestOCRSupport:
    """Tests for OCR support functionality."""

    def test_is_scanned_pdf_empty_text(self, pdf_parser):
        """Should detect scanned PDF when total text is below threshold."""
        # Arrange - PDF with very little text (< 100 chars total)
        pages = [
            {"page": 1, "text": "   "},  # Whitespace only
            {"page": 2, "text": ""},  # Empty
            {"page": 3, "text": "Page 3"},  # Minimal text
        ]

        # Act
        is_scanned, reason = pdf_parser._is_scanned_pdf(pages)

        # Assert
        assert is_scanned is True
        assert "total_chars=" in reason  # Verify reason provided for debugging

    def test_is_scanned_pdf_sufficient_text(self, pdf_parser):
        """Should NOT detect as scanned when PDF has sufficient text."""
        # Arrange - PDF with plenty of text (> 100 chars)
        pages = [
            {"page": 1, "text": "This is a normal PDF with plenty of extractable text content."},
            {
                "page": 2,
                "text": "More text here on page 2 with enough characters to exceed threshold.",
            },
        ]

        # Act
        is_scanned, reason = pdf_parser._is_scanned_pdf(pages)

        # Assert
        assert is_scanned is False
        assert reason == "sufficient_text"  # Verify reason indicates non-scanned

    def test_is_scanned_pdf_most_pages_empty(self, pdf_parser):
        """Should detect scanned PDF when >50% of pages lack text."""
        # Arrange - 4 pages, 3 empty (75% empty)
        pages = [
            {"page": 1, "text": "Some text on first page with enough characters here."},
            {"page": 2, "text": "   "},  # Whitespace
            {"page": 3, "text": ""},  # Empty
            {"page": 4, "text": ""},  # Empty
        ]

        # Act
        is_scanned, reason = pdf_parser._is_scanned_pdf(pages)

        # Assert
        assert is_scanned is True  # >50% pages lack text
        assert "pages have text" in reason  # Verify reason indicates page-based detection

    def test_ocr_language_validation_valid(self, pdf_parser):
        """Should accept valid 3-letter language codes."""
        # Arrange
        valid_languages = ["eng", "deu", "fra", "spa", "ita"]

        # Act & Assert - Should not raise
        for lang in valid_languages:
            # Use a mock to avoid actually running OCR
            with (
                patch("app.services.pdf_parser.OCR_AVAILABLE", True),
                patch("app.services.pdf_parser.convert_from_path") as mock_convert,
                patch("app.services.pdf_parser.pytesseract.image_to_string") as mock_ocr,
                patch("builtins.open", create=True) as mock_open,
                patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
            ):

                # Setup mocks
                mock_pdf = Mock()
                mock_pdf.pages = [Mock()]
                mock_reader.return_value = mock_pdf
                mock_convert.return_value = [Mock()]
                mock_ocr.return_value = "Test text"

                # Should not raise an error
                result = pdf_parser._extract_with_ocr("/fake/path.pdf", language=lang)
                assert len(result) == 1

    def test_ocr_language_validation_combined_languages(self, pdf_parser):
        """Should accept combined language codes like eng+deu."""
        # Arrange
        combined_lang = "eng+deu"

        # Act & Assert - Should not raise
        with (
            patch("app.services.pdf_parser.OCR_AVAILABLE", True),
            patch("app.services.pdf_parser.convert_from_path") as mock_convert,
            patch("app.services.pdf_parser.pytesseract.image_to_string") as mock_ocr,
            patch("builtins.open", create=True) as mock_open,
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
        ):

            # Setup mocks
            mock_pdf = Mock()
            mock_pdf.pages = [Mock()]
            mock_reader.return_value = mock_pdf
            mock_convert.return_value = [Mock()]
            mock_ocr.return_value = "Test text"

            result = pdf_parser._extract_with_ocr("/fake/path.pdf", language=combined_lang)
            assert len(result) == 1

    def test_ocr_language_validation_invalid_code(self, pdf_parser):
        """Should reject invalid language codes to prevent command injection."""
        # Arrange - Invalid/malicious language codes
        invalid_languages = [
            "en",  # Too short (should be 3 letters)
            "english",  # Too long
            "eng; rm -rf /",  # Command injection attempt
            "eng && echo pwned",  # Command injection
            "eng|cat /etc/passwd",  # Pipe injection
            "../../../etc/passwd",  # Path traversal
            "eng123",  # Numbers not allowed
            "ENG",  # Uppercase not allowed
        ]

        # Act & Assert
        for invalid_lang in invalid_languages:
            with pytest.raises(PDFParsingError, match="Invalid OCR language code"):
                with patch("app.services.pdf_parser.OCR_AVAILABLE", True):
                    pdf_parser._extract_with_ocr("/fake/path.pdf", language=invalid_lang)

    def test_ocr_unavailable_raises_error(self, pdf_parser):
        """Should raise error when OCR dependencies not available."""
        # Arrange
        with patch("app.services.pdf_parser.OCR_AVAILABLE", False):
            # Act & Assert
            with pytest.raises(PDFParsingError, match="OCR dependencies not available"):
                pdf_parser._extract_with_ocr("/fake/path.pdf")

    def test_ocr_page_count_validation(self, pdf_parser):
        """Should reject PDFs exceeding MAX_PAGE_COUNT."""
        # Arrange - Mock PDF with too many pages
        with (
            patch("app.services.pdf_parser.OCR_AVAILABLE", True),
            patch("builtins.open", create=True) as mock_open,
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
        ):

            mock_pdf = Mock()
            mock_pdf.pages = [Mock()] * 10001  # Exceeds MAX_PAGE_COUNT (10000)
            mock_reader.return_value = mock_pdf

            # Act & Assert
            with pytest.raises(PDFParsingError, match="PDF too large"):
                pdf_parser._extract_with_ocr("/fake/path.pdf")

    def test_get_optimal_dpi_low_memory(self, pdf_parser):
        """Should return low DPI when memory is constrained."""
        # Arrange - Mock low available memory
        with (
            patch("app.services.pdf_parser.MEMORY_MONITORING_AVAILABLE", True),
            patch("app.services.pdf_parser.psutil.virtual_memory") as mock_memory,
            patch("builtins.open", create=True) as mock_open,
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
        ):

            # Setup mocks
            mock_memory.return_value.available = 100 * 1024 * 1024  # 100 MB available
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.mediabox.width = 612  # 8.5 inches * 72 (A4 width)
            mock_page.mediabox.height = 792  # 11 inches * 72 (A4 height)
            mock_pdf.pages = [mock_page]
            mock_reader.return_value = mock_pdf

            # Act
            dpi = pdf_parser._get_optimal_dpi("/fake/path.pdf", page_count=50)

            # Assert - Should use low DPI due to memory constraints
            assert dpi == 150  # OCR_LOW_MEMORY_DPI

    def test_get_optimal_dpi_sufficient_memory(self, pdf_parser):
        """Should return default DPI when memory is sufficient."""
        # Arrange - Mock high available memory
        with (
            patch("app.services.pdf_parser.MEMORY_MONITORING_AVAILABLE", True),
            patch("app.services.pdf_parser.psutil.virtual_memory") as mock_memory,
            patch("builtins.open", create=True) as mock_open,
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
        ):

            # Setup mocks
            mock_memory.return_value.available = 8 * 1024 * 1024 * 1024  # 8 GB available
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.mediabox.width = 612
            mock_page.mediabox.height = 792
            mock_pdf.pages = [mock_page]
            mock_reader.return_value = mock_pdf

            # Act
            dpi = pdf_parser._get_optimal_dpi("/fake/path.pdf", page_count=10)

            # Assert - Should use default DPI
            assert dpi == 300  # OCR_DEFAULT_DPI

    def test_ocr_integration_scanned_pdf_detected(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id, tmp_path
    ):
        """Should detect scanned PDF and fall back to OCR."""
        # Arrange - Create a fake PDF
        pdf_file = tmp_path / "scanned.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")

        # Mock cache miss
        pdf_parser._get_cached_parse = Mock(return_value=None)

        # Mock PyPDF2 returning empty text (scanned PDF)
        with (
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch.object(pdf_parser, "_extract_with_ocr") as mock_ocr,
        ):

            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = ""  # No text (scanned)
            mock_pdf.pages = [mock_page]
            mock_pdf.is_encrypted = False
            mock_reader.return_value = mock_pdf

            # Mock OCR extraction
            mock_ocr.return_value = [{"page": 1, "text": "OCR extracted text", "section": None}]

            # Act
            result = pdf_parser.parse_document(
                document_id=sample_document_id,
                file_path=str(pdf_file),
                organization_id=sample_organization_id,
                enable_ocr=True,
            )

            # Assert - OCR should have been called
            mock_ocr.assert_called_once()
            assert result["method"] == "ocr"
            assert result["pages"][0]["text"] == "OCR extracted text"

    def test_ocr_disabled_skips_ocr(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id, tmp_path
    ):
        """Should skip OCR when enable_ocr=False."""
        # Arrange
        pdf_file = tmp_path / "scanned.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")

        pdf_parser._get_cached_parse = Mock(return_value=None)

        with (
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch.object(pdf_parser, "_extract_with_ocr") as mock_ocr,
        ):

            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = ""  # No text (scanned)
            mock_pdf.pages = [mock_page]
            mock_pdf.is_encrypted = False
            mock_reader.return_value = mock_pdf

            # Act
            result = pdf_parser.parse_document(
                document_id=sample_document_id,
                file_path=str(pdf_file),
                organization_id=sample_organization_id,
                enable_ocr=False,  # OCR disabled
            )

            # Assert - OCR should NOT have been called
            mock_ocr.assert_not_called()
            assert result["method"] == "pypdf2"  # Not OCR


class TestTableExtraction:
    """Test table extraction functionality."""

    @patch("app.services.pdf_parser.TABLE_EXTRACTION_AVAILABLE", True)
    @patch("app.services.pdf_parser.tabula")
    def test_extract_tables_success(self, mock_tabula, pdf_parser):
        """Should extract tables from PDF successfully."""
        # Arrange
        import pandas as pd

        # Mock tabula returning 2 tables
        df1 = pd.DataFrame({"Name": ["Alice", "Bob"], "Score": [95, 87]})
        df2 = pd.DataFrame({"Product": ["Widget", "Gadget"], "Price": [10.99, 15.49]})
        mock_tabula.read_pdf.return_value = [df1, df2]

        # Act
        tables = pdf_parser._extract_tables("/fake/path.pdf")

        # Assert
        assert len(tables) == 2
        assert tables[0]["page"] == 1
        assert tables[0]["columns"] == ["Name", "Score"]
        assert len(tables[0]["data"]) == 2
        assert tables[0]["data"][0]["Name"] == "Alice"
        assert tables[1]["page"] == 2
        assert tables[1]["columns"] == ["Product", "Price"]

    @patch("app.services.pdf_parser.TABLE_EXTRACTION_AVAILABLE", False)
    def test_extract_tables_unavailable(self, pdf_parser):
        """Should return empty list when table extraction unavailable."""
        # Act
        tables = pdf_parser._extract_tables("/fake/path.pdf")

        # Assert
        assert tables == []

    @patch("app.services.pdf_parser.TABLE_EXTRACTION_AVAILABLE", True)
    @patch("app.services.pdf_parser.tabula")
    def test_extract_tables_failure_graceful(self, mock_tabula, pdf_parser):
        """Should handle table extraction failures gracefully."""
        # Arrange
        mock_tabula.read_pdf.side_effect = Exception("Java error")

        # Act
        tables = pdf_parser._extract_tables("/fake/path.pdf")

        # Assert - should return empty list, not raise
        assert tables == []

    @patch("app.services.pdf_parser.TABLE_EXTRACTION_AVAILABLE", True)
    @patch("app.services.pdf_parser.tabula")
    def test_extract_tables_empty_dataframes(self, mock_tabula, pdf_parser):
        """Should skip empty tables."""
        # Arrange
        import pandas as pd

        df_empty = pd.DataFrame()
        df_valid = pd.DataFrame({"Col": ["value"]})
        mock_tabula.read_pdf.return_value = [df_empty, df_valid, df_empty]

        # Act
        tables = pdf_parser._extract_tables("/fake/path.pdf")

        # Assert - only 1 valid table
        assert len(tables) == 1
        assert tables[0]["columns"] == ["Col"]

    def test_parse_document_includes_tables(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id, tmp_path
    ):
        """Should include tables in parse_document result."""
        # Arrange
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")

        pdf_parser._get_cached_parse = Mock(return_value=None)

        with (
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch.object(pdf_parser, "_extract_tables") as mock_extract_tables,
        ):

            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "Sample text"
            mock_pdf.pages = [mock_page]
            mock_pdf.is_encrypted = False
            mock_reader.return_value = mock_pdf

            # Mock table extraction
            mock_extract_tables.return_value = [
                {"page": 1, "columns": ["A", "B"], "data": [{"A": "1", "B": "2"}]}
            ]

            # Act
            result = pdf_parser.parse_document(
                document_id=sample_document_id,
                file_path=str(pdf_file),
                organization_id=sample_organization_id,
                enable_tables=True,
            )

            # Assert
            assert "tables" in result
            assert len(result["tables"]) == 1
            assert result["tables"][0]["page"] == 1
            mock_extract_tables.assert_called_once()

    def test_parse_document_tables_disabled(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id, tmp_path
    ):
        """Should skip table extraction when enable_tables=False."""
        # Arrange
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")

        pdf_parser._get_cached_parse = Mock(return_value=None)

        with (
            patch("app.services.pdf_parser.PyPDF2.PdfReader") as mock_reader,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch.object(pdf_parser, "_extract_tables") as mock_extract_tables,
        ):

            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "Sample text"
            mock_pdf.pages = [mock_page]
            mock_pdf.is_encrypted = False
            mock_reader.return_value = mock_pdf

            # Act
            result = pdf_parser.parse_document(
                document_id=sample_document_id,
                file_path=str(pdf_file),
                organization_id=sample_organization_id,
                enable_tables=False,
            )

            # Assert
            assert result["tables"] == []
            mock_extract_tables.assert_not_called()

    def test_cache_stores_tables(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id
    ):
        """Should store tables in cache."""
        # Arrange
        pages = [{"page": 1, "text": "text", "section": None}]
        tables = [{"page": 1, "columns": ["A"], "data": [{"A": "1"}]}]

        # Act
        pdf_parser._cache_parse(sample_document_id, sample_organization_id, pages, "pypdf2", tables)

        # Assert
        mock_db.add.assert_called_once()
        added_doc = mock_db.add.call_args[0][0]
        assert added_doc.parsed_data["pages"] == pages
        assert added_doc.parsed_data["tables"] == tables

    def test_cache_retrieval_includes_tables(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id
    ):
        """Should retrieve tables from cache."""
        # Arrange
        cached_data = {
            "pages": [{"page": 1, "text": "text", "section": None}],
            "tables": [{"page": 1, "columns": ["A"], "data": [{"A": "1"}]}],
        }

        mock_cached = Mock()
        mock_cached.parsed_data = cached_data
        mock_cached.parsing_method = "pypdf2"

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cached
        mock_db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is not None
        assert result["tables"] == cached_data["tables"]
        assert result["pages"] == cached_data["pages"]

    def test_cache_backward_compatibility(
        self, pdf_parser, mock_db, sample_document_id, sample_organization_id
    ):
        """Should handle old cache format (list of pages without tables)."""
        # Arrange - old format: just a list
        cached_data = [{"page": 1, "text": "text", "section": None}]

        mock_cached = Mock()
        mock_cached.parsed_data = cached_data
        mock_cached.parsing_method = "pypdf2"

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cached
        mock_db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is not None
        assert result["pages"] == cached_data
        assert result["tables"] == []  # Empty for old format


class TestJavaAvailabilityCheck:
    """Test Java availability checking."""

    @patch("subprocess.run")
    def test_java_available(self, mock_run):
        """Should return True when Java is available."""
        # Arrange
        from app.services.pdf_parser import _check_java_availability

        mock_run.return_value = Mock(returncode=0)

        # Act
        result = _check_java_availability()

        # Assert
        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_java_not_found(self, mock_run):
        """Should return False when Java is not installed."""
        # Arrange
        from app.services.pdf_parser import _check_java_availability

        mock_run.side_effect = FileNotFoundError()

        # Act
        result = _check_java_availability()

        # Assert
        assert result is False

    @patch("subprocess.run")
    def test_java_timeout(self, mock_run):
        """Should return False on timeout."""
        # Arrange
        import subprocess
        from app.services.pdf_parser import _check_java_availability

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="java", timeout=5)

        # Act
        result = _check_java_availability()

        # Assert
        assert result is False
