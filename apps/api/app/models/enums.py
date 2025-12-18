"""
Enumeration types for Qteria application.

This module defines role-based access control (RBAC) enums and permission mappings.

============================================================================
THIS IS THE SOURCE OF TRUTH FOR RBAC DEFINITIONS
============================================================================

Frontend/Backend Permission Sync
--------------------------------

The frontend mirrors these definitions for UX purposes. When modifying:

1. Update this file FIRST (it's the authoritative source)
2. Update frontend mirror: apps/web/lib/rbac.ts
3. Run tests to verify sync:
   - Backend: pytest tests/test_rbac.py
   - Frontend: npm run test (runs rbac.test.ts)

What frontend mirrors:
- UserRole enum values
- Permission enum values
- ROLE_PERMISSIONS mapping

What frontend does NOT mirror:
- ROLE_DESCRIPTIONS (backend-only documentation)
- has_permission() implementation (frontend has its own)
- get_role_permissions() implementation (frontend has its own)

Security Note
-------------
Frontend RBAC is UX-only (hiding buttons users can't use).
Backend RBAC in auth.py is the actual security enforcement.
Never trust frontend-only checks for authorization.

@see apps/web/lib/rbac.ts - Frontend mirror (TypeScript)
@see apps/api/app/core/auth.py - Backend enforcement
"""

from enum import Enum
from typing import Set


class UserRole(str, Enum):
    """
    User roles for role-based access control.

    Roles:
        - PROCESS_MANAGER: Can create/edit workflows, view assessments
        - PROJECT_HANDLER: Can run assessments, upload documents
        - ADMIN: Full access to all features within their organization

    @sync apps/web/lib/rbac.ts:UserRole
    """

    PROCESS_MANAGER = "process_manager"
    PROJECT_HANDLER = "project_handler"
    ADMIN = "admin"


class Permission(str, Enum):
    """
    Fine-grained permissions for RBAC.

    Format: resource:action

    @sync apps/web/lib/rbac.ts:Permission
    """

    # Workflow permissions
    WORKFLOWS_CREATE = "workflows:create"
    WORKFLOWS_READ = "workflows:read"
    WORKFLOWS_UPDATE = "workflows:update"
    WORKFLOWS_DELETE = "workflows:delete"

    # Assessment permissions
    ASSESSMENTS_CREATE = "assessments:create"
    ASSESSMENTS_READ = "assessments:read"
    ASSESSMENTS_UPDATE = "assessments:update"
    ASSESSMENTS_DELETE = "assessments:delete"

    # Document permissions
    DOCUMENTS_UPLOAD = "documents:upload"
    DOCUMENTS_READ = "documents:read"
    DOCUMENTS_DELETE = "documents:delete"

    # Organization permissions (admin only)
    ORGANIZATIONS_READ = "organizations:read"
    ORGANIZATIONS_UPDATE = "organizations:update"

    # User management permissions (admin only)
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"

    # Wildcard for admin
    ALL = "*"


# Role-to-Permission mapping
# Defines what each role can do in the system
# @sync apps/web/lib/rbac.ts:ROLE_PERMISSIONS
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.PROCESS_MANAGER: {
        # Workflow management (full CRUD)
        Permission.WORKFLOWS_CREATE,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_UPDATE,
        Permission.WORKFLOWS_DELETE,
        # Assessment access (read-only)
        Permission.ASSESSMENTS_READ,
        # Document access (read-only)
        Permission.DOCUMENTS_READ,
    },
    UserRole.PROJECT_HANDLER: {
        # Workflow access (read-only)
        Permission.WORKFLOWS_READ,
        # Assessment management
        Permission.ASSESSMENTS_CREATE,
        Permission.ASSESSMENTS_READ,
        # Document management
        Permission.DOCUMENTS_UPLOAD,
        Permission.DOCUMENTS_READ,
    },
    UserRole.ADMIN: {
        # Full access (wildcard)
        Permission.ALL,
    },
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        role: The user's role
        permission: The permission to check

    Returns:
        True if the role has the permission, False otherwise
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())

    # Admin has all permissions
    if Permission.ALL in role_perms:
        return True

    return permission in role_perms


def get_role_permissions(role: UserRole) -> Set[Permission]:
    """
    Get all permissions for a role.

    Args:
        role: The user's role

    Returns:
        Set of permissions for the role
    """
    return ROLE_PERMISSIONS.get(role, set())


# Role hierarchy for documentation
ROLE_DESCRIPTIONS = {
    UserRole.PROCESS_MANAGER: {
        "title": "Process Manager",
        "description": "Creates and manages validation workflows and criteria",
        "can_do": [
            "Create, edit, and delete workflows",
            "Define document buckets and validation criteria",
            "View assessment results",
        ],
        "cannot_do": [
            "Run assessments",
            "Upload documents for validation",
            "Manage organization settings",
            "Manage users",
        ],
    },
    UserRole.PROJECT_HANDLER: {
        "title": "Project Handler",
        "description": "Runs assessments and validates documents",
        "can_do": [
            "View available workflows",
            "Upload documents for validation",
            "Start and run assessments",
            "View assessment results",
        ],
        "cannot_do": [
            "Create or modify workflows",
            "Delete validation criteria",
            "Manage organization settings",
            "Manage users",
        ],
    },
    UserRole.ADMIN: {
        "title": "Administrator",
        "description": "Full access to all features within their organization",
        "can_do": [
            "Everything Process Manager can do",
            "Everything Project Handler can do",
            "Manage organization settings",
            "Invite and manage users",
            "View audit logs",
        ],
        "cannot_do": [
            "Access other organizations' data (multi-tenancy enforced)",
        ],
    },
}
