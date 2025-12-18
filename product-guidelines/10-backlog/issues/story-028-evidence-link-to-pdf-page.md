# [STORY-028] Evidence Link to PDF Page

**Epic**: EPIC-06 - Results & Evidence Display
**Priority**: P0 (MVP Critical)
**Estimated Effort**: 2 days
**Journey Step**: Step 3 (Visual) - Click Evidence to Verify

---

## User Story

**As a** Project Handler
**I want to** click evidence links to open PDFs at specific pages
**So that** I can verify AI findings and see exact issue locations myself

---

## Acceptance Criteria

- [ ] Evidence links clickable in results page
- [ ] Clicking link opens PDF in browser at specific page
- [ ] URL includes page anchor (e.g., `/documents/doc_123?page=8#page=8`)
- [ ] PDF displays correctly in browser (Chrome, Firefox, Safari)
- [ ] Section reference shown if available (e.g., "Section 3.2")
- [ ] Download fallback if browser can't display PDF
- [ ] Works for all document types uploaded
- [ ] Link generation <100ms

---

## Technical Details

**Tech Stack**:

- Frontend: Next.js (evidence link click handler)
- Backend: FastAPI (`GET /v1/documents/:id?page=X`)
- Storage: Vercel Blob (document retrieval)
- PDF Display: Browser native (with `#page=` anchor)

**Evidence Link Flow**:

1. User clicks evidence link (e.g., "📄 test-report.pdf, page 8")
2. Frontend calls `GET /v1/documents/doc_123?page=8`
3. Backend streams PDF from Vercel Blob
4. Frontend opens PDF in new tab/window with URL anchor: `#page=8`
5. Browser scrolls to page 8 automatically

**API Implementation**:

```python
# backend/app/api/v1/documents.py

@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    page: Optional[int] = Query(None),
    user: User = Depends(get_current_user)
):
    # Verify user has access to document
    document = await db.get_document(document_id)
    if document.organization_id != user.organization_id:
        raise HTTPException(403, "Forbidden")

    # Stream PDF from Vercel Blob
    blob_url = document.blob_url
    async with httpx.AsyncClient() as client:
        response = await client.get(blob_url)

    # Return PDF with content-disposition header
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f"inline; filename={document.name}"
    }

    return Response(content=response.content, headers=headers)
```

**Frontend Implementation**:

```tsx
// frontend/components/EvidenceLink.tsx

interface EvidenceLinkProps {
  documentId: string
  documentName: string
  page: number
  section?: string
}

export function EvidenceLink({ documentId, documentName, page, section }: EvidenceLinkProps) {
  const handleClick = async () => {
    // Open PDF in new tab with page anchor
    const url = `/api/documents/${documentId}?page=${page}#page=${page}`
    window.open(url, '_blank')
  }

  return (
    <button onClick={handleClick} className="text-blue-600 hover:underline flex items-center gap-1">
      📄 {documentName} (page {page}
      {section && `, section ${section}`})
    </button>
  )
}
```

**Browser PDF Display**:

- Use native browser PDF viewer (Chrome/Firefox/Safari)
- URL anchor `#page=8` scrolls to page automatically
- Fallback: If browser doesn't support, download PDF

**Alternative Approach** (if native viewer unreliable):

- Embed PDF.js library for custom PDF viewer
- More control but adds complexity (~50KB bundle)
- Only implement if native viewer fails in testing

---

## Dependencies

**Blocks**:

- None (nice-to-have feature, improves UX)

**Blocked By**:

- STORY-015: Document upload (needs documents in storage)
- STORY-027: Results display (needs evidence links UI)

---

## Testing Requirements

**Unit Tests** (50% coverage):

- [ ] EvidenceLink component renders correctly
- [ ] Click handler generates correct URL
- [ ] Page parameter appended to URL
- [ ] Section displayed if available

**Integration Tests**:

- [ ] GET /v1/documents/:id streams PDF
- [ ] GET /v1/documents/:id?page=8 includes page parameter
- [ ] 403 if user lacks access to document

**E2E Tests** (critical):

- [ ] Click evidence link from results page
- [ ] PDF opens in new tab
- [ ] Browser scrolls to specified page
- [ ] Test across Chrome, Firefox, Safari

**Browser Compatibility**:

- [ ] Chrome: PDF displays with #page= anchor
- [ ] Firefox: PDF displays with #page= anchor
- [ ] Safari: PDF displays (Safari sometimes inconsistent)

---

## Design Reference

**Evidence Link Style**:

```
📄 test-report.pdf (page 8, section 3.2)
   ^               ^       ^            ^
   Icon            Name    Page         Section
```

**Hover State**:

- Underline on hover
- Pointer cursor
- Blue color (#2563eb from design system)

---

## RICE Score

**Reach**: 100 (every user clicks evidence)
**Impact**: 3 (high - critical for trust)
**Confidence**: 90% (browser compatibility risk)
**Effort**: 2 days

**RICE Score**: (100 × 3 × 0.90) ÷ 2 = **135**

---

## Definition of Done

- [ ] Evidence links clickable in results UI
- [ ] API endpoint `GET /v1/documents/:id?page=X` working
- [ ] PDF streams from Vercel Blob
- [ ] Opens in new tab with #page= anchor
- [ ] Browser scrolls to correct page
- [ ] Multi-tenant access control (can't access other org's docs)
- [ ] Download fallback if browser can't display
- [ ] Tested across Chrome, Firefox, Safari
- [ ] Unit tests pass (50% coverage)
- [ ] E2E test: Click evidence link → PDF opens at page
- [ ] Code reviewed and merged to main
- [ ] Deployed to staging

---

## Risks & Mitigations

**Risk**: Browser PDF viewer inconsistent across browsers (Safari issues)

- **Mitigation**: Test across all browsers; fallback to download if display fails
- **Alternative**: Embed PDF.js for custom viewer (adds complexity)

**Risk**: Large PDFs load slowly (>10MB files)

- **Mitigation**: Stream PDF (don't load entire file); show loading indicator

**Risk**: Page anchor doesn't work (browser ignores #page=)

- **Mitigation**: Test extensively; use PDF.js if native anchors unreliable

---

## Notes

This story delivers the **proof** that users need to trust AI results. Clicking evidence and seeing the exact page/section builds confidence that AI isn't hallucinating.

**Reference**: `product-guidelines/00-user-journey.md` (Step 3 - "AHA MOMENT")
