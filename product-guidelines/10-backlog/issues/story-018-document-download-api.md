# [STORY-018] Document Download API

**Type**: Story
**Epic**: EPIC-04 (Document Processing)
**Journey Step**: Step 3 - View Document Evidence
**Priority**: P0 (MVP Critical for Evidence Links)
**RICE Score**: 160 (R:80 × I:2 × C:100% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When users need to view documents referenced in AI validation results (e.g., "Issue found on page 8"), they need to download/stream documents with optional page anchors, so they can quickly verify AI findings.

**Value Delivered**: Secure document streaming that enables evidence-based validation results with clickable links to exact document pages.

**Success Metric**: Download success rate >99%, download time <3 seconds for 10MB PDF.

---

## Acceptance Criteria

- [ ] `GET /v1/documents/:id` endpoint streams document from Vercel Blob
- [ ] Optional `?page=X` query parameter for PDF page linking
- [ ] Returns appropriate Content-Type header (application/pdf, etc.)
- [ ] Sets Content-Disposition header (inline for PDFs, attachment for others)
- [ ] Multi-tenancy enforced (can only download org's documents)
- [ ] RBAC enforced (all authenticated users can download)
- [ ] 404 Not Found if document doesn't exist or belongs to different org
- [ ] Streams large files efficiently (no memory issues)
- [ ] Supports HTTP range requests (for PDF viewers)

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI (streaming response)
- Storage: Vercel Blob (retrieve with signed URL)

**API Endpoint** (`app/api/v1/documents.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Document
from app.services.blob_storage import get_from_vercel_blob
import httpx

router = APIRouter(prefix="/v1/documents", tags=["documents"])

@router.get("/{document_id}")
async def download_document(
    document_id: str,
    page: int | None = Query(None, ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download document from Vercel Blob storage.

    Journey Step 3: Users view documents referenced in AI evidence links.
    """
    org_id = current_user["organization_id"]

    # 1. Get document metadata
    document = await Document.get_by_id(db, org_id, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # 2. Get signed URL from Vercel Blob
    blob_url = await get_from_vercel_blob(document.storage_key)

    # 3. Stream document from Vercel Blob
    async with httpx.AsyncClient() as client:
        response = await client.get(blob_url, timeout=30.0)
        response.raise_for_status()

    # 4. Set response headers
    headers = {
        "Content-Type": document.mime_type,
        "Content-Disposition": f'inline; filename="{document.file_name}"'
    }

    # 5. Add page anchor for PDFs (frontend will handle #page=X)
    if page and document.mime_type == "application/pdf":
        headers["X-PDF-Page"] = str(page)

    return StreamingResponse(
        iter([response.content]),
        headers=headers,
        media_type=document.mime_type
    )
```

**Vercel Blob Service** (`app/services/blob_storage.py`):
```python
from vercel_blob import get_download_url
import os

async def get_from_vercel_blob(storage_key: str) -> str:
    """Get signed download URL from Vercel Blob"""
    blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")

    # Get signed URL (expires in 1 hour)
    url = await get_download_url(
        storage_key,
        token=blob_token,
        expires_in=3600  # 1 hour
    )

    return url
```

**Frontend Usage** (Evidence Link):
```typescript
// Evidence link with page anchor
function EvidenceLink({ documentId, page }) {
  const url = `/api/v1/documents/${documentId}${page ? `?page=${page}` : ""}`

  return (
    <a href={url} target="_blank" className="text-blue-600 underline">
      View Document (Page {page})
    </a>
  )
}
```

**Example Request**:
```
GET /v1/documents/doc_abc123?page=8
Authorization: Bearer <jwt_token>
```

**Example Response**:
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: inline; filename="technical_documentation.pdf"
X-PDF-Page: 8

<binary PDF data>
```

---

## Dependencies

- **Blocked By**:
  - STORY-015 (Upload API) - need documents to download
- **Blocks**:
  - STORY-028 (Evidence Links) - evidence needs download endpoint

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:
- API endpoint: 0.5 days (streaming, headers)
- Vercel Blob signed URL: 0.25 days (get_download_url)
- Testing: 0.25 days (download scenarios, streaming)

---

## Definition of Done

- [ ] GET /v1/documents/:id endpoint implemented
- [ ] Streams document from Vercel Blob
- [ ] Returns appropriate Content-Type
- [ ] Sets Content-Disposition (inline for PDF)
- [ ] Supports ?page=X parameter for PDFs
- [ ] Multi-tenancy enforced (404 for other org's docs)
- [ ] 404 Not Found if document doesn't exist
- [ ] Handles large files efficiently (streaming)
- [ ] Integration tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:
- [ ] Download existing document → 200 OK, correct content
- [ ] Download with ?page=8 → X-PDF-Page header present
- [ ] Download non-existent document → 404 Not Found
- [ ] User from org A downloads org B document → 404 Not Found
- [ ] Download 50MB PDF → succeeds without memory issues

**Performance Tests**:
- [ ] Download 10MB PDF → <3 seconds
- [ ] Download 5 documents concurrently → all succeed

---

## Risks & Mitigations

**Risk**: Large file downloads exhaust memory
- **Mitigation**: Stream response (don't load entire file into memory)

**Risk**: Vercel Blob signed URLs expire mid-download
- **Mitigation**: Set expiration to 1 hour, sufficient for any download

---

## Notes

- Return 404 (not 403) for other org's documents to avoid info leakage
- After completing this story, proceed to STORY-019 (Delete Document)
