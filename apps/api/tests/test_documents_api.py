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
                files={"files": ("test-document.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()

        # Response should be a list (even for single file upload)
        assert isinstance(data, list)
        assert len(data) == 1

        # Verify first document structure
        doc = data[0]
        assert "id" in doc
        assert doc["file_name"] == "test-document.pdf"
        assert doc["file_size"] == len(pdf_content)
        assert doc["mime_type"] == "application/pdf"
        assert "storage_key" in doc
        assert "uploaded_at" in doc
        assert "uploaded_by" in doc

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
                files={"files": ("test-document.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc = data[0]
        assert doc["file_name"] == "test-document.docx"
        assert doc["mime_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": bucket_id},
            )

            assert response.status_code == 201
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            doc = data[0]
            assert doc["bucket_id"] == bucket_id
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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": invalid_bucket_id},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "BUCKET_NOT_FOUND"
        assert "access denied" in data["error"]["message"].lower()

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": org_b_bucket_id},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "BUCKET_NOT_FOUND"

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
                data={"bucket_id": invalid_bucket_id},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_BUCKET_ID"
        assert "uuid" in data["error"]["message"].lower()

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
                files={"files": ("image.jpg", jpg_file, "image/jpeg")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "image/jpeg" in data["error"]["message"]
        assert "allowed_types" in data["error"]["details"]
        # Verify XLSX is included in allowed types (API contract compliance)
        allowed_types = data["error"]["details"]["allowed_types"]
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in allowed_types

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
                files={"files": ("large.pdf", large_file, "application/pdf")},
            )

        assert response.status_code == 413
        data = response.json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"
        assert "max_size_bytes" in data["error"]["details"]
        assert data["error"]["details"]["max_size_bytes"] == 50 * 1024 * 1024

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
                files={"files": ("empty.pdf", empty_file, "application/pdf")},
            )

        # Empty files should return 400 Bad Request with EMPTY_FILE code
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "EMPTY_FILE"
        assert "empty" in data["error"]["message"].lower()

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
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        # Should return 401 for missing authentication (not 403)
        # 401 = missing/invalid auth, 403 = valid auth but insufficient permissions
        assert response.status_code == 401

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "UPLOAD_FAILED"

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

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
                files={"files": (unicode_filename, pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc = data[0]
        assert doc["file_name"] == unicode_filename

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

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
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "MIME_DETECTION_FAILED"
        assert "unable to validate file type" in data["error"]["message"].lower()

    def test_upload_xlsx_success(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful XLSX upload (Issue #90 - Add XLSX file type support).

        Acceptance Criteria:
        - XLSX files are accepted
        - Returns 201 Created with correct MIME type
        - Verifies guideline compliance (product-guidelines/08-api-contracts.md:363)
        """
        # Create XLSX file content with magic bytes
        xlsx_content = b"PK\x03\x04 XLSX content"
        xlsx_file = io.BytesIO(xlsx_content)

        # Mock XLSX MIME type (modern Office Open XML format)
        mock_magic.from_buffer.return_value = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("test-data.xlsx", xlsx_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc = data[0]
        assert doc["file_name"] == "test-data.xlsx"
        assert doc["mime_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # Verify blob storage called
        assert mock_blob_storage.upload_file.called

        # Verify audit log created
        assert mock_audit_service['log_event'].called

    def test_upload_xls_success(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful XLS upload (Issue #90 - Legacy Excel format support).

        Acceptance Criteria:
        - Legacy XLS files are accepted for backward compatibility
        - Returns 201 Created with correct MIME type
        """
        # Create XLS file content
        xls_content = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1 XLS content"
        xls_file = io.BytesIO(xls_content)

        # Mock legacy XLS MIME type
        mock_magic.from_buffer.return_value = "application/vnd.ms-excel"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("legacy-data.xls", xls_file, "application/vnd.ms-excel")},
            )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc = data[0]
        assert doc["file_name"] == "legacy-data.xls"
        assert doc["mime_type"] == "application/vnd.ms-excel"

    def test_upload_csv_rejected(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for CSV files (Issue #90 - CSV not in allowed types).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code INVALID_FILE_TYPE
        - CSV files are rejected despite being spreadsheet format
        - Rationale: CSV is structured data format, not document format for AI validation
        """
        csv_content = b"Column1,Column2,Column3\nValue1,Value2,Value3"
        csv_file = io.BytesIO(csv_content)

        # Mock CSV MIME type
        mock_magic.from_buffer.return_value = "text/csv"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("data.csv", csv_file, "text/csv")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "text/csv" in data["error"]["message"]
        assert "allowed_types" in data["error"]["details"]
        # Verify all allowed types are present (PDF, DOCX, XLSX, XLS)
        assert len(data["error"]["details"]["allowed_types"]) == 4
        assert "application/pdf" in data["error"]["details"]["allowed_types"]
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in data["error"]["details"]["allowed_types"]
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in data["error"]["details"]["allowed_types"]
        assert "application/vnd.ms-excel" in data["error"]["details"]["allowed_types"]

        # Verify audit log for security monitoring
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"

    def test_upload_ods_rejected(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for ODS files (Issue #90 - OpenDocument Spreadsheet not supported).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code INVALID_FILE_TYPE
        - ODS files are rejected (not in guideline requirement)
        """
        ods_content = b"PK\x03\x04 ODS content"
        ods_file = io.BytesIO(ods_content)

        # Mock ODS MIME type
        mock_magic.from_buffer.return_value = "application/vnd.oasis.opendocument.spreadsheet"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("data.ods", ods_file, "application/vnd.oasis.opendocument.spreadsheet")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.oasis.opendocument.spreadsheet" in data["error"]["message"]
        # Verify all allowed types are present in error details (PDF, DOCX, XLSX, XLS)
        assert "allowed_types" in data["error"]["details"]
        assert len(data["error"]["details"]["allowed_types"]) == 4
        assert "application/pdf" in data["error"]["details"]["allowed_types"]
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in data["error"]["details"]["allowed_types"]
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in data["error"]["details"]["allowed_types"]
        assert "application/vnd.ms-excel" in data["error"]["details"]["allowed_types"]

        # Verify audit log for security monitoring
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"

    def test_upload_xlsm_rejected_security(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for XLSM files (SECURITY - macro-enabled Excel).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code INVALID_FILE_TYPE
        - XLSM files are explicitly rejected due to macro security risks
        - Security-specific error message about macro-enabled files
        - Audit log created for security monitoring

        Rationale: XLSM files can contain embedded macros that execute arbitrary code,
        posing a significant security risk in document validation workflows.
        """
        # Create XLSM file content (macro-enabled Excel)
        xlsm_content = b"PK\x03\x04 XLSM content with macros"
        xlsm_file = io.BytesIO(xlsm_content)

        # Mock XLSM MIME type (macro-enabled Excel 2007+)
        mock_magic.from_buffer.return_value = "application/vnd.ms-excel.sheet.macroEnabled.12"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("malicious-data.xlsm", xlsm_file, "application/vnd.ms-excel.sheet.macroEnabled.12")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.ms-excel.sheet.macroEnabled.12" in data["error"]["message"]
        # Verify security-specific error message
        assert "macro" in data["error"]["message"].lower()

        # Verify audit log for security monitoring (macro upload attempt)
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"
        assert call_args["metadata"]["detected_mime_type"] == "application/vnd.ms-excel.sheet.macroEnabled.12"

    def test_upload_docm_rejected_security(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for DOCM files (SECURITY - macro-enabled Word).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code INVALID_FILE_TYPE
        - DOCM files are explicitly rejected due to macro security risks
        - Security-specific error message about macro-enabled files
        """
        # Create DOCM file content (macro-enabled Word)
        docm_content = b"PK\x03\x04 DOCM content with macros"
        docm_file = io.BytesIO(docm_content)

        # Mock DOCM MIME type (macro-enabled Word 2007+)
        mock_magic.from_buffer.return_value = "application/vnd.ms-word.document.macroEnabled.12"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("malicious-doc.docm", docm_file, "application/vnd.ms-word.document.macroEnabled.12")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.ms-word.document.macroEnabled.12" in data["error"]["message"]
        # Verify security-specific error message
        assert "macro" in data["error"]["message"].lower()

        # Verify audit log for security monitoring
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"

    def test_upload_pptm_rejected_security(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for PPTM files (SECURITY - macro-enabled PowerPoint).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code INVALID_FILE_TYPE
        - PPTM files are explicitly rejected due to macro security risks
        - Security-specific error message about macro-enabled files
        - Audit log created for security monitoring

        Rationale:
        PPTM files can contain VBA macros that could execute malicious code.
        While PowerPoint presentations are not currently accepted in any form,
        explicitly rejecting PPTM ensures defense-in-depth security posture
        and provides clear error messages if acceptance criteria change.
        """
        # Create PPTM file content (macro-enabled PowerPoint)
        pptm_content = b"PK\x03\x04 PPTM content with macros"
        pptm_file = io.BytesIO(pptm_content)

        # Mock PPTM MIME type (macro-enabled PowerPoint 2007+)
        mock_magic.from_buffer.return_value = "application/vnd.ms-powerpoint.presentation.macroEnabled.12"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("malicious-presentation.pptm", pptm_file, "application/vnd.ms-powerpoint.presentation.macroEnabled.12")},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.ms-powerpoint.presentation.macroEnabled.12" in data["error"]["message"]
        # Verify security-specific error message
        assert "macro" in data["error"]["message"].lower()

        # Verify audit log for security monitoring (macro upload attempt)
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"
        assert call_args["metadata"]["detected_mime_type"] == "application/vnd.ms-powerpoint.presentation.macroEnabled.12"


class TestBatchDocumentUpload:
    """Tests for batch document upload (Issue #91 - Guideline Compliance)."""

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

    def test_upload_single_file_backwards_compatibility(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test single file upload still works (backwards compatibility).

        Acceptance Criteria:
        - Returns 201 Created
        - Returns list with single DocumentResponse
        - Existing frontend code continues to work
        """
        pdf_content = b"%PDF-1.4 Test PDF content"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("test-document.pdf", pdf_file, "application/pdf")},
            )

        assert response.status_code == 201
        data = response.json()

        # Response should be a list (even for single file)
        assert isinstance(data, list)
        assert len(data) == 1

        # Verify first document
        doc = data[0]
        assert doc["file_name"] == "test-document.pdf"
        assert doc["file_size"] == len(pdf_content)
        assert doc["mime_type"] == "application/pdf"

    def test_upload_multiple_files_success(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful upload of multiple files (2-5 files).

        Acceptance Criteria:
        - Returns 201 Created
        - Returns list of DocumentResponse objects
        - All files validated and uploaded
        - Audit logs created for each file
        """
        # Create 5 test files
        files_data = [
            ("file1.pdf", b"%PDF-1.4 File 1"),
            ("file2.pdf", b"%PDF-1.4 File 2"),
            ("file3.pdf", b"%PDF-1.4 File 3"),
            ("file4.docx", b"PK\x03\x04 DOCX"),
            ("file5.xlsx", b"PK\x03\x04 XLSX"),
        ]

        # Mock different MIME types
        mime_types = [
            "application/pdf",
            "application/pdf",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        mock_magic.from_buffer.side_effect = mime_types

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Create file objects
        file_objects = [
            ("files", (name, io.BytesIO(content), "application/octet-stream"))
            for name, content in files_data
        ]

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=file_objects,
            )

        assert response.status_code == 201
        data = response.json()

        # Verify response is list with 5 items
        assert isinstance(data, list)
        assert len(data) == 5

        # Verify all filenames present
        returned_filenames = {doc["file_name"] for doc in data}
        expected_filenames = {name for name, _ in files_data}
        assert returned_filenames == expected_filenames

        # Verify blob storage called 5 times
        assert mock_blob_storage.upload_file.call_count == 5

        # Verify audit logs created for each file
        success_logs = [
            call for call in mock_audit_service['log_event'].call_args_list
            if call[1].get("action") == "document.upload.success"
        ]
        assert len(success_logs) == 5

    def test_upload_twenty_files_max_allowed(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload with maximum allowed files (20).

        Acceptance Criteria:
        - Returns 201 Created
        - All 20 files uploaded successfully
        - Guideline compliance: product-guidelines/08-api-contracts.md:364
        """
        # Create 20 test files
        files_data = [(f"file{i}.pdf", b"%PDF-1.4 content") for i in range(1, 21)]

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        file_objects = [
            ("files", (name, io.BytesIO(content), "application/pdf"))
            for name, content in files_data
        ]

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=file_objects,
            )

        assert response.status_code == 201
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 20

        # Verify blob storage called 20 times
        assert mock_blob_storage.upload_file.call_count == 20

    def test_upload_twentyone_files_rejected(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test upload rejection for exceeding max files (21 files).

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error code BATCH_SIZE_EXCEEDED
        - No files uploaded (atomic failure)
        - Audit log created
        """
        # Create 21 test files
        files_data = [(f"file{i}.pdf", b"%PDF-1.4 content") for i in range(1, 22)]

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        file_objects = [
            ("files", (name, io.BytesIO(content), "application/pdf"))
            for name, content in files_data
        ]

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=file_objects,
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "BATCH_SIZE_EXCEEDED"
        assert "21" in data["error"]["message"]
        assert "20" in data["error"]["message"]
        assert data["error"]["details"]["file_count"] == 21
        assert data["error"]["details"]["max_files"] == 20

        # Verify NO files uploaded
        assert not mock_blob_storage.upload_file.called

        # Verify audit log
        assert mock_audit_service['log_event'].called
        call_args = mock_audit_service['log_event'].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "batch_size_exceeded"

    def test_upload_batch_with_one_invalid_file_atomic_failure(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test atomic failure when one file in batch is invalid.

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Error indicates which file failed
        - NO files uploaded (atomic operation)
        - Validates ALL before uploading ANY
        """
        # Create 3 files: 2 valid PDFs, 1 invalid JPG
        files_data = [
            ("file1.pdf", b"%PDF-1.4 File 1"),
            ("invalid.jpg", b"\xFF\xD8\xFF JPG content"),  # Invalid
            ("file3.pdf", b"%PDF-1.4 File 3"),
        ]

        # Mock MIME types
        mime_types = [
            "application/pdf",
            "image/jpeg",  # Invalid type
            "application/pdf",
        ]
        mock_magic.from_buffer.side_effect = mime_types

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        file_objects = [
            ("files", (name, io.BytesIO(content), "application/octet-stream"))
            for name, content in files_data
        ]

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=file_objects,
            )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "invalid.jpg" in data["error"]["message"]
        assert "image/jpeg" in data["error"]["message"]

        # Verify NO files uploaded (atomic failure)
        assert not mock_blob_storage.upload_file.called

    def test_upload_batch_with_one_oversized_file_atomic_failure(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test atomic failure when one file exceeds size limit.

        Acceptance Criteria:
        - Returns 413 Payload Too Large
        - Error indicates which file is too large
        - NO files uploaded (atomic operation)
        """
        # Create 3 files: 2 valid, 1 too large
        files_data = [
            ("file1.pdf", b"%PDF-1.4 content"),
            ("huge.pdf", b"X" * (51 * 1024 * 1024)),  # 51MB - too large
            ("file3.pdf", b"%PDF-1.4 content"),
        ]

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        file_objects = [
            ("files", (name, io.BytesIO(content), "application/pdf"))
            for name, content in files_data
        ]

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=file_objects,
            )

        assert response.status_code == 413
        data = response.json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"
        assert "huge.pdf" in data["error"]["message"]
        assert data["error"]["details"]["file_name"] == "huge.pdf"

        # Verify NO files uploaded
        assert not mock_blob_storage.upload_file.called

    def test_upload_batch_with_mixed_file_types(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test successful upload with mixed valid file types (PDF, DOCX, XLSX).

        Acceptance Criteria:
        - Returns 201 Created
        - All file types accepted
        - Response preserves correct MIME types
        """
        files_data = [
            ("report.pdf", b"%PDF-1.4 Report"),
            ("document.docx", b"PK\x03\x04 DOCX"),
            ("data.xlsx", b"PK\x03\x04 XLSX"),
        ]

        mime_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        mock_magic.from_buffer.side_effect = mime_types

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        file_objects = [
            ("files", (name, io.BytesIO(content), "application/octet-stream"))
            for name, content in files_data
        ]

        with patch('app.api.v1.endpoints.documents.get_db', return_value=iter([MagicMock()])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=file_objects,
            )

        assert response.status_code == 201
        data = response.json()

        assert len(data) == 3

        # Verify each file type
        mime_types_returned = {doc["mime_type"] for doc in data}
        assert mime_types_returned == set(mime_types)
