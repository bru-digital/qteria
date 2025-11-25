"""
Workflow API endpoints.

This module implements workflow-related endpoints:
- GET /v1/workflows/:id - Get workflow details with nested buckets and criteria

Journey Context:
- Step 1: Process Manager views workflow details before creating assessments
- Step 2: Project Handler selects workflow before document upload
- Value: Clear understanding of validation requirements before assessment

Reference: product-guidelines/00-user-journey.md (Step 1, lines 69-96)
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.auth import AuthenticatedUser
from app.core.dependencies import get_db
from app.models.models import Workflow, Bucket, Criteria
from app.schemas.workflow import WorkflowDetailResponse, BucketDetail, CriteriaDetail, WorkflowStats

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get(
    "/{workflow_id}",
    response_model=WorkflowDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get workflow details",
    description="""
    Get complete workflow details including all nested buckets and criteria.

    **Journey Step 1**: Users view complete workflow structure before assessment.

    **Multi-Tenancy**: Only returns workflow if it belongs to user's organization.
    Returns 404 (not 403) for other organization's workflows to avoid leaking existence.

    **Performance**: Uses eager loading (single database query) to avoid N+1 queries.
    Target: P95 response time <300ms.

    **Error Responses**:
    - 401: Invalid or missing JWT token
    - 404: Workflow not found or belongs to different organization
    """,
    responses={
        200: {
            "description": "Workflow details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Medical Device - Class II",
                        "description": "Validation workflow for Class II medical devices",
                        "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                        "created_by": "770e8400-e29b-41d4-a716-446655440000",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                        "is_active": True,
                        "buckets": [
                            {
                                "id": "880e8400-e29b-41d4-a716-446655440000",
                                "name": "Technical Documentation",
                                "required": True,
                                "order_index": 0
                            },
                            {
                                "id": "990e8400-e29b-41d4-a716-446655440000",
                                "name": "Test Reports",
                                "required": True,
                                "order_index": 1
                            }
                        ],
                        "criteria": [
                            {
                                "id": "aa0e8400-e29b-41d4-a716-446655440000",
                                "name": "All documents must be signed",
                                "description": "Each document should have authorized signature",
                                "applies_to_bucket_ids": [
                                    "880e8400-e29b-41d4-a716-446655440000",
                                    "990e8400-e29b-41d4-a716-446655440000"
                                ]
                            }
                        ],
                        "stats": {
                            "bucket_count": 2,
                            "criteria_count": 1
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing JWT token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "code": "INVALID_TOKEN",
                            "message": "Could not validate credentials"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Not Found - Workflow doesn't exist or belongs to different organization",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "code": "WORKFLOW_NOT_FOUND",
                            "message": "Workflow not found",
                            "workflow_id": "550e8400-e29b-41d4-a716-446655440000"
                        }
                    }
                }
            }
        }
    }
)
async def get_workflow(
    workflow_id: UUID,
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
) -> WorkflowDetailResponse:
    """
    Get workflow details with nested buckets and criteria.

    **Journey Context**: Step 1 - Users view complete workflow structure before assessment.

    **Multi-Tenancy**: Filters by organization_id from JWT to ensure data isolation.

    **Performance**: Uses SQLAlchemy selectinload() for eager loading (single query).

    Args:
        workflow_id: UUID of the workflow to retrieve
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        WorkflowDetailResponse with complete workflow details

    Raises:
        HTTPException 404: Workflow not found or belongs to different organization
    """
    # Query workflow with eager loading of buckets and criteria (single query)
    # This prevents N+1 query problem
    query = (
        db.query(Workflow)
        .options(
            selectinload(Workflow.buckets),
            selectinload(Workflow.criteria)
        )
        .filter(
            Workflow.id == workflow_id,
            Workflow.organization_id == current_user.organization_id  # Multi-tenancy
        )
    )

    workflow = query.first()

    # Return 404 for non-existent or other organization's workflows
    # Use 404 (not 403) to avoid leaking workflow existence
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": "Workflow not found",
                "workflow_id": str(workflow_id)
            }
        )

    # Map buckets to response schema
    buckets_response: List[BucketDetail] = [
        BucketDetail(
            id=bucket.id,
            name=bucket.name,
            required=bucket.required,
            order_index=bucket.order_index
        )
        for bucket in workflow.buckets
    ]

    # Map criteria to response schema
    criteria_response: List[CriteriaDetail] = [
        CriteriaDetail(
            id=criteria.id,
            name=criteria.name,
            description=criteria.description,
            applies_to_bucket_ids=criteria.applies_to_bucket_ids or []
        )
        for criteria in workflow.criteria
    ]

    # Build response with statistics
    return WorkflowDetailResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        organization_id=workflow.organization_id,
        created_by=workflow.created_by,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        is_active=workflow.is_active,
        buckets=buckets_response,
        criteria=criteria_response,
        stats=WorkflowStats(
            bucket_count=len(workflow.buckets),
            criteria_count=len(workflow.criteria)
        )
    )
