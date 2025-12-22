"""
Authentication and authorization dependencies for FastAPI.

This module provides:
- JWT token validation
- User extraction from tokens
- Role-based access control (RBAC) dependencies
- Audit logging for auth/authz events (SOC2 compliance)

Usage:
    from app.core.auth import get_current_user, require_role
    from app.models.enums import UserRole

    @router.get("/protected")
    async def protected_endpoint(
        current_user: CurrentUser = Depends(get_current_user)
    ):
        return {"user_id": current_user.id}

    @router.post("/admin-only")
    async def admin_endpoint(
        current_user: CurrentUser = Depends(require_role(UserRole.ADMIN))
    ):
        return {"message": "Admin access granted"}
"""

from datetime import datetime, timezone
from typing import Annotated
from collections.abc import Awaitable, Callable
from uuid import UUID
import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.exceptions import create_error_response
from app.models.enums import UserRole, Permission, has_permission
from app.services.audit import AuditService

logger = logging.getLogger(__name__)


# HTTP Bearer security scheme
# NOTE: auto_error=False so we can return 401 (not 403) for missing credentials
# This follows REST API convention: 401 = missing/invalid auth, 403 = insufficient permissions
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token",
    auto_error=False,
)


class CurrentUser(BaseModel):
    """
    Current authenticated user extracted from JWT token.

    This model represents the user context available to all authenticated endpoints.
    """

    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    role: UserRole = Field(..., description="User's role for RBAC")
    organization_id: UUID = Field(..., description="User's organization ID for multi-tenancy")
    name: str | None = Field(default=None, description="User's display name")

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make immutable for security


class TokenPayload(BaseModel):
    """
    JWT token payload structure.

    Expected JWT payload format from Auth.js:
    {
        "sub": "user-uuid",
        "email": "user@example.com",
        "role": "process_manager",
        "org_id": "org-uuid",
        "name": "John Doe",
        "iat": 1234567890,
        "exp": 1234567890
    }
    """

    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    org_id: str = Field(..., description="Organization ID")
    name: str | None = Field(default=None, description="User name")
    iat: int | None = Field(default=None, description="Issued at timestamp")
    exp: int | None = Field(default=None, description="Expiration timestamp")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    request: Request,
    db: Session = Depends(get_db),
) -> CurrentUser:
    """
    Extract and validate current user from JWT token.

    This dependency:
    1. Extracts the JWT token from Authorization header
    2. Validates the token signature
    3. Checks token expiration
    4. Extracts user information
    5. Validates the user role
    6. Logs authentication events for audit trail (SOC2)

    Args:
        credentials: HTTP Bearer credentials containing JWT token (None if missing)
        request: FastAPI request for audit logging
        db: Database session for audit logging

    Returns:
        CurrentUser: Validated user information

    Raises:
        HTTPException: 401 if token is missing, invalid, expired, or malformed
    """
    # Handle missing credentials (auto_error=False means credentials can be None)
    if credentials is None:
        AuditService.log_token_invalid(
            db=db,
            reason="missing_credentials",
            request=request,
            token_snippet="N/A",
        )
        error = create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="MISSING_CREDENTIALS",
            message="Missing authentication credentials",
            request=request,
        )
        error.headers = {"WWW-Authenticate": "Bearer"}
        raise error

    token = credentials.credentials

    # Get token snippet for audit logging (first 8 + last 8 chars)
    token_snippet = f"{token[:8]}...{token[-8:]}" if len(token) > 16 else "***"

    def get_credentials_exception() -> HTTPException:
        """Helper to create credentials exception with headers."""
        error = create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN",
            message="Could not validate credentials",
            request=request,
        )
        error.headers = {"WWW-Authenticate": "Bearer"}
        return error

    try:
        # Decode JWT token
        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Extract required fields
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        organization_id = payload.get("org_id")
        name = payload.get("name")

        # Validate required fields
        if not all([user_id, email, role, organization_id]):
            AuditService.log_token_invalid(
                db=db,
                reason="missing_required_fields",
                request=request,
                token_snippet=token_snippet,
            )
            raise get_credentials_exception()

        # Validate role
        try:
            validated_role = UserRole(role)
        except ValueError:
            AuditService.log_token_invalid(
                db=db,
                reason=f"invalid_role:{role}",
                request=request,
                token_snippet=token_snippet,
            )
            error = create_error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="INVALID_ROLE",
                message=f"Invalid user role: {role}",
                request=request,
            )
            error.headers = {"WWW-Authenticate": "Bearer"}
            raise error

        # Check token expiration (if present)
        exp = payload.get("exp")
        if exp is not None:
            expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
            if datetime.now(timezone.utc) > expiration:
                AuditService.log_token_expired(
                    db=db,
                    user_id=UUID(user_id) if user_id else None,
                    organization_id=UUID(organization_id) if organization_id else None,
                    request=request,
                )
                error = create_error_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error_code="TOKEN_EXPIRED",
                    message="Token has expired",
                    request=request,
                )
                error.headers = {"WWW-Authenticate": "Bearer"}
                raise error

        # Create current user
        current_user = CurrentUser(
            id=UUID(user_id),
            email=email,
            role=validated_role,
            organization_id=UUID(organization_id),
            name=name,
        )

        # Log successful authentication (only on first request in session)
        # Note: We log sparingly to avoid bloat - consider caching recent auth
        logger.debug(
            "auth_success",
            extra={
                "user_id": user_id,
                "organization_id": organization_id,
                "role": role,
            },
        )

        return current_user

    except JWTError as e:
        AuditService.log_token_invalid(
            db=db,
            reason=f"jwt_error:{str(e)}",
            request=request,
            token_snippet=token_snippet,
        )
        error = create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="JWT_ERROR",
            message=f"JWT validation failed: {str(e)}",
            request=request,
        )
        error.headers = {"WWW-Authenticate": "Bearer"}
        raise error
    except ValueError as e:
        # UUID parsing errors
        AuditService.log_token_invalid(
            db=db,
            reason=f"invalid_format:{str(e)}",
            request=request,
            token_snippet=token_snippet,
        )
        error = create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN_FORMAT",
            message=f"Token contains invalid data format: {str(e)}",
            request=request,
        )
        error.headers = {"WWW-Authenticate": "Bearer"}
        raise error


