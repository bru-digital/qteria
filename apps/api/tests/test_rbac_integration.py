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
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt

from app.main import app
from app.core.config import settings
from app.core.dependencies import get_db
from app.models.base import SessionLocal
from app.models.models import Organization, User, AuditLog
from app.models.enums import UserRole


# Test data constants
TEST_ORG_A_NAME = "Integration Test Org A"
TEST_ORG_B_NAME = "Integration Test Org B"


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

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class TestDatabaseSetup:
    """Helper class for database setup and teardown."""

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

    @staticmethod
    def cleanup_test_data(db: Session, org_ids: list[UUID]) -> None:
        """Clean up test data after tests."""
        for org_id in org_ids:
            org = db.query(Organization).filter(Organization.id == org_id).first()
            if org:
                db.delete(org)
        db.commit()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create a database session for integration tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_orgs(db_session: Session) -> Generator[tuple[Organization, Organization], None, None]:
    """Create two test organizations for multi-tenancy tests."""
    org_a = TestDatabaseSetup.create_test_organization(db_session, TEST_ORG_A_NAME)
    org_b = TestDatabaseSetup.create_test_organization(db_session, TEST_ORG_B_NAME)

    yield org_a, org_b

    # Cleanup
    TestDatabaseSetup.cleanup_test_data(db_session, [org_a.id, org_b.id])


@pytest.fixture
def test_users(db_session: Session, test_orgs) -> Generator[dict, None, None]:
    """Create test users for each organization and role."""
    org_a, org_b = test_orgs

    users = {
        "org_a_admin": TestDatabaseSetup.create_test_user(
            db_session, org_a.id, "admin@org-a.test", UserRole.ADMIN.value, "Org A Admin"
        ),
        "org_a_process_manager": TestDatabaseSetup.create_test_user(
            db_session, org_a.id, "pm@org-a.test", UserRole.PROCESS_MANAGER.value, "Org A PM"
        ),
        "org_a_project_handler": TestDatabaseSetup.create_test_user(
            db_session, org_a.id, "ph@org-a.test", UserRole.PROJECT_HANDLER.value, "Org A PH"
        ),
        "org_b_admin": TestDatabaseSetup.create_test_user(
            db_session, org_b.id, "admin@org-b.test", UserRole.ADMIN.value, "Org B Admin"
        ),
    }

    yield users

    # Users are cascade deleted with organizations


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

    def test_non_admin_cannot_access_other_organization(self, client, test_orgs, test_users, db_session):
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

    def test_admin_cannot_update_other_organization(self, client, test_orgs, test_users, db_session):
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

    def test_project_handler_cannot_create_organization(self, client, test_orgs, test_users, db_session):
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
        assert "admin" in data["error"]["required_roles"]

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
        logs_before = db_session.query(AuditLog).filter(
            AuditLog.action == "auth.token.invalid"
        ).count()

        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )

        assert response.status_code == 401

        # Count audit logs after
        logs_after = db_session.query(AuditLog).filter(
            AuditLog.action == "auth.token.invalid"
        ).count()

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
        logs_before_expired = db_session.query(AuditLog).filter(
            AuditLog.action == "auth.token.expired"
        ).count()
        logs_before_invalid = db_session.query(AuditLog).filter(
            AuditLog.action == "auth.token.invalid"
        ).count()

        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

        # Count audit logs after
        logs_after_expired = db_session.query(AuditLog).filter(
            AuditLog.action == "auth.token.expired"
        ).count()
        logs_after_invalid = db_session.query(AuditLog).filter(
            AuditLog.action == "auth.token.invalid"
        ).count()

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
        latest_log = (
            db_session.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .first()
        )

        assert latest_log is not None
        assert latest_log.user_agent is not None
        # IP might be testclient in test environment
        assert latest_log.ip_address is not None


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
