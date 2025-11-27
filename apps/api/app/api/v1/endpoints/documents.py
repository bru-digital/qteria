"""
Document upload API endpoints.

Journey Step 2: Project Handlers upload certification documents for AI validation.

Endpoints:
- POST /v1/documents - Upload document to Vercel Blob storage
- GET /v1/documents/{id} - Download document (future)
- DELETE /v1/documents/{id} - Delete uploaded document (future)

Note: This endpoint is synchronous (def, not async def) following codebase patterns.
Documents are uploaded to Vercel Blob storage with encryption at rest and multi-tenant isolation.
"""
import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

import magic  # python-magic for MIME type detection

from app.core.auth import AuthenticatedUser
from app.core.dependencies import get_db
from app.schemas.document import (
    DocumentResponse,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
    validate_file_size,
    validate_file_type,
)
from app.services.blob_storage import BlobStorageService
from app.services.audit import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
    description="""
Upload a document to Vercel Blob storage for later use in assessments.

**Authorization**: Requires authentication (project_handler, process_manager, or admin).

**Multi-Tenancy**: Document is automatically assigned to user's organization.

**Journey Step 2**: Project Handler uploads documents into workflow buckets.

**File Requirements**:
- Accepted types: PDF, DOCX
- Maximum size: 50MB
- Content-based validation (not just extension)

**Example Request** (multipart/form-data):
```
POST /v1/documents
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: <binary PDF data>
bucket_id: 660e8400-e29b-41d4-a716-446655440001 (optional)
```

**Example Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "technical-spec.pdf",
  "file_size": 2048576,
  "mime_type": "application/pdf",
  "storage_key": "https://blob.vercel-storage.com/documents/...",
  "bucket_id": "660e8400-e29b-41d4-a716-446655440001",
  "uploaded_at": "2024-11-17T14:30:00Z",
  "uploaded_by": "770e8400-e29b-41d4-a716-446655440002"
}
```
    """,
)
def upload_document(
    file: UploadFile = File(..., description="Document file (PDF or DOCX)"),
    bucket_id: Optional[str] = Form(
        None, description="Optional bucket ID for validation"
    ),
    current_user: AuthenticatedUser = Depends(),
    request: Request = None,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """
    Upload document to Vercel Blob storage.

    Journey Step 2: Project Handler uploads documents into workflow buckets.

    Args:
        file: Uploaded file (PDF or DOCX)
        bucket_id: Optional bucket ID for early validation
        current_user: Authenticated user (from JWT)
        request: FastAPI request for audit logging
        db: Database session for audit logging

    Returns:
        DocumentResponse: Document metadata including storage URL

    Raises:
        HTTPException: 400 for invalid file type/size, 500 for upload failures
    """
    try:
        # Read file content
        file_content = file.file.read()
        file_size = len(file_content)

        # Log upload attempt
        logger.info(
            "Document upload started",
            extra={
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "filename": file.filename,
                "file_size": file_size,
                "bucket_id": bucket_id,
            },
        )

        # 1. Validate file size
        if not validate_file_size(file_size):
            error_msg = f"File too large: {file_size} bytes. Maximum allowed: {MAX_FILE_SIZE_BYTES} bytes (50MB)."
            logger.warning(
                "Document upload failed - file too large",
                extra={
                    "user_id": str(current_user.id),
                    "filename": file.filename,
                    "file_size": file_size,
                },
            )

            # Audit log for security monitoring
            AuditService.log_event(
                db=db,
                action="document.upload.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "filename": file.filename,
                    "file_size": file_size,
                    "reason": "file_too_large",
                },
                request=request,
            )

            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "code": "FILE_TOO_LARGE",
                    "message": error_msg,
                    "file_size_bytes": file_size,
                    "max_size_bytes": MAX_FILE_SIZE_BYTES,
                },
            )

        # 2. Validate file type using python-magic (content-based detection)
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
        except Exception as e:
            logger.error(
                "Failed to detect MIME type",
                extra={
                    "filename": file.filename,
                    "error": str(e),
                },
                exc_info=True,
            )
            # Fallback to file extension check if magic fails
            mime_type = file.content_type or "application/octet-stream"

        if not validate_file_type(mime_type):
            allowed_types_str = ", ".join(ALLOWED_MIME_TYPES)
            error_msg = f"Invalid file type: {mime_type}. Only PDF and DOCX files are allowed."
            logger.warning(
                "Document upload failed - invalid file type",
                extra={
                    "user_id": str(current_user.id),
                    "filename": file.filename,
                    "detected_mime_type": mime_type,
                },
            )

            # Audit log for security monitoring (potential malicious upload attempt)
            AuditService.log_event(
                db=db,
                action="document.upload.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "filename": file.filename,
                    "detected_mime_type": mime_type,
                    "reason": "invalid_file_type",
                },
                request=request,
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_FILE_TYPE",
                    "message": error_msg,
                    "detected_mime_type": mime_type,
                    "allowed_types": list(ALLOWED_MIME_TYPES),
                },
            )

        # 3. Generate document ID for tracking
        document_id = str(uuid4())

        # 4. Upload to Vercel Blob storage
        try:
            # Note: BlobStorageService methods need to be awaited
            # but we're using sync endpoint pattern, so we need to handle this
            import asyncio

            storage_url = asyncio.run(
                BlobStorageService.upload_file(
                    file_content=file_content,
                    filename=file.filename,
                    content_type=mime_type,
                    organization_id=current_user.organization_id,
                    document_id=document_id,
                )
            )
        except Exception as e:
            logger.error(
                "Failed to upload file to Vercel Blob",
                extra={
                    "user_id": str(current_user.id),
                    "filename": file.filename,
                    "error": str(e),
                },
                exc_info=True,
            )

            # Audit log for operational monitoring
            AuditService.log_event(
                db=db,
                action="document.upload.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "filename": file.filename,
                    "reason": "blob_storage_error",
                    "error": str(e),
                },
                request=request,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UPLOAD_FAILED",
                    "message": "Failed to upload file to storage. Please try again.",
                },
            )

        # 5. Log successful upload for audit trail (SOC2 compliance)
        AuditService.log_event(
            db=db,
            action="document.upload.success",
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            resource_type="document",
            resource_id=UUID(document_id),
            metadata={
                "filename": file.filename,
                "file_size": file_size,
                "mime_type": mime_type,
                "bucket_id": bucket_id,
            },
            request=request,
        )

        logger.info(
            "Document upload completed successfully",
            extra={
                "document_id": document_id,
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "filename": file.filename,
                "storage_url": storage_url,
            },
        )

        # 6. Return document response
        # Note: In the MVP, we return metadata for the frontend to use when creating assessments
        # The document will be formally saved to assessment_documents table when assessment is created
        from datetime import datetime, timezone

        return DocumentResponse(
            id=UUID(document_id),
            file_name=file.filename,
            file_size=file_size,
            mime_type=mime_type,
            storage_key=storage_url,
            bucket_id=UUID(bucket_id) if bucket_id else None,
            uploaded_at=datetime.now(timezone.utc),
            uploaded_by=current_user.id,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(
            "Unexpected error during document upload",
            extra={
                "user_id": str(current_user.id),
                "filename": file.filename if file else "unknown",
                "error": str(e),
            },
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during upload.",
            },
        )
    finally:
        # Ensure file handle is closed
        if file and hasattr(file.file, "close"):
            file.file.close()
