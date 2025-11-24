"""
Organization CRUD endpoints.

All organization management endpoints require admin role.
Multi-tenancy is enforced: users can only access their own organization.
Audit logging enabled for SOC2/ISO 27001 compliance.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.auth import (
    get_current_user,
    require_role,
    CurrentUser,
    AdminOnly,
    AuthenticatedUser,
)
from app.models.models import Organization
from app.models.enums import UserRole
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from app.services.audit import AuditService

router = APIRouter()


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Organizations"],
    summary="Create a new organization (Admin only)",
)
def create_organization(
    organization: OrganizationCreate,
    current_user: AdminOnly,
    db: Session = Depends(get_db),
):
    """
    Create a new organization.

    **Required Role**: Admin

    Args:
        organization: Organization creation data
        current_user: Authenticated admin user
        db: Database session

    Returns:
        OrganizationResponse: Created organization

    Raises:
        HTTPException: 400 if organization with same name already exists
        HTTPException: 401 if not authenticated
        HTTPException: 403 if not an admin
    """
    # Check if organization with same name exists
    existing = db.query(Organization).filter(Organization.name == organization.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with name '{organization.name}' already exists",
        )

    # Create new organization
    db_organization = Organization(**organization.model_dump())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

    return db_organization


@router.get(
    "/organizations",
    response_model=List[OrganizationResponse],
    tags=["Organizations"],
    summary="List organizations (Admin: all, Others: own only)",
)
def list_organizations(
    current_user: AuthenticatedUser,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List organizations with pagination.

    **Required Role**: Any authenticated user

    - **Admin**: Can see all organizations
    - **Other roles**: Can only see their own organization

    Args:
        current_user: Authenticated user
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[OrganizationResponse]: List of organizations
    """
    # Multi-tenancy: non-admins can only see their own organization
    if current_user.role == UserRole.ADMIN:
        organizations = db.query(Organization).offset(skip).limit(limit).all()
    else:
        organizations = (
            db.query(Organization)
            .filter(Organization.id == current_user.organization_id)
            .all()
        )
    return organizations


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    tags=["Organizations"],
    summary="Get organization by ID",
)
def get_organization(
    organization_id: UUID,
    current_user: AuthenticatedUser,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get a single organization by ID.

    **Required Role**: Any authenticated user

    Multi-tenancy enforced: Non-admin users can only access their own organization.

    Args:
        organization_id: Organization UUID
        current_user: Authenticated user
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        OrganizationResponse: Organization details

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if trying to access another organization (non-admin)
        HTTPException: 404 if organization not found
    """
    # Multi-tenancy: non-admins can only access their own organization
    if current_user.role != UserRole.ADMIN and organization_id != current_user.organization_id:
        # Log multi-tenancy violation attempt
        AuditService.log_multi_tenancy_violation(
            db=db,
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_organization_id=organization_id,
            resource_type="organization",
            resource_id=organization_id,
            request=request,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCESS_DENIED",
                "message": "You can only access your own organization",
            },
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {organization_id} not found",
        )

    return organization


@router.patch(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    tags=["Organizations"],
    summary="Update organization (Admin only)",
)
def update_organization(
    organization_id: UUID,
    organization_update: OrganizationUpdate,
    current_user: AdminOnly,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Update an organization by ID.

    **Required Role**: Admin

    Admins can only update their own organization (multi-tenancy enforced).

    Args:
        organization_id: Organization UUID
        organization_update: Fields to update
        current_user: Authenticated admin user
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        OrganizationResponse: Updated organization

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if not an admin or accessing another org
        HTTPException: 404 if organization not found
    """
    # Multi-tenancy: admins can only update their own organization
    if organization_id != current_user.organization_id:
        # Log multi-tenancy violation attempt
        AuditService.log_multi_tenancy_violation(
            db=db,
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_organization_id=organization_id,
            resource_type="organization",
            resource_id=organization_id,
            request=request,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCESS_DENIED",
                "message": "You can only update your own organization",
            },
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {organization_id} not found",
        )

    # Update only provided fields
    update_data = organization_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    db.commit()
    db.refresh(organization)

    # Log successful organization update (sensitive operation)
    AuditService.log_access_granted(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        endpoint=str(request.url.path),
        resource_type="organization",
        resource_id=organization_id,
        request=request,
    )

    return organization


@router.delete(
    "/organizations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Organizations"],
    summary="Delete organization (Admin only)",
)
def delete_organization(
    organization_id: UUID,
    current_user: AdminOnly,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Delete an organization by ID.

    **Required Role**: Admin

    **Warning**: This is a destructive operation. Deletes all related users,
    workflows, assessments, and documents (CASCADE).

    Admins can only delete their own organization (multi-tenancy enforced).

    Args:
        organization_id: Organization UUID
        current_user: Authenticated admin user
        request: FastAPI request for audit logging
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if not an admin or accessing another org
        HTTPException: 404 if organization not found
    """
    # Multi-tenancy: admins can only delete their own organization
    if organization_id != current_user.organization_id:
        # Log multi-tenancy violation attempt
        AuditService.log_multi_tenancy_violation(
            db=db,
            user_id=current_user.id,
            user_organization_id=current_user.organization_id,
            attempted_organization_id=organization_id,
            resource_type="organization",
            resource_id=organization_id,
            request=request,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCESS_DENIED",
                "message": "You can only delete your own organization",
            },
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {organization_id} not found",
        )

    # Log organization deletion (critical operation - log before delete)
    AuditService.log_event(
        db=db,
        action="organization.deleted",
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        resource_type="organization",
        resource_id=organization_id,
        metadata={
            "organization_name": organization.name,
            "deleted_by_email": current_user.email,
        },
        request=request,
    )

    db.delete(organization)
    db.commit()

    return None
