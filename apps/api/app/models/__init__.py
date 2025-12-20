"""
Qteria database models.
Import all models here to ensure they're registered with SQLAlchemy.
"""

from .base import Base, engine, SessionLocal, get_db
from .models import (
    Organization,
    User,
    Workflow,
    Bucket,
    Criteria,
    Assessment,
    Document,
    ParsedDocument,
    AssessmentDocument,
    AssessmentResult,
    AuditLog,
)
from .enums import (
    UserRole,
    Permission,
    ROLE_PERMISSIONS,
    ROLE_DESCRIPTIONS,
    has_permission,
    get_role_permissions,
)
from .mixins import (
    OrganizationScopedMixin,
    get_scoped_or_404,
    filter_by_organization,
)

__all__ = [
    # Base and session
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    # Models
    "Organization",
    "User",
    "Workflow",
    "Bucket",
    "Criteria",
    "Assessment",
    "Document",
    "ParsedDocument",
    "AssessmentDocument",
    "AssessmentResult",
    "AuditLog",
    # Enums and RBAC
    "UserRole",
    "Permission",
    "ROLE_PERMISSIONS",
    "ROLE_DESCRIPTIONS",
    "has_permission",
    "get_role_permissions",
    # Multi-tenancy mixins
    "OrganizationScopedMixin",
    "get_scoped_or_404",
    "filter_by_organization",
]
