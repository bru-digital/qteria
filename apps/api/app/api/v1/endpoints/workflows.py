"""
Workflow management API endpoints.

Journey Step 1: Process Managers create and manage validation workflows.

Endpoints:
- POST /v1/workflows - Create workflow with nested buckets and criteria
- GET /v1/workflows - List workflows for organization
- GET /v1/workflows/{id} - Get workflow details
- PUT /v1/workflows/{id} - Update workflow
- DELETE /v1/workflows/{id} - Archive workflow (soft delete)
"""
from typing import List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.core.auth import ProcessManagerOrAdmin, AuthenticatedUser, CurrentUser
from app.core.dependencies import get_db
from app.models import Workflow, Bucket, Criteria
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowListItem,
)
from app.services.audit import AuditService, AuditEventType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


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
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: ProcessManagerOrAdmin,
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
                [bucket_index_to_id[bucket_idx] for bucket_idx in criteria_data.applies_to_bucket_ids]
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
        return WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            organization_id=workflow.organization_id,
            created_by=workflow.created_by,
            is_active=workflow.is_active,
            created_at=workflow.created_at,
            buckets=[
                {
                    "id": bucket.id,
                    "name": bucket.name,
                    "required": bucket.required,
                    "order_index": bucket.order_index,
                }
                for bucket in workflow.buckets
            ],
            criteria=[
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "applies_to_bucket_ids": c.applies_to_bucket_ids or [],
                    "order_index": c.order_index,
                }
                for c in workflow.criteria
            ],
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(
            "workflow_creation_integrity_error",
            extra={
                "error": str(e),
                "organization_id": str(current_user.organization_id),
                "user_id": str(current_user.id),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to create workflow due to database constraint violation",
            },
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "WORKFLOW_CREATION_FAILED",
                "message": f"Failed to create workflow: {str(e)}",
            },
        )


@router.get(
    "",
    response_model=List[WorkflowListItem],
    summary="List workflows",
    description="""
List all workflows for the current user's organization.

**Authorization**: Requires authentication (all roles).

**Multi-Tenancy**: Only shows workflows from user's organization.

**Filtering**: Returns only active workflows by default.
    """,
)
async def list_workflows(
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
    is_active: bool = True,
) -> List[WorkflowListItem]:
    """
    List workflows for current user's organization.

    Args:
        current_user: Authenticated user
        db: Database session
        is_active: Filter by active status (default: True)

    Returns:
        List[WorkflowListItem]: List of workflows with counts
    """
    # Use subqueries for efficient counting without loading all relationships
    buckets_count_subquery = (
        db.query(func.count(Bucket.id))
        .filter(Bucket.workflow_id == Workflow.id)
        .scalar_subquery()
    )

    criteria_count_subquery = (
        db.query(func.count(Criteria.id))
        .filter(Criteria.workflow_id == Workflow.id)
        .scalar_subquery()
    )

    workflows = (
        db.query(
            Workflow,
            buckets_count_subquery.label('buckets_count'),
            criteria_count_subquery.label('criteria_count'),
        )
        .filter(
            Workflow.organization_id == current_user.organization_id,
            Workflow.is_active == is_active,
        )
        .order_by(Workflow.created_at.desc())
        .all()
    )

    return [
        WorkflowListItem(
            id=wf.Workflow.id,
            name=wf.Workflow.name,
            description=wf.Workflow.description,
            is_active=wf.Workflow.is_active,
            created_at=wf.Workflow.created_at,
            buckets_count=wf.buckets_count,
            criteria_count=wf.criteria_count,
        )
        for wf in workflows
    ]


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow details",
    description="""
Get detailed workflow information including all buckets and criteria.

**Authorization**: Requires authentication (all roles).

**Multi-Tenancy**: Returns 404 if workflow not in user's organization.
    """,
)
async def get_workflow(
    workflow_id: UUID,
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    """
    Get workflow details by ID.

    Args:
        workflow_id: Workflow UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        WorkflowResponse: Workflow with buckets and criteria

    Raises:
        HTTPException 404: Workflow not found or not in user's organization
    """
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found",
            },
        )

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        organization_id=workflow.organization_id,
        created_by=workflow.created_by,
        is_active=workflow.is_active,
        created_at=workflow.created_at,
        buckets=[
            {
                "id": bucket.id,
                "name": bucket.name,
                "required": bucket.required,
                "order_index": bucket.order_index,
            }
            for bucket in workflow.buckets
        ],
        criteria=[
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "applies_to_bucket_ids": c.applies_to_bucket_ids or [],
                "order_index": c.order_index,
            }
            for c in workflow.criteria
        ],
    )
