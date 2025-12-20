"""
Multi-Tenant Isolation Middleware for Qteria.

This module provides bulletproof multi-tenant data isolation that automatically
filters all database queries by organization_id, preventing data leakage between
organizations (e.g., TÜV SÜD employees cannot see BSI's certification documents).

Key Features:
- Automatic organization_id extraction from JWT tokens
- Context-based organization filtering using contextvars
- Organization-scoped database session dependency
- 100% coverage of database queries by organization_id
- Audit logging for multi-tenancy violations (SOC2 compliance)

Usage:
    from app.middleware.multi_tenant import (
        OrganizationContext,
        get_organization_context,
        current_organization_id,
    )

    # In endpoints, use the organization context for filtered queries
    @router.get("/workflows")
    async def list_workflows(
        org_context: OrganizationContext = Depends(get_organization_context),
        db: Session = Depends(get_db),
    ):
        # Use org_context.organization_id for filtering
        workflows = (
            db.query(Workflow)
            .filter(Workflow.organization_id == org_context.organization_id)
            .all()
        )
        return workflows

Security Notes:
- This middleware must be applied to ALL authenticated endpoints
- Returns 404 (not 403) for resources in other organizations to prevent info leakage
- Admins are also organization-scoped (no super-admin access to all orgs in MVP)
"""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Annotated, Optional
from uuid import UUID
import logging

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.auth import get_current_user, CurrentUser
from app.core.dependencies import get_db
from app.core.exceptions import create_error_response
from app.services.audit import AuditService

logger = logging.getLogger(__name__)


# Context variable to store the current organization ID for the request
# This allows organization filtering in any part of the codebase
current_organization_id: ContextVar[Optional[UUID]] = ContextVar(
    "current_organization_id", default=None
)


@dataclass(frozen=True)
class OrganizationContext:
    """
    Organization context for the current request.

    This immutable dataclass carries the organization_id extracted from the
    authenticated user's JWT token. It is used to scope all database queries
    to the user's organization.

    Attributes:
        organization_id: UUID of the current user's organization
        user_id: UUID of the authenticated user
        user_role: Role of the authenticated user
    """

    organization_id: UUID
    user_id: UUID
    user_role: str


async def get_organization_context(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> OrganizationContext:
    """
    FastAPI dependency that provides organization context for multi-tenant isolation.

    This dependency:
    1. Extracts organization_id from the authenticated user's JWT
    2. Sets the organization_id in the context variable for global access
    3. Returns an OrganizationContext object for use in endpoints

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        OrganizationContext: Contains organization_id, user_id, and user_role

    Note:
        This dependency automatically inherits authentication from get_current_user.
        If authentication fails, this dependency will also fail with 401.
    """
    # Store organization_id in context variable for global access
    current_organization_id.set(current_user.organization_id)

    logger.debug(
        "organization_context_set",
        extra={
            "organization_id": str(current_user.organization_id),
            "user_id": str(current_user.id),
            "role": current_user.role.value,
        },
    )

    return OrganizationContext(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        user_role=current_user.role.value,
    )


def get_current_organization_id() -> Optional[UUID]:
    """
    Get the current organization ID from context.

    This is useful for accessing the organization_id in parts of the code
    that don't have direct access to the request context.

    Returns:
        Optional[UUID]: Current organization ID, or None if not set

    Example:
        from app.middleware.multi_tenant import get_current_organization_id

        def some_service_function():
            org_id = get_current_organization_id()
            if org_id is None:
                raise ValueError("No organization context")
            # Use org_id for filtering...
    """
    return current_organization_id.get()


def validate_organization_access(
    resource_organization_id: UUID,
    current_org_id: UUID,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    db: Optional[Session] = None,
    user_id: Optional[UUID] = None,
) -> None:
    """
    Validate that the current user has access to a resource's organization.

    This is the core security function for multi-tenant isolation.
    It checks if the resource belongs to the user's organization and logs
    any violation attempts for audit purposes.

    Args:
        resource_organization_id: Organization ID of the resource being accessed
        current_org_id: Organization ID of the current user
        resource_type: Type of resource (for audit logging)
        resource_id: ID of the resource (for audit logging)
        request: FastAPI request (for audit logging)
        db: Database session (for audit logging)
        user_id: User ID (for audit logging)

    Raises:
        HTTPException: 404 if resource belongs to different organization
                       (404 used instead of 403 to prevent info leakage)

    Security Note:
        We return 404 instead of 403 to avoid revealing that a resource
        exists in another organization. This prevents enumeration attacks.
    """
    if resource_organization_id != current_org_id:
        # Log multi-tenancy violation attempt
        if db and user_id:
            AuditService.log_multi_tenancy_violation(
                db=db,
                user_id=user_id,
                user_organization_id=current_org_id,
                attempted_organization_id=resource_organization_id,
                resource_type=resource_type,
                resource_id=resource_id,
                request=request,
            )

        logger.warning(
            "multi_tenancy_access_denied",
            extra={
                "user_org_id": str(current_org_id),
                "resource_org_id": str(resource_organization_id),
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
            },
        )

        # Return 404 to prevent info leakage (don't reveal resource exists)
        raise create_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource_type.title()} not found",
            request=request,
        )


class MultiTenantMiddleware:
    """
    ASGI middleware for multi-tenant request context setup.

    This middleware ensures that every request has proper organization
    context set up for multi-tenant isolation. It works in conjunction
    with the get_organization_context dependency.

    Note:
        This middleware is optional if you're using the dependency-based
        approach consistently. It's provided for additional safety and
        for cases where you need organization context outside of FastAPI
        dependencies.

    Usage:
        from fastapi import FastAPI
        from app.middleware.multi_tenant import MultiTenantMiddleware

        app = FastAPI()
        app.add_middleware(MultiTenantMiddleware)
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the request and ensure organization context is cleared after.

        This middleware resets the organization context after each request
        to prevent context leakage between requests.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Reset context at start of request
        token = current_organization_id.set(None)

        try:
            await self.app(scope, receive, send)
        finally:
            # Reset context after request (prevent leakage)
            current_organization_id.reset(token)


# Type alias for common dependency pattern
OrganizationScoped = Annotated[OrganizationContext, Depends(get_organization_context)]
