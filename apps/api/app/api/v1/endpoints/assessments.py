"""
Assessment API endpoints.

Journey Step 2→3: Project Handler starts assessment → AI validates documents.

Endpoints:
- POST /v1/assessments - Start new assessment (creates record, validates documents, enqueues background job)

Assessments represent the AI validation process where uploaded documents are checked
against workflow criteria.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.auth import AuthenticatedUser
from app.core.dependencies import get_db
from app.core.exceptions import create_error_response
from app.models import Assessment, AssessmentDocument, Workflow
from app.schemas.assessment import AssessmentCreate, AssessmentResponse
from app.services.audit import AuditService

router = APIRouter(prefix="/assessments", tags=["Assessments"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start new assessment",
    description="""
Start a new assessment with uploaded documents.

**Journey Step 2→3**: Project Handler finishes uploading documents and starts AI validation.

**Authorization**: Requires authentication (project_handler, process_manager, or admin).

**Multi-Tenancy**: Can only use workflows and documents from user's organization.

**Process**:
1. Validates workflow exists and belongs to user's organization
2. Validates all required buckets have at least one document
3. Validates all bucket references belong to the workflow
4. Creates assessment record with status "pending"
5. Creates assessment_documents join records
6. Enqueues Celery background job for AI validation (STORY-023 - stubbed for now)
7. Returns assessment details with estimated completion time

