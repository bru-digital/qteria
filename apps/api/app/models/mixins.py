"""
SQLAlchemy model mixins for organization-scoped queries.

This module provides mixins that implement automatic organization filtering
for multi-tenant data isolation. All models with organization_id should
use these mixins to ensure data is properly isolated between organizations.

Key Features:
- Automatic organization filtering on all queries
- Type-safe query methods
- Consistent error handling (404 for missing or other-org resources)
- Support for both single record and list queries

Usage:
    from app.models.mixins import OrganizationScopedMixin

    class Workflow(Base, OrganizationScopedMixin):
        __tablename__ = "workflows"
        id = Column(UUID(as_uuid=True), primary_key=True)
        organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
        name = Column(String(255))

    # In endpoints:
    workflow = Workflow.get_by_id_scoped(db, org_id=org_context.organization_id, id=workflow_id)
    workflows = Workflow.get_all_scoped(db, org_id=org_context.organization_id)

Security Note:
    All queries through these mixins are automatically filtered by organization_id.
    Never bypass these methods for user-facing queries.
"""
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.services.audit import AuditService

# Generic type variable for model classes
T = TypeVar("T")


class OrganizationScopedMixin(Generic[T]):
    """
    Mixin for models that are scoped to an organization.

    This mixin provides organization-filtered query methods that ensure
    all database access is properly isolated by organization_id.

    All models with organization_id column should use this mixin.

    Example:
        class Workflow(Base, OrganizationScopedMixin):
            __tablename__ = "workflows"
            organization_id = Column(UUID(as_uuid=True), ...)

        # Get single workflow with org filtering
        workflow = Workflow.get_by_id_scoped(db, org_id, workflow_id)

        # Get all workflows for organization
        workflows = Workflow.get_all_scoped(db, org_id)
    """

    # These class attributes are expected to be defined by SQLAlchemy models
    id: UUID
    organization_id: UUID

    @classmethod
    def get_by_id_scoped(
        cls: Type[T],
        db: Session,
        org_id: UUID,
        record_id: UUID,
    ) -> Optional[T]:
        """
        Get a single record by ID, filtered by organization.

        This is the primary method for fetching individual records with
        organization filtering. It ensures users can only access records
        belonging to their organization.

        Args:
            db: SQLAlchemy database session
            org_id: Organization ID to filter by (from user's JWT)
            record_id: Primary key ID of the record

        Returns:
            Optional[T]: The record if found and belongs to org, None otherwise

        Security Note:
            Returns None for both non-existent records AND records belonging
            to other organizations (prevents info leakage).

        Example:
            workflow = Workflow.get_by_id_scoped(
                db=db,
                org_id=current_user.organization_id,
                record_id=workflow_id
            )
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
        """
        return (
            db.query(cls)
            .filter(
                and_(
                    cls.organization_id == org_id,
                    cls.id == record_id,
                )
            )
            .first()
        )

    @classmethod
    def get_all_scoped(
        cls: Type[T],
        db: Session,
        org_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[T]:
        """
        Get all records for an organization with pagination.

        This method returns all records belonging to the specified organization,
        with support for pagination via skip and limit parameters.

        Args:
            db: SQLAlchemy database session
            org_id: Organization ID to filter by
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List[T]: List of records belonging to the organization

        Example:
            workflows = Workflow.get_all_scoped(
                db=db,
                org_id=current_user.organization_id,
                skip=0,
                limit=50
            )
        """
        return (
            db.query(cls)
            .filter(cls.organization_id == org_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def count_scoped(
        cls: Type[T],
        db: Session,
        org_id: UUID,
    ) -> int:
        """
        Count all records for an organization.

        Args:
            db: SQLAlchemy database session
            org_id: Organization ID to filter by

        Returns:
            int: Number of records belonging to the organization
        """
        return db.query(cls).filter(cls.organization_id == org_id).count()

    @classmethod
    def exists_scoped(
        cls: Type[T],
        db: Session,
        org_id: UUID,
        record_id: UUID,
    ) -> bool:
        """
        Check if a record exists within an organization.

        More efficient than get_by_id_scoped when you only need to check existence.

        Args:
            db: SQLAlchemy database session
            org_id: Organization ID to filter by
            record_id: Primary key ID to check

        Returns:
            bool: True if record exists and belongs to organization
        """
        return (
            db.query(cls)
            .filter(
                and_(
                    cls.organization_id == org_id,
                    cls.id == record_id,
                )
            )
            .count()
            > 0
        )

    @classmethod
    def get_by_id_scoped_or_404(
        cls: Type[T],
        db: Session,
        org_id: UUID,
        record_id: UUID,
        resource_name: Optional[str] = None,
    ) -> T:
        """
        Get a single record by ID, or raise 404 if not found.

        This is a convenience method that combines get_by_id_scoped with
        automatic 404 handling, reducing boilerplate in endpoints.

        Args:
            db: SQLAlchemy database session
            org_id: Organization ID to filter by
            record_id: Primary key ID of the record
            resource_name: Human-readable name for error message (default: class name)

        Returns:
            T: The record if found

        Raises:
            HTTPException: 404 if record not found or belongs to other org

        Example:
            workflow = Workflow.get_by_id_scoped_or_404(
                db=db,
                org_id=current_user.organization_id,
                record_id=workflow_id,
                resource_name="Workflow"
            )
            # workflow is guaranteed to exist and belong to user's org
        """
        resource = resource_name or cls.__name__

        record = cls.get_by_id_scoped(db, org_id, record_id)

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"{resource} not found",
                },
            )

        return record

    @classmethod
    def delete_scoped(
        cls: Type[T],
        db: Session,
        org_id: UUID,
        record_id: UUID,
    ) -> bool:
        """
        Delete a record by ID within an organization.

        This method safely deletes a record only if it belongs to the
        specified organization.

        Args:
            db: SQLAlchemy database session
            org_id: Organization ID to filter by
            record_id: Primary key ID of the record to delete

        Returns:
            bool: True if record was deleted, False if not found

        Note:
            Returns False for both non-existent records AND records
            belonging to other organizations (security by design).
        """
        deleted = (
            db.query(cls)
            .filter(
                and_(
                    cls.organization_id == org_id,
                    cls.id == record_id,
                )
            )
            .delete()
        )
        db.commit()
        return deleted > 0


def get_scoped_or_404(
    db: Session,
    model_class: Type[T],
    org_id: UUID,
    record_id: UUID,
    resource_name: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
) -> T:
    """
    Get a record by ID with organization scoping, or raise 404.

    This is a standalone function for models that don't use the mixin.
    It provides the same security guarantees as the mixin methods.

    Args:
        db: SQLAlchemy database session
        model_class: SQLAlchemy model class to query
        org_id: Organization ID to filter by
        record_id: Primary key ID of the record
        resource_name: Human-readable name for error message
        user_id: User ID for audit logging (optional)
        request: FastAPI request for audit logging (optional)

    Returns:
        T: The record if found

    Raises:
        HTTPException: 404 if record not found or belongs to other org

    Example:
        from app.models.mixins import get_scoped_or_404

        workflow = get_scoped_or_404(
            db=db,
            model_class=Workflow,
            org_id=current_user.organization_id,
            record_id=workflow_id,
            resource_name="Workflow",
            user_id=current_user.id,
            request=request,
        )
    """
    record = (
        db.query(model_class)
        .filter(
            and_(
                model_class.organization_id == org_id,
                model_class.id == record_id,
            )
        )
        .first()
    )

    if record is None:
        # Check if record exists in different org (for audit logging)
        exists_elsewhere = (
            db.query(model_class)
            .filter(model_class.id == record_id)
            .first()
        )

        if exists_elsewhere and user_id:
            # Log multi-tenancy violation attempt
            AuditService.log_multi_tenancy_violation(
                db=db,
                user_id=user_id,
                user_organization_id=org_id,
                attempted_organization_id=exists_elsewhere.organization_id,
                resource_type=resource_name.lower(),
                resource_id=record_id,
                request=request,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": f"{resource_name} not found",
            },
        )

    return record


def filter_by_organization(
    db: Session,
    model_class: Type[T],
    org_id: UUID,
) -> List[T]:
    """
    Filter all records by organization ID.

    Simple utility function for basic organization filtering.

    Args:
        db: SQLAlchemy database session
        model_class: SQLAlchemy model class to query
        org_id: Organization ID to filter by

    Returns:
        List[T]: All records belonging to the organization

    Example:
        workflows = filter_by_organization(db, Workflow, org_id)
    """
    return db.query(model_class).filter(model_class.organization_id == org_id).all()
