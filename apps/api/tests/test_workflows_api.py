"""
Tests for Workflow API endpoints.

This module tests:
- DELETE /v1/workflows/{id} - Archive workflow (soft delete)
- GET /v1/workflows - List workflows with archive filtering
- GET /v1/workflows/{id} - Get single workflow
- RBAC enforcement (process_manager/admin only for delete)
- Multi-tenancy isolation
- Assessment count check (409 Conflict if assessments exist)
- Audit logging

These are integration tests with mocked database queries.
For full E2E tests, see test_workflows_e2e.py.

Coverage target: 80% for API routes, 100% for multi-tenancy security
"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.models import Workflow, Assessment
from app.models.enums import UserRole
from tests.conftest import (
    create_test_token,
    TEST_ORG_A_ID,
    TEST_ORG_B_ID,
    TEST_USER_A_ID,
    TEST_USER_B_ID,
)


# Apply mock_audit_service fixture to all tests in this module
pytestmark = pytest.mark.usefixtures("mock_audit_service")


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_workflow():
    """Create a mock workflow object."""
    workflow_id = uuid4()
    return MagicMock(
        id=workflow_id,
        organization_id=UUID(TEST_ORG_A_ID),
        created_by=UUID(TEST_USER_A_ID),
        name="Test Workflow",
        description="Test Description",
        is_active=True,
        archived=False,
        archived_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_archived_workflow():
    """Create a mock archived workflow object."""
    workflow_id = uuid4()
    return MagicMock(
        id=workflow_id,
        organization_id=UUID(TEST_ORG_A_ID),
        created_by=UUID(TEST_USER_A_ID),
        name="Archived Workflow",
        description="Archived",
        is_active=True,
        archived=True,
        archived_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestListWorkflows:
    """Tests for GET /v1/workflows endpoint."""

    def test_list_workflows_success(self, client, mock_workflow):
        """Test listing workflows returns workflows from user's org."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROCESS_MANAGER.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.all.return_value = [mock_workflow]

            response = client.get(
                "/v1/workflows",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            workflows = response.json()
            assert len(workflows) == 1
            assert workflows[0]["name"] == "Test Workflow"
            assert workflows[0]["archived"] == False

    def test_list_workflows_excludes_archived_by_default(
        self, client, mock_workflow, mock_archived_workflow
    ):
        """Test that archived workflows are excluded by default."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROCESS_MANAGER.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain - filter is called twice (org + archived)
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.all.return_value = [mock_workflow]  # Only non-archived

            response = client.get(
                "/v1/workflows",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            workflows = response.json()
            assert len(workflows) == 1
            assert workflows[0]["archived"] == False

    def test_list_workflows_includes_archived_when_requested(
        self, client, mock_workflow, mock_archived_workflow
    ):
        """Test that include_archived=true shows archived workflows."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.ADMIN.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.all.return_value = [mock_workflow, mock_archived_workflow]

            response = client.get(
                "/v1/workflows?include_archived=true",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            workflows = response.json()
            assert len(workflows) == 2

    def test_list_workflows_requires_authentication(self, client):
        """Test that listing workflows requires authentication."""
        response = client.get("/v1/workflows")
        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"


class TestGetWorkflow:
    """Tests for GET /v1/workflows/{id} endpoint."""

    def test_get_workflow_success(self, client, mock_workflow):
        """Test getting a workflow returns workflow details."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROJECT_HANDLER.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_workflow

            response = client.get(
                f"/v1/workflows/{mock_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            workflow = response.json()
            assert workflow["name"] == "Test Workflow"

    def test_get_archived_workflow_success(self, client, mock_archived_workflow):
        """Test that archived workflows are still accessible via GET."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.ADMIN.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_archived_workflow

            response = client.get(
                f"/v1/workflows/{mock_archived_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            workflow = response.json()
            assert workflow["archived"] == True

    def test_get_workflow_not_found(self, client):
        """Test that getting non-existent workflow returns 404."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROCESS_MANAGER.value,
        )
        workflow_id = uuid4()

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain - return None
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None

            response = client.get(
                f"/v1/workflows/{workflow_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 404
            assert response.json()["detail"]["code"] == "RESOURCE_NOT_FOUND"

    def test_get_workflow_multi_tenancy_violation(self, client, mock_workflow):
        """Test that user cannot access workflow from other org (404)."""
        # User from org B tries to access org A's workflow
        token = create_test_token(
            user_id=TEST_USER_B_ID,
            organization_id=TEST_ORG_B_ID,
            role=UserRole.ADMIN.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock query chain - returns None due to org filter
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None

            response = client.get(
                f"/v1/workflows/{mock_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 404
            assert response.json()["detail"]["code"] == "RESOURCE_NOT_FOUND"


class TestDeleteWorkflow:
    """Tests for DELETE /v1/workflows/{id} endpoint (soft delete/archive)."""

    def test_delete_workflow_success_no_assessments(self, client, mock_workflow):
        """Test deleting workflow with no assessments succeeds (204)."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROCESS_MANAGER.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock workflow query
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_workflow

            # Mock assessment count query (returns 0)
            mock_query.scalar.return_value = 0

            response = client.delete(
                f"/v1/workflows/{mock_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 204
            # Verify workflow was archived (not deleted)
            assert mock_workflow.archived == True
            assert mock_workflow.archived_at is not None
            mock_db.commit.assert_called_once()

    def test_delete_workflow_conflict_with_assessments(self, client, mock_workflow):
        """Test deleting workflow with assessments returns 409 Conflict."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.ADMIN.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock workflow query
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_workflow

            # Mock assessment count query (returns 5)
            mock_query.scalar.return_value = 5

            response = client.delete(
                f"/v1/workflows/{mock_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 409
            detail = response.json()["detail"]
            assert detail["code"] == "RESOURCE_HAS_DEPENDENCIES"
            assert detail["assessment_count"] == 5
            # Verify workflow was NOT archived
            assert mock_workflow.archived == False

    def test_delete_workflow_not_found(self, client):
        """Test deleting non-existent workflow returns 404."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROCESS_MANAGER.value,
        )
        workflow_id = uuid4()

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock workflow query - returns None
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None

            response = client.delete(
                f"/v1/workflows/{workflow_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 404
            assert response.json()["detail"]["code"] == "RESOURCE_NOT_FOUND"

    def test_delete_workflow_multi_tenancy_violation(self, client, mock_workflow):
        """Test that user cannot delete workflow from other org (404)."""
        # User from org B tries to delete org A's workflow
        token = create_test_token(
            user_id=TEST_USER_B_ID,
            organization_id=TEST_ORG_B_ID,
            role=UserRole.ADMIN.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock workflow query - returns None due to org filter
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None

            response = client.delete(
                f"/v1/workflows/{mock_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 404
            assert response.json()["detail"]["code"] == "RESOURCE_NOT_FOUND"

    def test_delete_workflow_requires_process_manager_or_admin(
        self, client, mock_workflow
    ):
        """Test that project_handler cannot delete workflows (403)."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.PROJECT_HANDLER.value,
        )

        response = client.delete(
            f"/v1/workflows/{mock_workflow.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "INSUFFICIENT_PERMISSIONS"
        assert "process_manager" in response.json()["detail"]["required_roles"]

    def test_delete_workflow_requires_authentication(self, client):
        """Test that deleting workflow requires authentication (401)."""
        workflow_id = uuid4()
        response = client.delete(f"/v1/workflows/{workflow_id}")
        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_delete_workflow_admin_always_authorized(self, client, mock_workflow):
        """Test that admin can delete workflows (admin bypass in role checker)."""
        token = create_test_token(
            user_id=TEST_USER_A_ID,
            organization_id=TEST_ORG_A_ID,
            role=UserRole.ADMIN.value,
        )

        with patch("app.api.v1.endpoints.workflows.get_db") as mock_get_db:
            mock_db = MagicMock(spec=Session)
            mock_get_db.return_value = mock_db

            # Mock workflow query
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_workflow

            # Mock assessment count query (0 assessments)
            mock_query.scalar.return_value = 0

            response = client.delete(
                f"/v1/workflows/{mock_workflow.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 204
            assert mock_workflow.archived == True
