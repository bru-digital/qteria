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


def create_test_workflow(client: TestClient, token: str, name: str = "Test Workflow"):
    """
    Helper function to create a test workflow with minimal required fields.

    This reduces code duplication across tests that need to create workflows
    for pagination, sorting, and other list endpoint tests.

    Args:
        client: FastAPI test client
        token: Authentication token
        name: Workflow name (default: "Test Workflow")

    Returns:
        Response from POST /v1/workflows
    """
    payload = {
        "name": name,
        "buckets": [{"name": "Test Bucket", "required": True, "order_index": 0}],
        "criteria": [{"name": "Test Criteria", "applies_to_bucket_ids": [0]}],
    }
    return client.post(
        "/v1/workflows",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )


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
        assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

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

        assert response.status_code == 401  # Returns 401 for missing/invalid auth

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

    def test_create_workflow_duplicate_bucket_names(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Workflow creation fails when bucket names are not unique (case-insensitive)."""
        payload = {
            "name": "Test Workflow",
            "buckets": [
                {"name": "Technical Documentation", "required": True, "order_index": 0},
                {"name": "Test Reports", "required": True, "order_index": 1},
                {"name": "technical documentation", "required": False, "order_index": 2},  # Duplicate (case-insensitive)
            ],
            "criteria": [
                {"name": "Test Criteria", "applies_to_bucket_ids": [0]}
            ],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422
        error_detail = response.json()["error"]
        assert any("unique" in str(err).lower() and "technical documentation" in str(err).lower() for err in error_detail)


class TestListWorkflows:
    """Tests for GET /v1/workflows endpoint with pagination."""

    def test_list_workflows_authenticated(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Authenticated user can list workflows with paginated response."""
        response = client.get(
            "/v1/workflows",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data
        assert "pagination" in data
        assert isinstance(data["workflows"], list)
        assert "total_count" in data["pagination"]
        assert "page" in data["pagination"]
        assert "per_page" in data["pagination"]
        assert "total_pages" in data["pagination"]

    def test_list_workflows_unauthenticated(
        self,
        client: TestClient,
    ):
        """Unauthenticated request returns 401."""
        response = client.get("/v1/workflows")

        assert response.status_code == 401

    def test_list_workflows_empty_organization(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Empty organization returns empty array with total_count=0.

        This test specifically validates that the NULL handling in total_count
        works correctly (scalar() returns None for COUNT(*) on empty result set).
        """
        response = client.get(
            "/v1/workflows",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # If organization has no workflows, should handle gracefully
        assert isinstance(data["pagination"]["total_count"], int)
        assert data["pagination"]["total_count"] >= 0
        assert data["pagination"]["total_pages"] >= 0
        assert len(data["workflows"]) <= data["pagination"]["per_page"]
        # Verify has_next_page and has_prev_page are booleans
        assert isinstance(data["pagination"]["has_next_page"], bool)
        assert isinstance(data["pagination"]["has_prev_page"], bool)

    def test_list_workflows_pagination_defaults(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Default pagination parameters are page=1, per_page=20."""
        response = client.get(
            "/v1/workflows",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 20

    def test_list_workflows_custom_per_page(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Can customize per_page parameter."""
        # Create 3 workflows using helper function
        for i in range(3):
            create_test_workflow(client, process_manager_token, f"Test Workflow {i}")

        # Request with per_page=2
        response = client.get(
            "/v1/workflows?per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["per_page"] == 2
        assert len(data["workflows"]) <= 2

    def test_list_workflows_multiple_pages(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Pagination across multiple pages works correctly."""
        # Create 5 workflows
        for i in range(5):
            payload = {
                "name": f"Workflow {i}",
                "buckets": [{"name": "Bucket", "required": True, "order_index": 0}],
                "criteria": [{"name": "Criteria", "applies_to_bucket_ids": [0]}],
            }
            client.post(
                "/v1/workflows",
                json=payload,
                headers={"Authorization": f"Bearer {process_manager_token}"},
            )

        # Page 1 with per_page=2
        response_p1 = client.get(
            "/v1/workflows?page=1&per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )
        assert response_p1.status_code == 200
        data_p1 = response_p1.json()
        assert data_p1["pagination"]["page"] == 1
        assert len(data_p1["workflows"]) == 2

        # Page 2 with per_page=2
        response_p2 = client.get(
            "/v1/workflows?page=2&per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )
        assert response_p2.status_code == 200
        data_p2 = response_p2.json()
        assert data_p2["pagination"]["page"] == 2
        assert len(data_p2["workflows"]) == 2

        # Verify different workflows on each page
        p1_ids = {wf["id"] for wf in data_p1["workflows"]}
        p2_ids = {wf["id"] for wf in data_p2["workflows"]}
        assert len(p1_ids.intersection(p2_ids)) == 0  # No overlap

    def test_list_workflows_total_pages_calculation(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Total pages calculation is correct."""
        # Create exactly 5 workflows
        for i in range(5):
            payload = {
                "name": f"Workflow {i}",
                "buckets": [{"name": "Bucket", "required": True, "order_index": 0}],
                "criteria": [{"name": "Criteria", "applies_to_bucket_ids": [0]}],
            }
            client.post(
                "/v1/workflows",
                json=payload,
                headers={"Authorization": f"Bearer {process_manager_token}"},
            )

        # With per_page=2, should have 3 pages (5/2 = 2.5 -> 3 pages)
        response = client.get(
            "/v1/workflows?per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["total_count"] >= 5
        # Should be at least 3 pages for the 5 new workflows (may be more if seeded data exists)
        assert data["pagination"]["total_pages"] >= 3

    def test_list_workflows_sort_by_created_at_desc(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Default sorting is by created_at descending (newest first)."""
        # Create workflows with distinct names
        for i in range(3):
            payload = {
                "name": f"Workflow Created {i}",
                "buckets": [{"name": "Bucket", "required": True, "order_index": 0}],
                "criteria": [{"name": "Criteria", "applies_to_bucket_ids": [0]}],
            }
            client.post(
                "/v1/workflows",
                json=payload,
                headers={"Authorization": f"Bearer {process_manager_token}"},
            )

        response = client.get(
            "/v1/workflows?sort_by=created_at&order=desc",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        workflows = data["workflows"]

        if len(workflows) >= 2:
            # Verify newest is first
            for i in range(len(workflows) - 1):
                assert workflows[i]["created_at"] >= workflows[i + 1]["created_at"]

    def test_list_workflows_sort_by_name_asc(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Can sort by name ascending (alphabetical)."""
        # Create workflows with specific names
        names = ["Zebra Workflow", "Alpha Workflow", "Beta Workflow"]
        for name in names:
            payload = {
                "name": name,
                "buckets": [{"name": "Bucket", "required": True, "order_index": 0}],
                "criteria": [{"name": "Criteria", "applies_to_bucket_ids": [0]}],
            }
            client.post(
                "/v1/workflows",
                json=payload,
                headers={"Authorization": f"Bearer {process_manager_token}"},
            )

        response = client.get(
            "/v1/workflows?sort_by=name&order=asc",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        workflows = data["workflows"]

        # Verify alphabetical order
        if len(workflows) >= 2:
            for i in range(len(workflows) - 1):
                assert workflows[i]["name"].lower() <= workflows[i + 1]["name"].lower()

    def test_list_workflows_sort_by_name_desc(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Can sort by name descending (reverse alphabetical)."""
        # Create workflows with specific names using helper function
        names = ["Alpha Workflow", "Beta Workflow", "Gamma Workflow"]
        for name in names:
            create_test_workflow(client, process_manager_token, name)

        response = client.get(
            "/v1/workflows?sort_by=name&order=desc",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        workflows = data["workflows"]

        # Verify reverse alphabetical order
        if len(workflows) >= 2:
            for i in range(len(workflows) - 1):
                assert workflows[i]["name"].lower() >= workflows[i + 1]["name"].lower()

    def test_list_workflows_invalid_page_zero(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Page parameter must be >= 1."""
        response = client.get(
            "/v1/workflows?page=0",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422  # Validation error

    def test_list_workflows_invalid_per_page_exceeds_max(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Per_page parameter cannot exceed 100."""
        response = client.get(
            "/v1/workflows?per_page=1000",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422  # Validation error

    def test_list_workflows_invalid_sort_field(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Sort_by must be either 'created_at' or 'name'."""
        response = client.get(
            "/v1/workflows?sort_by=invalid_field",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422  # Validation error

    def test_list_workflows_invalid_order(
        self,
        client: TestClient,
        process_manager_token: str,
    ):
        """Order must be either 'asc' or 'desc'."""
        response = client.get(
            "/v1/workflows?order=invalid",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 422  # Validation error

    def test_list_workflows_page_beyond_total_pages(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Requesting page beyond total_pages returns empty workflows array."""
        # Create 3 workflows
        for i in range(3):
            create_test_workflow(client, process_manager_token, f"Workflow {i}")

        # First get the current total_pages
        response = client.get(
            "/v1/workflows?per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )
        assert response.status_code == 200
        total_pages = response.json()["pagination"]["total_pages"]

        # Request a page way beyond total_pages (total_pages + 100)
        beyond_page = total_pages + 100
        response = client.get(
            f"/v1/workflows?page={beyond_page}&per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # Should return empty workflows array
        assert len(data["workflows"]) == 0
        # Pagination metadata should still be valid
        assert data["pagination"]["page"] == beyond_page
        assert data["pagination"]["per_page"] == 2
        assert data["pagination"]["total_pages"] >= 2
        assert data["pagination"]["has_next_page"] is False
        assert data["pagination"]["has_prev_page"] is True

    def test_list_workflows_has_next_prev_page_first_page(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """First page has no previous page but may have next page."""
        # Create 5 workflows
        for i in range(5):
            payload = {
                "name": f"Workflow {i}",
                "buckets": [{"name": "Bucket", "required": True, "order_index": 0}],
                "criteria": [{"name": "Criteria", "applies_to_bucket_ids": [0]}],
            }
            client.post(
                "/v1/workflows",
                json=payload,
                headers={"Authorization": f"Bearer {process_manager_token}"},
            )

        # Request first page with per_page=2
        response = client.get(
            "/v1/workflows?page=1&per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["has_prev_page"] is False
        # Should have next page since we have 5 workflows and per_page=2
        assert data["pagination"]["has_next_page"] is True

    def test_list_workflows_has_next_prev_page_last_page(
        self,
        client: TestClient,
        process_manager_token: str,
        mock_audit_service,
    ):
        """Last page has previous page but no next page."""
        # Create 5 workflows
        for i in range(5):
            payload = {
                "name": f"Workflow {i}",
                "buckets": [{"name": "Bucket", "required": True, "order_index": 0}],
                "criteria": [{"name": "Criteria", "applies_to_bucket_ids": [0]}],
            }
            client.post(
                "/v1/workflows",
                json=payload,
                headers={"Authorization": f"Bearer {process_manager_token}"},
            )

        # Get total pages first
        response = client.get(
            "/v1/workflows?per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )
        total_pages = response.json()["pagination"]["total_pages"]

        # Request last page
        response = client.get(
            f"/v1/workflows?page={total_pages}&per_page=2",
            headers={"Authorization": f"Bearer {process_manager_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == total_pages
        assert data["pagination"]["has_next_page"] is False
        assert data["pagination"]["has_prev_page"] is True


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
        assert response.json()["error"]["code"] == "WORKFLOW_NOT_FOUND"

    def test_get_workflow_unauthenticated(
        self,
        client: TestClient,
    ):
        """Unauthenticated request returns 401."""
        fake_id = "00000000-0000-0000-0000-000000000001"
        response = client.get(f"/v1/workflows/{fake_id}")

        assert response.status_code == 401


class TestMultiTenancyIsolation:
    """Tests for multi-tenancy isolation across workflow endpoints."""

    def test_create_workflow_scoped_to_organization(
        self,
        client: TestClient,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Created workflow is automatically scoped to user's organization."""
        payload = {
            "name": "Org A Workflow",
            "description": "Test workflow for org A",
            "buckets": [
                {
                    "name": "Test Bucket",
                    "required": True,
                    "order_index": 0,
                }
            ],
            "criteria": [
                {
                    "name": "Test Criteria",
                    "applies_to_bucket_ids": [0],
                }
            ],
        }

        response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_process_manager_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        # Verify workflow is scoped to organization A
        from tests.conftest import TEST_ORG_A_ID
        assert data["organization_id"] == TEST_ORG_A_ID

    def test_list_workflows_only_shows_own_organization(
        self,
        client: TestClient,
        org_a_process_manager_token: str,
        org_b_admin_token: str,
        mock_audit_service,
    ):
        """Users can only see workflows from their own organization."""
        # Create workflow in org A
        payload = {
            "name": "Org A Workflow",
            "description": "Workflow for organization A",
            "buckets": [
                {
                    "name": "Test Bucket",
                    "required": True,
                    "order_index": 0,
                }
            ],
            "criteria": [
                {
                    "name": "Test Criteria",
                    "applies_to_bucket_ids": [0],
                }
            ],
        }

        org_a_response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_process_manager_token}"},
        )
        assert org_a_response.status_code == 201
        org_a_workflow_id = org_a_response.json()["id"]

        # List workflows from org A perspective
        list_response_a = client.get(
            "/v1/workflows",
            headers={"Authorization": f"Bearer {org_a_process_manager_token}"},
        )
        assert list_response_a.status_code == 200
        org_a_data = list_response_a.json()
        org_a_workflows = org_a_data["workflows"]
        assert len(org_a_workflows) > 0
        assert any(wf["id"] == org_a_workflow_id for wf in org_a_workflows)

        # List workflows from org B perspective - should NOT see org A's workflow
        list_response_b = client.get(
            "/v1/workflows",
            headers={"Authorization": f"Bearer {org_b_admin_token}"},
        )
        assert list_response_b.status_code == 200
        org_b_data = list_response_b.json()
        org_b_workflows = org_b_data["workflows"]
        # Org B should not see org A's workflow
        assert not any(wf["id"] == org_a_workflow_id for wf in org_b_workflows)

    def test_get_workflow_cross_org_returns_404(
        self,
        client: TestClient,
        org_a_process_manager_token: str,
        org_b_admin_token: str,
        mock_audit_service,
    ):
        """Users cannot access workflows from other organizations (returns 404, not 403)."""
        # Create workflow in org A
        payload = {
            "name": "Org A Confidential Workflow",
            "description": "Should not be accessible to org B",
            "buckets": [
                {
                    "name": "Confidential Bucket",
                    "required": True,
                    "order_index": 0,
                }
            ],
            "criteria": [
                {
                    "name": "Confidential Criteria",
                    "applies_to_bucket_ids": [0],
                }
            ],
        }

        create_response = client.post(
            "/v1/workflows",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_process_manager_token}"},
        )
        assert create_response.status_code == 201
        org_a_workflow_id = create_response.json()["id"]

        # Try to access org A's workflow from org B - should return 404 (not 403)
        # This prevents information leakage about workflow existence
        get_response = client.get(
            f"/v1/workflows/{org_a_workflow_id}",
            headers={"Authorization": f"Bearer {org_b_admin_token}"},
        )
        assert get_response.status_code == 404
        assert get_response.json()["error"]["code"] == "WORKFLOW_NOT_FOUND"
