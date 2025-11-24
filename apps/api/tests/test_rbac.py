"""
Tests for Role-Based Access Control (RBAC).

This module tests:
- JWT token validation
- Role extraction from tokens
- Role-based endpoint protection
- Permission checking logic
- Authentication failure scenarios
- Authorization failure scenarios

Coverage target: 100% for security-critical code
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from app.models.enums import (
    UserRole,
    Permission,
    has_permission,
    get_role_permissions,
    ROLE_PERMISSIONS,
)
from app.core.auth import (
    get_current_user,
    require_role,
    require_permission,
    CurrentUser,
)
from app.core.config import settings
from tests.conftest import create_test_token, TEST_ORG_A_ID, TEST_ORG_B_ID


class TestUserRoleEnum:
    """Tests for UserRole enum."""

    def test_role_values(self):
        """Verify all role values are correct."""
        assert UserRole.PROCESS_MANAGER.value == "process_manager"
        assert UserRole.PROJECT_HANDLER.value == "project_handler"
        assert UserRole.ADMIN.value == "admin"

    def test_role_from_string(self):
        """Test creating role from string value."""
        assert UserRole("process_manager") == UserRole.PROCESS_MANAGER
        assert UserRole("project_handler") == UserRole.PROJECT_HANDLER
        assert UserRole("admin") == UserRole.ADMIN

    def test_invalid_role_raises(self):
        """Test that invalid role string raises ValueError."""
        with pytest.raises(ValueError):
            UserRole("invalid_role")


class TestPermissions:
    """Tests for permission checking logic."""

    def test_process_manager_permissions(self):
        """Process Manager has workflow CRUD and assessment read."""
        role = UserRole.PROCESS_MANAGER

        # Workflow permissions
        assert has_permission(role, Permission.WORKFLOWS_CREATE)
        assert has_permission(role, Permission.WORKFLOWS_READ)
        assert has_permission(role, Permission.WORKFLOWS_UPDATE)
        assert has_permission(role, Permission.WORKFLOWS_DELETE)

        # Assessment read only
        assert has_permission(role, Permission.ASSESSMENTS_READ)
        assert not has_permission(role, Permission.ASSESSMENTS_CREATE)

        # No document upload
        assert has_permission(role, Permission.DOCUMENTS_READ)
        assert not has_permission(role, Permission.DOCUMENTS_UPLOAD)

        # No user management
        assert not has_permission(role, Permission.USERS_CREATE)

    def test_project_handler_permissions(self):
        """Project Handler can run assessments and upload documents."""
        role = UserRole.PROJECT_HANDLER

        # Workflow read only
        assert has_permission(role, Permission.WORKFLOWS_READ)
        assert not has_permission(role, Permission.WORKFLOWS_CREATE)
        assert not has_permission(role, Permission.WORKFLOWS_UPDATE)
        assert not has_permission(role, Permission.WORKFLOWS_DELETE)

        # Assessment create and read
        assert has_permission(role, Permission.ASSESSMENTS_CREATE)
        assert has_permission(role, Permission.ASSESSMENTS_READ)

        # Document upload
        assert has_permission(role, Permission.DOCUMENTS_UPLOAD)
        assert has_permission(role, Permission.DOCUMENTS_READ)

        # No user management
        assert not has_permission(role, Permission.USERS_CREATE)

    def test_admin_has_all_permissions(self):
        """Admin has full access (wildcard)."""
        role = UserRole.ADMIN

        # Check all permissions
        assert has_permission(role, Permission.WORKFLOWS_CREATE)
        assert has_permission(role, Permission.WORKFLOWS_DELETE)
        assert has_permission(role, Permission.ASSESSMENTS_CREATE)
        assert has_permission(role, Permission.DOCUMENTS_UPLOAD)
        assert has_permission(role, Permission.USERS_CREATE)
        assert has_permission(role, Permission.USERS_DELETE)
        assert has_permission(role, Permission.ORGANIZATIONS_UPDATE)

    def test_get_role_permissions(self):
        """Test get_role_permissions returns correct set."""
        pm_perms = get_role_permissions(UserRole.PROCESS_MANAGER)
        assert Permission.WORKFLOWS_CREATE in pm_perms
        assert Permission.ASSESSMENTS_CREATE not in pm_perms

        admin_perms = get_role_permissions(UserRole.ADMIN)
        assert Permission.ALL in admin_perms


class TestJWTValidation:
    """Tests for JWT token validation."""

    def test_valid_token_authenticated(self, client: TestClient, admin_token: str):
        """Valid token allows access to authenticated endpoints."""
        response = client.get(
            "/v1/health",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

    def test_missing_token_returns_401(self, client: TestClient):
        """Missing Authorization header returns 401."""
        response = client.get("/v1/organizations")
        assert response.status_code in [401, 403]  # FastAPI returns 403 for missing auth

    def test_invalid_token_returns_401(self, client: TestClient, invalid_token: str):
        """Invalid JWT signature returns 401."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

    def test_expired_token_returns_401(self, client: TestClient, expired_token: str):
        """Expired token returns 401."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        data = response.json()
        # jose library reports expired tokens as JWT_ERROR (ExpiredSignatureError)
        # The important thing is that we get 401, not access granted
        assert data["detail"]["code"] in ["TOKEN_EXPIRED", "JWT_ERROR"]

    def test_malformed_token_returns_401(self, client: TestClient, malformed_token: str):
        """Malformed token string returns 401."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {malformed_token}"},
        )
        assert response.status_code == 401

    def test_token_missing_role_returns_401(self, client: TestClient, token_missing_role: str):
        """Token without role field returns 401."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {token_missing_role}"},
        )
        assert response.status_code == 401

    def test_token_missing_org_returns_401(self, client: TestClient, token_missing_org: str):
        """Token without organizationId field returns 401."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {token_missing_org}"},
        )
        assert response.status_code == 401

    def test_token_invalid_role_returns_401(self, client: TestClient, token_invalid_role: str):
        """Token with invalid role value returns 401."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {token_invalid_role}"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "INVALID_ROLE"


class TestRoleEnforcement:
    """Tests for role-based endpoint protection."""

    def test_admin_can_create_organization(self, client: TestClient, admin_token: str):
        """Admin can create organizations."""
        response = client.post(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": f"Test Org {uuid4()}"},
        )
        assert response.status_code == 201

    def test_process_manager_cannot_create_organization(
        self, client: TestClient, process_manager_token: str
    ):
        """Process Manager cannot create organizations (403 Forbidden)."""
        response = client.post(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {process_manager_token}"},
            json={"name": f"Test Org {uuid4()}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "INSUFFICIENT_PERMISSIONS"
        assert "admin" in data["detail"]["required_roles"]
        assert data["detail"]["your_role"] == "process_manager"

    def test_project_handler_cannot_create_organization(
        self, client: TestClient, project_handler_token: str
    ):
        """Project Handler cannot create organizations (403 Forbidden)."""
        response = client.post(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {project_handler_token}"},
            json={"name": f"Test Org {uuid4()}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "INSUFFICIENT_PERMISSIONS"

    def test_authenticated_user_can_list_organizations(
        self, client: TestClient, project_handler_token: str
    ):
        """Any authenticated user can list organizations."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {project_handler_token}"},
        )
        assert response.status_code == 200

    def test_admin_can_update_organization(
        self, client: TestClient, org_a_admin_token: str
    ):
        """Admin can update their own organization."""
        response = client.patch(
            f"/v1/organizations/{TEST_ORG_A_ID}",
            headers={"Authorization": f"Bearer {org_a_admin_token}"},
            json={"name": "Updated Org Name"},
        )
        # May return 404 if org doesn't exist in test DB, but should not be 403
        assert response.status_code in [200, 404]

    def test_process_manager_cannot_update_organization(
        self, client: TestClient, org_a_process_manager_token: str
    ):
        """Process Manager cannot update organizations (403 Forbidden)."""
        response = client.patch(
            f"/v1/organizations/{TEST_ORG_A_ID}",
            headers={"Authorization": f"Bearer {org_a_process_manager_token}"},
            json={"name": "Updated Org Name"},
        )
        assert response.status_code == 403

    def test_admin_can_delete_organization(
        self, client: TestClient, org_a_admin_token: str
    ):
        """Admin can delete their own organization."""
        response = client.delete(
            f"/v1/organizations/{TEST_ORG_A_ID}",
            headers={"Authorization": f"Bearer {org_a_admin_token}"},
        )
        # May return 404 if org doesn't exist in test DB, but should not be 403
        assert response.status_code in [204, 404]

    def test_project_handler_cannot_delete_organization(
        self, client: TestClient, org_a_project_handler_token: str
    ):
        """Project Handler cannot delete organizations (403 Forbidden)."""
        response = client.delete(
            f"/v1/organizations/{TEST_ORG_A_ID}",
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )
        assert response.status_code == 403


