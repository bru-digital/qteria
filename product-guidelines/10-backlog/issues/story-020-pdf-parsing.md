# [STORY-020] PDF Parsing with PyPDF2

**Type**: Story
**Epic**: EPIC-05 (AI Validation Engine)
**Journey Step**: Step 3 - Extract Document Text for AI
**Priority**: P0 (MVP Critical - Enables AI)
**RICE Score**: 90 (R:100 × I:3 × C:90% ÷ E:3)

---

## User Value

**Job-to-Be-Done**: When the AI needs to validate document content, it needs structured text extracted from PDFs with page boundaries and section detection, so it can provide evidence-based validation with exact page/section references.

**Value Delivered**: Accurate PDF text extraction that preserves document structure, enabling AI to cite exact locations when finding issues.

**Success Metric**: PDF parsing accuracy >95%, parsing time <5 seconds for 10MB PDF.

---

## Acceptance Criteria

- [ ] Extracts full text from PDF documents
- [ ] Preserves page boundaries (know which text is on which page)
- [ ] Detects sections (headings, numbered sections, table of contents)
- [ ] Handles various PDF formats (text-based, scanned with OCR)
- [ ] Caches parsed text in PostgreSQL (avoid re-parsing same document)
- [ ] Returns structured data: `{page_number: int, section: str, text: str}[]`
- [ ] Parsing completes in <5 seconds for 10MB PDF
- [ ] Handles parsing errors gracefully (corrupt PDFs)
- [ ] Supports PDFs up to 50MB

---

## Technical Approach

**Tech Stack Components Used**:
- PDF Libraries: PyPDF2 (primary), pdfplumber (fallback)
- OCR: pytesseract (optional, for scanned PDFs)
- Caching: PostgreSQL (parsed_documents table)

**PDF Parsing Service** (`app/services/pdf_parser.py`):
```python
import PyPDF2
import pdfplumber
import re
from typing import List, Dict
from app.models import ParsedDocument

class PDFParser:
    """Extract structured text from PDF documents"""

    def parse_pdf(self, file_path: str, document_id: str) -> List[Dict]:
        """
        Parse PDF and return structured text with page/section info.

        Returns: [
            {
                "page": 1,
                "section": "1. Introduction",
                "text": "This document describes..."
            },
            ...
        ]
        """
        # 1. Check cache first
        cached = await self._get_cached_parse(document_id)
        if cached:
            return cached

        # 2. Extract text with PyPDF2
        try:
            pages = self._extract_with_pypdf2(file_path)
        except Exception as e:
            # Fallback to pdfplumber
            pages = self._extract_with_pdfplumber(file_path)

        # 3. Detect sections across pages
        structured_pages = self._detect_sections(pages)

        # 4. Cache parsed result
        await self._cache_parse(document_id, structured_pages)

        return structured_pages

    def _extract_with_pypdf2(self, file_path: str) -> List[Dict]:
        """Extract text using PyPDF2"""
        pages = []
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                pages.append({
                    "page": page_num,
                    "text": text,
                    "section": None  # Detect later
                })
        return pages

    def _extract_with_pdfplumber(self, file_path: str) -> List[Dict]:
        """Fallback: Extract text using pdfplumber"""
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                pages.append({
                    "page": page_num,
                    "text": text,
                    "section": None
                })
        return pages

    def _detect_sections(self, pages: List[Dict]) -> List[Dict]:
        """
        Detect section headings across pages.

        Looks for patterns:
        - Numbered sections: "1. Introduction", "2.3 Test Results"
        - Headings: ALL CAPS lines, bold markers
        - Table of contents references
        """
        current_section = None

        for page in pages:
            text = page["text"]

            # Look for numbered section headings
            section_match = re.search(r'^(\d+\.?\d*\.?\s+[A-Z][^\n]+)', text, re.MULTILINE)
            if section_match:
                current_section = section_match.group(1).strip()

            # Assign section to page
            page["section"] = current_section or "Untitled Section"

        return pages

    async def _get_cached_parse(self, document_id: str) -> List[Dict] | None:
        """Get cached parsed text from database"""
        cached = await ParsedDocument.get_by_document_id(document_id)
        if cached:
            return cached.parsed_data  # JSON field
        return None

    async def _cache_parse(self, document_id: str, parsed_data: List[Dict]):
        """Cache parsed text in database"""
        parsed_doc = ParsedDocument(
            document_id=document_id,
            parsed_data=parsed_data,  # Store as JSONB
            parsed_at=datetime.utcnow()
        )
        await parsed_doc.save()
```

