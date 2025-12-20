"""
Workflow management API endpoints.

Journey Step 1: Process Managers create and manage validation workflows.

Endpoints:
- POST /v1/workflows - Create workflow with nested buckets and criteria
- GET /v1/workflows - List workflows for organization
- GET /v1/workflows/{id} - Get workflow details
- PUT /v1/workflows/{id} - Update workflow
- DELETE /v1/workflows/{id} - Archive workflow (soft delete)

Note: All endpoints use `def` (not `async def`) because:
- No async operations (no await calls to async DB, external APIs, etc.)
- SQLAlchemy ORM operations are synchronous
- FastAPI handles both sync and async functions efficiently
- Using `def` is more accurate and avoids unnecessary async overhead
"""

from typing import List
from uuid import UUID
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.core.auth import ProcessManagerOrAdmin, AuthenticatedUser, CurrentUser
from app.core.dependencies import get_db
from app.core.exceptions import create_error_response
from app.models import Workflow, Bucket, Criteria, Assessment
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListItem,
    WorkflowListResponse,
    PaginationMeta,
)
from app.services.audit import AuditService, AuditEventType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])

# Allowed sort fields mapping for security and maintainability
ALLOWED_SORT_FIELDS = {
    "created_at": Workflow.created_at,
    "name": Workflow.name,
}


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workflow",
    description="""
Create a new validation workflow with nested buckets and criteria in a single transaction.

**Authorization**: Requires `process_manager` or `admin` role.

**Multi-Tenancy**: Workflow is automatically assigned to user's organization.

**Journey Step 1**: Process Manager defines validation workflow structure.

**Example Request**:
```json
{
  "name": "Medical Device - Class II",
  "description": "Validation workflow for Class II medical devices",
  "buckets": [
    {
      "name": "Technical Documentation",
      "required": true,
      "order_index": 0
    },
    {
      "name": "Test Reports",
      "required": true,
      "order_index": 1
    }
  ],
  "criteria": [
    {
      "name": "All documents must be signed",
      "description": "Each document should have authorized signature",
      "applies_to_bucket_ids": [0, 1]
    }
  ]
}
```
    """,
)
def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: ProcessManagerOrAdmin,
    request: Request,
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """
    Create workflow with nested buckets and criteria.

    This endpoint creates:
    1. Workflow record
    2. Associated bucket records
    3. Associated criteria records

    All in a single database transaction (atomic operation).

    Args:
        workflow_data: Workflow creation data with nested buckets and criteria
        current_user: Authenticated user (requires process_manager or admin role)
        db: Database session

    Returns:
        WorkflowResponse: Created workflow with all nested data and generated IDs

    Raises:
        HTTPException 400: Validation error (invalid data)
        HTTPException 403: Insufficient permissions (not process_manager/admin)
        HTTPException 500: Database error
    """
    try:
        # Validate duplicate bucket names (case-insensitive)
        from collections import Counter

        bucket_names = [bucket.name for bucket in workflow_data.buckets]
        bucket_names_lower = [name.lower() for name in bucket_names]

        # Find duplicates
        name_counts = Counter(bucket_names_lower)
        duplicates = [name for name, count in name_counts.items() if count > 1]

        if duplicates:
            raise create_error_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="VALIDATION_ERROR",
                message="Duplicate bucket names not allowed within a workflow",
                details={
                    "duplicate_names": duplicates,
                    "bucket_names": bucket_names
                },
                request=request,
            )

        # Begin transaction (SQLAlchemy session handles this)
        # 1. Create workflow
        workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            organization_id=current_user.organization_id,
            created_by=current_user.id,
            is_active=True,
        )
        db.add(workflow)
        db.flush()  # Get workflow.id without committing

        # 2. Create buckets
        buckets = []
        for bucket_data in workflow_data.buckets:
            bucket = Bucket(
                workflow_id=workflow.id,
                name=bucket_data.name,
                required=bucket_data.required,
                order_index=bucket_data.order_index,
            )
            db.add(bucket)
            buckets.append(bucket)

        db.flush()  # Get bucket IDs

        # 3. Create criteria
        # Map bucket indexes to actual bucket UUIDs
        bucket_index_to_id = {i: bucket.id for i, bucket in enumerate(buckets)}

        for idx, criteria_data in enumerate(workflow_data.criteria):
            # Convert bucket indexes to UUIDs
            applies_to_bucket_ids = (
                [
                    bucket_index_to_id[bucket_idx]
                    for bucket_idx in criteria_data.applies_to_bucket_ids
                ]
                if criteria_data.applies_to_bucket_ids
                else None  # None = applies to all buckets
            )

            criteria = Criteria(
                workflow_id=workflow.id,
                name=criteria_data.name,
                description=criteria_data.description,
                applies_to_bucket_ids=applies_to_bucket_ids,
                order_index=idx,
            )
            db.add(criteria)

        db.flush()

        # 4. Log workflow creation (audit trail) - BEFORE commit for atomicity
        AuditService.log_workflow_created(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            request=request,
        )

        # 5. Commit transaction (includes audit log)
        db.commit()

        # 6. Refresh to get all relationships
        db.refresh(workflow)

        # 7. Log success
        logger.info(
            "workflow_created",
            extra={
                "workflow_id": str(workflow.id),
                "organization_id": str(current_user.organization_id),
                "created_by": str(current_user.id),
                "buckets_count": len(buckets),
                "criteria_count": len(workflow.criteria),
            },
        )

        # 8. Return workflow response
        # Use Pydantic's ORM mode to automatically map SQLAlchemy model to response schema
        # This ensures type safety and validates all fields according to the schema
        return WorkflowResponse.model_validate(workflow)

    except IntegrityError as e:
        db.rollback()

        # Extract detailed SQL error information for debugging
        error_details = {
            "error": str(e),
            "error_orig": str(e.orig) if hasattr(e, "orig") else None,
            "statement": str(e.statement) if hasattr(e, "statement") else None,
            "params": str(e.params) if hasattr(e, "params") else None,
            "organization_id": str(current_user.organization_id),
            "user_id": str(current_user.id),
        }

        # Try to extract constraint name from PostgreSQL error
        if hasattr(e, "orig") and hasattr(e.orig, "diag"):
            diag = e.orig.diag
            error_details["constraint_name"] = getattr(diag, "constraint_name", None)
            error_details["column_name"] = getattr(diag, "column_name", None)
            error_details["table_name"] = getattr(diag, "table_name", None)

        logger.error(
            "workflow_creation_integrity_error",
            extra=error_details,
        )
        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message="Failed to create workflow due to database constraint violation",
            request=request,
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "workflow_creation_error",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "organization_id": str(current_user.organization_id),
                "user_id": str(current_user.id),
            },
        )
        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="WORKFLOW_CREATION_FAILED",
            message=f"Failed to create workflow: {str(e)}",
            request=request,
        )


