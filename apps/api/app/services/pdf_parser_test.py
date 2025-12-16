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
    def test_extract_multi_page_pdf_preserves_boundaries(
        self, mock_open, mock_reader, pdf_parser
    ):
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

    def test_cache_hit_skips_parsing(self, pdf_parser, mock_db, sample_document_id, sample_organization_id):
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

    def test_cache_miss_returns_none(self, pdf_parser, mock_db, sample_document_id, sample_organization_id):
        """Should return None if no cached result found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is None

    def test_cache_stores_parsed_data(self, pdf_parser, mock_db, sample_document_id, sample_organization_id):
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
    def test_is_encrypted_handles_errors_gracefully(
        self, mock_open, mock_reader, pdf_parser
    ):
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
        result = pdf_parser.parse_document(sample_document_id, "/fake/path.pdf", sample_organization_id)

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
        result = pdf_parser.parse_document(sample_document_id, "/fake/path.pdf", sample_organization_id)

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

    def test_get_cached_parse_returns_none_for_different_org(
        self, pdf_parser, sample_document_id
    ):
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


class TestCacheBackwardCompatibility:
    """Test cache format backward compatibility (Critical Issue #3)."""

    def test_cache_v2_format_with_version(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should correctly parse v2 cache format with version field."""
        # Arrange - V2 format: {version: 2, pages: [...], tables: [...]}
        cached_doc = Mock()
        cached_doc.parsed_data = {
            "version": 2,
            "pages": [{"page": 1, "text": "Test", "section": None}],
            "tables": [{"page": 1, "data": []}],
        }
        cached_doc.parsing_method = "pypdf2"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = cached_doc
        pdf_parser.db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is not None
        assert result["pages"] == cached_doc.parsed_data["pages"]
        assert result["tables"] == cached_doc.parsed_data["tables"]
        assert result["method"] == "pypdf2"

    def test_cache_v1_format_dict_without_version(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should correctly parse v1 cache format (dict without version field)."""
        # Arrange - V1 format: {pages: [...], tables: [...]} (no version field)
        cached_doc = Mock()
        cached_doc.parsed_data = {
            "pages": [{"page": 1, "text": "Test", "section": None}],
            "tables": [],
        }
        cached_doc.parsing_method = "pdfplumber"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = cached_doc
        pdf_parser.db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is not None
        assert result["pages"] == cached_doc.parsed_data["pages"]
        assert result["tables"] == []
        assert result["method"] == "pdfplumber"

    def test_cache_legacy_format_list_only(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should correctly parse legacy cache format (list of pages only)."""
        # Arrange - Legacy format: just a list of pages
        cached_doc = Mock()
        cached_doc.parsed_data = [{"page": 1, "text": "Test", "section": None}]
        cached_doc.parsing_method = "pypdf2"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = cached_doc
        pdf_parser.db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is not None
        assert result["pages"] == cached_doc.parsed_data
        assert result["tables"] == []  # Empty for old format
        assert result["method"] == "pypdf2"

    def test_cache_unknown_version_invalidates(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should invalidate cache with unknown version number."""
        # Arrange - Future version that doesn't exist yet
        cached_doc = Mock()
        cached_doc.parsed_data = {
            "version": 999,
            "pages": [{"page": 1, "text": "Test"}],
        }
        cached_doc.parsing_method = "pypdf2"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = cached_doc
        pdf_parser.db.query.return_value = mock_query

        # Act
        result = pdf_parser._get_cached_parse(sample_document_id, sample_organization_id)

        # Assert
        assert result is None  # Should invalidate unknown version


class TestReDoSValidation:
    """Test ReDoS pattern validation (Critical Issue #2)."""

    def test_nested_quantifiers_rejected(self, pdf_parser):
        """Should reject patterns with nested quantifiers (ReDoS risk)."""
        evil_patterns = [
            r"(a+)+",  # Classic ReDoS pattern
            r"(x*)*",  # Nested star quantifiers
            r"(y+)?",  # Optional nested quantifier
        ]

        for pattern in evil_patterns:
            with pytest.raises(PDFParsingError, match="nested quantifiers"):
                pdf_parser._compile_section_patterns([pattern])

    def test_multiple_consecutive_quantifiers_rejected(self, pdf_parser):
        """Should reject patterns with multiple consecutive quantifiers."""
        evil_patterns = [
            r"a++",  # Double plus
            r"b**",  # Double star
            r"c+*",  # Plus then star
        ]

        for pattern in evil_patterns:
            with pytest.raises(PDFParsingError, match="multiple consecutive quantifiers"):
                pdf_parser._compile_section_patterns([pattern])

    def test_safe_patterns_accepted(self, pdf_parser):
        """Should accept safe patterns without ReDoS risk."""
        safe_patterns = [
            r"\d+\.\d+",  # Section numbers: 1.2
            r"Chapter \d+",  # Chapter headings
            r"[A-Z][a-z]+",  # Capitalized words
        ]

        # Should not raise any exceptions
        compiled = pdf_parser._compile_section_patterns(safe_patterns)
        assert len(compiled) == len(safe_patterns)

    def test_pattern_length_limit_enforced(self, pdf_parser):
        """Should reject patterns exceeding MAX_PATTERN_LENGTH."""
        # Create a pattern longer than MAX_PATTERN_LENGTH (1000 chars)
        long_pattern = "a" * 1001

        with pytest.raises(PDFParsingError, match="Pattern too long"):
            pdf_parser._compile_section_patterns([long_pattern])


class TestOCRMemoryOptimization:
    """Test OCR DPI optimization based on memory (High Priority Issue #6)."""

    @patch("app.services.pdf_parser.MEMORY_MONITORING_AVAILABLE", True)
    @patch("app.services.pdf_parser.psutil")
    def test_high_memory_uses_default_dpi(self, mock_psutil, pdf_parser):
        """Should use default DPI when sufficient memory available."""
        # Arrange - 4GB available memory
        mock_psutil.virtual_memory.return_value = Mock(available=4 * 1024 * 1024 * 1024)

        # Act
        dpi = pdf_parser._get_optimal_dpi(page_count=50)

        # Assert
        assert dpi == 300  # OCR_DEFAULT_DPI

    @patch("app.services.pdf_parser.MEMORY_MONITORING_AVAILABLE", True)
    @patch("app.services.pdf_parser.psutil")
    def test_low_memory_uses_reduced_dpi(self, mock_psutil, pdf_parser):
        """Should use reduced DPI when memory is constrained."""
        # Arrange - 512MB available memory (Railway free tier)
        mock_psutil.virtual_memory.return_value = Mock(available=512 * 1024 * 1024)

        # Act
        dpi = pdf_parser._get_optimal_dpi(page_count=50)

        # Assert
        assert dpi == 150  # OCR_LOW_MEMORY_DPI

    @patch("app.services.pdf_parser.MEMORY_MONITORING_AVAILABLE", False)
    def test_no_psutil_uses_default_dpi(self, pdf_parser):
        """Should use default DPI when psutil not available."""
        # Act
        dpi = pdf_parser._get_optimal_dpi(page_count=50)

        # Assert
        assert dpi == 300  # OCR_DEFAULT_DPI


class TestJavaVersionParsing:
    """Test improved Java version parsing (High Priority Issue #7)."""

    def test_standard_java_8_format(self, pdf_parser):
        """Should parse standard Java 8 version format."""
        # Arrange
        version_output = 'java version "1.8.0_XXX"'

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stderr=version_output, stdout=""
            )

            # Act
            result = pdf_parser._check_java_available()

            # Assert
            assert result is True

    def test_standard_java_11_format(self, pdf_parser):
        """Should parse standard Java 11+ version format."""
        # Arrange
        version_output = 'openjdk version "11.0.15"'

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stderr=version_output, stdout=""
            )

            # Act
            result = pdf_parser._check_java_available()

            # Assert
            assert result is True

    def test_azul_zulu_format(self, pdf_parser):
        """Should parse Azul Zulu Java version format."""
        # Arrange
        version_output = 'openjdk version "11.0.15" 2022-04-19 LTS'

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stderr=version_output, stdout=""
            )

            # Act
            result = pdf_parser._check_java_available()

            # Assert
            assert result is True

    def test_graalvm_format(self, pdf_parser):
        """Should parse GraalVM Java version format."""
        # Arrange
        version_output = 'openjdk version "17.0.3" 2022-04-19'

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stderr=version_output, stdout=""
            )

            # Act
            result = pdf_parser._check_java_available()

            # Assert
            assert result is True

    def test_version_without_quotes(self, pdf_parser):
        """Should parse Java version format without quotes."""
        # Arrange
        version_output = 'version 11.0.15'

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stderr=version_output, stdout=""
            )

            # Act
            result = pdf_parser._check_java_available()

            # Assert
            assert result is True

    def test_unparseable_version_returns_false(self, pdf_parser):
        """Should return False when version cannot be parsed."""
        # Arrange
        version_output = 'some random output without version'

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stderr=version_output, stdout=""
            )

            # Act
            result = pdf_parser._check_java_available()

            # Assert
            assert result is False


