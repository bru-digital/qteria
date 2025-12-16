# PDF Parser Service

Structured text extraction from PDF documents with caching, section detection, OCR support, table extraction, and parallel processing.

## Overview

The PDF Parser Service extracts text from PDF documents while preserving:
- **Page boundaries** - Track which text appears on which page
- **Section detection** - Identify numbered sections (1., 2.3, 3.2.1) and headings
- **Caching** - Store parsed results in database to avoid re-parsing
- **OCR support** - Extract text from scanned PDFs using pytesseract
- **Table extraction** - Parse structured tables with tabula-py
- **Parallel processing** - Process large PDFs faster with async page parsing
- **Custom patterns** - Configure section detection patterns per workflow

## Features

- **Dual library support**: PyPDF2 (primary) with pdfplumber fallback
- **OCR fallback**: Automatically detects scanned PDFs and uses pytesseract
- **Table extraction**: Extracts tables as structured JSON using tabula-py
- **Parallel page processing**: Uses asyncio for concurrent page parsing (faster for 50+ page PDFs)
- **Configurable section detection**: Custom regex patterns per workflow
- **Database caching**: Stores parsed data in `parsed_documents` table
- **Error handling**: Detects encrypted and corrupt PDFs
- **Structured output**: Returns JSON with page boundaries, section names, and tables
- **Graceful degradation**: Continues if OCR or table extraction fails

## Usage

### Basic Example

```python
from app.services import PDFParserService
from app.database import get_db

# Initialize service with database session
db = next(get_db())
parser = PDFParserService(db=db)

# Parse document with all features enabled (default)
result = parser.parse_document(
    document_id=uuid4(),
    file_path="/path/to/document.pdf",
    organization_id=uuid4(),
    enable_ocr=True,        # Auto-detect scanned PDFs and use OCR
    enable_tables=True,      # Extract tables
    enable_parallel=True,    # Use parallel page processing
    custom_patterns=None     # Use default section patterns
)

# Access parsed pages
for page in result["pages"]:
    print(f"Page {page['page']}: {page['section']}")
    print(page['text'][:100])  # First 100 chars

# Access extracted tables
for table in result["tables"]:
    print(f"Table {table['table_index']}: {table['row_count']} rows")
    print(table['data'][:5])  # First 5 rows

# Check parsing method used
print(f"Method: {result['method']}")  # 'pypdf2_parallel', 'ocr', etc.
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
            "table_index": 0,
            "data": [
                {"Test": "Voltage", "Result": "Pass", "Value": "230V"},
                {"Test": "Current", "Result": "Pass", "Value": "10A"}
            ],
            "columns": ["Test", "Result", "Value"],
            "row_count": 2
        }
    ],
    "method": "pypdf2_parallel",  # or "pypdf2", "pdfplumber", "ocr"
    "cached": False  # True if result came from cache
}
```

## Architecture

### Parsing Flow

1. **Check cache** - Query `parsed_documents` table for existing result
2. **Validate PDF** - Check file exists, is readable, not encrypted
3. **Extract text** - Use PyPDF2 (parallel if enabled), fallback to pdfplumber if fails
4. **OCR fallback** - If scanned PDF detected (< 100 chars extracted), use pytesseract
5. **Extract tables** - Use tabula-py to extract structured tables (if enabled)
6. **Detect sections** - Apply regex patterns (custom or default) to find section headings
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

### Caching Strategy

- **Key**: `document_id` (UUID)
- **Storage**: PostgreSQL `parsed_documents` table (JSON column)
- **TTL**: No expiration (delete manually or with document)
- **Invalidation**: CASCADE delete when document is deleted

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

| PDF Size | Pages | Parse Time (Sequential) | Parse Time (Parallel) | OCR Time | Cache Hit |
|----------|-------|-------------------------|----------------------|----------|-----------|
| 1MB      | 10    | <1s                     | <0.5s                | ~5s      | <100ms    |
| 10MB     | 50    | ~5s                     | ~2s                  | ~30s     | <100ms    |
| 10MB     | 100   | ~10s                    | ~4s                  | ~60s     | <100ms    |
| 50MB     | 500   | ~50s                    | ~20s                 | ~300s    | <100ms    |

**Notes:**
- Parallel processing provides 2-3x speedup for large PDFs
- OCR is significantly slower (5-10x) than text extraction
- Table extraction adds ~1-2s overhead
- Cache hits are always fast (<100ms) regardless of document size

