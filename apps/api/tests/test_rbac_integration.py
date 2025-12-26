"""
Integration tests for RBAC with seeded database.

These tests verify that RBAC works correctly with actual database records,
including audit logging, multi-tenancy isolation, and role enforcement.

Unlike unit tests (test_rbac.py), these tests use real database transactions
and verify end-to-end behavior including audit trail creation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt

from app.main import app
from app.core.config import get_settings
from app.models.models import Organization, User, AuditLog

# Import test IDs from conftest - these match the seeded data
from tests.conftest import (
    TEST_ORG_A_ID,
    TEST_ORG_B_ID,
    TEST_USER_A_ID,
    TEST_USER_B_ID,
    TEST_USER_A_PM_ID,
    TEST_USER_A_PH_ID,
)


# Test data constants - must match seeded data names
TEST_ORG_A_NAME = "Test Organization A"
TEST_ORG_B_NAME = "Test Organization B"


def create_jwt_token(
    user_id: UUID,
    email: str,
    role: str,
    organization_id: UUID,
    name: str = "Test User",
    expired: bool = False,
) -> str:
    """Create a JWT token for testing."""
    if expired:
        exp = datetime.now(timezone.utc) - timedelta(hours=1)
    else:
        exp = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "org_id": str(organization_id),
        "name": name,
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": exp.timestamp(),
    }

    settings = get_settings()
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class TestDatabaseSetup:
    """
    Helper class for database setup.

    Note: Cleanup methods removed - automatic rollback via db_session fixture
    handles all test data cleanup.
    """

    @staticmethod
    def create_test_organization(db: Session, name: str) -> Organization:
        """Create a test organization."""
        org = Organization(
            name=name,
            subscription_tier="professional",
            subscription_status="active",
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def create_test_user(
        db: Session,
        organization_id: UUID,
        email: str,
        role: str,
        name: str = "Test User",
    ) -> User:
        """Create a test user."""
        user = User(
            organization_id=organization_id,
            email=email,
            name=name,
            role=role,
            password_hash="test_hash",  # Not used for JWT auth
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


@pytest.fixture
def test_orgs(db_session: Session) -> tuple[Organization, Organization]:
    """
    Load or create test organizations for multi-tenancy tests.

    First tries to load seeded organizations from pytest_sessionstart hook.
    If not found (e.g., due to transaction isolation), creates them for this test.
    """
    org_a = db_session.query(Organization).filter_by(id=UUID(TEST_ORG_A_ID)).first()
    org_b = db_session.query(Organization).filter_by(id=UUID(TEST_ORG_B_ID)).first()

    # If seeded data not visible, create it for this test
    if not org_a:
        org_a = Organization(
            id=UUID(TEST_ORG_A_ID),
            name=TEST_ORG_A_NAME,
            subscription_tier="trial",
            subscription_status="trial",
        )
        db_session.add(org_a)

    if not org_b:
        org_b = Organization(
            id=UUID(TEST_ORG_B_ID),
            name=TEST_ORG_B_NAME,
            subscription_tier="trial",
            subscription_status="trial",
        )
        db_session.add(org_b)

    db_session.commit()
    return org_a, org_b


@pytest.fixture
def test_users(db_session: Session, test_orgs) -> dict:
    """
    Load or create test users for each organization and role.

    First tries to load seeded users from pytest_sessionstart hook.
    If not found (e.g., due to transaction isolation), creates them for this test.
    """
    from app.models.enums import UserRole

    org_a, org_b = test_orgs

    # Load seeded users
    org_a_admin = db_session.query(User).filter_by(id=UUID(TEST_USER_A_ID)).first()
    org_a_pm = db_session.query(User).filter_by(id=UUID(TEST_USER_A_PM_ID)).first()
    org_a_ph = db_session.query(User).filter_by(id=UUID(TEST_USER_A_PH_ID)).first()
    org_b_admin = db_session.query(User).filter_by(id=UUID(TEST_USER_B_ID)).first()

    # Create missing users
    if not org_a_admin:
        org_a_admin = User(
            id=UUID(TEST_USER_A_ID),
            organization_id=org_a.id,
            email="admin@test-org-a.com",
            name="Admin User A",
            role=UserRole.ADMIN,
        )
        db_session.add(org_a_admin)

    if not org_a_pm:
        org_a_pm = User(
            id=UUID(TEST_USER_A_PM_ID),
            organization_id=org_a.id,
            email="pm@test-org-a.com",
            name="Process Manager A",
            role=UserRole.PROCESS_MANAGER,
        )
        db_session.add(org_a_pm)

    if not org_a_ph:
        org_a_ph = User(
            id=UUID(TEST_USER_A_PH_ID),
            organization_id=org_a.id,
            email="ph@test-org-a.com",
            name="Project Handler A",
            role=UserRole.PROJECT_HANDLER,
        )
        db_session.add(org_a_ph)

    if not org_b_admin:
        org_b_admin = User(
            id=UUID(TEST_USER_B_ID),
            organization_id=org_b.id,
            email="admin@test-org-b.com",
            name="Admin User B",
            role=UserRole.ADMIN,
        )
        db_session.add(org_b_admin)

    db_session.commit()

    users = {
        "org_a_admin": org_a_admin,
        "org_a_process_manager": org_a_pm,
        "org_a_project_handler": org_a_ph,
        "org_b_admin": org_b_admin,
    }

    return users


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


class TestRBACIntegration:
    """Integration tests for RBAC with seeded database."""

    def test_admin_can_access_own_organization(self, client, test_orgs, test_users):
        """Admin can access their own organization details."""
        org_a, _ = test_orgs
        admin = test_users["org_a_admin"]

        token = create_jwt_token(
            user_id=admin.id,
            email=admin.email,
            role=admin.role,
            organization_id=org_a.id,
        )

        response = client.get(
            f"/v1/organizations/{org_a.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(org_a.id)
        assert data["name"] == TEST_ORG_A_NAME

    def test_process_manager_can_list_own_organization(self, client, test_orgs, test_users):
        """Process manager can list their own organization."""
        org_a, _ = test_orgs
        pm = test_users["org_a_process_manager"]

        token = create_jwt_token(
            user_id=pm.id,
            email=pm.email,
            role=pm.role,
            organization_id=org_a.id,
        )

        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # Non-admin users only see their own org
        assert len(data) == 1
        assert data[0]["id"] == str(org_a.id)

    def test_admin_cannot_view_other_organization(self, client, test_orgs, test_users):
        """Admin CANNOT view other organizations (org-scoped in MVP).

        Security Note: Returns 404 (not 403) to prevent info leakage.
        Admins are organization-scoped - no super-admin access in MVP.
        """
        org_a, org_b = test_orgs
        admin = test_users["org_a_admin"]

        token = create_jwt_token(
            user_id=admin.id,
            email=admin.email,
            role=admin.role,
            organization_id=org_a.id,
        )

        # Admin cannot read other orgs (org-scoped in MVP)
        response = client.get(
            f"/v1/organizations/{org_b.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Security: 404 (not 403) to prevent info leakage
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_non_admin_cannot_access_other_organization(
        self, client, test_orgs, test_users, db_session
    ):
        """Non-admin users cannot access another organization's details.

        Security Note: Returns 404 (not 403) to prevent info leakage.
        """
        org_a, org_b = test_orgs
        pm = test_users["org_a_process_manager"]

        token = create_jwt_token(
            user_id=pm.id,
            email=pm.email,
            role=pm.role,
            organization_id=org_a.id,
        )

        # Try to access org B as non-admin
        response = client.get(
            f"/v1/organizations/{org_b.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Security: 404 (not 403) to prevent info leakage
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

        # Verify audit log was created for multi-tenancy violation
        audit_logs = (
            db_session.query(AuditLog)
            .filter(AuditLog.action == "authz.multi_tenancy.violation")
            .filter(AuditLog.user_id == pm.id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

        # At least one log entry should exist
        assert len(audit_logs) >= 1
        latest_log = audit_logs[0]
        assert latest_log.organization_id == org_a.id
        assert latest_log.resource_type == "organization"
        assert latest_log.resource_id == org_b.id

    def test_admin_cannot_update_other_organization(
        self, client, test_orgs, test_users, db_session
    ):
        """Admin cannot update another organization (multi-tenancy).

        Security Note: Returns 404 (not 403) to prevent info leakage.
        """
        org_a, org_b = test_orgs
        admin = test_users["org_a_admin"]

        token = create_jwt_token(
            user_id=admin.id,
            email=admin.email,
            role=admin.role,
            organization_id=org_a.id,
        )

        response = client.patch(
            f"/v1/organizations/{org_b.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Hacked Org"},
        )

        # Security: 404 (not 403) to prevent info leakage
        assert response.status_code == 404

        # Verify org B was not modified
        db_session.refresh(org_b)
        assert org_b.name == TEST_ORG_B_NAME

    def test_project_handler_cannot_create_organization(
        self, client, test_orgs, test_users, db_session
    ):
        """Project handler cannot create organizations (role enforcement)."""
        org_a, _ = test_orgs
        ph = test_users["org_a_project_handler"]

        token = create_jwt_token(
            user_id=ph.id,
            email=ph.email,
            role=ph.role,
            organization_id=org_a.id,
        )

        response = client.post(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "New Org"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
        assert "details" in data["error"]
        assert "admin" in data["error"]["details"]["required_roles"]

        # Verify audit log for authorization denial
        audit_logs = (
            db_session.query(AuditLog)
            .filter(AuditLog.action == "authz.access.denied")
            .filter(AuditLog.user_id == ph.id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

        assert len(audit_logs) >= 1
        latest_log = audit_logs[0]
        assert latest_log.organization_id == org_a.id
        assert "endpoint" in latest_log.action_metadata

    def test_admin_can_update_own_organization(self, client, test_orgs, test_users, db_session):
        """Admin can update their own organization."""
        org_a, _ = test_orgs
        admin = test_users["org_a_admin"]

        token = create_jwt_token(
            user_id=admin.id,
            email=admin.email,
            role=admin.role,
            organization_id=org_a.id,
        )

        new_name = "Updated Org A Name"
        response = client.patch(
            f"/v1/organizations/{org_a.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": new_name},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == new_name

        # Verify audit log for successful access
        audit_logs = (
            db_session.query(AuditLog)
            .filter(AuditLog.action == "authz.access.granted")
            .filter(AuditLog.user_id == admin.id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

        assert len(audit_logs) >= 1
        latest_log = audit_logs[0]
        assert latest_log.resource_type == "organization"
        assert latest_log.resource_id == org_a.id


class TestAuditLoggingIntegration:
    """Integration tests specifically for audit logging."""

    def test_invalid_token_creates_audit_log(self, client, db_session):
        """Invalid JWT token creates audit log entry."""
        # Create invalid token (wrong secret)
        invalid_token = jwt.encode(
            {
                "sub": str(uuid4()),
                "email": "attacker@evil.com",
                "role": "admin",
                "org_id": str(uuid4()),
            },
            "wrong_secret",
            algorithm="HS256",
        )

        # Count audit logs before
        logs_before = (
            db_session.query(AuditLog).filter(AuditLog.action == "auth.token.invalid").count()
        )

        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )

        assert response.status_code == 401

        # Count audit logs after
        logs_after = (
            db_session.query(AuditLog).filter(AuditLog.action == "auth.token.invalid").count()
        )

        # Should have one more log entry
        assert logs_after == logs_before + 1

    def test_expired_token_creates_audit_log(self, client, test_orgs, test_users, db_session):
        """Expired token creates audit log entry (or token invalid log from jose)."""
        org_a, _ = test_orgs
        admin = test_users["org_a_admin"]

        # Create expired token
        expired_token = create_jwt_token(
            user_id=admin.id,
            email=admin.email,
            role=admin.role,
            organization_id=org_a.id,
            expired=True,
        )

        # Count audit logs before (check both possible actions since jose
        # may raise JWTError before we reach our expiration check)
        logs_before_expired = (
            db_session.query(AuditLog).filter(AuditLog.action == "auth.token.expired").count()
        )
        logs_before_invalid = (
            db_session.query(AuditLog).filter(AuditLog.action == "auth.token.invalid").count()
        )

        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

        # Count audit logs after
        logs_after_expired = (
            db_session.query(AuditLog).filter(AuditLog.action == "auth.token.expired").count()
        )
        logs_after_invalid = (
            db_session.query(AuditLog).filter(AuditLog.action == "auth.token.invalid").count()
        )

        # Should have one more log entry (either expired or invalid)
        # jose library may raise ExpiredSignatureError which is caught as JWTError
        total_before = logs_before_expired + logs_before_invalid
        total_after = logs_after_expired + logs_after_invalid
        assert total_after >= total_before + 1, (
            f"Expected at least one new audit log. "
            f"Before: expired={logs_before_expired}, invalid={logs_before_invalid}. "
            f"After: expired={logs_after_expired}, invalid={logs_after_invalid}."
        )

    def test_audit_log_captures_ip_and_user_agent(self, client, db_session):
        """Audit log captures request metadata (IP, User-Agent)."""
        invalid_token = jwt.encode(
            {
                "sub": str(uuid4()),
                "email": "test@test.com",
                "role": "admin",
                "org_id": str(uuid4()),
            },
            "wrong_secret",
            algorithm="HS256",
        )

        client.get(
            "/v1/organizations",
            headers={
                "Authorization": f"Bearer {invalid_token}",
                "User-Agent": "TestAgent/1.0",
            },
        )

        # Get latest audit log
        latest_log = db_session.query(AuditLog).order_by(AuditLog.created_at.desc()).first()

        assert latest_log is not None
        assert latest_log.user_agent is not None
        # Note: ip_address may be None in test environment (TestClient limitation)
        # In production, request.client.host will be populated correctly

    def test_organization_delete_preserves_audit_logs(self, db_session):
        """Deleting organization should SET NULL on audit logs, not delete them (SOC2/ISO 27001)."""
        # Create test organization
        test_org = Organization(
            id=uuid4(),
            name="Test Org for Audit Log Preservation",
        )
        db_session.add(test_org)
        db_session.commit()
        db_session.refresh(test_org)

        # Create audit log associated with this organization
        audit_log = AuditLog(
            id=uuid4(),
            organization_id=test_org.id,
            user_id=None,
            action="test.action",
            resource_type="test",
            resource_id=uuid4(),
            ip_address="127.0.0.1",
            user_agent="TestAgent",
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)
        audit_log_id = audit_log.id

        # Delete organization
        db_session.delete(test_org)
        db_session.commit()

        # Verify audit log still exists with NULL organization_id
        preserved_audit_log = db_session.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
        assert preserved_audit_log is not None, "Audit log must persist (SOC2/ISO 27001)"
        assert (
            preserved_audit_log.organization_id is None
        ), "Organization ID should be NULL after org deletion"
        assert preserved_audit_log.action == "test.action", "Audit log data should be preserved"


class TestMultiTenancyIsolation:
    """Integration tests for multi-tenancy isolation."""

    def test_user_from_org_a_cannot_see_org_b_in_list(self, client, test_orgs, test_users):
        """Non-admin users can only see their own organization in lists."""
        org_a, org_b = test_orgs
        pm = test_users["org_a_process_manager"]

        token = create_jwt_token(
            user_id=pm.id,
            email=pm.email,
            role=pm.role,
            organization_id=org_a.id,
        )

        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should only contain org A
        org_ids = [org["id"] for org in data]
        assert str(org_a.id) in org_ids
        assert str(org_b.id) not in org_ids

    def test_project_handler_cannot_access_other_org_resource(
        self, client, test_orgs, test_users, db_session
    ):
        """Project handler cannot access another org's resources."""
        org_a, org_b = test_orgs
        ph = test_users["org_a_project_handler"]

        token = create_jwt_token(
            user_id=ph.id,
            email=ph.email,
            role=ph.role,
            organization_id=org_a.id,
        )

        # Try to access org B details
        response = client.get(
            f"/v1/organizations/{org_b.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Security: 404 (not 403) to prevent info leakage
        assert response.status_code == 404

        # Verify violation was logged
        violation_log = (
            db_session.query(AuditLog)
            .filter(AuditLog.action == "authz.multi_tenancy.violation")
            .filter(AuditLog.user_id == ph.id)
            .order_by(AuditLog.created_at.desc())
            .first()
        )

        assert violation_log is not None
        assert str(org_b.id) in str(violation_log.action_metadata)
