# [STORY-015] Document Upload API

**Type**: Story
**Epic**: EPIC-04 (Document Processing)
**Journey Step**: Step 2 - Upload Documents to Buckets
**Priority**: P0 (MVP Critical)
**RICE Score**: 135 (R:100 × I:3 × C:90% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When Project Handlers need to upload certification documents for validation, they need a secure API endpoint that accepts PDFs/DOCX files and stores them encrypted, so documents are ready for AI assessment.

**Value Delivered**: Secure, validated document upload that stores files encrypted in Vercel Blob, enabling the document collection step of the assessment workflow.

**Success Metric**: Upload success rate >95%, upload time <10 seconds for 10MB PDF.

---

## Acceptance Criteria

- [ ] `POST /v1/documents` endpoint accepts multipart/form-data
- [ ] Validates file type (PDF, DOCX only)
- [ ] Validates file size (max 50MB)
- [ ] Uploads file to Vercel Blob storage (encrypted at rest)
- [ ] Stores metadata in PostgreSQL (document_id, file_name, storage_key, bucket_id, organization_id)
- [ ] Returns document ID, file name, size, upload timestamp
- [ ] Multi-tenancy enforced (document assigned to user's organization)
- [ ] RBAC enforced (project_handler, process_manager, admin can upload)
- [ ] 400 Bad Request for invalid file type/size
- [ ] 413 Payload Too Large for files >50MB

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI (multipart/form-data handling)
- Storage: Vercel Blob (encrypted, 1GB free tier)
- Database: PostgreSQL (assessment_documents table)

**API Endpoint** (`app/api/v1/documents.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Document
from app.services.blob_storage import upload_to_vercel_blob
import magic  # python-magic for file type detection

router = APIRouter(prefix="/v1/documents", tags=["documents"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # DOCX
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    bucket_id: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload document to Vercel Blob storage.

    Journey Step 2: Project Handler uploads documents into workflow buckets.
    """
    # 1. Validate file type
    file_content = await file.read()
    mime_type = magic.from_buffer(file_content, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {mime_type}. Only PDF and DOCX allowed."
        )

    # 2. Validate file size
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large: {file_size} bytes. Max 50MB."
        )

    # 3. Upload to Vercel Blob
    try:
        storage_key = await upload_to_vercel_blob(
            file_content,
            filename=file.filename,
            content_type=mime_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

    # 4. Store metadata in database
    document = Document(
        organization_id=current_user["organization_id"],
        bucket_id=bucket_id,
        file_name=file.filename,
        file_size=file_size,
        mime_type=mime_type,
        storage_key=storage_key,
        uploaded_by=current_user["id"]
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return {
        "id": document.id,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "bucket_id": document.bucket_id,
        "uploaded_at": document.created_at,
        "storage_key": document.storage_key  # For internal use only
    }
```

**Vercel Blob Service** (`app/services/blob_storage.py`):
```python
from vercel_blob import put
import os
from datetime import datetime

async def upload_to_vercel_blob(
    file_content: bytes,
    filename: str,
    content_type: str
) -> str:
    """Upload file to Vercel Blob and return storage key"""
    blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")

    # Generate unique key with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    storage_key = f"documents/{timestamp}_{filename}"

    # Upload to Vercel Blob
    response = await put(
        storage_key,
        file_content,
        {
            "access": "private",  # Requires authentication
            "contentType": content_type,
            "addRandomSuffix": True  # Avoid collisions
        },
        token=blob_token
    )

    return response["url"]  # Return blob URL
```

**Example Request**:
```
POST /v1/documents
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <binary PDF data>
bucket_id: bucket_xyz
```

**Example Response**:
```json
{
  "id": "doc_abc123",
  "file_name": "technical_documentation.pdf",
  "file_size": 2048576,
  "mime_type": "application/pdf",
  "bucket_id": "bucket_xyz",
  "uploaded_at": "2025-11-17T14:30:00Z",
  "storage_key": "documents/20251117_143000_technical_documentation_xyz.pdf"
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-001 (Database Schema) - need assessment_documents table
  - STORY-009 (Create Workflow) - buckets must exist
- **Blocks**:
  - STORY-017 (Upload UI) - UI needs this endpoint
  - STORY-020 (PDF Parsing) - AI needs uploaded documents

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:
- API endpoint: 0.5 days (multipart handling)
- File validation: 0.5 days (type/size checks)
- Vercel Blob integration: 0.5 days (upload service)
- Testing: 0.5 days (upload scenarios, error cases)

---

## Definition of Done

- [ ] POST /v1/documents endpoint implemented
- [ ] Accepts multipart/form-data (file + bucket_id)
- [ ] Validates file type (PDF/DOCX only)
- [ ] Validates file size (<50MB)
- [ ] Uploads to Vercel Blob successfully
- [ ] Stores metadata in PostgreSQL
- [ ] Returns 201 Created with document details
- [ ] 400 Bad Request for invalid file type
- [ ] 413 Payload Too Large for files >50MB
- [ ] Multi-tenancy enforced (document.organization_id set)
- [ ] Integration tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:
- [ ] Upload valid PDF → 201 Created, file in Vercel Blob
- [ ] Upload DOCX → 201 Created
- [ ] Upload invalid file type (JPG) → 400 Bad Request
- [ ] Upload file >50MB → 413 Payload Too Large
- [ ] Upload without bucket_id → 400 Bad Request
- [ ] Vercel Blob upload fails → 500 Internal Server Error
- [ ] Document metadata stored with correct organization_id

**Performance Tests**:
- [ ] Upload 10MB PDF → <10 seconds
- [ ] Upload 5 documents concurrently → all succeed

---

## Risks & Mitigations

**Risk**: Large file uploads timeout
- **Mitigation**: Increase timeout to 60 seconds, use chunked upload if needed

**Risk**: Vercel Blob storage limits exceeded (1GB free)
- **Mitigation**: Monitor usage, upgrade to paid tier or migrate to S3

**Risk**: Malicious file upload (virus, script injection)
- **Mitigation**: Validate file type with magic bytes (not just extension), consider virus scanning

---

## Notes

- Store files with private access (authentication required)
- After completing this story, proceed to STORY-016 (Start Assessment API)