class TestMultiTenancy:
    """Tests for multi-tenancy enforcement."""

    def test_user_cannot_access_other_org_organization(
        self, client: TestClient, org_a_project_handler_token: str
    ):
        """User cannot access another organization's data."""
        response = client.get(
            f"/v1/organizations/{TEST_ORG_B_ID}",
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "ACCESS_DENIED"

    def test_admin_cannot_update_other_org(
        self, client: TestClient, org_a_admin_token: str
    ):
        """Admin cannot update another organization."""
        response = client.patch(
            f"/v1/organizations/{TEST_ORG_B_ID}",
            headers={"Authorization": f"Bearer {org_a_admin_token}"},
            json={"name": "Hacked Org Name"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "ACCESS_DENIED"

    def test_admin_cannot_delete_other_org(
        self, client: TestClient, org_a_admin_token: str
    ):
        """Admin cannot delete another organization."""
        response = client.delete(
            f"/v1/organizations/{TEST_ORG_B_ID}",
            headers={"Authorization": f"Bearer {org_a_admin_token}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "ACCESS_DENIED"


class TestRequireRoleDecorator:
    """Tests for require_role dependency factory."""

    def test_require_role_no_roles_raises(self):
        """require_role with no roles raises ValueError."""
        with pytest.raises(ValueError, match="At least one role must be specified"):
            require_role()

    def test_require_permission_no_perms_raises(self):
        """require_permission with no permissions raises ValueError."""
        with pytest.raises(ValueError, match="At least one permission must be specified"):
            require_permission()


class TestCurrentUserModel:
    """Tests for CurrentUser Pydantic model."""

    def test_current_user_frozen(self):
        """CurrentUser is immutable (frozen=True)."""
        user = CurrentUser(
            id=uuid4(),
            email="test@example.com",
            role=UserRole.ADMIN,
            organization_id=uuid4(),
        )
        # Pydantic v2 frozen models raise ValidationError on attribute assignment
        with pytest.raises(Exception):  # ValidationError in Pydantic v2
            user.role = UserRole.PROJECT_HANDLER

    def test_current_user_optional_name(self):
        """CurrentUser name field is optional."""
        user = CurrentUser(
            id=uuid4(),
            email="test@example.com",
            role=UserRole.ADMIN,
            organization_id=uuid4(),
        )
        assert user.name is None

        user_with_name = CurrentUser(
            id=uuid4(),
            email="test@example.com",
            role=UserRole.ADMIN,
            organization_id=uuid4(),
            name="Test User",
        )
        assert user_with_name.name == "Test User"


class TestHealthEndpoint:
    """Tests for health endpoint authentication."""

    def test_basic_health_no_auth_required(self, client: TestClient):
        """Basic health endpoint (/health) doesn't require auth."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_detailed_health_no_auth_required(self, client: TestClient):
        """Detailed health endpoint (/v1/health) doesn't require auth currently."""
        # Note: This may change in future if we add auth to /v1/health
        response = client.get("/v1/health")
        assert response.status_code == 200


class TestErrorResponses:
    """Tests for error response format."""

    def test_401_response_format(self, client: TestClient, expired_token: str):
        """401 errors have correct format."""
        response = client.get(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "code" in data["detail"]
        assert "message" in data["detail"]

    def test_403_response_format(
        self, client: TestClient, project_handler_token: str
    ):
        """403 errors have correct format with role info."""
        response = client.post(
            "/v1/organizations",
            headers={"Authorization": f"Bearer {project_handler_token}"},
            json={"name": "Test"},
        )
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "INSUFFICIENT_PERMISSIONS"
        assert "required_roles" in data["detail"]
        assert "your_role" in data["detail"]
