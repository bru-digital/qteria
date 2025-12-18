# PDF Parser Service

Structured text extraction from PDF documents with caching and section detection.

## Overview

The PDF Parser Service extracts text from PDF documents while preserving:
- **Page boundaries** - Track which text appears on which page
- **Section detection** - Identify numbered sections (1., 2.3, 3.2.1) and headings
- **Caching** - Store parsed results in database to avoid re-parsing

## Features

- **Dual library support**: PyPDF2 (primary) with pdfplumber fallback
- **Section detection**: Regex patterns for numbered sections and uppercase headings
- **Table extraction**: Structured extraction of tabular data using tabula-py
- **OCR support**: Scanned PDF processing with pytesseract
- **Database caching**: Stores parsed data in `parsed_documents` table
- **Error handling**: Detects encrypted and corrupt PDFs
- **Structured output**: Returns JSON with page boundaries, section names, and tables
- **Graceful degradation**: Features degrade gracefully when dependencies unavailable

## Usage

### Basic Example

```python
from app.services import PDFParserService
from app.database import get_db

# Initialize service with database session
db = next(get_db())
parser = PDFParserService(db=db)

# Parse document (synchronous - wrap in Celery task for background processing)
result = parser.parse_document(
    document_id=uuid4(),
    file_path="/path/to/document.pdf",
    organization_id=uuid4()
)

# Access parsed pages
for page in result["pages"]:
    print(f"Page {page['page']}: {page['section']}")
    print(page['text'][:100])  # First 100 chars
```

### Return Format

```python
{
    "document_id": UUID,
    "pages": [
        {
            "page": 1,
            "section": "1. Introduction",
            "text": "This document describes..."
        },
        {
            "page": 2,
            "section": "1. Introduction",  # Section persists
            "text": "Continued from previous page..."
        },
        {
            "page": 8,
            "section": "3.2 Test Results",
            "text": "Test results show..."
        }
    ],
    "tables": [
        {
            "page": 8,
            "columns": ["Test Name", "Result", "Status"],
            "data": [
                {"Test Name": "Voltage Test", "Result": "5.0V", "Status": "Pass"},
                {"Test Name": "Current Test", "Result": "2.1A", "Status": "Pass"}
            ]
        }
    ],
    "method": "pypdf2",  # or "pdfplumber" or "ocr"
    "cached": False  # True if result came from cache
}
```

## Architecture

### Parsing Flow

1. **Check cache** - Query `parsed_documents` table for existing result
2. **Validate PDF** - Check file exists, is readable, not encrypted
3. **Extract text** - Use PyPDF2, fallback to pdfplumber if fails
4. **Check for scanned PDF** - If no text, fallback to OCR (pytesseract)
5. **Detect sections** - Apply regex patterns to find section headings
6. **Extract tables** - Use tabula-py to extract structured table data
7. **Cache result** - Store pages and tables in database with parsing method

### Section Detection

Detects multiple heading patterns:

**Numbered sections:**
```
1. Introduction
2.3 Test Results
3.2.1 Detailed Analysis
```

**Uppercase headings:**
```
TECHNICAL SPECIFICATIONS
CHAPTER 2 - METHODS
```

**Underlined headings:**
```
Test Results
============
```

### Table Extraction

Extracts structured tabular data from PDFs using tabula-py (Java-based):

**Features:**
- Automatic table detection across all pages
- Column header inference
- Structured JSON output with page numbers
- Graceful degradation if Java unavailable

**Example output:**
```python
{
    "page": 3,
    "columns": ["Test Name", "Result", "Status"],
    "data": [
        {"Test Name": "Voltage", "Result": "5.0V", "Status": "Pass"},
        {"Test Name": "Current", "Result": "2.1A", "Status": "Pass"}
    ]
}
```

**Configuration:**
```python
# Enable/disable table extraction
result = parser.parse_document(
    document_id=uuid4(),
    file_path="/path/to/document.pdf",
    organization_id=uuid4(),
    enable_tables=True  # Default: True
)
```

**Performance:**
- Adds ~1-2 seconds per document with tables
- Minimal overhead for documents without tables
- Processes all pages in single pass

### Caching Strategy

- **Key**: `document_id` (UUID)
- **Storage**: PostgreSQL `parsed_documents` table (JSONB column)
- **Data cached**: Pages (text + sections) and tables
- **Format**: `{"pages": [...], "tables": [...]}`
- **TTL**: No expiration (delete manually or with document)
- **Invalidation**: CASCADE delete when document is deleted
- **Backward compatibility**: Old cache format (list of pages) supported

## Error Handling

### Exception Hierarchy