@router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List workflows",
    description="""
List all workflows for the current user's organization with pagination.

**Authorization**: Requires authentication (all roles).

**Multi-Tenancy**: Only shows workflows from user's organization.

**Pagination**: Supports page and per_page parameters (default 20 per page, max 100).
- Requesting a page beyond total_pages returns 200 with empty workflows array
- Check pagination.has_next_page and pagination.has_prev_page for navigation
- Use pagination.total_pages to determine valid page range

**Sorting**: Supports sort_by (created_at, name) and order (asc, desc) parameters.

**Filtering**: Returns only active workflows by default. Use `include_archived=true` to show archived workflows.
    """,
)
def list_workflows(
    current_user: AuthenticatedUser,
    request: Request,
    db: Session = Depends(get_db),
    is_active: bool = True,
    include_archived: bool = Query(False, description="Include archived workflows"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    sort_by: str = Query("created_at", pattern="^(created_at|name)$", description="Sort field"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
) -> WorkflowListResponse:
    """
    List workflows for current user's organization with pagination.

    Args:
        current_user: Authenticated user
        db: Database session
        is_active: Filter by active status (default: True)
        include_archived: Include archived workflows (default: False)
        page: Page number (1-indexed)
        per_page: Items per page (max 100)
        sort_by: Sort field (created_at or name)
        order: Sort order (asc or desc)

    Returns:
        WorkflowListResponse: Paginated list of workflows with metadata
    """
    # Build filters for total count query
    filters = [
        Workflow.organization_id == current_user.organization_id,
        Workflow.is_active == is_active,
    ]

    # Exclude archived workflows by default (soft delete pattern)
    if not include_archived:
        filters.append(Workflow.archived.is_not(True))

    # Count total workflows for pagination metadata
    # Note: scalar() returns None if no rows match, so we default to 0
    total_count = (db.query(func.count(Workflow.id)).filter(*filters).scalar()) or 0

    # Calculate pagination values
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
    offset = (page - 1) * per_page

    # Use subqueries for efficient counting without loading all relationships
    buckets_count_subquery = (
        db.query(func.count(Bucket.id)).filter(Bucket.workflow_id == Workflow.id).scalar_subquery()
    )

    criteria_count_subquery = (
        db.query(func.count(Criteria.id))
        .filter(Criteria.workflow_id == Workflow.id)
        .scalar_subquery()
    )

    # Build query with sorting - apply same filters as count query
    query = db.query(
        Workflow,
        buckets_count_subquery.label("buckets_count"),
        criteria_count_subquery.label("criteria_count"),
    ).filter(*filters)

    # Apply sorting using explicit field mapping (defense-in-depth)
    # FastAPI regex validation already enforces sort_by in ALLOWED_SORT_FIELDS,
    # but we add defensive handling in case of future middleware changes
    sort_column = ALLOWED_SORT_FIELDS.get(sort_by)
    if not sort_column:
        raise create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="INVALID_SORT_FIELD",
            message=f"Invalid sort field: {sort_by}. Allowed fields: {', '.join(ALLOWED_SORT_FIELDS.keys())}",
            request=request,
        )

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    workflows = query.offset(offset).limit(per_page).all()

    # Build response
    workflow_items = [
        WorkflowListItem(
            id=wf.Workflow.id,
            name=wf.Workflow.name,
            description=wf.Workflow.description,
            is_active=wf.Workflow.is_active,
            archived=wf.Workflow.archived,
            archived_at=wf.Workflow.archived_at,
            created_at=wf.Workflow.created_at,
            buckets_count=wf.buckets_count,
            criteria_count=wf.criteria_count,
        )
        for wf in workflows
    ]

    return WorkflowListResponse(
        workflows=workflow_items,
        pagination=PaginationMeta(
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            # Edge case: When total_count=0, total_pages=0, page=1 → both flags are False
            has_next_page=page < total_pages,
            has_prev_page=page > 1,
        ),
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow details",
    description="""
Get detailed workflow information including all buckets and criteria.

**Authorization**: Requires authentication (all roles).

**Multi-Tenancy**: Returns 404 if workflow not in user's organization.

**Archived Workflows**: Archived workflows are still accessible via this endpoint
for audit trail purposes (SOC2/ISO 27001 compliance). Use the `archived` field
in the response to check if a workflow has been archived.
    """,
)
def get_workflow(
    workflow_id: UUID,
    current_user: AuthenticatedUser,
    request: Request,
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """
    Get workflow details by ID.

    Multi-tenancy is enforced at the database query level (not after fetching).
    This prevents loading data from other organizations and is consistent with
    the pattern used in list_workflows.

    Args:
        workflow_id: Workflow UUID
        current_user: Authenticated user
        request: FastAPI request (for future audit logging enhancements)
        db: Database session

    Returns:
        WorkflowResponse: Workflow with buckets and criteria

    Raises:
        HTTPException 404: Workflow not found or not in user's organization
    """
    # Query workflow with eager loading + organization filter
    # Multi-tenancy: Filter at query level (secure, efficient, consistent)
    workflow = (
        db.query(Workflow)
        .options(
            selectinload(Workflow.buckets),
            selectinload(Workflow.criteria),
        )
        .filter(
            Workflow.id == workflow_id,
            Workflow.organization_id == current_user.organization_id,  # Multi-tenancy filter
        )
        .first()
    )

    # Return 404 for both "not found" and "wrong organization" cases
    # This prevents information leakage (attacker can't enumerate valid IDs)
    if not workflow:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="WORKFLOW_NOT_FOUND",
            message="Workflow not found",
            details={"workflow_id": str(workflow_id)},
            request=request,
        )

    # Use Pydantic's ORM mode to automatically map SQLAlchemy model to response schema
    # This ensures type safety and validates all fields according to the schema
    return WorkflowResponse.model_validate(workflow)


@router.put(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Update workflow",
    description="""
Update workflow with nested buckets and criteria in a single transaction.

**Authorization**: Requires `process_manager` or `admin` role.

**Multi-Tenancy**: Returns 404 if workflow not in user's organization.

**Differential Updates**: Supports add/update/delete operations:
- Bucket/Criteria with id=None: Create new
- Bucket/Criteria with id=UUID: Update existing
- Bucket/Criteria omitted from request: Delete

**Journey Step 1**: Process Manager refines validation workflow based on feedback.

**Example Request**:
```json
{
  "name": "Medical Device - Class II (Updated)",
  "description": "Updated validation workflow",
  "buckets": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Technical Documentation (Renamed)",
      "required": true,
      "order_index": 0
    },
    {
      "name": "Test Reports",
      "required": false,
      "order_index": 1
    }
  ],
  "criteria": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "name": "All documents must be signed",
      "description": "Updated description",
      "applies_to_bucket_ids": ["123e4567-e89b-12d3-a456-426614174000"]
    }
  ]
}
```
    """,
)
def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    current_user: ProcessManagerOrAdmin,
    request: Request,
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """
    Update workflow with nested buckets and criteria.

    This endpoint supports differential updates:
    1. Update workflow metadata (name, description)
    2. Add new buckets (id=None)
    3. Update existing buckets (id=UUID)
    4. Delete removed buckets (not in request)
    5. Add new criteria (id=None)
    6. Update existing criteria (id=UUID)
    7. Delete removed criteria (not in request)

    All operations occur in a single database transaction (atomic).

    Args:
        workflow_id: Workflow UUID to update
        workflow_data: Updated workflow data with nested buckets and criteria
        current_user: Authenticated user (requires process_manager or admin role)
        request: FastAPI request (for audit logging)
        db: Database session

    Returns:
        WorkflowResponse: Updated workflow with all nested data

    Raises:
        HTTPException 400: Validation error (invalid data)
        HTTPException 403: Insufficient permissions (not process_manager/admin)
        HTTPException 404: Workflow not found or not in user's organization
        HTTPException 500: Database error
    """
    try:
        # 1. Get existing workflow with multi-tenancy check
        workflow = (
            db.query(Workflow)
            .options(
                selectinload(Workflow.buckets),
                selectinload(Workflow.criteria),
            )
            .filter(
                Workflow.id == workflow_id,
                Workflow.organization_id == current_user.organization_id,
            )
            .first()
        )

        if not workflow:
            raise create_error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="RESOURCE_NOT_FOUND",
                message="Workflow not found",
                request=request,
            )

        # Track changes for audit logging
        buckets_added = 0
        buckets_updated = 0
        buckets_deleted = 0
        criteria_added = 0
        criteria_updated = 0
        criteria_deleted = 0

        # 2. Update workflow metadata
        workflow.name = workflow_data.name
        workflow.description = workflow_data.description
        workflow.updated_at = datetime.now(timezone.utc)

        # 3. Update buckets (delete, update, create)
        existing_bucket_ids = {bucket.id for bucket in workflow.buckets}
        incoming_bucket_ids = {
            bucket.id for bucket in workflow_data.buckets if bucket.id is not None
        }

        # Delete removed buckets
        buckets_to_delete = existing_bucket_ids - incoming_bucket_ids
        if buckets_to_delete:
            db.query(Bucket).filter(Bucket.id.in_(buckets_to_delete)).delete(
                synchronize_session=False
            )
            buckets_deleted = len(buckets_to_delete)

            # Clean up criteria that reference deleted buckets
            # This prevents orphaned bucket IDs in criteria.applies_to_bucket_ids
            for criteria in workflow.criteria:
                if criteria.applies_to_bucket_ids:
                    # Remove deleted bucket IDs from criteria
                    updated_ids = [
                        bid
                        for bid in criteria.applies_to_bucket_ids
                        if bid not in buckets_to_delete
                    ]
                    # Convert empty list to None (applies to all buckets)
                    criteria.applies_to_bucket_ids = updated_ids if updated_ids else None

        # Create a mapping of existing buckets for quick lookup
        # Filter out deleted buckets to prevent race condition
        existing_buckets_map = {
            bucket.id: bucket for bucket in workflow.buckets if bucket.id not in buckets_to_delete
        }

        # Update/create buckets
        for bucket_data in workflow_data.buckets:
            if bucket_data.id and bucket_data.id in existing_buckets_map:
                # Update existing bucket
                bucket = existing_buckets_map[bucket_data.id]
                bucket.name = bucket_data.name
                bucket.required = bucket_data.required
                bucket.order_index = bucket_data.order_index
                buckets_updated += 1
            else:
                # Create new bucket
                bucket = Bucket(
                    workflow_id=workflow.id,
                    name=bucket_data.name,
                    required=bucket_data.required,
                    order_index=bucket_data.order_index,
                )
                db.add(bucket)
                buckets_added += 1

        db.flush()  # Get new bucket IDs

        # 4. Update criteria (delete, update, create)
        existing_criteria_ids = {criteria.id for criteria in workflow.criteria}
        incoming_criteria_ids = {
            criteria.id for criteria in workflow_data.criteria if criteria.id is not None
        }

        # Delete removed criteria
        criteria_to_delete = existing_criteria_ids - incoming_criteria_ids
        if criteria_to_delete:
            db.query(Criteria).filter(Criteria.id.in_(criteria_to_delete)).delete(
                synchronize_session=False
            )
            criteria_deleted = len(criteria_to_delete)

        # Create a mapping of existing criteria for quick lookup
        existing_criteria_map = {criteria.id: criteria for criteria in workflow.criteria}

        # Update/create criteria
        for criteria_data in workflow_data.criteria:
            # Convert empty list to None for applies_to_all semantics
            applies_to_bucket_ids = (
                criteria_data.applies_to_bucket_ids if criteria_data.applies_to_bucket_ids else None
            )

            if criteria_data.id and criteria_data.id in existing_criteria_map:
                # Update existing criteria
                criteria = existing_criteria_map[criteria_data.id]
                criteria.name = criteria_data.name
                criteria.description = criteria_data.description
                criteria.applies_to_bucket_ids = applies_to_bucket_ids
                criteria.order_index = criteria_data.order_index
                criteria_updated += 1
            else:
                # Create new criteria
                criteria = Criteria(
                    workflow_id=workflow.id,
                    name=criteria_data.name,
                    description=criteria_data.description,
                    applies_to_bucket_ids=applies_to_bucket_ids,
                    order_index=criteria_data.order_index,
                )
                db.add(criteria)
                criteria_added += 1

        db.flush()

        # 5. Log workflow update (audit trail) - BEFORE commit for atomicity
        AuditService.log_workflow_updated(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            buckets_added=buckets_added,
            buckets_updated=buckets_updated,
            buckets_deleted=buckets_deleted,
            criteria_added=criteria_added,
            criteria_updated=criteria_updated,
            criteria_deleted=criteria_deleted,
            request=request,
        )

        # 6. Commit transaction (includes audit log)
        db.commit()

        # 7. Refresh to get all relationships
        db.refresh(workflow)

        # 8. Log success with structured logging
        logger.info(
            "workflow_updated",
            extra={
                "workflow_id": str(workflow.id),
                "organization_id": str(current_user.organization_id),
                "updated_by": str(current_user.id),
                "request_id": getattr(request.state, "request_id", None),
                "buckets_added": buckets_added,
                "buckets_updated": buckets_updated,
                "buckets_deleted": buckets_deleted,
                "criteria_added": criteria_added,
                "criteria_updated": criteria_updated,
                "criteria_deleted": criteria_deleted,
            },
        )

        # 9. Return updated workflow response
        return WorkflowResponse.model_validate(workflow)

    except HTTPException:
        # Re-raise HTTP exceptions (404, etc.)
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "workflow_update_integrity_error",
            extra={
                "error": str(e),
                "workflow_id": str(workflow_id),
                "organization_id": str(current_user.organization_id),
                "user_id": str(current_user.id),
                "request_id": getattr(request.state, "request_id", None),
            },
        )
        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message="Invalid bucket references in criteria or database constraint violation",
            request=request,
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "workflow_update_error",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "workflow_id": str(workflow_id),
                "organization_id": str(current_user.organization_id),
                "user_id": str(current_user.id),
                "request_id": getattr(request.state, "request_id", None),
            },
        )
        raise create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="WORKFLOW_UPDATE_FAILED",
            message=f"Failed to update workflow: {str(e)}",
            request=request,
        )


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive workflow (soft delete)",
    description="""
Archive a workflow (soft delete pattern).

**Authorization**: Requires `process_manager` or `admin` role.

**Soft Delete**: Marks workflow as archived instead of physically deleting it.
This preserves data integrity and maintains audit trail for SOC2/ISO 27001 compliance.

**Data Integrity Protection**: Cannot archive workflow if it has assessments (409 Conflict).

**Multi-Tenancy**: Returns 404 if workflow not in user's organization.

**Archived Workflow Behavior**:
- Hidden from list endpoint by default (use include_archived=true to show)
- Still accessible via direct GET (for audit trail)
- Cannot be used for new assessments
    """,
)
def archive_workflow(
    workflow_id: UUID,
    current_user: ProcessManagerOrAdmin,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    """
    Archive a workflow (soft delete).

    Args:
        workflow_id: Workflow UUID to archive
        current_user: Authenticated user (requires process_manager or admin role)
        request: FastAPI request (for audit logging)
        db: Database session

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException 400: Workflow is already archived
        HTTPException 403: Insufficient permissions (not process_manager/admin)
        HTTPException 404: Workflow not found or not in user's organization
        HTTPException 409: Workflow has assessments (cannot archive)
    """
    # Multi-tenancy: Get workflow only if it belongs to user's organization
    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == workflow_id,
            Workflow.organization_id == current_user.organization_id,
        )
        .first()
    )

    if not workflow:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Workflow not found",
            details={"workflow_id": str(workflow_id)},
            request=request,
        )

    # Data integrity check: Prevent archiving if workflow has assessments
    # Check external dependencies first (before checking internal state)
    assessment_count = (
        db.query(func.count(Assessment.id)).filter(Assessment.workflow_id == workflow_id).scalar()
    ) or 0

    if assessment_count > 0:
        raise create_error_response(
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_HAS_DEPENDENCIES",
            message=f"Cannot archive workflow with {assessment_count} existing assessments",
            details={"assessment_count": assessment_count},
            request=request,
        )

    # Check if workflow is already archived
    if workflow.archived:
        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ALREADY_ARCHIVED",
            message="Workflow is already archived",
            details={
                "archived_at": workflow.archived_at.isoformat() if workflow.archived_at else None
            },
            request=request,
        )

    # Soft delete: Mark as archived
    workflow.archived = True
    workflow.archived_at = datetime.now(timezone.utc)
    db.commit()

    # Log workflow archive (important operation for audit trail)
    AuditService.log_event(
        db=db,
        action="workflow.archived",
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        resource_type="workflow",
        resource_id=workflow_id,
        metadata={
            "workflow_name": workflow.name,
            "archived_by_email": current_user.email,
            "archived_at": workflow.archived_at.isoformat(),
        },
        request=request,
    )

    logger.info(
        "workflow_archived",
        extra={
            "workflow_id": str(workflow_id),
            "organization_id": str(current_user.organization_id),
            "archived_by": str(current_user.id),
            "request_id": getattr(request.state, "request_id", None),
        },
    )
