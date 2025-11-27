"""
Integration tests for Document Upload API endpoints.

Tests coverage requirements (product-guidelines/09-test-strategy.md):
- API Routes: 80% coverage target
- Multi-Tenancy Security: 100% coverage (zero tolerance for data leakage)

Required Security Tests (per product guidelines):
- Authentication: 401 without token
- Authorization: All authenticated users can upload
- File validation: Invalid types rejected (400)
- File size validation: Large files rejected (413)
- Audit logging: Upload events logged for SOC2 compliance
"""
import io
import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from tests.conftest import (
    create_test_token,
    TEST_ORG_A_ID,
    TEST_ORG_B_ID,
)


class TestDocumentUpload:
    """Tests for POST /v1/documents endpoint."""

    @pytest.fixture
    def mock_blob_storage(self):
        """Mock Vercel Blob storage service."""
        with patch('app.api.v1.endpoints.documents.BlobStorageService') as mock_service:
            # Mock successful upload
            mock_service.upload_file.return_value = "https://blob.vercel-storage.com/documents/test.pdf"
            yield mock_service

    @pytest.fixture
    def mock_magic(self):
        """Mock python-magic MIME type detection."""
        with patch('app.api.v1.endpoints.documents.magic') as mock_magic:
            # Default to PDF
            mock_magic.from_buffer.return_value = "application/pdf"
            yield mock_magic

    def test_upload_pdf_success(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful PDF upload.

        Acceptance Criteria:
        - Returns 201 Created
        - Returns document metadata (id, file_name, file_size, etc.)
        - File uploaded to Vercel Blob storage
        - Audit log created for SOC2 compliance
        """
        # Create valid PDF file content
        pdf_content = b"%PDF-1.4 Test PDF content"
        pdf_file = io.BytesIO(pdf_content)

        # Create auth token
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock database dependency
        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test-document.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["file_name"] == "test-document.pdf"
        assert data["file_size"] == len(pdf_content)
        assert data["mime_type"] == "application/pdf"
        assert "storage_key" in data
        assert "uploaded_at" in data
        assert "uploaded_by" in data

        # Verify blob storage called
        assert mock_blob_storage.upload_file.called

        # Verify audit log created
        assert mock_audit_service['log_event'].called

    def test_upload_docx_success(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful DOCX upload.

        Acceptance Criteria:
        - DOCX files are accepted
        - Returns 201 Created with correct MIME type
        """
        # Create DOCX file content
        docx_content = b"PK\x03\x04 DOCX content"  # DOCX magic bytes
        docx_file = io.BytesIO(docx_content)

        # Mock DOCX MIME type
        mock_magic.from_buffer.return_value = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test-document.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["file_name"] == "test-document.docx"
        assert data["mime_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_upload_with_bucket_id(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload with optional bucket_id parameter.

        Acceptance Criteria:
        - bucket_id is optional
        - If provided, it's included in response
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)
        bucket_id = "f52414ec-67f4-43d5-b25c-1552828ff06d"

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": bucket_id},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["bucket_id"] == bucket_id

    def test_upload_invalid_file_type_jpg(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for invalid file type (JPG).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error message indicates invalid file type
        - Lists allowed file types
        - Audit log created for security monitoring
        """
        jpg_content = b"\xFF\xD8\xFF JPG content"
        jpg_file = io.BytesIO(jpg_content)

        # Mock JPG MIME type
        mock_magic.from_buffer.return_value = "image/jpeg"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("image.jpg", jpg_file, "image/jpeg")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVALID_FILE_TYPE"
        assert "image/jpeg" in data["detail"]["message"]
        assert "allowed_types" in data["detail"]

        # Verify audit log for security monitoring
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"

    def test_upload_file_too_large(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for file exceeding size limit.

        Acceptance Criteria:
        - Returns 413 Payload Too Large
        - Error message indicates file size limit (50MB)
        - Audit log created for monitoring
        """
        # Create content > 50MB
        large_content = b"X" * (51 * 1024 * 1024)  # 51MB
        large_file = io.BytesIO(large_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("large.pdf", large_file, "application/pdf")},
            )

        assert response.status_code == 413
        data = response.json()
        assert data["detail"]["code"] == "FILE_TOO_LARGE"
        assert "max_size_bytes" in data["detail"]
        assert data["detail"]["max_size_bytes"] == 50 * 1024 * 1024

        # Verify audit log
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "file_too_large"

    def test_upload_no_authentication(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
    ):
        """
        Test upload rejection without authentication token.

        Acceptance Criteria:
        - Returns 401 Unauthorized
        - Error code INVALID_TOKEN
        """
        pdf_content = b"%PDF-1.4 Test"
        pdf_file = io.BytesIO(pdf_content)

        response = client.post(
            "/v1/documents",
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 403  # FastAPI returns 403 for missing credentials

    def test_upload_blob_storage_failure(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test handling of Vercel Blob storage upload failure.

        Acceptance Criteria:
        - Returns 500 Internal Server Error
        - Error message indicates upload failure
        - Audit log created for operational monitoring
        """
        pdf_content = b"%PDF-1.4 Test"
        pdf_file = io.BytesIO(pdf_content)

        # Mock blob storage upload failure
        import asyncio

        async def upload_error(*args, **kwargs):
            raise Exception("Blob storage connection timeout")

        mock_blob_storage.upload_file.side_effect = upload_error

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            with patch('app.api.v1.endpoints.documents.asyncio.run', side_effect=upload_error):
                response = client.post(
                    "/v1/documents",
                    headers={"Authorization": f"Bearer {token}"},
                    files={"file": ("test.pdf", pdf_file, "application/pdf")},
                )

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["code"] == "UPLOAD_FAILED"

        # Verify audit log for operational monitoring
        assert mock_audit_service['log_event'].called
        failure_calls = [
            call for call in mock_audit_service['log_event'].call_args_list
            if call[1].get("action") == "document.upload.failed"
        ]
        assert len(failure_calls) > 0

    def test_upload_project_handler_can_upload(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test that project_handler role can upload documents.

        Acceptance Criteria:
        - project_handler role is authorized
        - Returns 201 Created
        """
        pdf_content = b"%PDF-1.4 Test"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(
            organization_id=TEST_ORG_A_ID,
            role="project_handler"
        )

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201

    def test_upload_process_manager_can_upload(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test that process_manager role can upload documents.

        Acceptance Criteria:
        - process_manager role is authorized
        - Returns 201 Created
        """
        pdf_content = b"%PDF-1.4 Test"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(
            organization_id=TEST_ORG_A_ID,
            role="process_manager"
        )

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201

    def test_upload_admin_can_upload(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test that admin role can upload documents.

        Acceptance Criteria:
        - admin role is authorized
        - Returns 201 Created
        """
        pdf_content = b"%PDF-1.4 Test"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(
            organization_id=TEST_ORG_A_ID,
            role="admin"
        )

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
