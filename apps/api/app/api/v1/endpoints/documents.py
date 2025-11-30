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
from datetime import datetime, timezone
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

# Initialize logger before importing magic (needed for startup validation)
logger = logging.getLogger(__name__)

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
from app.core.exceptions import create_error_response
from app.models import Bucket, Workflow
from app.schemas.document import (
    DocumentResponse,
    ALLOWED_MIME_TYPES,
    REJECTED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
    validate_file_size,
    validate_file_type,
)
from app.services.blob_storage import BlobStorageService
from app.services.audit import AuditService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload document(s)",
    description="""
Upload one or more documents to Vercel Blob storage for later use in assessments.

**Authorization**: Requires authentication (project_handler, process_manager, or admin).

**Multi-Tenancy**: Documents are automatically assigned to user's organization.

**Journey Step 2**: Project Handler uploads documents into workflow buckets.

**File Requirements**:
- Accepted types: PDF, DOCX, XLSX
- Maximum size per file: 50MB
- Maximum files per request: 20
- Content-based validation (not just extension)

**Example Request - Single File** (multipart/form-data):
```
POST /v1/documents
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

files: <binary PDF data>
bucket_id: 660e8400-e29b-41d4-a716-446655440001 (optional)
```

**Example Request - Multiple Files** (multipart/form-data):
```
POST /v1/documents
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

files: <binary PDF data 1>
files: <binary PDF data 2>
files: <binary DOCX data>
bucket_id: 660e8400-e29b-41d4-a716-446655440001 (optional)
```

**Example Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "technical-spec.pdf",
    "file_size": 2048576,
    "mime_type": "application/pdf",
    "storage_key": "https://blob.vercel-storage.com/documents/...",
    "bucket_id": "660e8400-e29b-41d4-a716-446655440001",
    "uploaded_at": "2024-11-17T14:30:00Z",
    "uploaded_by": "770e8400-e29b-41d4-a716-446655440002"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "file_name": "test-report.pdf",
    "file_size": 1024576,
    "mime_type": "application/pdf",
    "storage_key": "https://blob.vercel-storage.com/documents/...",
    "bucket_id": "660e8400-e29b-41d4-a716-446655440001",
    "uploaded_at": "2024-11-17T14:30:01Z",
    "uploaded_by": "770e8400-e29b-41d4-a716-446655440002"
  }
]
```
    """,
)
async def upload_document(
    current_user: AuthenticatedUser,
    files: list[UploadFile] = File(..., description="Document files (PDF, DOCX, or XLSX) - max 20 files"),
    bucket_id: Optional[str] = Form(
        None, description="Optional bucket ID for validation"
    ),
    request: Request = None,
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    """
    Upload one or more documents to Vercel Blob storage (batch upload).

    Journey Step 2: Project Handler uploads documents into workflow buckets.

    Args:
        files: List of uploaded files (PDF, DOCX, or XLSX) - max 20 files
        bucket_id: Optional bucket ID for early validation
        current_user: Authenticated user (from JWT)
        request: FastAPI request for audit logging
        db: Database session for audit logging

    Returns:
        list[DocumentResponse]: List of document metadata including storage URLs

    Raises:
        HTTPException: 400 for invalid file count/type/size, 500 for upload failures
    """
    try:
        # 1. Validate batch size (max 20 files per request)
        #
        # DESIGN RATIONALE: Atomic batch validation
        # - All files validated before ANY uploads (fail-fast pattern)
        # - Prevents partial uploads on batch size violation
        # - Guideline compliance: product-guidelines/08-api-contracts.md:364
        if len(files) > 20:
            logger.warning(
                "Document upload failed - too many files in batch",
                extra={
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                    "file_count": len(files),
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
                    "file_count": len(files),
                    "reason": "batch_size_exceeded",
                },
                request=request,
            )

            raise create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="BATCH_SIZE_EXCEEDED",
                message=f"Too many files in request: {len(files)}. Maximum allowed: 20 files per request.",
                details={
                    "file_count": len(files),
                    "max_files": 20,
                },
                request=request,
            )

        # Log batch upload attempt
        logger.info(
            "Document batch upload started",
            extra={
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "file_count": len(files),
                "file_names": [f.filename for f in files],
                "bucket_id": bucket_id,
            },
        )

        # 2. Validate bucket_id if provided (multi-tenancy check) - BEFORE processing files
        bucket = None
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
                raise create_error_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code="INVALID_BUCKET_ID",
                    message="bucket_id must be a valid UUID",
                    request=request,
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
                        "file_count": len(files),
                        "bucket_id": bucket_id,
                        "reason": "invalid_bucket_id",
                    },
                    request=request,
                )

                raise create_error_response(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_code="BUCKET_NOT_FOUND",
                    message="Bucket not found or access denied",
                    request=request,
                )

        # 3. Read and validate ALL files BEFORE uploading ANY (atomic validation)
        #
        # DESIGN RATIONALE: Fail-fast atomic batch processing
        # - Validate all files before uploading to prevent partial success scenarios
        # - If any file fails validation, entire batch fails (consistency)
        # - Single file failure = entire batch fails (atomic semantics)
        # - Memory impact: 20 files × 50MB = 1GB max (acceptable for MVP)
        #
        # Alternative approaches considered:
        # - Partial success with rollback: Too complex, requires tracking uploaded blobs
        # - Stream validation: Adds complexity without meaningful benefit at MVP scale
        # - Per-file validation + upload: Risk of partial uploads on mid-batch failure
        #
        # This approach optimizes for data consistency over memory efficiency.

        file_data_list = []
        for file in files:
            # Read file content and validate size
            file_content = file.file.read()
            file_size = len(file_content)

            # Validate file size using centralized validation function
            if not validate_file_size(file_size):
                # Check for empty file first (more specific error message)
                if file_size == 0:
                    logger.warning(
                        "Document upload failed - empty file in batch",
                        extra={
                            "user_id": str(current_user.id),
                            "file_name": file.filename,
                            "file_count": len(files),
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
                            "file_count": len(files),
                            "reason": "empty_file",
                        },
                        request=request,
                    )

                    raise create_error_response(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        error_code="EMPTY_FILE",
                        message=f"File '{file.filename}' is empty. Please upload valid documents.",
                        details={"file_name": file.filename},
                        request=request,
                    )

                # File too large
                error_msg = f"File '{file.filename}' too large: {file_size} bytes. Maximum allowed: {MAX_FILE_SIZE_BYTES} bytes (50MB)."
                logger.warning(
                    "Document upload failed - file too large in batch",
                    extra={
                        "user_id": str(current_user.id),
                        "file_name": file.filename,
                        "file_size": file_size,
                        "file_count": len(files),
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
                        "file_count": len(files),
                        "reason": "file_too_large",
                    },
                    request=request,
                )

                raise create_error_response(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    error_code="FILE_TOO_LARGE",
                    message=error_msg,
                    details={
                        "file_name": file.filename,
                        "file_size_bytes": file_size,
                        "max_size_bytes": MAX_FILE_SIZE_BYTES,
                    },
                    request=request,
                )

            # Validate file type using python-magic (content-based detection)
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
            except Exception as e:
                logger.error(
                    "Failed to detect MIME type in batch",
                    extra={
                        "file_name": file.filename,
                        "file_count": len(files),
                        "error": str(e),
                    },
                    exc_info=True,
                )
                # SECURITY: Fail closed - do not trust client-provided content_type
                # If content validation fails, reject the entire batch
                raise create_error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    error_code="MIME_DETECTION_FAILED",
                    message=f"Unable to validate file type for '{file.filename}'. Please try again.",
                    details={"file_name": file.filename},
                    request=request,
                )

            if not validate_file_type(mime_type):
                # SECURITY: Provide specific error message for macro-enabled files
                if mime_type in REJECTED_MIME_TYPES:
                    error_msg = f"Security: Macro-enabled files are not allowed. Detected: {mime_type} in '{file.filename}'. Please use standard formats (XLSX, DOCX, PDF)."
                else:
                    error_msg = f"Invalid file type: {mime_type} in '{file.filename}'. Only PDF, DOCX, and XLSX files are allowed."

                logger.warning(
                    "Document upload failed - invalid file type in batch",
                    extra={
                        "user_id": str(current_user.id),
                        "file_name": file.filename,
                        "detected_mime_type": mime_type,
                        "is_macro_enabled": mime_type in REJECTED_MIME_TYPES,
                        "file_count": len(files),
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
                        "file_count": len(files),
                        "reason": "invalid_file_type",
                    },
                    request=request,
                )

                raise create_error_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code="INVALID_FILE_TYPE",
                    message=error_msg,
                    details={
                        "file_name": file.filename,
                        "detected_mime_type": mime_type,
                        "allowed_types": list(ALLOWED_MIME_TYPES),
                    },
                    request=request,
                )

            # Store validated file data for upload phase
            file_data_list.append({
                "filename": file.filename,
                "content": file_content,
                "size": file_size,
                "mime_type": mime_type,
            })

        # 4. ALL files validated successfully - now upload to Vercel Blob storage
        #
        # DESIGN: Process files sequentially to manage memory usage
        # - Sequential uploads prevent 20 concurrent HTTP connections
        # - Simpler error handling (no partial upload cleanup needed)
        # - Memory-efficient (release each file after upload)
        # - Trade-off: Slower batch upload time, but acceptable for MVP
        #
        # Future optimization: Parallel uploads with asyncio.gather() for >10 file batches

        document_responses = []
        upload_timestamp = datetime.now(timezone.utc)

        for file_data in file_data_list:
            # Generate unique document ID for tracking
            document_id = str(uuid4())

            # Upload to Vercel Blob storage
            try:
                storage_url = await BlobStorageService.upload_file(
                    file_content=file_data["content"],
                    filename=file_data["filename"],
                    content_type=file_data["mime_type"],
                    organization_id=current_user.organization_id,
                    document_id=document_id,
                )
            except Exception as e:
                logger.error(
                    "Failed to upload file to Vercel Blob in batch",
                    extra={
                        "user_id": str(current_user.id),
                        "file_name": file_data["filename"],
                        "file_count": len(file_data_list),
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
                        "file_name": file_data["filename"],
                        "file_count": len(file_data_list),
                        "reason": "blob_storage_error",
                        "error": str(e),
                    },
                    request=request,
                )

                raise create_error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    error_code="UPLOAD_FAILED",
                    message=f"Failed to upload file '{file_data['filename']}' to storage. Please try again.",
                    details={"file_name": file_data["filename"]},
                    request=request,
                )

            # Log successful upload for audit trail (SOC2 compliance)
            AuditService.log_event(
                db=db,
                action="document.upload.success",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                resource_id=UUID(document_id),
                metadata={
                    "filename": file_data["filename"],
                    "file_size": file_data["size"],
                    "mime_type": file_data["mime_type"],
                    "bucket_id": bucket_id,
                    "batch_size": len(file_data_list),
                },
                request=request,
            )

            logger.info(
                "Document uploaded successfully in batch",
                extra={
                    "document_id": document_id,
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                    "file_name": file_data["filename"],
                    "storage_url": storage_url,
                    "batch_size": len(file_data_list),
                },
            )

            # Create response object
            document_responses.append(
                DocumentResponse(
                    id=UUID(document_id),
                    file_name=file_data["filename"],
                    file_size=file_data["size"],
                    mime_type=file_data["mime_type"],
                    storage_key=storage_url,
                    bucket_id=UUID(bucket_id) if bucket_id else None,
                    uploaded_at=upload_timestamp,
                    uploaded_by=current_user.id,
                )
            )

        logger.info(
            "Document batch upload completed successfully",
            extra={
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "file_count": len(document_responses),
                "file_names": [doc.file_name for doc in document_responses],
            },
        )

        # Return list of document responses
        #
        # DESIGN DECISION: No database persistence at upload time
        #
        # In the MVP, we return metadata for the frontend to use when creating assessments.
        # The documents will be formally saved to assessment_documents table when assessment is created.
        #
        # Rationale (same as single file upload):
        # - Simplifies upload flow (no database writes during upload)
        # - Assessment creation is the atomic operation that links documents to buckets/workflows
        # - Orphaned blobs are acceptable for MVP (cleanup job can be added post-launch)
        #
        # This design optimizes for Journey Step 3 (AI validation speed) over administrative queries.

        return document_responses

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors during batch upload
        logger.error(
            "Unexpected error during document batch upload",
            extra={
                "user_id": str(current_user.id),
                "file_count": len(files) if files else 0,
                "file_names": [f.filename for f in files] if files else [],
                "error": str(e),
            },
            exc_info=True,
        )

        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred during batch upload.",
            request=request,
        )
    finally:
        # Ensure all file handles are closed (defensive cleanup)
        if files:
            for file in files:
                if file and hasattr(file, 'file') and hasattr(file.file, "close"):
                    try:
                        file.file.close()
                    except Exception:
                        # Ignore cleanup errors - file might already be closed
                        pass
