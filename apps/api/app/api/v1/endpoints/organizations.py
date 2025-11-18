"""
Organization CRUD endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.models import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

router = APIRouter()


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Organizations"],
)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new organization.

    Args:
        organization: Organization creation data
        db: Database session

    Returns:
        OrganizationResponse: Created organization

    Raises:
        HTTPException: If organization with same name already exists
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
)
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List all organizations with pagination.

    Args:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[OrganizationResponse]: List of organizations
    """
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    tags=["Organizations"],
)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a single organization by ID.

    Args:
        organization_id: Organization UUID
        db: Database session

    Returns:
        OrganizationResponse: Organization details

    Raises:
        HTTPException: If organization not found
    """
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
)
def update_organization(
    organization_id: UUID,
    organization_update: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an organization by ID.

    Args:
        organization_id: Organization UUID
        organization_update: Fields to update
        db: Database session

    Returns:
        OrganizationResponse: Updated organization

    Raises:
        HTTPException: If organization not found
    """
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

    return organization


@router.delete(
    "/organizations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Organizations"],
)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete an organization by ID.

    Args:
        organization_id: Organization UUID
        db: Database session

    Raises:
        HTTPException: If organization not found

    Note:
        Deletes all related users, workflows, and assessments (CASCADE).
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {organization_id} not found",
        )

    db.delete(organization)
    db.commit()

    return None
