"""
Document upload API endpoints.

Journey Step 2: Project Handlers upload certification documents for AI validation.

Endpoints:
- POST /v1/documents - Upload document to Vercel Blob storage
- GET /v1/documents/{id} - Download document (future)
- DELETE /v1/documents/{id} - Delete uploaded document (future)

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

# Validate that libmagic is available at startup (fail fast if not installed)
try:
    # Test that libmagic system library is available
    magic.from_buffer(b"test", mime=True)
except Exception as e:
    logger.critical(
        "libmagic system library not available - python-magic requires libmagic to be installed",
        extra={"error": str(e)},
    )
    raise RuntimeError(
        "libmagic system library not found. "
        "Install it using: brew install libmagic (macOS) or apt-get install libmagic1 (Ubuntu)"
    ) from e

from app.core.auth import AuthenticatedUser
from app.core.dependencies import get_db
from app.models import Bucket, Workflow
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
async def upload_document(
    current_user: AuthenticatedUser,
    file: UploadFile = File(..., description="Document file (PDF or DOCX)"),
    bucket_id: Optional[str] = Form(
        None, description="Optional bucket ID for validation"
    ),
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
        # 1. Validate file size first (before reading into memory)
        # Get file size without reading entire content
        file.file.seek(0, 2)  # Seek to end of file
        file_size = file.file.tell()  # Get current position (file size)
        file.file.seek(0)  # Reset to beginning for later reading

        # Log upload attempt
        logger.info(
            "Document upload started",
            extra={
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "file_name": file.filename,
                "file_size": file_size,
                "bucket_id": bucket_id,
            },
        )

        # Check for empty file first (more specific error message)
        if file_size == 0:
            logger.warning(
                "Document upload failed - empty file",
                extra={
                    "user_id": str(current_user.id),
                    "file_name": file.filename,
                },
            )

            # Audit log for monitoring
            AuditService.log_event(
                db=db,
                action="document.upload.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "file_name": file.filename,
                    "file_size": 0,
                    "reason": "empty_file",
                },
                request=request,
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "EMPTY_FILE",
                    "message": "File is empty. Please upload a valid document.",
                },
            )

        # Check file size limit
        if file_size > MAX_FILE_SIZE_BYTES:
            error_msg = f"File too large: {file_size} bytes. Maximum allowed: {MAX_FILE_SIZE_BYTES} bytes (50MB)."
            logger.warning(
                "Document upload failed - file too large",
                extra={
                    "user_id": str(current_user.id),
                    "file_name": file.filename,
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
                    "file_name": file.filename,
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

        # 2. Validate bucket_id if provided (multi-tenancy check)
        if bucket_id:
            # Validate UUID format first
            try:
                bucket_uuid = UUID(bucket_id)
            except ValueError:
                logger.warning(
                    "Document upload failed - invalid bucket UUID format",
                    extra={
                        "user_id": str(current_user.id),
                        "bucket_id": bucket_id,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_BUCKET_ID",
                        "message": "bucket_id must be a valid UUID",
                    },
                )

            # Query bucket and join with workflow to check organization_id
            bucket = db.query(Bucket).join(Workflow).filter(
                Bucket.id == bucket_uuid,
                Workflow.organization_id == current_user.organization_id
            ).first()

            if not bucket:
                logger.warning(
                    "Document upload failed - invalid bucket",
                    extra={
                        "user_id": str(current_user.id),
                        "organization_id": str(current_user.organization_id),
                        "bucket_id": bucket_id,
                    },
                )

                # Audit log for security monitoring (potential cross-org access attempt)
                AuditService.log_event(
                    db=db,
                    action="document.upload.failed",
                    organization_id=current_user.organization_id,
                    user_id=current_user.id,
                    resource_type="document",
                    metadata={
                        "file_name": file.filename,
                        "bucket_id": bucket_id,
                        "reason": "invalid_bucket_id",
                    },
                    request=request,
                )

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "BUCKET_NOT_FOUND",
                        "message": "Bucket not found or access denied"
                    }
                )

        # 3. Read file content now that size and bucket are validated
        file_content = file.file.read()

        # 4. Validate file type using python-magic (content-based detection)
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
        except Exception as e:
            logger.error(
                "Failed to detect MIME type",
                extra={
                    "file_name": file.filename,
                    "error": str(e),
                },
                exc_info=True,
            )
            # SECURITY: Fail closed - do not trust client-provided content_type
            # If content validation fails, reject the upload
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "MIME_DETECTION_FAILED",
                    "message": "Unable to validate file type. Please try again.",
                },
            )

        if not validate_file_type(mime_type):
            error_msg = f"Invalid file type: {mime_type}. Only PDF and DOCX files are allowed."
            logger.warning(
                "Document upload failed - invalid file type",
                extra={
                    "user_id": str(current_user.id),
                    "file_name": file.filename,
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
                    "file_name": file.filename,
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

        # 5. Generate document ID for tracking
        document_id = str(uuid4())

        # 6. Upload to Vercel Blob storage
        try:
            storage_url = await BlobStorageService.upload_file(
                file_content=file_content,
                filename=file.filename,
                content_type=mime_type,
                organization_id=current_user.organization_id,
                document_id=document_id,
            )
        except Exception as e:
            logger.error(
                "Failed to upload file to Vercel Blob",
                extra={
                    "user_id": str(current_user.id),
                    "file_name": file.filename,
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
                    "file_name": file.filename,
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

        # 7. Log successful upload for audit trail (SOC2 compliance)
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
                "file_name": file.filename,
                "storage_url": storage_url,
            },
        )

        # 8. Return document response
        #
        # DESIGN DECISION: No database persistence at upload time
        #
        # In the MVP, we return metadata for the frontend to use when creating assessments.
        # The document will be formally saved to assessment_documents table when assessment is created.
        #
        # Rationale:
        # - Simplifies upload flow (no database writes during upload)
        # - Assessment creation is the atomic operation that links documents to buckets/workflows
        # - Orphaned blobs are acceptable for MVP (cleanup job can be added post-launch)
        #
        # Trade-offs:
        # - Risk: If frontend crashes after upload but before assessment creation, blob becomes orphaned
        # - Risk: No query capability for "all uploaded documents" or "documents uploaded in last 30 days"
        # - Mitigation: Vercel Blob has built-in retention policies; orphaned blobs auto-expire
        # - Future: Add documents table with status field (uploaded, attached, orphaned) post-MVP
        #
        # This design optimizes for Journey Step 3 (AI validation speed) over administrative queries.
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
                "file_name": file.filename if file else "unknown",
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
