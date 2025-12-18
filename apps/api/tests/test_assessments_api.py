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

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.models.enums import UserRole
from tests.conftest import TEST_ORG_A_ID, TEST_ORG_B_ID


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
        """Assessment creation fails when referencing bucket from another workflow."""
        # Create two workflows
        workflow_1_id, bucket_1_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )
        workflow_2_id, bucket_2_id, _ = create_test_workflow_with_buckets(
            client, org_a_process_manager_token
        )

        # Try to start assessment on workflow 1 with bucket from workflow 2
        payload = {
            "workflow_id": workflow_1_id,
            "documents": [
                {
                    "bucket_id": bucket_2_id,  # Bucket from different workflow
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
        assert "invalid bucket references" in data["error"]["message"].lower()

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
        assert data["error"]["code"] == "INVALID_TOKEN"

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
                        "document_id": f"550e8400-e29b-41d4-a716-44665544{role_name[:4]}",
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
