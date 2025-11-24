"""
Authentication and authorization dependencies for FastAPI.

This module provides:
- JWT token validation
- User extraction from tokens
- Role-based access control (RBAC) dependencies

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
from typing import Annotated, Callable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.enums import UserRole, Permission, has_permission


# HTTP Bearer security scheme
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token",
    auto_error=True,
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
    name: Optional[str] = Field(default=None, description="User's display name")

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
        "organizationId": "org-uuid",
        "name": "John Doe",
        "iat": 1234567890,
        "exp": 1234567890
    }
    """

    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    organizationId: str = Field(..., alias="organizationId", description="Organization ID")
    name: Optional[str] = Field(default=None, description="User name")
    iat: Optional[int] = Field(default=None, description="Issued at timestamp")
    exp: Optional[int] = Field(default=None, description="Expiration timestamp")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    """
    Extract and validate current user from JWT token.

    This dependency:
    1. Extracts the JWT token from Authorization header
    2. Validates the token signature
    3. Checks token expiration
    4. Extracts user information
    5. Validates the user role

    Args:
        credentials: HTTP Bearer credentials containing JWT token

    Returns:
        CurrentUser: Validated user information

    Raises:
        HTTPException: 401 if token is invalid, expired, or malformed
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "INVALID_TOKEN",
            "message": "Could not validate credentials",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Extract required fields
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        organization_id = payload.get("organizationId")
        name = payload.get("name")

        # Validate required fields
        if not all([user_id, email, role, organization_id]):
            raise credentials_exception

        # Validate role
        try:
            validated_role = UserRole(role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_ROLE",
                    "message": f"Invalid user role: {role}",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check token expiration (if present)
        exp = payload.get("exp")
        if exp is not None:
            expiration = datetime.fromtimestamp(exp, tz=timezone.utc)
            if datetime.now(timezone.utc) > expiration:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "TOKEN_EXPIRED",
                        "message": "Token has expired",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Create current user
        return CurrentUser(
            id=UUID(user_id),
            email=email,
            role=validated_role,
            organization_id=UUID(organization_id),
            name=name,
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "JWT_ERROR",
                "message": f"JWT validation failed: {str(e)}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        # UUID parsing errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN_FORMAT",
                "message": f"Token contains invalid data format: {str(e)}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Create a dependency that requires specific role(s) for access.

    This is a factory function that returns a FastAPI dependency.
    Use it to protect endpoints that require specific roles.

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "You do not have permission to perform this action",
                    "required_roles": allowed_role_names,
                    "your_role": current_user.role.value,
                },
            )

        return current_user

    return role_checker


def require_permission(*required_permissions: Permission) -> Callable:
    """
    Create a dependency that requires specific permission(s) for access.

    This provides more granular access control than role-based checks.

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
    ) -> CurrentUser:
        """Validate that current user has all required permissions."""
        missing_permissions = []

        for permission in required_permissions:
            if not has_permission(current_user.role, permission):
                missing_permissions.append(permission.value)

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "You do not have permission to perform this action",
                    "missing_permissions": missing_permissions,
                    "your_role": current_user.role.value,
                },
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
