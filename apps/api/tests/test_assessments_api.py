"""
Integration tests for Assessment API endpoints.

Tests POST /v1/assessments endpoint for:
- Creating assessments with document mappings
- Required bucket validation
- Invalid bucket reference validation
- RBAC enforcement (all roles can start assessments)
- Multi-tenancy isolation
- Transaction handling (rollback on errors)

Journey Step 2→3: Project Handler starts AI validation assessment.
"""

from fastapi.testclient import TestClient


def create_test_workflow_with_buckets(client: TestClient, token: str):
    """
    Helper to create a test workflow with required and optional buckets.

    Returns:
        tuple: (workflow_id, required_bucket_id, optional_bucket_id)
    """
    payload = {
        "name": "Test Workflow for Assessments",
        "buckets": [
            {"name": "Required Bucket", "required": True, "order_index": 0},
            {"name": "Optional Bucket", "required": False, "order_index": 1},
        ],
        "criteria": [
            {
                "name": "Test Criteria",
                "description": "Test validation rule",
                "applies_to_bucket_ids": [0, 1],
            }
        ],
    }

    response = client.post(
        "/v1/workflows",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()

    return (
        data["id"],
        data["buckets"][0]["id"],  # Required bucket
        data["buckets"][1]["id"],  # Optional bucket
    )


class TestStartAssessment:
    """Tests for POST /v1/assessments endpoint."""

    def test_start_assessment_success(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Project handler can start assessment with valid documents."""
        # Create workflow
        workflow_id, required_bucket_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Start assessment with document mapping
        payload = {
            "workflow_id": workflow_id,
            "documents": [
                {
                    "bucket_id": required_bucket_id,
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()

        # Verify assessment data
        assert data["workflow_id"] == workflow_id
        assert data["status"] == "pending"
        assert data["document_count"] == 1
        assert "id" in data
        assert "started_at" in data
        assert "estimated_completion_at" in data

    def test_start_assessment_missing_required_bucket(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Assessment creation fails when required bucket has no documents."""
        # Create workflow
        workflow_id, required_bucket_id, optional_bucket_id = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Try to start assessment WITHOUT required bucket document (only optional bucket)
        payload = {
            "workflow_id": workflow_id,
            "documents": [
                {
                    "bucket_id": optional_bucket_id,  # Optional bucket only
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "required buckets" in data["error"]["message"].lower()
        assert "missing_bucket_names" in data["error"]["details"]

    def test_start_assessment_invalid_bucket_reference(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Assessment creation fails when referencing bucket from another workflow.

        VALIDATION ORDER: When user uploads to invalid bucket (from different workflow)
        AND workflow has required buckets, the error message should be "missing required buckets"
        NOT "invalid bucket reference". This is better UX because fixing the required bucket
        is the primary action the user should take.

        Example scenario:
        - Workflow has required bucket: "Test Reports"
        - User uploads to: Invalid bucket from different workflow
        - User forgot: "Test Reports" (required)

        Good UX: "Missing documents for required buckets: Test Reports"
        Bad UX: "Invalid bucket reference: bucket does not belong to this workflow"
        (User thinks they need to fix bucket reference, but they're missing required document!)
        """
        # Create two workflows
        workflow_1_id, bucket_1_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )
        workflow_2_id, bucket_2_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Try to start assessment on workflow 1 with bucket from workflow 2
        # Note: workflow 1 has REQUIRED bucket (bucket_1_id), but user uploads to invalid bucket only
        payload = {
            "workflow_id": workflow_1_id,
            "documents": [
                {
                    "bucket_id": bucket_2_id,  # Bucket from different workflow (invalid)
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

        # VALIDATION ORDER FIX: Should return "missing required buckets" error
        # because validation checks missing required buckets BEFORE invalid bucket references
        # (see apps/api/app/api/v1/endpoints/assessments.py:173-223 vs 225-266)
        error_msg = data["error"]["message"].lower()
        assert "missing documents for required buckets" in error_msg
        assert "missing_bucket_names" in data["error"]["details"]

    def test_start_assessment_workflow_not_found(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        mock_audit_service,
    ):
        """Assessment creation fails when workflow doesn't exist."""
        payload = {
            "workflow_id": "00000000-0000-0000-0000-000000000000",  # Non-existent workflow
            "documents": [
                {
                    "bucket_id": "11111111-1111-1111-1111-111111111111",
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify error response
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "workflow not found" in data["error"]["message"].lower()

    def test_start_assessment_requires_authentication(
        self,
        client: TestClient,
        org_a_process_manager_token: str,
    ):
        """Assessment creation requires authentication."""
        # Create workflow
        workflow_id, required_bucket_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        payload = {
            "workflow_id": workflow_id,
            "documents": [
                {
                    "bucket_id": required_bucket_id,
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
            ],
        }

        # Try without authentication
        response = client.post("/v1/assessments", json=payload)

        # Verify authentication required
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        # Code may be INVALID_TOKEN, JWT_ERROR, MISSING_CREDENTIALS, or similar auth error
        assert data["error"]["code"] in [
            "INVALID_TOKEN",
            "JWT_ERROR",
            "TOKEN_REQUIRED",
            "MISSING_CREDENTIALS",
        ]

    def test_start_assessment_all_roles_allowed(
        self,
        client: TestClient,
        org_a_admin_token: str,
        org_a_process_manager_token: str,
        org_a_project_handler_token: str,
        mock_audit_service,
    ):
        """All roles (admin, process_manager, project_handler) can start assessments."""
        # Create workflow
        workflow_id, required_bucket_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Define valid UUIDs for each role (hex-only characters)
        document_ids = {
            "admin": "550e8400-e29b-41d4-a716-446655440001",
            "process_manager": "550e8400-e29b-41d4-a716-446655440002",
            "project_handler": "550e8400-e29b-41d4-a716-446655440003",
        }

        # Test each role
        for role_name, token in [
            ("admin", org_a_admin_token),
            ("process_manager", org_a_process_manager_token),
            ("project_handler", org_a_project_handler_token),
        ]:
            payload = {
                "workflow_id": workflow_id,
                "documents": [
                    {
                        "bucket_id": required_bucket_id,
                        "document_id": document_ids[role_name],
                        "file_name": f"{role_name}-document.pdf",
                        "storage_key": f"https://blob.vercel-storage.com/{role_name}.pdf",
                        "file_size": 1024,
                    }
                ],
            }

            response = client.post(
                "/v1/assessments",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

            # Verify success for all roles
            assert response.status_code == 201, f"Failed for role: {role_name}"
            data = response.json()
            assert data["workflow_id"] == workflow_id
            assert data["status"] == "pending"

    def test_validation_order_missing_required_takes_precedence(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Verify that 'missing required bucket' error is shown before 'invalid bucket' error.

        VALIDATION ORDER RATIONALE (UX):
        When both errors are present, showing "missing required buckets" is better UX because:
        1. User must fix required bucket anyway (critical error)
        2. Invalid bucket reference might be incidental (user uploaded wrong file)
        3. Clearer action: "Upload Test Reports" vs "Check bucket references"

        This test ensures validation order is maintained and protects against regressions
        if validation logic is refactored in the future.
        """
        # Create two workflows
        workflow_1_id, required_bucket_1_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )
        workflow_2_id, bucket_2_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Scenario: User uploads to INVALID bucket (from workflow 2) and MISSING required bucket (from workflow 1)
        payload = {
            "workflow_id": workflow_1_id,
            "documents": [
                {
                    "bucket_id": bucket_2_id,  # INVALID: bucket from different workflow
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
                # MISSING: required_bucket_1_id has no document uploaded
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify error response prioritizes "missing required buckets"
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        error_msg = data["error"]["message"].lower()

        # Should return "missing required buckets" error (NOT "invalid bucket reference")
        assert "missing documents for required buckets" in error_msg
        assert "missing_bucket_names" in data["error"]["details"]

        # Should NOT mention invalid bucket references
        assert "invalid bucket" not in error_msg
        assert "do not belong to this workflow" not in error_msg

    def test_validation_order_only_invalid_bucket_when_no_missing_required(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Verify that 'invalid bucket reference' error is shown when all required buckets satisfied.

        VALIDATION ORDER: Invalid bucket reference error should ONLY be shown
        when all required buckets have documents. This ensures the validation
        order is correctly implemented:

        1. Check missing required buckets (lines 173-223)
        2. Check invalid bucket references (lines 225-266)
        """
        # Create two workflows
        workflow_1_id, required_bucket_1_id, optional_bucket_1_id = (
            create_test_workflow_with_buckets(client, org_a_process_manager_token)
        )
        workflow_2_id, bucket_2_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Scenario: User uploads to REQUIRED bucket (satisfied) AND INVALID bucket (from workflow 2)
        payload = {
            "workflow_id": workflow_1_id,
            "documents": [
                {
                    "bucket_id": required_bucket_1_id,  # VALID: required bucket satisfied
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "required-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/required.pdf",
                    "file_size": 1024,
                },
                {
                    "bucket_id": bucket_2_id,  # INVALID: bucket from different workflow
                    "document_id": "550e8400-e29b-41d4-a716-446655440001",
                    "file_name": "invalid-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/invalid.pdf",
                    "file_size": 2048,
                },
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify error response shows "invalid bucket reference"
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        error_msg = data["error"]["message"].lower()

        # Should return "invalid bucket reference" error (all required buckets satisfied)
        assert "invalid bucket" in error_msg or "do not belong to this workflow" in error_msg
        assert "invalid_bucket_ids" in data["error"]["details"]

        # Should NOT mention missing required buckets
        assert "missing documents for required buckets" not in error_msg


class TestAssessmentMultiTenancy:
    """Tests for multi-tenancy isolation in assessments."""

    def test_start_assessment_cross_organization_workflow_access_denied(
        self,
        client: TestClient,
        org_a_process_manager_token: str,
        org_b_admin_token: str,
        mock_audit_service,
    ):
        """User from organization B cannot start assessment on organization A's workflow."""
        # Create workflow in organization A
        workflow_id, required_bucket_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Try to start assessment from organization B
        payload = {
            "workflow_id": workflow_id,  # Org A's workflow
            "documents": [
                {
                    "bucket_id": required_bucket_id,
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_name": "test-document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/test.pdf",
                    "file_size": 1024,
                }
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_b_admin_token}"},
        )

        # Verify access denied (404 to not reveal existence)
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_start_assessment_multiple_documents_per_bucket(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Multiple documents can be assigned to the same bucket."""
        # Create workflow
        workflow_id, required_bucket_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Start assessment with multiple documents in same bucket
        payload = {
            "workflow_id": workflow_id,
            "documents": [
                {
                    "bucket_id": required_bucket_id,
                    "document_id": "550e8400-e29b-41d4-a716-446655440001",
                    "file_name": "document-1.pdf",
                    "storage_key": "https://blob.vercel-storage.com/doc1.pdf",
                    "file_size": 1024,
                },
                {
                    "bucket_id": required_bucket_id,
                    "document_id": "550e8400-e29b-41d4-a716-446655440002",
                    "file_name": "document-2.pdf",
                    "storage_key": "https://blob.vercel-storage.com/doc2.pdf",
                    "file_size": 2048,
                },
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify success
        assert response.status_code == 201
        data = response.json()
        assert data["document_count"] == 2

    def test_start_assessment_duplicate_document_rejected(
        self,
        client: TestClient,
        org_a_project_handler_token: str,
        org_a_process_manager_token: str,
        mock_audit_service,
    ):
        """Same document cannot be assigned to multiple buckets."""
        # Create workflow
        workflow_id, required_bucket_id, optional_bucket_id = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Try to assign same document to two buckets
        document_id = "550e8400-e29b-41d4-a716-446655440000"
        payload = {
            "workflow_id": workflow_id,
            "documents": [
                {
                    "bucket_id": required_bucket_id,
                    "document_id": document_id,
                    "file_name": "document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/doc.pdf",
                    "file_size": 1024,
                },
                {
                    "bucket_id": optional_bucket_id,
                    "document_id": document_id,  # Same document ID
                    "file_name": "document.pdf",
                    "storage_key": "https://blob.vercel-storage.com/doc.pdf",
                    "file_size": 1024,
                },
            ],
        }

        response = client.post(
            "/v1/assessments",
            json=payload,
            headers={"Authorization": f"Bearer {org_a_project_handler_token}"},
        )

        # Verify validation error
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "duplicate" in data["detail"][0]["msg"].lower()
