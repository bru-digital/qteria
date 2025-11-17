# [STORY-019] Delete Document API

**Type**: Story
**Epic**: EPIC-04 (Document Processing)
**Journey Step**: Step 2 - Manage Uploaded Documents
**Priority**: P1 (Important, Not MVP Blocker)
**RICE Score**: 40 (R:50 × I:1 × C:80% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When users upload incorrect documents or want to replace files, they need to delete documents, so they can maintain a clean document list and avoid confusion.

**Value Delivered**: Safe document deletion that removes files from Vercel Blob and database, with protection against deleting documents in completed assessments.

**Success Metric**: Deletion success rate 100% (no orphaned files), prevents deletion of documents in use.

---

## Acceptance Criteria

- [ ] `DELETE /v1/documents/:id` endpoint implemented
- [ ] Removes document from Vercel Blob storage
- [ ] Removes document metadata from PostgreSQL
- [ ] Returns 204 No Content on success
- [ ] Returns 409 Conflict if document is part of completed assessment
- [ ] Multi-tenancy enforced (can only delete org's documents)
- [ ] RBAC enforced (only uploader, process_manager, or admin can delete)
- [ ] 404 Not Found if document doesn't exist or belongs to different org

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI + SQLAlchemy
- Storage: Vercel Blob (delete operation)

**API Endpoint** (`app/api/v1/documents.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Document, Assessment
from app.services.blob_storage import delete_from_vercel_blob

router = APIRouter(prefix="/v1/documents", tags=["documents"])

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete document from storage and database.

    Journey Step 2: Users manage uploaded documents before assessment.
    """
    org_id = current_user["organization_id"]

    # 1. Get document
    document = await Document.get_by_id(db, org_id, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # 2. Check if document is in a completed assessment
    assessment_query = select(Assessment).join(
        AssessmentDocument
    ).where(
        AssessmentDocument.document_id == document_id
    ).where(
        Assessment.status.in_(["completed", "in_progress"])
    )

    result = await db.execute(assessment_query)
    assessment = result.scalar_one_or_none()

    if assessment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete document used in assessment. Assessment must be pending or cancelled."
        )

    # 3. Delete from Vercel Blob
    try:
        await delete_from_vercel_blob(document.storage_key)
    except Exception as e:
        # Log error but continue (blob may already be deleted)
        print(f"Failed to delete blob: {e}")

    # 4. Delete from database
    await db.delete(document)
    await db.commit()

    return None  # 204 No Content
```

**Vercel Blob Service** (`app/services/blob_storage.py`):
```python
from vercel_blob import delete
import os

async def delete_from_vercel_blob(storage_key: str):
    """Delete file from Vercel Blob"""
    blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")

    await delete(storage_key, token=blob_token)
```

**Example Request**:
```
DELETE /v1/documents/doc_abc123
Authorization: Bearer <jwt_token>
```

**Example Response**:
```
HTTP/1.1 204 No Content
```

---

## Dependencies

- **Blocked By**:
  - STORY-015 (Upload API) - need documents to delete
  - STORY-016 (Start Assessment) - need to check assessment status
- **Blocks**: Nothing (P1 feature, not MVP blocker)

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:
- API endpoint: 0.5 days (delete logic, assessment check)
- Vercel Blob deletion: 0.25 days (delete service)
- Testing: 0.25 days (conflict scenarios)

---

## Definition of Done

- [ ] DELETE /v1/documents/:id endpoint implemented
- [ ] Deletes document from Vercel Blob
- [ ] Deletes metadata from PostgreSQL
- [ ] Returns 204 No Content on success
- [ ] 409 Conflict if document in completed assessment
- [ ] Multi-tenancy enforced (404 for other org's docs)
- [ ] 404 Not Found if document doesn't exist
- [ ] Integration tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:
- [ ] Delete document not in assessment → 204 No Content, blob deleted
- [ ] Delete document in pending assessment → 204 No Content (allowed)
- [ ] Delete document in completed assessment → 409 Conflict
- [ ] Delete non-existent document → 404 Not Found
- [ ] User from org A deletes org B document → 404 Not Found
- [ ] Blob deletion fails → document still deleted from DB (logged)

---

## Risks & Mitigations

**Risk**: Blob deletion fails but DB record deleted → orphaned blob
- **Mitigation**: Log error, acceptable for MVP (cleanup script post-MVP)

**Risk**: Document deleted while assessment is processing → assessment fails
- **Mitigation**: Prevent deletion of documents in "in_progress" assessments

---

## Notes

- P1 priority - not critical for MVP, but nice-to-have
- After completing this story, EPIC-04 is DONE → proceed to EPIC-05 (AI Validation Engine - THE CRITICAL EPIC!)