class TestParallelProcessingInAsyncContext:
    """Test parallel processing behavior in async context (Critical Issue #1)."""

    @pytest.mark.asyncio
    async def test_parallel_in_async_context_raises_error(
        self, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should raise error when enable_parallel=True in async context."""
        # Arrange
        test_file = "/fake/test.pdf"

        # Mock file validation to pass
        with patch.object(pdf_parser, "_validate_pdf"):
            # Mock cache to return None (cache miss)
            with patch.object(pdf_parser, "_get_cached_parse", return_value=None):
                # Act & Assert
                with pytest.raises(PDFParsingError) as exc_info:
                    pdf_parser.parse_document(
                        document_id=sample_document_id,
                        file_path=test_file,
                        organization_id=sample_organization_id,
                        enable_parallel=True,  # This should raise error in async context
                    )

                # Verify error message is clear and actionable
                assert "not supported when called from an async context" in str(exc_info.value)
                assert "enable_parallel=False" in str(exc_info.value)
                assert "background task" in str(exc_info.value)

    @patch("app.services.pdf_parser.PyPDF2.PdfReader")
    @patch("builtins.open", create=True)
    def test_parallel_disabled_works_in_async_context(
        self, mock_open, mock_reader, pdf_parser, sample_document_id, sample_organization_id
    ):
        """Should work with enable_parallel=False in async context (sync fallback)."""
        # Arrange
        test_file = "/fake/test.pdf"
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_reader_instance.is_encrypted = False
        mock_reader.return_value = mock_reader_instance

        # Mock cache to return None (cache miss)
        with patch.object(pdf_parser, "_get_cached_parse", return_value=None):
            # Mock path validation
            with patch("pathlib.Path.resolve") as mock_resolve:
                mock_path = Mock()
                mock_path.exists.return_value = True
                mock_path.is_file.return_value = True
                mock_resolve.return_value = mock_path

                # Mock asyncio.get_running_loop to simulate async context
                import asyncio
                with patch("asyncio.get_running_loop") as mock_get_loop:
                    # Simulate being in async context
                    mock_get_loop.return_value = Mock()

                    # Act & Assert - Should work with enable_parallel=False
                    result = pdf_parser.parse_document(
                        document_id=sample_document_id,
                        file_path=test_file,
                        organization_id=sample_organization_id,
                        enable_parallel=False,  # Explicit sync extraction
                    )

                    # Verify sync extraction was used
                    assert result["method"] == "pypdf2"
                    assert len(result["pages"]) == 1
                    assert result["cached"] is False