### Optimization Tips

1. **Enable caching** - First parse is slow, subsequent calls are <100ms
2. **Use parallel processing** - Enabled by default, provides 2-3x speedup for 50+ page PDFs
3. **Disable OCR if not needed** - Set `enable_ocr=False` for digital PDFs (faster)
4. **Disable table extraction if not needed** - Set `enable_tables=False` to save 1-2s
5. **Batch processing** - Parse multiple documents in parallel (separate Celery tasks)
6. **Cleanup** - Delete old `parsed_documents` entries to reduce DB size

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

## Advanced Features

### OCR Support for Scanned PDFs

The parser automatically detects scanned PDFs (documents with < 100 extractable characters) and falls back to OCR using pytesseract:

```python
# OCR is enabled by default
result = parser.parse_document(
    document_id=uuid4(),
    file_path="scanned_certificate.pdf",
    organization_id=uuid4(),
    enable_ocr=True  # Default
)

# Check if OCR was used
if result["method"] == "ocr":
    print("Document was scanned - OCR used for text extraction")
```

**Requirements**: tesseract-ocr system library must be installed (see Dockerfile).

### Table Extraction

Extracts structured tables from PDFs using tabula-py:

```python
result = parser.parse_document(
    document_id=uuid4(),
    file_path="test_report_with_tables.pdf",
    organization_id=uuid4(),
    enable_tables=True  # Default
)

# Access extracted tables
for table in result["tables"]:
    print(f"Table {table['table_index']}: {table['row_count']} rows")
    for row in table["data"]:
        print(row)  # Dict with column headers as keys
```

**Requirements**: Java runtime must be installed (see Dockerfile).

### Parallel Page Processing

Processes large PDFs faster using asyncio to parse pages concurrently:

```python
# Parallel processing enabled by default
result = parser.parse_document(
    document_id=uuid4(),
    file_path="large_document_100_pages.pdf",
    organization_id=uuid4(),
    enable_parallel=True  # Default
)

# Check method to confirm parallel processing
if result["method"] == "pypdf2_parallel":
    print("Pages processed concurrently for faster parsing")
```

**Performance**: ~2-3x faster for 50+ page PDFs compared to sequential parsing.

### Custom Section Detection Patterns

Configure custom regex patterns per workflow for domain-specific documents:

```python
# Medical device documentation patterns
medical_patterns = [
    r"^(SECTION \d+\s+-\s+[A-Z][^\n]{5,100})",  # SECTION 1 - OVERVIEW
    r"^(\d+\.\d+\s+[A-Z][a-z\s]{5,100})",       # 1.1 Device Description
]

result = parser.parse_document(
    document_id=uuid4(),
    file_path="medical_device_cert.pdf",
    organization_id=uuid4(),
    custom_patterns=medical_patterns
)

# Sections detected using custom patterns
for page in result["pages"]:
    if page["section"]:
        print(f"Page {page['page']}: {page['section']}")
```

**Pattern Validation**: Patterns are validated to prevent ReDoS attacks (max 1000 chars, must compile).

## Future Enhancements

- [ ] Multi-column layout detection
- [ ] Image extraction
- [ ] DOCX parsing (python-docx)
- [ ] Multi-language OCR support (currently English only)

## Dependencies

**Python Packages:**
- **PyPDF2 3.0.1** - Primary PDF parsing
- **pdfplumber 0.10.3** - Fallback extraction
- **pytesseract 0.3.10** - OCR for scanned PDFs
- **pdf2image 1.16.3** - PDF to image conversion for OCR
- **tabula-py 2.9.0** - Table extraction
- **SQLAlchemy 2.0+** - Database ORM
- **PostgreSQL 15+** - Caching storage

**System Dependencies:**
- **tesseract-ocr** - OCR engine (required for scanned PDF support)
- **poppler-utils** - PDF to image conversion (required for OCR)
- **default-jre** - Java runtime (required for table extraction)

These are automatically installed in Docker via `apps/api/Dockerfile`.

## Related Documentation

- [Database Schema](../../../product-guidelines/07-database-schema.md)
- [Testing Strategy](../../../product-guidelines/09-test-strategy.md)
- [Story 020 - PDF Parsing](https://github.com/bru-digital/qteria/issues/30)

## Support

For issues or questions, see:
- Unit tests: `app/services/pdf_parser_test.py`
- Integration tests: `tests/test_pdf_parser_integration.py`
- GitHub Issue: #30
