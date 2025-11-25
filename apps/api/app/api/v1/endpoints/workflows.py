"""
Workflow CRUD endpoints.

All workflow management endpoints enforce RBAC:
- CREATE/UPDATE/DELETE: process_manager or admin roles only
- READ: all authenticated users

Multi-tenancy is enforced: users can only access workflows from their own organization.
Audit logging enabled for SOC2/ISO 27001 compliance.

Security Notes:
- Returns 404 (not 403) when accessing other org's data to prevent info leakage
- Soft delete pattern (archive) preserves data integrity and audit trail
- DELETE prevents deletion if workflow has assessments (409 Conflict)
"""
from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db
from app.core.auth import (
    get_current_user,
    require_role,
    CurrentUser,
    ProcessManagerOrAdmin,
    AuthenticatedUser,
)
from app.models.models import Workflow, Assessment
from app.models.enums import UserRole
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
)
from app.services.audit import AuditService

router = APIRouter()


@router.get(
    "/workflows",
    response_model=List[WorkflowResponse],
    tags=["Workflows"],
    summary="List workflows for organization",
)
def list_workflows(
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
    include_archived: bool = Query(
        False, description="Include archived workflows in response"
    ),
):
    """
    List all workflows for the current user's organization.

    **Required Role**: Any authenticated user

    By default, archived workflows are excluded from the list. Use
    `include_archived=true` to show archived workflows (useful for admins).

    Multi-tenancy enforced: Only returns workflows from user's organization.

    Args:
        include_archived: Whether to include archived workflows (default: False)
        current_user: Authenticated user
        db: Database session

    Returns:
        List[WorkflowResponse]: List of workflows
    """
    query = db.query(Workflow).filter(
        Workflow.organization_id == current_user.organization_id
    )

    # Exclude archived workflows by default
    if not include_archived:
        query = query.filter(Workflow.archived == False)

    workflows = query.order_by(Workflow.created_at.desc()).all()
    return workflows


@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    tags=["Workflows"],
    summary="Get workflow by ID",
)
def get_workflow(
    workflow_id: UUID,
    current_user: AuthenticatedUser,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get a single workflow by ID.

    **Required Role**: Any authenticated user

    Multi-tenancy enforced: Returns 404 for workflows from other organizations.
    Archived workflows are still accessible (for audit trail purposes).

    Args:
        workflow_id: Workflow UUID
        current_user: Authenticated user
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        WorkflowResponse: Workflow details

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 404 if workflow not found or belongs to other org
    """
    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.id == workflow_id,
            Workflow.organization_id == current_user.organization_id,
        )
        .first()
    )

    if not workflow:
        # Log multi-tenancy violation attempt
        AuditService.log_multi_tenancy_violation(
            db=db,
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_organization_id=None,  # Unknown since workflow not found
            resource_type="workflow",
            resource_id=workflow_id,
            request=request,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": "Workflow not found",
            },
        )

    return workflow


@router.delete(
    "/workflows/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Workflows"],
    summary="Archive workflow (soft delete)",
)
def delete_workflow(
    workflow_id: UUID,
    current_user: ProcessManagerOrAdmin,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Archive a workflow (soft delete).

    **Required Role**: process_manager or admin

    **Soft Delete Pattern**: Marks workflow as `archived=True` instead of physically
    deleting it. This preserves data integrity and maintains audit trail for
    SOC2/ISO 27001 compliance.

    **Data Integrity Protection**: Prevents deletion if workflow has assessments.
    Returns 409 Conflict with assessment count if deletion is blocked.

    **Multi-tenancy**: Only workflows from user's organization can be deleted.
    Returns 404 for other orgs to prevent info leakage.

    **Archived Workflow Behavior**:
    - Hidden from list endpoint by default (use `include_archived=true` to show)
    - Still accessible via direct GET (for audit trail)
    - Cannot be used for new assessments (business logic to be implemented)

    Args:
        workflow_id: Workflow UUID
        current_user: Authenticated process_manager or admin
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if not process_manager or admin
        HTTPException: 404 if workflow not found or belongs to other org
        HTTPException: 409 if workflow has assessments (cannot delete)
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
        # Log multi-tenancy violation attempt
        AuditService.log_multi_tenancy_violation(
            db=db,
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_organization_id=None,  # Unknown since workflow not found
            resource_type="workflow",
            resource_id=workflow_id,
            request=request,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": "Workflow not found",
            },
        )

    # Data integrity check: Prevent deletion if workflow has assessments
    assessment_count = (
        db.query(func.count(Assessment.id))
        .filter(Assessment.workflow_id == workflow_id)
        .scalar()
    )

    if assessment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "RESOURCE_HAS_DEPENDENCIES",
                "message": f"Cannot delete workflow with {assessment_count} existing assessments. Archive instead or delete assessments first.",
                "assessment_count": assessment_count,
            },
        )

    # Soft delete: Mark as archived
    workflow.archived = True
    workflow.archived_at = datetime.utcnow()
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

    return None
