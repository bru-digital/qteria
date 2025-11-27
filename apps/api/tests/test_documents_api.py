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
from unittest.mock import patch, MagicMock, AsyncMock

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
            # Mock successful async upload
            mock_service.upload_file = AsyncMock(return_value="https://blob.vercel-storage.com/documents/test.pdf")
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

        # Mock database session to return a valid bucket when queried
        mock_db_session = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.id = bucket_id

        # Setup the query mock chain: db.query(Bucket).join(Workflow).filter(...).first()
        mock_query = mock_db_session.query.return_value
        mock_join = mock_query.join.return_value
        mock_filter = mock_join.filter.return_value
        mock_filter.first.return_value = mock_bucket

        # Mock get_db to yield our mock session
        def mock_get_db():
            yield mock_db_session

        # Override the FastAPI dependency
        from app.core.dependencies import get_db
        from app.main import app

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": bucket_id},
            )

            assert response.status_code == 201
            data = response.json()
            assert data["bucket_id"] == bucket_id
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_upload_invalid_bucket_id(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for non-existent bucket_id.

        Acceptance Criteria:
        - Returns 404 Not Found
        - Error message indicates bucket not found or access denied
        - Audit log created for security monitoring (potential cross-org access attempt)
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)
        # Use a valid UUID that doesn't exist in the database
        invalid_bucket_id = "00000000-0000-0000-0000-000000000000"

        # Mock database to return None for the bucket query with join
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_join = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # Bucket not found
        mock_join.filter.return_value = mock_filter
        mock_query.join.return_value = mock_join
        mock_db.query.return_value = mock_query

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([mock_db])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": invalid_bucket_id},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["code"] == "BUCKET_NOT_FOUND"
        assert "access denied" in data["detail"]["message"].lower()

        # Verify audit log for security monitoring
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_bucket_id"

    def test_upload_bucket_from_different_organization(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for bucket_id belonging to different organization (multi-tenancy check).

        Acceptance Criteria:
        - Returns 404 Not Found (not 403, to avoid leaking bucket existence)
        - Audit log created for security monitoring
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        # User from ORG_A trying to access bucket from ORG_B
        token = create_test_token(organization_id=TEST_ORG_A_ID)
        org_b_bucket_id = "f52414ec-67f4-43d5-b25c-1552828ff06d"

        # Mock database to return None (because organization_id filter excludes it)
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_join = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # Bucket not found due to org filter
        mock_join.filter.return_value = mock_filter
        mock_query.join.return_value = mock_join
        mock_db.query.return_value = mock_query

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([mock_db])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": org_b_bucket_id},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["code"] == "BUCKET_NOT_FOUND"

        # Verify audit log
        assert mock_audit_service['log_event'].called

    def test_upload_invalid_uuid_bucket_id(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for bucket_id with invalid UUID format.

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code INVALID_BUCKET_ID
        - Clear error message about UUID format
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)
        # Use an invalid UUID format
        invalid_bucket_id = "not-a-valid-uuid"

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": invalid_bucket_id},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "INVALID_BUCKET_ID"
        assert "uuid" in data["detail"]["message"].lower()

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

    def test_upload_empty_file(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for empty file (0 bytes).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error message indicates file is empty
        - Audit log created for monitoring
        """
        # Create empty file content
        empty_content = b""
        empty_file = io.BytesIO(empty_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("empty.pdf", empty_file, "application/pdf")},
            )

        # Empty files should return 400 Bad Request with EMPTY_FILE code
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "EMPTY_FILE"
        assert "empty" in data["detail"]["message"].lower()

    def test_upload_no_authentication(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
    ):
        """
        Test upload rejection without authentication token.

        Acceptance Criteria:
        - Returns 403 Forbidden (FastAPI behavior for missing credentials)
        - No authenticated user in context
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
        async def upload_error(*args, **kwargs):
            raise Exception("Blob storage connection timeout")

        mock_blob_storage.upload_file.side_effect = upload_error

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
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

    def test_upload_unicode_filename(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful upload with Unicode characters in filename (internationalization).

        Acceptance Criteria:
        - Unicode filenames are accepted
        - Returns 201 Created
        - Filename is preserved correctly in response
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(
            organization_id=TEST_ORG_A_ID,
            role="project_handler"
        )

        # Test various Unicode filenames
        unicode_filename = "文档_test_αβγ_тест.pdf"

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (unicode_filename, pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["file_name"] == unicode_filename

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

    def test_upload_mime_detection_fails(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test handling when python-magic fails to detect MIME type.

        Acceptance Criteria:
        - Returns 500 Internal Server Error
        - Error code is MIME_DETECTION_FAILED
        - Security: Fails closed instead of trusting client-provided MIME type
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        # Mock MIME detection failure
        mock_magic.from_buffer.side_effect = Exception("libmagic error")

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["code"] == "MIME_DETECTION_FAILED"
        assert "unable to validate file type" in data["detail"]["message"].lower()
