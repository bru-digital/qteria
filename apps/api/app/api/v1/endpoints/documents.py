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
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict, cast
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
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

from app.constants import AssessmentStatus
from app.core.auth import AuthenticatedUser
from app.core.dependencies import get_db, check_upload_rate_limit, RedisClient
from app.core.exceptions import create_error_response
from app.models import Bucket, Workflow, Document, Assessment, AssessmentDocument
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


# TypedDict for file data structure used during batch upload
class FileData(TypedDict):
    """Type definition for file data dict during upload processing."""

    filename: str
    content: bytes
    size: int
    mime_type: str


def calculate_rate_limit_headers(
    redis: RedisClient,
    new_upload_count: int,
    current_user: AuthenticatedUser,
) -> dict[str, str]:
    """
    Calculate rate limit headers for successful uploads.

    Args:
        redis: Redis client (can be None if Redis unavailable)
        new_upload_count: Updated upload count after increment
        current_user: Authenticated user for logging context

    Returns:
        dict[str, str]: Rate limit headers to add to response (empty dict if calculation fails)

    Note:
        Graceful degradation: Returns empty dict if calculation fails
        (upload succeeds even if headers can't be calculated)
    """
    rate_limit_headers = {}

    try:
        if redis and new_upload_count > 0:
            from app.core.config import settings

            # Calculate headers immediately (minimize race window)
            # NOTE: Headers may be briefly stale under high concurrent load.
            # This is acceptable as enforcement (INCRBY in check_upload_rate_limit) is atomic.
            # Headers provide best-effort information, not enforcement.
            now_for_headers = datetime.now(timezone.utc)
            uploads_remaining = max(0, settings.UPLOAD_RATE_LIMIT_PER_HOUR - new_upload_count)

            # Calculate reset timestamp (next hour)
            reset_time = now_for_headers.replace(minute=0, second=0, microsecond=0) + timedelta(
                hours=1
            )
            reset_timestamp = int(reset_time.timestamp())

            # Store header values for later addition to response
            rate_limit_headers = {
                "Cache-Control": "no-store",  # Prevent caching of potentially stale values
                "X-RateLimit-Limit": str(settings.UPLOAD_RATE_LIMIT_PER_HOUR),
                "X-RateLimit-Remaining": str(uploads_remaining),
                "X-RateLimit-Reset": str(reset_timestamp),
            }

            logger.debug(
                "Rate limit headers calculated",
                extra={
                    "user_id": str(current_user.id),
                    "uploads_remaining": uploads_remaining,
                    "reset_timestamp": reset_timestamp,
                },
            )
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        # Expected errors in header calculation/formatting:
        # - ValueError: Invalid int/string conversion
        # - TypeError: Unexpected type in arithmetic operations
        # - KeyError: Missing config setting
        # - AttributeError: Missing attribute access
        # Graceful degradation: Don't fail upload if header calculation fails
        logger.warning(
            "Failed to calculate rate limit headers",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
    except Exception as e:
        # Unexpected error - log at ERROR level for investigation
        logger.error(
            "Unexpected error calculating rate limit headers",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

    return rate_limit_headers


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
    response: Response,
    redis: RedisClient,
    request: Request,
    files: list[UploadFile] = File(
        ..., description="Document files (PDF, DOCX, or XLSX) - max 20 files"
    ),
    bucket_id: str | None = Form(None, description="Optional bucket ID for validation"),
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

        # 2. Check upload rate limit BEFORE processing files
        #
        # DESIGN RATIONALE: Per-file rate limiting
        # - Each file in batch counts toward the 100 uploads/hour limit
        # - Example: Uploading 20 files = 20 uploads toward limit
        # - Check happens AFTER batch size validation (fail fast on batch size first)
        # - Check happens BEFORE file validation (avoid wasted work if rate limited)
        # - Returns new upload count for accurate rate limit headers (fixes race condition)
        new_upload_count = check_upload_rate_limit(
            current_user=current_user,
            redis=redis,
            db=db,
            file_count=len(files),
            request=request,
        )

        # 2a. Calculate rate limit headers immediately to minimize race window
        #     (per API contract: product-guidelines/08-api-contracts.md:838-846)
        #
        # DESIGN RATIONALE: Minimize race window from ~350 lines to ~5 lines
        # - Calculate headers RIGHT AFTER rate limit check (before file processing)
        # - Reduces race window from ~350 lines of processing to ~5 lines
        # - Rate limit ENFORCEMENT is still atomic and correct (increment-first approach)
        # - Header values may still be briefly stale under concurrent load, but much more accurate
        #
        # Headers will be added to response at the end of the function (after upload completes)
        rate_limit_headers = calculate_rate_limit_headers(redis, new_upload_count, current_user)

        # 3. Validate bucket_id if provided (multi-tenancy check) - BEFORE processing files
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
            bucket = (
                db.query(Bucket)
                .join(Workflow)
                .filter(
                    Bucket.id == bucket_uuid,
                    Workflow.organization_id == current_user.organization_id,
                )
                .first()
            )

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

        # 4. Read and validate ALL files BEFORE uploading ANY (atomic validation)
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

        file_data_list: list[FileData] = []
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
            file_data_list.append(
                {
                    "filename": file.filename or "unknown.pdf",
                    "content": file_content,
                    "size": file_size,
                    "mime_type": mime_type,
                }
            )

        # 5. ALL files validated successfully - now upload to Vercel Blob storage
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
        uploaded_blobs = []  # Track blobs for cleanup if DB save fails

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
                uploaded_blobs.append(storage_url)  # Track for potential cleanup
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

            # Add document metadata to database session (don't commit yet)
            # This completes STORY-015 acceptance criteria: "Stores metadata in PostgreSQL"
            document_record = Document(
                id=cast(Any, UUID(document_id)),  # SQLAlchemy _UUID_RETURN workaround
                organization_id=cast(
                    Any, current_user.organization_id
                ),  # SQLAlchemy _UUID_RETURN workaround
                file_name=file_data["filename"],
                file_size=file_data["size"],
                mime_type=file_data["mime_type"],
                storage_key=storage_url,
                bucket_id=(
                    cast(Any, UUID(bucket_id)) if bucket_id else None
                ),  # SQLAlchemy _UUID_RETURN workaround
                uploaded_by=cast(Any, current_user.id),  # SQLAlchemy _UUID_RETURN workaround
            )
            db.add(document_record)

            logger.debug(
                "Document metadata added to database session",
                extra={
                    "document_id": document_id,
                    "organization_id": str(current_user.organization_id),
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

        # Commit all documents in a single transaction
        # This is more performant than N commits for batch uploads
        try:
            db.commit()
            logger.info(
                "All document metadata committed to database",
                extra={
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                    "file_count": len(document_responses),
                },
            )
        except Exception as e:
            # Database save failed - rollback and clean up all uploaded blobs
            db.rollback()

            # Clean up all blobs from this batch (best effort)
            cleanup_errors = []
            for blob_url in uploaded_blobs:
                try:
                    await BlobStorageService.delete_file(blob_url)
                except Exception as cleanup_error:
                    cleanup_errors.append({"blob_url": blob_url, "error": str(cleanup_error)})

            if cleanup_errors:
                logger.error(
                    "Failed to clean up some orphaned blobs after database error",
                    extra={"cleanup_errors": cleanup_errors},
                    exc_info=True,
                )

            logger.error(
                "Failed to save document metadata to database",
                extra={
                    "user_id": str(current_user.id),
                    "file_count": len(file_data_list),
                    "error": str(e),
                },
                exc_info=True,
            )

            # Fail the upload - don't return success when database save fails
            raise create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="DATABASE_ERROR",
                message="Failed to save document metadata. Please try again.",
                details={"file_count": len(file_data_list)},
                request=request,
            )

        # Log successful upload for audit trail (SOC2 compliance)
        for i, doc_response in enumerate(document_responses):
            AuditService.log_event(
                db=db,
                action="document.upload.success",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                resource_id=doc_response.id,
                metadata={
                    "filename": doc_response.file_name,
                    "file_size": doc_response.file_size,
                    "mime_type": doc_response.mime_type,
                    "bucket_id": str(bucket_id) if bucket_id else None,
                    "batch_size": len(file_data_list),
                },
                request=request,
            )

            logger.info(
                "Document uploaded successfully in batch",
                extra={
                    "document_id": str(doc_response.id),
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                    "file_name": doc_response.file_name,
                    "storage_url": doc_response.storage_key,
                    "batch_size": len(file_data_list),
                },
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

        # Add rate limit headers to response (using pre-calculated values)
        # Headers were calculated immediately after rate limit check to minimize race window
        # (see header calculation at line ~236)
        try:
            if rate_limit_headers:
                for header_name, header_value in rate_limit_headers.items():
                    response.headers[header_name] = header_value

                logger.debug(
                    "Rate limit headers added to response",
                    extra={
                        "user_id": str(current_user.id),
                        "headers": rate_limit_headers,
                    },
                )
        except Exception as e:
            # Unexpected error adding headers - log but don't fail upload
            # (upload already completed successfully by this point)
            logger.warning(
                "Failed to add rate limit headers to response",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )

        # Return list of document responses
        #
        # DESIGN: Documents are now persisted to database at upload time
        #
        # This enables:
        # - Multi-tenancy validation for document downloads (STORY-018)
        # - Document reuse across multiple assessments
        # - Audit trail for document access
        # - Orphan document cleanup queries
        #
        # Documents are saved to both:
        # 1. `documents` table (standalone upload record)
        # 2. `assessment_documents` table (when linked to assessment)
        #
        # This completes STORY-015 acceptance criteria: "Stores metadata in PostgreSQL"

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
                if file and hasattr(file, "file") and hasattr(file.file, "close"):
                    try:
                        file.file.close()
                    except Exception:
                        # Ignore cleanup errors - file might already be closed
                        pass


@router.get(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Download document",
    description="""
Download document from Vercel Blob storage with optional page parameter for PDFs.

**Authorization**: Requires authentication. Users can only download documents from their organization.

**Multi-Tenancy**: Enforced - returns 404 if document belongs to different organization.

**Journey Step 3**: Users view documents referenced in AI evidence links (e.g., "Issue found on page 8").

**Query Parameters**:
- `page` (optional): PDF page number to hint for viewer (returned in X-PDF-Page header)

**Example Request**:
```
GET /v1/documents/550e8400-e29b-41d4-a716-446655440000?page=8
Authorization: Bearer <jwt_token>
```

**Example Response Headers**:
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: inline; filename="technical-spec.pdf"
X-PDF-Page: 8
Location: https://blob.vercel-storage.com/documents/...
```

**Response**: 302 Redirect to signed Vercel Blob URL (expires in 1 hour)

**Error Responses**:
- 404: Document not found or belongs to different organization
- 401: Missing or invalid authentication token
    """,
)
async def download_document(
    document_id: UUID,
    request: Request,
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
    page: int | None = None,
) -> Response:
    """
    Download document from Vercel Blob storage.

    Journey Step 3: Users view documents referenced in AI validation results.

    This endpoint returns a redirect to a signed Vercel Blob URL that expires in 1 hour.
    The frontend receives the signed URL and can display it in a PDF viewer or download it.

    Args:
        document_id: UUID of the document to download
        page: Optional page number for PDF viewing hint
        current_user: Authenticated user (from JWT)
        request: FastAPI request for audit logging
        db: Database session for audit logging

    Returns:
        Response: 302 redirect to signed Vercel Blob URL with appropriate headers

    Raises:
        HTTPException: 404 if document not found or access denied
    """
    try:
        logger.info(
            "Document download requested",
            extra={
                "document_id": str(document_id),
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "page": page,
            },
        )

        # 1. Query document by ID with multi-tenancy enforcement
        # Return 404 (not 403) for documents in other orgs to avoid info leakage
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id, Document.organization_id == current_user.organization_id
            )
            .first()
        )

        if not document:
            logger.warning(
                "Document not found or access denied",
                extra={
                    "document_id": str(document_id),
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                },
            )

            # Audit log for security monitoring
            AuditService.log_event(
                db=db,
                action="document.download.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "document_id": str(document_id),
                    "reason": "not_found_or_access_denied",
                },
                request=request,
            )

            raise create_error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="RESOURCE_NOT_FOUND",
                message="Document not found",
                request=request,
            )

        # 2. Get download URL from Vercel Blob
        try:
            download_url = await BlobStorageService.get_download_url(
                cast(str, document.storage_key)
            )
        except Exception as e:
            logger.error(
                "Failed to get download URL from Vercel Blob",
                extra={
                    "document_id": str(document_id),
                    "storage_key": document.storage_key,
                    "error": str(e),
                },
                exc_info=True,
            )

            raise create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="DOWNLOAD_URL_FAILED",
                message="Failed to generate download URL",
                request=request,
            )

        # 3. Log successful download for audit trail (SOC2 compliance)
        AuditService.log_event(
            db=db,
            action="document.download.success",
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            resource_type="document",
            resource_id=document_id,
            metadata={
                "file_name": document.file_name,
                "file_size": document.file_size,
                "mime_type": document.mime_type,
                "page": page,
            },
            request=request,
        )

        logger.info(
            "Document download URL generated successfully",
            extra={
                "document_id": str(document_id),
                "user_id": str(current_user.id),
                "file_name": document.file_name,
            },
        )

        # 4. Return redirect response with appropriate headers
        # Using 307 Temporary Redirect to preserve the GET method
        redirect_response = Response(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={
                "Location": download_url,
                "Content-Type": cast(str, document.mime_type),
                "Content-Disposition": f'inline; filename="{cast(str, document.file_name)}"',
            },
        )

        # 5. Add X-PDF-Page header if page parameter provided (for PDF viewers)
        if page and document.mime_type == "application/pdf":
            redirect_response.headers["X-PDF-Page"] = str(page)

        return redirect_response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during document download",
            extra={
                "document_id": str(document_id),
                "user_id": str(current_user.id),
                "error": str(e),
            },
            exc_info=True,
        )

        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred during document download.",
            request=request,
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="""
Delete document from Vercel Blob storage and database.

**Authorization**: Requires authentication. Users can only delete documents from their organization.

**Multi-Tenancy**: Enforced - returns 404 if document belongs to different organization.

**Business Rules**:
- ✅ Can delete documents not in any assessment
- ✅ Can delete documents in pending assessments
- ❌ Cannot delete documents in completed or in_progress assessments (maintains data integrity)

**Journey Step 2**: Users remove incorrect documents before or after upload.

**Example Request**:
```
DELETE /v1/documents/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <jwt_token>
```

**Example Response**:
```
HTTP/1.1 204 No Content
```

**Error Responses**:
- 404: Document not found or belongs to different organization
- 409: Document is part of completed or in_progress assessment
- 401: Missing or invalid authentication token
    """,
)
async def delete_document(
    document_id: UUID,
    request: Request,
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
) -> Response:
    """
    Delete document from Vercel Blob storage and database.

    Journey Step 2: Users manage uploaded documents before assessment.

    Args:
        document_id: UUID of the document to delete
        current_user: Authenticated user (from JWT)
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        Response: 204 No Content on successful deletion

    Raises:
        HTTPException: 404 if document not found, 409 if document in use by assessment
    """
    try:
        logger.info(
            "Document deletion requested",
            extra={
                "document_id": str(document_id),
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
            },
        )

        # 1. Query document by ID with multi-tenancy enforcement
        # Return 404 (not 403) for documents in other orgs to avoid info leakage
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id, Document.organization_id == current_user.organization_id
            )
            .first()
        )

        if not document:
            logger.warning(
                "Document not found or access denied for deletion",
                extra={
                    "document_id": str(document_id),
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                },
            )

            # Audit log for security monitoring
            AuditService.log_event(
                db=db,
                action="document.delete.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "document_id": str(document_id),
                    "reason": "not_found_or_access_denied",
                },
                request=request,
            )

            raise create_error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="RESOURCE_NOT_FOUND",
                message="Document not found",
                request=request,
            )

        # 2. Check if document is in a completed or processing assessment
        #
        # DESIGN RATIONALE: Document-AssessmentDocument Relationship
        # - AssessmentDocument table does NOT have a document_id foreign key (by design)
        # - AssessmentDocument stores storage_key directly (the Vercel Blob URL)
        # - This decouples assessment records from the standalone documents table
        # - Allows documents to be deleted from documents table while preserving assessment history
        # - We match by storage_key to check if this blob URL is referenced in any active assessment
        #
        # Why no foreign key?
        # - Assessments are immutable once completed (audit trail requirement)
        # - Even if document is deleted from documents table, assessment_documents preserves the history
        # - storage_key is the source of truth for what blob was used in the assessment
        #
        # See: product-guidelines/07-database-schema-essentials.md for table relationships
        assessment_doc = (
            db.query(AssessmentDocument)
            .join(Assessment)
            .filter(
                AssessmentDocument.storage_key == document.storage_key,
                Assessment.status.in_([AssessmentStatus.COMPLETED, AssessmentStatus.PROCESSING]),
            )
            .first()
        )

        if assessment_doc:
            logger.warning(
                "Cannot delete document - in use by assessment",
                extra={
                    "document_id": str(document_id),
                    "user_id": str(current_user.id),
                    "assessment_id": str(assessment_doc.assessment_id),
                    "assessment_status": assessment_doc.assessment.status,
                },
            )

            # Audit log for monitoring
            AuditService.log_event(
                db=db,
                action="document.delete.failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                resource_id=document_id,
                metadata={
                    "reason": "document_in_use_by_assessment",
                    "assessment_id": str(assessment_doc.assessment_id),
                    "assessment_status": assessment_doc.assessment.status,
                },
                request=request,
            )

            raise create_error_response(
                status_code=status.HTTP_409_CONFLICT,
                error_code="DOCUMENT_IN_USE",
                message=f"Cannot delete document used in {assessment_doc.assessment.status} assessment. Assessment must be pending, failed, or cancelled.",
                details={
                    "assessment_id": str(assessment_doc.assessment_id),
                    "assessment_status": assessment_doc.assessment.status,
                },
                request=request,
            )

        # 3. Delete from Vercel Blob storage (graceful degradation if blob deletion fails)
        #
        # DESIGN RATIONALE: Fail-Safe Architecture (product-guidelines/04-architecture.md:199-206)
        # - Database is source of truth (if DB says deleted, it's deleted)
        # - Blob deletion failure is non-critical (blob can be cleaned up later)
        # - User experience prioritized: deletion succeeds even if storage service unavailable
        # - Failed deletions tracked in audit log with needs_cleanup flag for monitoring
        blob_deleted = False
        try:
            blob_deleted = await BlobStorageService.delete_file(cast(str, document.storage_key))
            if not blob_deleted:
                logger.warning(
                    "Blob deletion returned False but continuing with database deletion",
                    extra={
                        "document_id": str(document_id),
                        "storage_key": document.storage_key,
                    },
                )

                # Track failed deletion for cleanup job monitoring
                AuditService.log_event(
                    db=db,
                    action="document.delete.blob_failed",
                    organization_id=current_user.organization_id,
                    user_id=current_user.id,
                    resource_type="document",
                    resource_id=document_id,
                    metadata={
                        "storage_key": document.storage_key,
                        "file_name": document.file_name,
                        "reason": "blob_deletion_returned_false",
                        "needs_cleanup": True,  # Flag for background cleanup job
                    },
                    request=request,
                )
        except Exception as e:
            # Log error but continue (blob may already be deleted or storage service unavailable)
            # Database record will still be deleted (graceful degradation)
            logger.error(
                "Failed to delete blob but continuing with database deletion",
                extra={
                    "document_id": str(document_id),
                    "storage_key": document.storage_key,
                    "error": str(e),
                },
                exc_info=True,
            )

            # Track failed deletion with error details for cleanup job and monitoring
            AuditService.log_event(
                db=db,
                action="document.delete.blob_failed",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                resource_id=document_id,
                metadata={
                    "storage_key": document.storage_key,
                    "file_name": document.file_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "needs_cleanup": True,  # Flag for background cleanup job
                },
                request=request,
            )

        # 4. Delete from database
        try:
            db.delete(document)
            db.commit()

            logger.info(
                "Document deleted successfully",
                extra={
                    "document_id": str(document_id),
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                    "file_name": document.file_name,
                    "blob_deleted": blob_deleted,
                },
            )
        except Exception as e:
            db.rollback()
            logger.error(
                "Failed to delete document from database",
                extra={
                    "document_id": str(document_id),
                    "error": str(e),
                },
                exc_info=True,
            )

            raise create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="DATABASE_ERROR",
                message="Failed to delete document. Please try again.",
                request=request,
            )

        # 5. Log successful deletion for audit trail (SOC2 compliance)
        AuditService.log_event(
            db=db,
            action="document.delete.success",
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            resource_type="document",
            resource_id=document_id,
            metadata={
                "file_name": document.file_name,
                "file_size": document.file_size,
                "mime_type": document.mime_type,
                "blob_deleted": blob_deleted,
            },
            request=request,
        )

        # Return 204 No Content
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during document deletion",
            extra={
                "document_id": str(document_id),
                "user_id": str(current_user.id),
                "error": str(e),
            },
            exc_info=True,
        )

        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred during document deletion.",
            request=request,
        )
