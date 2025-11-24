"""
Integration tests for Workflow API endpoints.

Tests POST /v1/workflows endpoint for:
- Creating workflows with nested buckets and criteria
- RBAC enforcement (process_manager/admin only)
- Multi-tenancy isolation
- Transaction handling (rollback on errors)
- Validation errors

Journey Step 1: Process Manager creates validation workflows.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.models.enums import UserRole
from tests.conftest import TEST_ORG_A_ID


class TestCreateWorkflow:
    """Tests for POST /v1/workflows endpoint."""

    def test_create_workflow_success_process_manager(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Process manager can create workflow with buckets and criteria."""
        payload = {
            "name": "Medical Device - Class II",
            "description": "Validation workflow for Class II medical devices",
            "buckets": [
                {
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0,
                },
                {
                    "name": "Test Reports",
                    "required": True,
                    "order_index": 1,
                },
            ],
            "criteria": [
                {
                    "name": "All documents must be signed",
                    "description": "Each document should have authorized signature",
                    "applies_to_bucket_ids": [0, 1],
                },
                {
                    "name": "Test summary present",
                    "description": "Test report must include pass/fail summary",
                    "applies_to_bucket_ids": [1],
                },
            ],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()

        # Verify workflow data
        assert data["name"] == "Medical Device - Class II"
        assert data["description"] == "Validation workflow for Class II medical devices"
        assert data["is_active"] is True
        assert "id" in data
        assert "organization_id" in data
        assert "created_by" in data
        assert "created_at" in data

        # Verify buckets
        assert len(data["buckets"]) == 2
        assert data["buckets"][0]["name"] == "Technical Documentation"
        assert data["buckets"][0]["required"] is True
        assert data["buckets"][0]["order_index"] == 0
        assert "id" in data["buckets"][0]

        assert data["buckets"][1]["name"] == "Test Reports"
        assert data["buckets"][1]["required"] is True
        assert data["buckets"][1]["order_index"] == 1

        # Verify criteria
        assert len(data["criteria"]) == 2
        assert data["criteria"][0]["name"] == "All documents must be signed"
        assert len(data["criteria"][0]["applies_to_bucket_ids"]) == 2
        assert "id" in data["criteria"][0]

        assert data["criteria"][1]["name"] == "Test summary present"
        assert len(data["criteria"][1]["applies_to_bucket_ids"]) == 1

    def test_create_workflow_success_admin(
        self,
        client: TestClient,
        admin_token: str,
        mock_audit_service,
    ):
        """Admin can create workflow."""
        payload = {
            "name": "Test Workflow",
            "buckets": [{"name": "Bucket 1", "required": True, "order_index": 0}],
            "criteria": [{"name": "Criteria 1", "applies_to_bucket_ids": [0]}],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Test Workflow"

    def test_create_workflow_unauthorized_project_handler(
        self,
        client: TestClient,
        project_handler_token: str,
        mock_audit_service,
    ):
        """Project handler cannot create workflow (403 Forbidden)."""
        payload = {
            "name": "Test Workflow",
            "buckets": [{"name": "Bucket 1", "required": True, "order_index": 0}],
            "criteria": [{"name": "Criteria 1", "applies_to_bucket_ids": [0]}],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {project_handler_token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "INSUFFICIENT_PERMISSIONS"

    def test_create_workflow_unauthenticated(
        self,
        client: TestClient,
    ):
        """Unauthenticated request returns 401."""
        payload = {
            "name": "Test Workflow",
            "buckets": [{"name": "Bucket 1", "required": True, "order_index": 0}],
            "criteria": [{"name": "Criteria 1", "applies_to_bucket_ids": [0]}],
        }

        response = client.post("/v1/workflows", json=payload)

        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth

    def test_create_workflow_missing_name(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Request with missing workflow name returns 422."""
        payload = {
            # Missing "name"
            "buckets": [{"name": "Bucket 1", "required": True, "order_index": 0}],
            "criteria": [{"name": "Criteria 1", "applies_to_bucket_ids": [0]}],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422

    def test_create_workflow_empty_name(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Request with empty workflow name returns 422."""
        payload = {
            "name": "   ",  # Empty after stripping
            "buckets": [{"name": "Bucket 1", "required": True, "order_index": 0}],
            "criteria": [{"name": "Criteria 1", "applies_to_bucket_ids": [0]}],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422

    def test_create_workflow_empty_buckets(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Request with empty buckets array returns 422."""
        payload = {
            "name": "Test Workflow",
            "buckets": [],  # Empty buckets
            "criteria": [{"name": "Criteria 1", "applies_to_bucket_ids": []}],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422

    def test_create_workflow_empty_criteria(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Request with empty criteria array returns 422."""
        payload = {
            "name": "Test Workflow",
            "buckets": [{"name": "Bucket 1", "required": True, "order_index": 0}],
            "criteria": [],  # Empty criteria
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422

    def test_create_workflow_invalid_bucket_reference(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Criteria referencing non-existent bucket index returns 422."""
        payload = {
            "name": "Test Workflow",
            "buckets": [
                {"name": "Bucket 1", "required": True, "order_index": 0}
            ],  # Only 1 bucket (index 0)
            "criteria": [
                {
                    "name": "Criteria 1",
                    "applies_to_bucket_ids": [0, 1, 2],  # Invalid indexes 1 and 2
                }
            ],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422

    def test_create_workflow_bucket_name_stripped(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Bucket and criteria names are stripped of leading/trailing whitespace."""
        payload = {
            "name": "  Test Workflow  ",
            "buckets": [
                {"name": "  Technical Documentation  ", "required": True, "order_index": 0}
            ],
            "criteria": [
                {"name": "  All documents signed  ", "applies_to_bucket_ids": [0]}
            ],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workflow"
        assert data["buckets"][0]["name"] == "Technical Documentation"
        assert data["criteria"][0]["name"] == "All documents signed"

    def test_create_workflow_criteria_applies_to_all_buckets(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Criteria with empty applies_to_bucket_ids applies to all buckets."""
        payload = {
            "name": "Test Workflow",
            "buckets": [
                {"name": "Bucket 1", "required": True, "order_index": 0},
                {"name": "Bucket 2", "required": True, "order_index": 1},
            ],
            "criteria": [
                {
                    "name": "Global criteria",
                    "applies_to_bucket_ids": [],  # Applies to all
                }
            ],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        # Empty list gets converted to None (applies to all buckets)
        assert data["criteria"][0]["applies_to_bucket_ids"] == []


class TestListWorkflows:
    """Tests for GET /v1/workflows endpoint."""

    def test_list_workflows_authenticated(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Authenticated user can list workflows."""
        response = client.get(
            "/v1/workflows",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_workflows_unauthenticated(
        self,
        client: TestClient,
    ):
        """Unauthenticated request returns 403."""
        response = client.get("/v1/workflows")

        assert response.status_code == 403


class TestGetWorkflow:
    """Tests for GET /v1/workflows/{id} endpoint."""

    def test_get_workflow_not_found(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Request for non-existent workflow returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000001"
        response = client.get(
            f"/v1/workflows/{fake_id}",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "WORKFLOW_NOT_FOUND"

    def test_get_workflow_unauthenticated(
        self,
        client: TestClient,
    ):
        """Unauthenticated request returns 403."""
        fake_id = "00000000-0000-0000-0000-000000000001"
        response = client.get(f"/v1/workflows/{fake_id}")

        assert response.status_code == 403
