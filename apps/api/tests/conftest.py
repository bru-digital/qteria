"""
Pytest configuration and fixtures for API tests.
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Generator
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.core.config import settings
from app.models.enums import UserRole
from app.services.audit import AuditService


@pytest.fixture
def mock_audit_service():
    """
    Mock AuditService for unit tests to avoid database dependencies.

    This allows unit tests to run without requiring seeded database data
    while still testing the core RBAC logic.

    NOTE: This fixture is NOT autouse. Tests that need mocked audit service
    should explicitly request it, or use the unit_test_mocks fixture.
    Integration tests should NOT use this fixture.
    """
    with patch.object(AuditService, 'log_event', return_value=MagicMock()) as mock_event, \
         patch.object(AuditService, 'log_auth_success', return_value=MagicMock()) as mock_auth_success, \
         patch.object(AuditService, 'log_auth_failure', return_value=MagicMock()) as mock_auth_failure, \
         patch.object(AuditService, 'log_token_invalid', return_value=MagicMock()) as mock_token_invalid, \
         patch.object(AuditService, 'log_token_expired', return_value=MagicMock()) as mock_token_expired, \
         patch.object(AuditService, 'log_authz_denied', return_value=MagicMock()) as mock_authz_denied, \
         patch.object(AuditService, 'log_multi_tenancy_violation', return_value=MagicMock()) as mock_mt_violation, \
         patch.object(AuditService, 'log_permission_denied', return_value=MagicMock()) as mock_perm_denied, \
         patch.object(AuditService, 'log_access_granted', return_value=MagicMock()) as mock_access_granted, \
         patch.object(AuditService, 'log_workflow_created', return_value=MagicMock()) as mock_workflow_created, \
         patch.object(AuditService, 'log_workflow_updated', return_value=MagicMock()) as mock_workflow_updated:
        yield {
            'log_event': mock_event,
            'log_auth_success': mock_auth_success,
            'log_auth_failure': mock_auth_failure,
            'log_token_invalid': mock_token_invalid,
            'log_token_expired': mock_token_expired,
            'log_authz_denied': mock_authz_denied,
            'log_multi_tenancy_violation': mock_mt_violation,
            'log_permission_denied': mock_perm_denied,
            'log_access_granted': mock_access_granted,
            'log_workflow_created': mock_workflow_created,
            'log_workflow_updated': mock_workflow_updated,
        }


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


def create_test_token(
    user_id: str | None = None,
    email: str = "test@example.com",
    role: str = "project_handler",
    organization_id: str | None = None,
    name: str = "Test User",
    expired: bool = False,
    missing_fields: list[str] | None = None,
) -> str:
    """
    Create a JWT token for testing.

    Args:
        user_id: User UUID (auto-generated if not provided)
        email: User email
        role: User role
        organization_id: Organization UUID (auto-generated if not provided)
        name: User display name
        expired: If True, create an expired token
        missing_fields: List of fields to omit from token

    Returns:
        JWT token string
    """
    if user_id is None:
        user_id = str(uuid4())
    if organization_id is None:
        organization_id = str(uuid4())

    # Set expiration
    if expired:
        exp = datetime.now(timezone.utc) - timedelta(hours=1)
    else:
        exp = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "org_id": organization_id,
        "name": name,
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": exp.timestamp(),
    }

    # Remove specified fields
    if missing_fields:
        for field in missing_fields:
            payload.pop(field, None)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def admin_token() -> str:
    """Create a JWT token for an admin user (uses seeded test data)."""
    return create_test_token(
        user_id=TEST_USER_A_ID,
        organization_id=TEST_ORG_A_ID,
        role=UserRole.ADMIN.value,
        email="admin@test-org-a.com",
    )


@pytest.fixture
def process_manager_token() -> str:
    """Create a JWT token for a process manager user (uses seeded test data)."""
    return create_test_token(
        user_id=TEST_USER_A_PM_ID,
        organization_id=TEST_ORG_A_ID,
        role=UserRole.PROCESS_MANAGER.value,
        email="pm@test-org-a.com",
    )


@pytest.fixture
def project_handler_token() -> str:
    """Create a JWT token for a project handler user (random UUID - doesn't need DB record)."""
    return create_test_token(role=UserRole.PROJECT_HANDLER.value)


@pytest.fixture
def expired_token() -> str:
    """Create an expired JWT token."""
    return create_test_token(expired=True)


@pytest.fixture
def invalid_token() -> str:
    """Create an invalid JWT token (wrong signature)."""
    return jwt.encode(
        {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "role": "admin",
            "org_id": str(uuid4()),
        },
        "wrong_secret_key",
        algorithm="HS256",
    )


@pytest.fixture
def malformed_token() -> str:
    """Create a malformed token string."""
    return "not.a.valid.jwt.token"


@pytest.fixture
def token_missing_role() -> str:
    """Create a token missing the role field."""
    return create_test_token(missing_fields=["role"])


@pytest.fixture
def token_missing_org() -> str:
    """Create a token missing the org_id field."""
    return create_test_token(missing_fields=["org_id"])


@pytest.fixture
def token_invalid_role() -> str:
    """Create a token with an invalid role."""
    return create_test_token(role="invalid_role")


# Test organization and user IDs for multi-tenancy tests
# These are FIXED UUIDs that match the seed data in scripts/seed_test_data.py
# DO NOT change these values - they must match the seeded database records
TEST_ORG_A_ID = "f52414ec-67f4-43d5-b25c-1552828ff06d"
TEST_ORG_B_ID = "f171ee72-38bd-4a10-9682-a0c483ae365e"
TEST_USER_A_ID = "236c7750-e281-46d9-95b8-209ae5106221"  # Admin User A
TEST_USER_A_PM_ID = "bebffc00-a259-4fce-a873-371e6765811b"  # Process Manager A
TEST_USER_B_ID = "cf1a6da7-32bf-4f00-8893-0ec2e0bbbb22"  # Admin User B
TEST_USER_B_PM_ID = "11df2007-978f-4503-b89c-7b8eaa228859"  # Process Manager B


@pytest.fixture
def org_a_admin_token() -> str:
    """Admin token for organization A."""
    return create_test_token(
        user_id=TEST_USER_A_ID,
        email="admin@org-a.com",
        role=UserRole.ADMIN.value,
        organization_id=TEST_ORG_A_ID,
    )


@pytest.fixture
def org_b_admin_token() -> str:
    """Admin token for organization B."""
    return create_test_token(
        user_id=TEST_USER_B_ID,
        email="admin@org-b.com",
        role=UserRole.ADMIN.value,
        organization_id=TEST_ORG_B_ID,
    )


@pytest.fixture
def org_a_process_manager_token() -> str:
    """Process manager token for organization A."""
    return create_test_token(
        user_id=TEST_USER_A_PM_ID,
        email="pm@test-org-a.com",
        role=UserRole.PROCESS_MANAGER.value,
        organization_id=TEST_ORG_A_ID,
    )


@pytest.fixture
def org_a_project_handler_token() -> str:
    """Project handler token for organization A."""
    return create_test_token(
        email="ph@org-a.com",
        role=UserRole.PROJECT_HANDLER.value,
        organization_id=TEST_ORG_A_ID,
    )
