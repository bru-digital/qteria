"""
Organization CRUD endpoints.

All organization management endpoints require admin role.
Multi-tenancy is enforced: users can only access their own organization.
Audit logging enabled for SOC2/ISO 27001 compliance.

Security Notes:
- Non-admin users can only see/access their own organization
- Admin users are also organization-scoped (no super-admin in MVP)
- Returns 404 (not 403) when accessing other org's data to prevent info leakage
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
from app.core.exceptions import create_error_response
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
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Create a new organization.

    **Required Role**: Admin

    Args:
        organization: Organization creation data
        current_user: Authenticated admin user
        request: FastAPI request for audit logging
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
        raise create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=f"Organization with name '{organization.name}' already exists",
            details={"field": "name", "value": organization.name},
            request=request,
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
    summary="List organizations (own organization only)",
)
def list_organizations(
    current_user: AuthenticatedUser,
    db: Session = Depends(get_db),
):
    """
    List organizations.

    **Required Role**: Any authenticated user

    Multi-tenancy enforced: ALL users (including admins) can only see
    their own organization. This follows the principle that admins are
    organization-scoped in MVP (no super-admin access to all orgs).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List[OrganizationResponse]: List containing user's organization
    """
    # Multi-tenancy: ALL users (including admins) can only see their own organization
    # Note: Changed from previous behavior where admins could see all orgs
    # This follows the plan: "Admin from org A cannot see org B's data"
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

    Multi-tenancy enforced: All users (including admins) can only access
    their own organization. Returns 404 for other orgs to prevent info leakage.

    Args:
        organization_id: Organization UUID
        current_user: Authenticated user
        request: FastAPI request for audit logging
        db: Database session

    Returns:
        OrganizationResponse: Organization details

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 404 if organization not found or belongs to other org
    """
    # Multi-tenancy: ALL users (including admins) can only access their own organization
    # Note: Changed from previous behavior where admins could see all orgs
    # This follows the plan: "Admin users can only see their own organization's data"
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
        # Return 404 to prevent information leakage (don't reveal org exists)
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Organization not found",
            request=request,
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Organization not found",
            request=request,
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
    Returns 404 for other orgs to prevent info leakage.

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
        HTTPException: 403 if not an admin
        HTTPException: 404 if organization not found or belongs to other org
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
        # Return 404 to prevent information leakage (don't reveal org exists)
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Organization not found",
            request=request,
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Organization not found",
            request=request,
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
    Returns 404 for other orgs to prevent info leakage.

    Args:
        organization_id: Organization UUID
        current_user: Authenticated admin user
        request: FastAPI request for audit logging
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if not an admin
        HTTPException: 404 if organization not found or belongs to other org
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
        # Return 404 to prevent information leakage (don't reveal org exists)
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Organization not found",
            request=request,
        )

    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message="Organization not found",
            request=request,
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