```
PDFParsingError (base)
├── EncryptedPDFError - Password-protected PDF
└── CorruptPDFError - Malformed or unreadable PDF
```

### Example Error Handling

```python
try:
    result = parser.parse_document(doc_id, file_path, organization_id)
except EncryptedPDFError:
    # PDF is password-protected
    return {"error": "Document is encrypted"}
except CorruptPDFError:
    # PDF is malformed
    return {"error": "Document is corrupt"}
except PDFParsingError as e:
    # Other parsing failures
    return {"error": f"Parsing failed: {str(e)}"}
```

## Performance

### Benchmarks

| PDF Size | Pages | Parse Time | Cache Hit |
|----------|-------|------------|-----------|
| 1MB      | 10    | <1s        | <100ms    |
| 10MB     | 100   | <5s        | <100ms    |
| 50MB     | 500   | <30s       | <100ms    |

### Optimization Tips

1. **Enable caching** - First parse is slow, subsequent calls are <100ms
2. **Batch processing** - Parse multiple documents in parallel
3. **Section detection** - Disable if not needed (set `detect_sections=False`)
4. **Cleanup** - Delete old `parsed_documents` entries to reduce DB size

## Testing

### Unit Tests

Run unit tests with pytest:

```bash
pytest app/services/pdf_parser_test.py -v
```

Coverage target: **95%**

### Integration Tests

```bash
pytest tests/test_pdf_parser_integration.py -v --integration
```

**Note**: Integration tests require PDF fixtures in `tests/fixtures/`

## Database Schema

### `parsed_documents` Table

```sql
CREATE TABLE parsed_documents (
    id UUID PRIMARY KEY,
    document_id UUID UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    parsed_data JSON NOT NULL,  -- Array of {page, section, text}
    parsing_method VARCHAR(50),  -- 'pypdf2' or 'pdfplumber'
    parsed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_parsed_documents_document_id ON parsed_documents(document_id);
CREATE INDEX idx_parsed_documents_parsed_at ON parsed_documents(parsed_at);
```

## Troubleshooting

### "PDF file not found"

**Cause**: File path is invalid or file was deleted
**Solution**: Verify file exists and path is absolute

### "PDF is encrypted"

**Cause**: PDF is password-protected
**Solution**: Remove password protection or skip parsing

### "PyPDF2 failed to read PDF"

**Cause**: PDF is corrupt or uses unsupported features
**Solution**: Service automatically falls back to pdfplumber

### "Both PyPDF2 and pdfplumber failed"

**Cause**: PDF is severely corrupt or not a valid PDF
**Solution**: Validate file is actually a PDF, try opening in Adobe Reader

### Section detection not working

**Cause**: Document uses non-standard heading format
**Solution**: Add custom regex pattern in `_detect_sections()` method

## Future Enhancements

- [x] OCR support for scanned PDFs (pytesseract) - ✅ Implemented
- [x] Table extraction (tabula-py) - ✅ Implemented
- [x] Custom section detection rules (configurable patterns) - ✅ Implemented
- [ ] Multi-column layout detection
- [ ] Image extraction
- [ ] DOCX parsing (python-docx)
- [ ] Parallel page processing (asyncio)

## Dependencies

### Python Packages
- **PyPDF2 3.0.1** - Primary PDF parsing
- **pdfplumber 0.10.3** - Fallback extraction
- **tabula-py 2.9.0** - Table extraction
- **pytesseract 0.3.10** - OCR support
- **pdf2image 1.17.0** - PDF to image conversion for OCR
- **psutil 5.9.8** - Memory monitoring for OCR DPI optimization
- **SQLAlchemy 2.0+** - Database ORM
- **PostgreSQL 15+** - Caching storage

### System Dependencies
- **default-jre** - Java Runtime Environment (required for tabula-py)
- **tesseract-ocr** - OCR engine (required for pytesseract)
- **poppler-utils** - PDF utilities (required for pdf2image)

### Installation

**Python dependencies:**
```bash
pip install -r requirements.txt
```

**System dependencies (Linux/Ubuntu):**
```bash
apt-get install default-jre tesseract-ocr poppler-utils
```

**System dependencies (macOS):**
```bash
brew install openjdk tesseract poppler
```

## Related Documentation

- [Database Schema](../../../product-guidelines/07-database-schema.md)
- [Testing Strategy](../../../product-guidelines/09-test-strategy.md)
- [Story 020 - PDF Parsing](https://github.com/bru-digital/qteria/issues/30)

## Support

For issues or questions, see:
- Unit tests: `app/services/pdf_parser_test.py`
- Integration tests: `tests/test_pdf_parser_integration.py`
- GitHub Issue: #30