**Database Schema Addition**:
```sql
CREATE TABLE parsed_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES assessment_documents(id) ON DELETE CASCADE,
    parsed_data JSONB NOT NULL,  -- Structured text with pages/sections
    parsed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(document_id)
);

CREATE INDEX idx_parsed_documents_document_id ON parsed_documents(document_id);
```

**Example Output**:
```json
[
  {
    "page": 1,
    "section": "1. Introduction",
    "text": "This document describes the technical specifications for..."
  },
  {
    "page": 8,
    "section": "3.2 Test Results",
    "text": "The following tests were performed:\n\nTest 1: PASS\nTest 2: PASS\nTest 3: FAIL..."
  }
]
```

---

## Dependencies

- **Blocked By**:
  - STORY-015 (Document Upload) - need documents to parse
  - STORY-016 (Start Assessment) - triggers parsing
- **Blocks**:
  - STORY-021 (Claude AI) - AI needs parsed text
  - STORY-022 (Evidence Extraction) - needs section detection

---

## Estimation

**Effort**: 3 person-days

**Breakdown**:
- PyPDF2 integration: 0.5 days (basic extraction)
- Section detection: 1 day (regex patterns, testing)
- Caching logic: 0.5 days (database integration)
- Testing: 1 day (various PDF formats, edge cases)

---

## Definition of Done

- [ ] PDF text extraction working (PyPDF2 + pdfplumber fallback)
- [ ] Page boundaries preserved
- [ ] Section detection working (numbered sections, headings)
- [ ] Parsed text cached in PostgreSQL
- [ ] Cache hit skips re-parsing
- [ ] Parsing completes <5 seconds for 10MB PDF
- [ ] Handles corrupt PDFs gracefully (error message)
- [ ] Unit tests pass (95% coverage)
- [ ] Integration tests with real PDFs pass
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Unit Tests** (95% coverage):
- [ ] Extract text from simple PDF
- [ ] Extract text from complex PDF (multi-column, tables)
- [ ] Detect numbered sections (1., 1.1, 1.1.1)
- [ ] Detect heading sections (ALL CAPS, bold)
- [ ] Handle corrupt PDF → return error
- [ ] Cache hit → skip parsing

**Integration Tests**:
- [ ] Parse real TÜV SÜD document (Machinery Directive)
- [ ] Parse medical device technical documentation
- [ ] Verify section detection accuracy (manual review)

**Performance Tests**:
- [ ] Parse 1MB PDF → <1 second
- [ ] Parse 10MB PDF → <5 seconds
- [ ] Parse 50MB PDF → <30 seconds
- [ ] Cache lookup → <50ms

---

## Risks & Mitigations

**Risk**: Section detection unreliable (documents use varied formatting)
- **Mitigation**: Multiple detection strategies (numbered, headings, TOC), fallback to page-only

**Risk**: PyPDF2 fails on certain PDFs (encrypted, corrupt)
- **Mitigation**: Fallback to pdfplumber, clear error message if both fail

**Risk**: Parsing slow for large PDFs (50MB)
- **Mitigation**: Background job processing, caching, optimize parsing algorithm

---

## Notes

- This is the **foundation for AI validation** - accuracy is critical
- Test with real certification documents from TÜV SÜD
- After completing this story, proceed to STORY-021 (Claude AI Integration)