def require_role(*allowed_roles: UserRole) -> Callable[..., Awaitable[CurrentUser]]:
    """
    Create a dependency that requires specific role(s) for access.

    This is a factory function that returns a FastAPI dependency.
    Use it to protect endpoints that require specific roles.
    Logs authorization failures to audit trail for SOC2 compliance.

    Args:
        *allowed_roles: One or more UserRole values that are allowed

    Returns:
        Dependency function that validates role and returns CurrentUser

    Example:
        @router.post("/workflows")
        async def create_workflow(
            current_user: CurrentUser = Depends(
                require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN)
            )
        ):
            # Only Process Managers and Admins can access
            pass

    Raises:
        HTTPException: 403 if user's role is not in allowed_roles
    """
    if not allowed_roles:
        raise ValueError("At least one role must be specified")

    async def role_checker(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        request: Request,
        db: Session = Depends(get_db),
    ) -> CurrentUser:
        """
        Validate that current user has one of the required roles.

        Note: Admin role always passes since admins have full access.
        """
        # Admin always has access
        if current_user.role == UserRole.ADMIN:
            return current_user

        # Check if user's role is in allowed roles
        if current_user.role not in allowed_roles:
            allowed_role_names = [role.value for role in allowed_roles]

            # Log authorization failure
            AuditService.log_authz_denied(
                db=db,
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                required_roles=allowed_role_names,
                actual_role=current_user.role.value,
                endpoint=str(request.url.path),
                request=request,
            )

            raise create_error_response(
                status_code=status.HTTP_403_FORBIDDEN,
                error_code="INSUFFICIENT_PERMISSIONS",
                message="You do not have permission to perform this action",
                details={
                    "required_roles": allowed_role_names,
                    "your_role": current_user.role.value,
                },
                request=request,
            )

        return current_user

    return role_checker


def require_permission(*required_permissions: Permission) -> Callable[..., Awaitable[CurrentUser]]:
    """
    Create a dependency that requires specific permission(s) for access.

    This provides more granular access control than role-based checks.
    Logs authorization failures to audit trail for SOC2 compliance.

    Args:
        *required_permissions: One or more Permission values required

    Returns:
        Dependency function that validates permissions and returns CurrentUser

    Example:
        @router.delete("/workflows/{id}")
        async def delete_workflow(
            current_user: CurrentUser = Depends(
                require_permission(Permission.WORKFLOWS_DELETE)
            )
        ):
            # Only users with workflows:delete permission can access
            pass

    Raises:
        HTTPException: 403 if user lacks required permissions
    """
    if not required_permissions:
        raise ValueError("At least one permission must be specified")

    async def permission_checker(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        request: Request,
        db: Session = Depends(get_db),
    ) -> CurrentUser:
        """Validate that current user has all required permissions."""
        missing_permissions = []

        for permission in required_permissions:
            if not has_permission(current_user.role, permission):
                missing_permissions.append(permission.value)

        if missing_permissions:
            # Log permission denial
            AuditService.log_permission_denied(
                db=db,
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                required_permissions=missing_permissions,
                actual_role=current_user.role.value,
                endpoint=str(request.url.path),
                request=request,
            )

            raise create_error_response(
                status_code=status.HTTP_403_FORBIDDEN,
                error_code="INSUFFICIENT_PERMISSIONS",
                message="You do not have permission to perform this action",
                details={
                    "missing_permissions": missing_permissions,
                    "your_role": current_user.role.value,
                },
                request=request,
            )

        return current_user

    return permission_checker


# Type alias for common dependency pattern
AuthenticatedUser = Annotated[CurrentUser, Depends(get_current_user)]

# Pre-built role dependencies for common patterns
ProcessManagerOrAdmin = Annotated[
    CurrentUser, Depends(require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN))
]
ProjectHandlerOrAdmin = Annotated[
    CurrentUser, Depends(require_role(UserRole.PROJECT_HANDLER, UserRole.ADMIN))
]
AdminOnly = Annotated[CurrentUser, Depends(require_role(UserRole.ADMIN))]
