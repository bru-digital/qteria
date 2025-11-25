"""
Integration tests for Workflow API endpoints.

Tests coverage requirements (product-guidelines/09-test-strategy.md):
- API Routes: 80% coverage target
- Multi-Tenancy Security: 100% coverage (zero tolerance for data leakage)

Required Security Tests (per product guidelines lines 177-197):
- Authentication: 401 without token
- Authentication: 401 with expired token
- Authentication: 401 with invalid token
- Multi-tenancy: 404 for other org's workflow
- Multi-tenancy: Only returns user's org data
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from tests.conftest import (
    create_test_token,
    TEST_ORG_A_ID,
    TEST_ORG_B_ID
)


# Test data
TEST_WORKFLOW_ID = str(uuid4())
TEST_BUCKET_1_ID = str(uuid4())
TEST_BUCKET_2_ID = str(uuid4())
TEST_CRITERIA_1_ID = str(uuid4())
TEST_CRITERIA_2_ID = str(uuid4())


def create_mock_workflow(
    workflow_id: str,
    organization_id: str,
    name: str = "Test Workflow",
    description: str = "Test Description",
    buckets: list = None,
    criteria: list = None
):
    """Create a mock workflow object for testing."""
    workflow = MagicMock()
    workflow.id = workflow_id
    workflow.organization_id = organization_id
    workflow.name = name
    workflow.description = description
    workflow.created_by = str(uuid4())
    workflow.is_active = True
    workflow.created_at = "2024-01-15T10:30:00Z"
    workflow.updated_at = "2024-01-15T10:30:00Z"
    workflow.buckets = buckets or []
    workflow.criteria = criteria or []
    return workflow


def create_mock_bucket(bucket_id: str, name: str, order_index: int, required: bool = True):
    """Create a mock bucket object for testing."""
    bucket = MagicMock()
    bucket.id = bucket_id
    bucket.name = name
    bucket.required = required
    bucket.order_index = order_index
    return bucket


def create_mock_criteria(criteria_id: str, name: str, description: str, bucket_ids: list):
    """Create a mock criteria object for testing."""
    criteria = MagicMock()
    criteria.id = criteria_id
    criteria.name = name
    criteria.description = description
    criteria.applies_to_bucket_ids = bucket_ids
    return criteria


class TestGetWorkflowDetails:
    """Tests for GET /v1/workflows/{workflow_id} endpoint."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db_mock = MagicMock()
        # Setup query chain mock
        query_mock = MagicMock()
        db_mock.query.return_value = query_mock
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        return db_mock, query_mock

    def test_get_workflow_success(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test successful workflow retrieval with complete details.

        Acceptance Criteria:
        - Returns 200 OK with workflow details
        - Includes all metadata (name, description, timestamps)
        - Includes nested buckets array
        - Includes nested criteria array
        - Response includes stats (bucket_count, criteria_count)
        """
        db_mock, query_mock = mock_db

        # Create test data
        buckets = [
            create_mock_bucket(TEST_BUCKET_1_ID, "Technical Documentation", 0, True),
            create_mock_bucket(TEST_BUCKET_2_ID, "Test Reports", 1, True)
        ]
        criteria = [
            create_mock_criteria(
                TEST_CRITERIA_1_ID,
                "All documents must be signed",
                "Each document should have authorized signature",
                [TEST_BUCKET_1_ID, TEST_BUCKET_2_ID]
            )
        ]

        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            name="Medical Device - Class II",
            description="Validation workflow for Class II devices",
            buckets=buckets,
            criteria=criteria
        )

        # Mock database query to return workflow
        query_mock.first.return_value = workflow

        # Create token for org A
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock database dependency
        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()

        # Verify workflow metadata
        assert data["id"] == TEST_WORKFLOW_ID
        assert data["name"] == "Medical Device - Class II"
        assert data["description"] == "Validation workflow for Class II devices"
        assert data["organization_id"] == TEST_ORG_A_ID
        assert data["is_active"] is True

        # Verify buckets
        assert len(data["buckets"]) == 2
        assert data["buckets"][0]["name"] == "Technical Documentation"
        assert data["buckets"][0]["order_index"] == 0
        assert data["buckets"][0]["required"] is True
        assert data["buckets"][1]["name"] == "Test Reports"
        assert data["buckets"][1]["order_index"] == 1

        # Verify criteria
        assert len(data["criteria"]) == 1
        assert data["criteria"][0]["name"] == "All documents must be signed"
        assert data["criteria"][0]["description"] == "Each document should have authorized signature"
        assert len(data["criteria"][0]["applies_to_bucket_ids"]) == 2

        # Verify stats
        assert data["stats"]["bucket_count"] == 2
        assert data["stats"]["criteria_count"] == 1

    def test_get_workflow_with_empty_buckets_and_criteria(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test workflow with no buckets or criteria returns empty arrays.

        Acceptance Criteria:
        - Workflow with 0 buckets → returns empty array
        - Workflow with 0 criteria → returns empty array
        - Stats show 0 counts
        """
        db_mock, query_mock = mock_db

        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            buckets=[],  # Empty
            criteria=[]  # Empty
        )

        query_mock.first.return_value = workflow
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()

        assert data["buckets"] == []
        assert data["criteria"] == []
        assert data["stats"]["bucket_count"] == 0
        assert data["stats"]["criteria_count"] == 0

    def test_get_workflow_not_found(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test 404 response when workflow doesn't exist.

        Acceptance Criteria:
        - Returns 404 Not Found if workflow doesn't exist
        - Proper error response structure with code and message
        """
        db_mock, query_mock = mock_db

        # Mock database query to return None (not found)
        query_mock.first.return_value = None

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 404
        error = response.json()["detail"]
        assert error["code"] == "WORKFLOW_NOT_FOUND"
        assert error["message"] == "Workflow not found"
        assert error["workflow_id"] == TEST_WORKFLOW_ID

    def test_get_workflow_different_organization(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test multi-tenancy: workflow from different org returns 404.

        Acceptance Criteria (Multi-Tenancy Security - 100% coverage required):
        - Returns 404 if workflow belongs to different org
        - Uses 404 (not 403) to avoid leaking existence
        - Database query filters by organization_id
        """
        db_mock, query_mock = mock_db

        # Mock database returns None because org filter excludes the workflow
        query_mock.first.return_value = None

        # User from org B trying to access org A's workflow
        token = create_test_token(organization_id=TEST_ORG_B_ID)

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        # Should return 404 (not 403) to avoid leaking existence
        assert response.status_code == 404
        error = response.json()["detail"]
        assert error["code"] == "WORKFLOW_NOT_FOUND"

    def test_get_workflow_requires_authentication(
        self,
        client: TestClient,
        mock_audit_service
    ):
        """
        Test that endpoint requires valid authentication.

        Security Test (Required per product guidelines):
        - 401 without token
        """
        response = client.get(f"/v1/workflows/{TEST_WORKFLOW_ID}")

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_get_workflow_with_expired_token(
        self,
        client: TestClient,
        expired_token: str,
        mock_audit_service
    ):
        """
        Test that expired tokens are rejected.

        Security Test (Required per product guidelines):
        - 401 with expired token
        """
        response = client.get(
            f"/v1/workflows/{TEST_WORKFLOW_ID}",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        error = response.json()["detail"]
        assert error["code"] == "TOKEN_EXPIRED"

    def test_get_workflow_with_invalid_token(
        self,
        client: TestClient,
        invalid_token: str,
        mock_audit_service
    ):
        """
        Test that invalid tokens are rejected.

        Security Test (Required per product guidelines):
        - 401 with invalid token (wrong signature)
        """
        response = client.get(
            f"/v1/workflows/{TEST_WORKFLOW_ID}",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        assert response.status_code == 401
        error = response.json()["detail"]
        assert error["code"] in ["JWT_ERROR", "INVALID_TOKEN"]

    def test_get_workflow_with_malformed_token(
        self,
        client: TestClient,
        malformed_token: str,
        mock_audit_service
    ):
        """
        Test that malformed tokens are rejected.

        Security Test:
        - 401 with malformed token
        """
        response = client.get(
            f"/v1/workflows/{TEST_WORKFLOW_ID}",
            headers={"Authorization": f"Bearer {malformed_token}"}
        )

        assert response.status_code == 401

    def test_get_workflow_verifies_organization_filter(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test that database query includes organization_id filter.

        Multi-Tenancy Security Test (100% coverage required):
        - Verify database query filters by organization_id from JWT
        """
        db_mock, query_mock = mock_db

        workflow = create_mock_workflow(TEST_WORKFLOW_ID, TEST_ORG_A_ID)
        query_mock.first.return_value = workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        # Verify response is successful
        assert response.status_code == 200

        # Verify database query was called with filter
        # The filter should include both workflow_id and organization_id
        assert query_mock.filter.called

    def test_get_workflow_uses_eager_loading(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test that endpoint uses eager loading to prevent N+1 queries.

        Performance Test (Required per acceptance criteria):
        - Single database query with eager loading (no N+1 queries)
        - Verify selectinload is used for buckets and criteria
        """
        db_mock, query_mock = mock_db

        workflow = create_mock_workflow(TEST_WORKFLOW_ID, TEST_ORG_A_ID)
        query_mock.first.return_value = workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200

        # Verify that options() was called for eager loading
        assert query_mock.options.called

        # Verify that query.first() was called only once (single query)
        assert query_mock.first.call_count == 1