**Example Request**:
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "documents": [
    {
      "bucket_id": "660e8400-e29b-41d4-a716-446655440001",
      "document_id": "770e8400-e29b-41d4-a716-446655440002",
      "file_name": "technical-spec.pdf",
      "storage_key": "https://blob.vercel-storage.com/...",
      "file_size": 2048576
    },
    {
      "bucket_id": "660e8400-e29b-41d4-a716-446655440003",
      "document_id": "880e8400-e29b-41d4-a716-446655440004",
      "file_name": "test-report.pdf",
      "storage_key": "https://blob.vercel-storage.com/...",
      "file_size": 1536000
    }
  ]
}
```

**Example Response**:
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440005",
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "started_at": "2024-11-17T14:45:00Z",
  "estimated_completion_at": "2024-11-17T14:55:00Z",
  "document_count": 2
}
```
    """,
)
async def start_assessment(
    data: AssessmentCreate,
    current_user: AuthenticatedUser,
    request: Request,
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    """
    Start assessment with uploaded documents.

    Journey Step 2: Project Handler starts AI validation after uploading documents.

    Args:
        data: Assessment creation request with workflow_id and document mappings
        current_user: Authenticated user (from JWT)
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        AssessmentResponse: Assessment details with estimated completion time

    Raises:
        HTTPException: 404 if workflow/documents not found, 400 if missing required buckets
    """
    org_id = current_user.organization_id

    logger.info(
        "Starting assessment creation",
        extra={
            "user_id": str(current_user.id),
            "organization_id": str(org_id),
            "workflow_id": str(data.workflow_id),
            "document_count": len(data.documents),
        },
    )

    # 1. Get workflow and validate ownership (multi-tenancy)
    #
    # DESIGN: Eager load buckets for required bucket validation
    # - selectinload prevents N+1 queries
    # - Filter by organization_id enforces multi-tenancy
    workflow = (
        db.query(Workflow)
        .options(selectinload(Workflow.buckets))
        .filter(
            Workflow.id == data.workflow_id,
            Workflow.organization_id == org_id,
        )
        .first()
    )

    if not workflow:
        logger.warning(
            "Workflow not found or access denied",
            extra={
                "user_id": str(current_user.id),
                "workflow_id": str(data.workflow_id),
                "organization_id": str(org_id),
            },
        )

        # Audit log for security monitoring
        AuditService.log_event(
            db=db,
            action="assessment.create.failed",
            organization_id=org_id,
            user_id=current_user.id,
            resource_type="assessment",
            metadata={
                "workflow_id": str(data.workflow_id),
                "reason": "workflow_not_found",
            },
            request=request,
        )

        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Workflow not found",
            details={"workflow_id": str(data.workflow_id)},
            request=request,
        )

    # 2. Validate all required buckets have documents
    #
    # VALIDATION ORDER (UX): Check missing required buckets BEFORE invalid bucket references
    # This is intentional for better user experience:
    #
    # Example scenario:
    # - Workflow has required bucket: "Test Reports"
    # - User uploads to: Invalid bucket from different workflow
    # - User forgot: "Test Reports" (required)
    #
    # Good UX (current): "Missing documents for required buckets: Test Reports"
    # → User knows to upload Test Reports (clear action)
    #
    # Bad UX (if order reversed): "Invalid bucket reference: bucket does not belong to this workflow"
    # → User thinks they need to fix bucket reference (confusing - what's the right bucket?)
    # → They're still missing the required document anyway!
    #
    # DESIGN: Required bucket validation logic
    # - Build set of provided bucket IDs from document mappings
    # - Build set of required bucket IDs from workflow definition
    # - Check if all required buckets are covered
    required_buckets = [b for b in workflow.buckets if b.required]
    provided_bucket_ids: set[UUID] = {doc.bucket_id for doc in data.documents}
    required_bucket_ids: set[UUID] = {
        cast(UUID, b.id) for b in required_buckets if b.id is not None
    }

    missing_buckets = required_bucket_ids - provided_bucket_ids
    if missing_buckets:
        # Get bucket names for better error message
        missing_bucket_names = [b.name for b in required_buckets if b.id in missing_buckets]

        logger.warning(
            "Assessment creation failed - missing required buckets",
            extra={
                "user_id": str(current_user.id),
                "workflow_id": str(data.workflow_id),
                "missing_buckets": [str(bid) for bid in missing_buckets],
                "missing_bucket_names": missing_bucket_names,
            },
        )

        # Audit log for monitoring
        AuditService.log_event(
            db=db,
            action="assessment.create.failed",
            organization_id=org_id,
            user_id=current_user.id,
            resource_type="assessment",
            metadata={
                "workflow_id": str(data.workflow_id),
                "missing_buckets": [str(bid) for bid in missing_buckets],
                "missing_bucket_names": missing_bucket_names,
                "reason": "missing_required_buckets",
            },
            request=request,
        )

        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=f"Missing documents for required buckets: {', '.join(filter(None, missing_bucket_names))}",
            details={
                "missing_bucket_ids": [str(bid) for bid in missing_buckets],
                "missing_bucket_names": missing_bucket_names,
            },
            request=request,
        )

    # 3. Validate bucket IDs exist in workflow
    #
    # VALIDATION ORDER: This check happens AFTER required bucket validation
    # See comment above (lines 175-188) for UX rationale
    #
    # DESIGN: Validate that all referenced buckets belong to the workflow
    # - Prevents referencing buckets from other workflows
    # - Validates bucket ownership at API level (defense in depth with DB foreign keys)
    #
    # NOTE: Tests verify this order in test_validation_order_missing_required_takes_precedence()
    # and test_validation_order_only_invalid_bucket_when_no_missing_required()
    workflow_bucket_ids: set[UUID] = {
        cast(UUID, b.id) for b in workflow.buckets if b.id is not None
    }
    invalid_bucket_ids = provided_bucket_ids - workflow_bucket_ids

    if invalid_bucket_ids:
        logger.warning(
            "Assessment creation failed - invalid bucket references",
            extra={
                "user_id": str(current_user.id),
                "workflow_id": str(data.workflow_id),
                "invalid_bucket_ids": [str(bid) for bid in invalid_bucket_ids],
            },
        )

        # Audit log for monitoring
        AuditService.log_event(
            db=db,
            action="assessment.create.failed",
            organization_id=org_id,
            user_id=current_user.id,
            resource_type="assessment",
            metadata={
                "workflow_id": str(data.workflow_id),
                "invalid_bucket_ids": [str(bid) for bid in invalid_bucket_ids],
                "reason": "invalid_bucket_references",
            },
            request=request,
        )

        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=f"Invalid bucket references: buckets do not belong to this workflow",
            details={
                "invalid_bucket_ids": [str(bid) for bid in invalid_bucket_ids],
            },
            request=request,
        )

    # 4. Create assessment record
    #
    # DESIGN: Assessment creation with database transaction
    # - All assessment + assessment_documents created atomically
    # - Rollback on any error ensures data consistency
    # - Status starts as "pending" until background job picks it up
    try:
        assessment = Assessment(
            organization_id=cast(Any, org_id),
            workflow_id=cast(Any, data.workflow_id),
            created_by=cast(Any, current_user.id),
            status="pending",
            started_at=datetime.now(timezone.utc),
        )
        db.add(assessment)
        db.flush()  # Get assessment.id for join records

        # 5. Create assessment_documents join records
        #
        # DESIGN: Store document metadata in assessment_documents table
        # - Document metadata from upload API response (passed in request)
        # - Links assessment → bucket → document file
        # - Enables querying "which documents were used in this assessment"
        for doc_mapping in data.documents:
            assessment_doc = AssessmentDocument(
                assessment_id=assessment.id,
                bucket_id=cast(Any, doc_mapping.bucket_id),
                file_name=doc_mapping.file_name,
                storage_key=doc_mapping.storage_key,
                file_size_bytes=doc_mapping.file_size,
                uploaded_at=datetime.now(timezone.utc),
            )
            db.add(assessment_doc)

        db.commit()
        db.refresh(assessment)

        logger.info(
            "Assessment created successfully",
            extra={
                "user_id": str(current_user.id),
                "assessment_id": str(assessment.id),
                "workflow_id": str(data.workflow_id),
                "document_count": len(data.documents),
            },
        )

        # Audit log for compliance
        AuditService.log_event(
            db=db,
            action="assessment.created",
            organization_id=org_id,
            user_id=current_user.id,
            resource_type="assessment",
            resource_id=cast(UUID, assessment.id),
            metadata={
                "workflow_id": str(data.workflow_id),
                "document_count": len(data.documents),
            },
            request=request,
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(
            "Database integrity violation during assessment creation",
            extra={
                "user_id": str(current_user.id),
                "workflow_id": str(data.workflow_id),
                "error": str(e),
            },
            exc_info=True,
        )

        # Audit log for monitoring
        # NOTE: Audit logging after rollback uses the same session after rollback,
        # which is safe because AuditService.log_event() commits in a new transaction.
        # The structured logger above also captures this event for real-time monitoring.
        try:
            AuditService.log_event(
                db=db,
                action="assessment.create.failed",
                organization_id=org_id,
                user_id=current_user.id,
                resource_type="assessment",
                metadata={
                    "workflow_id": str(data.workflow_id),
                    "error": str(e),
                    "reason": "integrity_error",
                },
                request=request,
            )
        except Exception as audit_error:
            # If audit logging fails, log the failure but don't block the error response
            logger.warning(
                "Failed to write audit log after rollback",
                extra={
                    "original_error": str(e),
                    "audit_error": str(audit_error),
                },
            )

        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="DATABASE_ERROR",
            message="Invalid data reference. Please check your bucket and document IDs.",
            details={"error_detail": str(e)},
            request=request,
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Database error during assessment creation",
            extra={
                "user_id": str(current_user.id),
                "workflow_id": str(data.workflow_id),
                "error": str(e),
            },
            exc_info=True,
        )

        # Audit log for monitoring
        try:
            AuditService.log_event(
                db=db,
                action="assessment.create.failed",
                organization_id=org_id,
                user_id=current_user.id,
                resource_type="assessment",
                metadata={
                    "workflow_id": str(data.workflow_id),
                    "error": str(e),
                    "reason": "database_error",
                },
                request=request,
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to write audit log after rollback",
                extra={
                    "original_error": str(e),
                    "audit_error": str(audit_error),
                },
            )

        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message="Database error occurred. Please try again.",
            details={"error_detail": str(e)},
            request=request,
        )

    except Exception as e:
        db.rollback()
        logger.critical(
            "Unexpected error during assessment creation",
            extra={
                "user_id": str(current_user.id),
                "workflow_id": str(data.workflow_id),
                "error": str(e),
            },
            exc_info=True,
        )

        # Audit log for monitoring
        try:
            AuditService.log_event(
                db=db,
                action="assessment.create.failed",
                organization_id=org_id,
                user_id=current_user.id,
                resource_type="assessment",
                metadata={
                    "workflow_id": str(data.workflow_id),
                    "error": str(e),
                    "reason": "unexpected_error",
                },
                request=request,
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to write audit log after rollback",
                extra={
                    "original_error": str(e),
                    "audit_error": str(audit_error),
                },
            )

        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred. Please try again.",
            details={"error_detail": str(e)},
            request=request,
        )

    # 6. Enqueue background job for AI validation (STORY-023)
    #
    # DESIGN: Background job stub
    # - For MVP: Stub this out, implement in STORY-023
    # - Future: Enqueue Celery task for AI validation
    # - from app.tasks import run_ai_validation
    # - run_ai_validation.delay(assessment.id)
    #
    # NOTE: This is intentionally stubbed as per the issue description and approved plan

    # 7. Estimate completion time (5-10 minutes)
    #
    # DESIGN: Estimated completion time calculation
    # - Based on typical AI validation time (5-10 minutes per assessment)
    # - Used for frontend progress indicators
    # - Actual completion tracked via assessment.status updates
    estimated_completion = datetime.now(timezone.utc) + timedelta(minutes=10)

    return AssessmentResponse(
        id=assessment.id,
        workflow_id=assessment.workflow_id,
        status=assessment.status,
        started_at=assessment.started_at,
        estimated_completion_at=estimated_completion,
        document_count=len(data.documents),
    )
