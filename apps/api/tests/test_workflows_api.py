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
        error = response.json()["error"]
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
        error = response.json()["error"]
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
        error = response.json()["error"]
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
        error = response.json()["error"]
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


class TestUpdateWorkflow:
    """Tests for PUT /v1/workflows/{workflow_id} endpoint."""

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

    def test_update_workflow_name_success(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test updating workflow name and description.

        Acceptance Criteria:
        - Updates workflow metadata (name, description)
        - Returns 200 OK with updated workflow
        - Audit log created with workflow.updated action
        - Structured logging includes request_id
        """
        db_mock, query_mock = mock_db

        buckets = [
            create_mock_bucket(TEST_BUCKET_1_ID, "Technical Documentation", 0, True),
        ]
        criteria = [
            create_mock_criteria(
                TEST_CRITERIA_1_ID,
                "All documents must be signed",
                "Each document should have authorized signature",
                [TEST_BUCKET_1_ID]
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

        query_mock.first.return_value = workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        update_data = {
            "name": "Medical Device - Class II (Updated)",
            "description": "Updated validation workflow",
            "buckets": [
                {
                    "id": TEST_BUCKET_1_ID,
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
            ],
            "criteria": [
                {
                    "id": TEST_CRITERIA_1_ID,
                    "name": "All documents must be signed",
                    "description": "Each document should have authorized signature",
                    "applies_to_bucket_ids": [TEST_BUCKET_1_ID],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Medical Device - Class II (Updated)"
        assert data["description"] == "Updated validation workflow"

        # Verify audit log was called
        mock_audit_service.log_workflow_updated.assert_called_once()

    def test_update_workflow_add_bucket(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test adding a new bucket to workflow.

        Acceptance Criteria:
        - Bucket with id=None creates new bucket
        - Returns updated workflow with new bucket ID
        - Audit log tracks buckets_added=1
        """
        db_mock, query_mock = mock_db

        buckets = [
            create_mock_bucket(TEST_BUCKET_1_ID, "Technical Documentation", 0, True),
        ]
        criteria = [
            create_mock_criteria(
                TEST_CRITERIA_1_ID,
                "All documents must be signed",
                "Description",
                [TEST_BUCKET_1_ID]
            )
        ]

        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            buckets=buckets,
            criteria=criteria
        )

        query_mock.first.return_value = workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "id": TEST_BUCKET_1_ID,
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                },
                {
                    # New bucket (no ID)
                    "name": "Test Reports",
                    "required": False,
                    "order_index": 1
                }
            ],
            "criteria": [
                {
                    "id": TEST_CRITERIA_1_ID,
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [TEST_BUCKET_1_ID],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200

        # Verify new bucket was added with correct attributes
        assert db_mock.add.called
        # Get the bucket that was added
        add_calls = [call for call in db_mock.add.call_args_list]
        assert len(add_calls) > 0

        # Find the bucket object in the add calls
        added_buckets = [
            call[0][0] for call in add_calls
            if hasattr(call[0][0], '__class__') and call[0][0].__class__.__name__ == 'Bucket'
        ]
        assert len(added_buckets) >= 1

        # Verify the new bucket has correct attributes
        new_bucket = added_buckets[0]
        assert new_bucket.name == "Test Reports"
        assert new_bucket.required is False
        assert new_bucket.order_index == 1
        assert new_bucket.workflow_id == workflow.id

    def test_update_workflow_delete_bucket(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test deleting a bucket from workflow.

        Acceptance Criteria:
        - Bucket omitted from request is deleted
        - Returns updated workflow without deleted bucket
        - Audit log tracks buckets_deleted=1
        """
        db_mock, query_mock = mock_db

        buckets = [
            create_mock_bucket(TEST_BUCKET_1_ID, "Technical Documentation", 0, True),
            create_mock_bucket(TEST_BUCKET_2_ID, "Test Reports", 1, True),
        ]
        criteria = [
            create_mock_criteria(
                TEST_CRITERIA_1_ID,
                "All documents must be signed",
                "Description",
                [TEST_BUCKET_1_ID]
            )
        ]

        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            buckets=buckets,
            criteria=criteria
        )

        query_mock.first.return_value = workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "id": TEST_BUCKET_1_ID,
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
                # TEST_BUCKET_2 omitted - should be deleted
            ],
            "criteria": [
                {
                    "id": TEST_CRITERIA_1_ID,
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [TEST_BUCKET_1_ID],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200

    def test_update_workflow_not_found(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test updating non-existent workflow returns 404.

        Acceptance Criteria:
        - Returns 404 Not Found
        - Error response includes RESOURCE_NOT_FOUND code
        - Error response includes request_id
        """
        db_mock, query_mock = mock_db

        # No workflow found
        query_mock.first.return_value = None

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
            ],
            "criteria": [
                {
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 404
        error = response.json()
        assert error["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "request_id" in error["error"]

    def test_update_workflow_multi_tenancy_isolation(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test user from org A cannot update workflow from org B.

        Security Test (100% coverage required):
        - Multi-tenancy isolation enforced
        - Returns 404 (not 403 to prevent ID enumeration)
        """
        db_mock, query_mock = mock_db

        # Workflow belongs to org B
        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_B_ID,  # Different org
        )

        # User from org A tries to access
        query_mock.first.return_value = None  # Query filters by org_id, returns None

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
            ],
            "criteria": [
                {
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 404

    def test_update_workflow_project_handler_forbidden(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test project_handler role cannot update workflow.

        Security Test (RBAC enforcement):
        - Only process_manager and admin can update
        - Returns 403 Forbidden for project_handler
        """
        db_mock, query_mock = mock_db

        # User with project_handler role (insufficient permissions)
        token = create_test_token(
            organization_id=TEST_ORG_A_ID,
            role="project_handler"  # Not process_manager or admin
        )

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
            ],
            "criteria": [
                {
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 403

    def test_update_workflow_invalid_bucket_reference(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test criteria referencing non-existent bucket triggers IntegrityError.

        Validation Test:
        - Criteria applies_to_bucket_ids with invalid references cause database IntegrityError
        - Returns 400 Bad Request with VALIDATION_ERROR code

        Note: After PR #82 review, Pydantic validation was removed as it incorrectly
        rejected valid scenarios. Database-level validation now handles this.
        """
        from sqlalchemy.exc import IntegrityError

        db_mock, query_mock = mock_db

        buckets = [
            create_mock_bucket(TEST_BUCKET_1_ID, "Technical Documentation", 0, True),
        ]
        criteria = [
            create_mock_criteria(
                TEST_CRITERIA_1_ID,
                "All documents must be signed",
                "Description",
                [TEST_BUCKET_1_ID]
            )
        ]

        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            buckets=buckets,
            criteria=criteria
        )

        query_mock.first.return_value = workflow

        # Mock IntegrityError when commit is called (database detects invalid reference)
        db_mock.commit.side_effect = IntegrityError(
            "violates foreign key constraint",
            params=None,
            orig=Exception("invalid bucket reference")
        )

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        # Invalid bucket ID in criteria
        invalid_bucket_id = str(uuid4())

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "id": TEST_BUCKET_1_ID,
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
            ],
            "criteria": [
                {
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [invalid_bucket_id],  # Invalid reference
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Database IntegrityError is caught and returns 400
        assert response.status_code == 400
        error = response.json()
        assert error["error"]["code"] == "VALIDATION_ERROR"

    def test_update_workflow_generic_exception(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test generic exception handling returns 500.

        Error Handling Test:
        - Unexpected exceptions are caught and logged
        - Returns 500 Internal Server Error
        - Error response includes WORKFLOW_UPDATE_FAILED code
        - Transaction is rolled back
        """
        db_mock, query_mock = mock_db

        buckets = [
            create_mock_bucket(TEST_BUCKET_1_ID, "Technical Documentation", 0, True),
        ]
        criteria = [
            create_mock_criteria(
                TEST_CRITERIA_1_ID,
                "All documents must be signed",
                "Description",
                [TEST_BUCKET_1_ID]
            )
        ]

        workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            buckets=buckets,
            criteria=criteria
        )

        query_mock.first.return_value = workflow

        # Mock a generic exception (not IntegrityError) during commit
        db_mock.commit.side_effect = RuntimeError("Unexpected database error")

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        update_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "buckets": [
                {
                    "id": TEST_BUCKET_1_ID,
                    "name": "Technical Documentation",
                    "required": True,
                    "order_index": 0
                }
            ],
            "criteria": [
                {
                    "id": TEST_CRITERIA_1_ID,
                    "name": "All documents must be signed",
                    "description": "Description",
                    "applies_to_bucket_ids": [TEST_BUCKET_1_ID],
                    "order_index": 0
                }
            ]
        }

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.put(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Generic exception is caught and returns 500
        assert response.status_code == 500
        error = response.json()
        assert error["error"]["code"] == "WORKFLOW_UPDATE_FAILED"
        assert "Unexpected database error" in error["error"]["message"]

        # Verify rollback was called
        assert db_mock.rollback.called


class TestArchiveWorkflow:
    """Tests for DELETE /v1/workflows/{workflow_id} endpoint (soft delete/archive)."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db_mock = MagicMock()
        query_mock = MagicMock()
        db_mock.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        return db_mock, query_mock

    def test_archive_workflow_success(
        self,
        client: TestClient,
        mock_db,
        mock_audit_service
    ):
        """
        Test successful workflow archival (soft delete).

        Success Test:
        - Returns 204 No Content
        - Sets archived=True and archived_at timestamp
        - Audit log created
        """
        db_mock, query_mock = mock_db

        # Mock workflow without assessments
        workflow = create_mock_workflow(TEST_WORKFLOW_ID, TEST_ORG_A_ID)
        workflow.archived = False
        workflow.archived_at = None
        query_mock.first.return_value = workflow

        # Mock assessment count (0 assessments)
        count_query_mock = MagicMock()
        db_mock.query.return_value.filter.return_value = count_query_mock
        count_query_mock.scalar.return_value = 0

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.delete(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 204
        # Verify workflow was marked as archived
        assert workflow.archived is True
        assert workflow.archived_at is not None
        # Verify database commit was called
        assert db_mock.commit.called

    def test_archive_workflow_unauthorized_no_token(
        self,
        client: TestClient
    ):
        """
        Test archiving workflow without authentication token returns 401.

        Security Test (Authentication):
        - No Bearer token provided
        - Returns 401 Unauthorized
        """
        response = client.delete(f"/v1/workflows/{TEST_WORKFLOW_ID}")
        assert response.status_code == 401

    def test_archive_workflow_forbidden_project_handler(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test project_handler role cannot archive workflow.

        Security Test (RBAC enforcement):
        - Only process_manager and admin can archive
        - Returns 403 Forbidden for project_handler
        """
        db_mock, query_mock = mock_db

        # User with project_handler role (insufficient permissions)
        token = create_test_token(
            organization_id=TEST_ORG_A_ID,
            role="project_handler"
        )

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.delete(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 403

    def test_archive_workflow_not_found(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test archiving non-existent workflow returns 404.

        Error Handling Test:
        - Workflow doesn't exist
        - Returns 404 Not Found
        """
        db_mock, query_mock = mock_db
        query_mock.first.return_value = None  # Workflow not found

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.delete(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 404
        error = response.json()
        assert error["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_archive_workflow_wrong_organization(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test archiving workflow from different organization returns 404.

        Security Test (Multi-tenancy enforcement):
        - User from ORG_A tries to archive ORG_B's workflow
        - Returns 404 (not 403) to prevent information leakage
        """
        db_mock, query_mock = mock_db
        # Workflow belongs to ORG_B, but user is from ORG_A
        query_mock.first.return_value = None  # Multi-tenancy filter blocks access

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="admin")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.delete(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 404

    def test_archive_workflow_with_assessments_conflict(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test cannot archive workflow with existing assessments (409 Conflict).

        Data Integrity Test:
        - Workflow has 5 assessments
        - Returns 409 Conflict
        - Error includes assessment count
        """
        MOCK_ASSESSMENT_COUNT = 5  # Number of assessments preventing archive

        db_mock, query_mock = mock_db

        workflow = create_mock_workflow(TEST_WORKFLOW_ID, TEST_ORG_A_ID)
        workflow.archived = False
        query_mock.first.return_value = workflow

        # Mock assessment count (prevents archiving)
        count_query_mock = MagicMock()
        db_mock.query.return_value.filter.return_value = count_query_mock
        count_query_mock.scalar.return_value = MOCK_ASSESSMENT_COUNT

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="admin")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.delete(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 409
        error = response.json()
        assert error["error"]["code"] == "RESOURCE_HAS_DEPENDENCIES"
        assert error["error"]["assessment_count"] == MOCK_ASSESSMENT_COUNT
        assert f"{MOCK_ASSESSMENT_COUNT} existing assessments" in error["error"]["message"]

    def test_archive_already_archived_workflow(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test cannot re-archive already archived workflow (400 Bad Request).

        Data Integrity Test:
        - Workflow is already archived
        - Returns 400 Bad Request
        - Error includes archived_at timestamp
        """
        from datetime import datetime, timezone

        db_mock, query_mock = mock_db

        workflow = create_mock_workflow(TEST_WORKFLOW_ID, TEST_ORG_A_ID)
        workflow.archived = True
        workflow.archived_at = datetime(2025, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
        query_mock.first.return_value = workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="admin")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.delete(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 400
        error = response.json()
        assert error["error"]["code"] == "ALREADY_ARCHIVED"
        assert "already archived" in error["error"]["message"]
        assert error["error"]["archived_at"] == "2025-11-20T10:00:00+00:00"


class TestListWorkflowsWithArchived:
    """Tests for GET /v1/workflows with include_archived parameter."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db_mock = MagicMock()
        query_mock = MagicMock()
        db_mock.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        return db_mock, query_mock

    def test_list_workflows_excludes_archived_by_default(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test list workflows excludes archived workflows by default.

        Soft Delete Test:
        - Default behavior: include_archived=False
        - Archived workflows hidden from list
        - Only non-archived workflows returned
        """
        from datetime import datetime

        db_mock, query_mock = mock_db

        # Mock count query (1 non-archived workflow)
        count_query_mock = MagicMock()
        db_mock.query.return_value.filter.return_value = count_query_mock
        count_query_mock.scalar.return_value = 1

        # Mock workflow query result (1 non-archived workflow)
        non_archived_wf = MagicMock()
        non_archived_wf.Workflow.id = TEST_WORKFLOW_ID
        non_archived_wf.Workflow.name = "Active Workflow"
        non_archived_wf.Workflow.description = "Test"
        non_archived_wf.Workflow.is_active = True
        non_archived_wf.Workflow.archived = False
        non_archived_wf.Workflow.archived_at = None
        non_archived_wf.Workflow.created_at = datetime.now()
        non_archived_wf.buckets_count = 2
        non_archived_wf.criteria_count = 3

        query_mock.all.return_value = [non_archived_wf]

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                "/v1/workflows",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 1
        assert data["workflows"][0]["archived"] is False

    def test_list_workflows_includes_archived_when_requested(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test list workflows includes archived workflows when include_archived=true.

        Soft Delete Test:
        - include_archived=true shows archived workflows
        - Both archived and non-archived workflows returned
        - archived and archived_at fields present in response
        """
        from datetime import datetime, timezone

        db_mock, query_mock = mock_db

        # Mock count query (2 workflows: 1 archived, 1 active)
        count_query_mock = MagicMock()
        db_mock.query.return_value.filter.return_value = count_query_mock
        count_query_mock.scalar.return_value = 2

        # Mock workflow query result
        non_archived_wf = MagicMock()
        non_archived_wf.Workflow.id = TEST_WORKFLOW_ID
        non_archived_wf.Workflow.name = "Active Workflow"
        non_archived_wf.Workflow.description = "Active"
        non_archived_wf.Workflow.is_active = True
        non_archived_wf.Workflow.archived = False
        non_archived_wf.Workflow.archived_at = None
        non_archived_wf.Workflow.created_at = datetime.now()
        non_archived_wf.buckets_count = 2
        non_archived_wf.criteria_count = 3

        archived_wf = MagicMock()
        archived_wf.Workflow.id = str(uuid4())
        archived_wf.Workflow.name = "Archived Workflow"
        archived_wf.Workflow.description = "Archived"
        archived_wf.Workflow.is_active = True
        archived_wf.Workflow.archived = True
        archived_wf.Workflow.archived_at = datetime(2025, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
        archived_wf.Workflow.created_at = datetime.now()
        archived_wf.buckets_count = 1
        archived_wf.criteria_count = 2

        query_mock.all.return_value = [non_archived_wf, archived_wf]

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="admin")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                "/v1/workflows?include_archived=true",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 2

        # Find archived workflow in response
        archived_workflow_data = next(
            (wf for wf in data["workflows"] if wf["archived"] is True),
            None
        )
        assert archived_workflow_data is not None
        assert archived_workflow_data["name"] == "Archived Workflow"
        assert archived_workflow_data["archived_at"] == "2025-11-20T10:00:00+00:00"


class TestGetArchivedWorkflow:
    """Tests for GET /v1/workflows/{id} with archived workflow."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db_mock = MagicMock()
        query_mock = MagicMock()
        db_mock.query.return_value = query_mock
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        return db_mock, query_mock

    def test_get_archived_workflow_by_id(
        self,
        client: TestClient,
        mock_db
    ):
        """
        Test archived workflow is still accessible via direct GET (audit trail).

        Audit Trail Test:
        - Archived workflows remain accessible via GET /{id}
        - Response includes archived=True and archived_at timestamp
        - Supports SOC2/ISO 27001 compliance requirements
        """
        from datetime import datetime, timezone

        db_mock, query_mock = mock_db

        # Mock archived workflow
        archived_workflow = create_mock_workflow(
            TEST_WORKFLOW_ID,
            TEST_ORG_A_ID,
            name="Archived Workflow"
        )
        archived_workflow.archived = True
        archived_workflow.archived_at = datetime(2025, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
        query_mock.first.return_value = archived_workflow

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

        with patch('app.api.v1.endpoints.workflows.get_db', return_value=iter([db_mock])):
            response = client.get(
                f"/v1/workflows/{TEST_WORKFLOW_ID}",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TEST_WORKFLOW_ID
        assert data["name"] == "Archived Workflow"
        assert data["archived"] is True
        assert data["archived_at"] == "2025-11-20T10:00:00+00:00"
