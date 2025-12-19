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
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:
            # Mock successful async upload
            mock_service.upload_file = AsyncMock(
                return_value="https://blob.vercel-storage.com/documents/test.pdf"
            )
            yield mock_service

    @pytest.fixture
    def mock_magic(self):
        """Mock python-magic MIME type detection."""
        with patch("app.api.v1.endpoints.documents.magic") as mock_magic:
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
        assert mock_audit_service["log_event"].called

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
        mock_magic.from_buffer.return_value = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "files": (
                    "test-document.docx",
                    docx_file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc = data[0]
        assert doc["file_name"] == "test-document.docx"
        assert (
            doc["mime_type"]
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_upload_with_bucket_id(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        test_workflow_with_bucket,
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
        workflow_id, bucket_id = test_workflow_with_bucket

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
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_bucket_id"

    def test_upload_bucket_from_different_organization(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        test_workflow_with_bucket_org_b,
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
        _, org_b_bucket_id = test_workflow_with_bucket_org_b

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
        assert mock_audit_service["log_event"].called

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
        jpg_content = b"\xff\xd8\xff JPG content"
        jpg_file = io.BytesIO(jpg_content)

        # Mock JPG MIME type
        mock_magic.from_buffer.return_value = "image/jpeg"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

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
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
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
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
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

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "UPLOAD_FAILED"

        # Verify audit log for operational monitoring
        assert mock_audit_service["log_event"].called
        failure_calls = [
            call
            for call in mock_audit_service["log_event"].call_args_list
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

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="project_handler")

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

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="project_handler")

        # Test various Unicode filenames
        unicode_filename = "文档_test_αβγ_тест.pdf"

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

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="process_manager")

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

        token = create_test_token(organization_id=TEST_ORG_A_ID, role="admin")

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
        mock_magic.from_buffer.return_value = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "files": (
                    "test-data.xlsx",
                    xlsx_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc = data[0]
        assert doc["file_name"] == "test-data.xlsx"
        assert (
            doc["mime_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Verify blob storage called
        assert mock_blob_storage.upload_file.called

        # Verify audit log created
        assert mock_audit_service["log_event"].called

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
        xls_content = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1 XLS content"
        xls_file = io.BytesIO(xls_content)

        # Mock legacy XLS MIME type
        mock_magic.from_buffer.return_value = "application/vnd.ms-excel"

        token = create_test_token(organization_id=TEST_ORG_A_ID)

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
        assert (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            in data["error"]["details"]["allowed_types"]
        )
        assert (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in data["error"]["details"]["allowed_types"]
        )
        assert "application/vnd.ms-excel" in data["error"]["details"]["allowed_types"]

        # Verify audit log for security monitoring
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
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

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "files": (
                    "data.ods",
                    ods_file,
                    "application/vnd.oasis.opendocument.spreadsheet",
                )
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.oasis.opendocument.spreadsheet" in data["error"]["message"]
        # Verify all allowed types are present in error details (PDF, DOCX, XLSX, XLS)
        assert "allowed_types" in data["error"]["details"]
        assert len(data["error"]["details"]["allowed_types"]) == 4
        assert "application/pdf" in data["error"]["details"]["allowed_types"]
        assert (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            in data["error"]["details"]["allowed_types"]
        )
        assert (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in data["error"]["details"]["allowed_types"]
        )
        assert "application/vnd.ms-excel" in data["error"]["details"]["allowed_types"]

        # Verify audit log for security monitoring
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
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

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "files": (
                    "malicious-data.xlsm",
                    xlsm_file,
                    "application/vnd.ms-excel.sheet.macroEnabled.12",
                )
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.ms-excel.sheet.macroEnabled.12" in data["error"]["message"]
        # Verify security-specific error message
        assert "macro" in data["error"]["message"].lower()

        # Verify audit log for security monitoring (macro upload attempt)
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"
        assert (
            call_args["metadata"]["detected_mime_type"]
            == "application/vnd.ms-excel.sheet.macroEnabled.12"
        )

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

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "files": (
                    "malicious-doc.docm",
                    docm_file,
                    "application/vnd.ms-word.document.macroEnabled.12",
                )
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "application/vnd.ms-word.document.macroEnabled.12" in data["error"]["message"]
        # Verify security-specific error message
        assert "macro" in data["error"]["message"].lower()

        # Verify audit log for security monitoring
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
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
        mock_magic.from_buffer.return_value = (
            "application/vnd.ms-powerpoint.presentation.macroEnabled.12"
        )

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "files": (
                    "malicious-presentation.pptm",
                    pptm_file,
                    "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
                )
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert (
            "application/vnd.ms-powerpoint.presentation.macroEnabled.12" in data["error"]["message"]
        )
        # Verify security-specific error message
        assert "macro" in data["error"]["message"].lower()

        # Verify audit log for security monitoring (macro upload attempt)
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "document.upload.failed"
        assert call_args["metadata"]["reason"] == "invalid_file_type"
        assert (
            call_args["metadata"]["detected_mime_type"]
            == "application/vnd.ms-powerpoint.presentation.macroEnabled.12"
        )


class TestBatchDocumentUpload:
    """Tests for batch document upload (Issue #91 - Guideline Compliance)."""

    @pytest.fixture
    def mock_blob_storage(self):
        """Mock Vercel Blob storage service."""
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:
            # Mock successful async upload
            mock_service.upload_file = AsyncMock(
                return_value="https://blob.vercel-storage.com/documents/test.pdf"
            )
            yield mock_service

    @pytest.fixture
    def mock_magic(self):
        """Mock python-magic MIME type detection."""
        with patch("app.api.v1.endpoints.documents.magic") as mock_magic:
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
            call
            for call in mock_audit_service["log_event"].call_args_list
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
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
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
            ("invalid.jpg", b"\xff\xd8\xff JPG content"),  # Invalid
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


class TestDocumentUploadRateLimiting:
    """Tests for rate limiting on document upload (Issue #93 - Guideline Compliance)."""

    @pytest.fixture
    def mock_blob_storage(self):
        """Mock Vercel Blob storage service."""
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:
            mock_service.upload_file = AsyncMock(
                return_value="https://blob.vercel-storage.com/documents/test.pdf"
            )
            yield mock_service

    @pytest.fixture
    def mock_magic(self):
        """Mock python-magic MIME type detection."""
        with patch("app.api.v1.endpoints.documents.magic") as mock_magic:
            mock_magic.from_buffer.return_value = "application/pdf"
            yield mock_magic

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client for rate limiting."""
        mock_redis_client = MagicMock()
        # Default: No rate limit (counter at 0)
        mock_redis_client.get.return_value = None
        mock_redis_client.pipeline.return_value = mock_redis_client
        mock_redis_client.incrby.return_value = 1
        mock_redis_client.expire.return_value = True
        mock_redis_client.execute.return_value = [1, True]
        return mock_redis_client

    @pytest.fixture
    def mock_dependencies(self, mock_redis):
        """
        Fixture to patch all rate limiting dependencies at once.

        This simplifies test code by avoiding triple-nested context managers.
        Usage: Just include 'mock_dependencies' in test parameters.
        """
        mock_db = MagicMock()

        with (
            patch("app.core.dependencies._redis_client", mock_redis),
            patch("app.core.dependencies.get_redis", return_value=iter([mock_redis])),
            patch("app.api.v1.endpoints.documents.get_db", return_value=iter([mock_db])),
        ):
            yield {
                "redis": mock_redis,
                "db": mock_db,
            }

    def test_rate_limit_enforced_at_100_uploads(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test rate limit rejection at 100th upload.

        Acceptance Criteria:
        - Returns 429 Too Many Requests on 101st upload
        - Error code RATE_LIMIT_EXCEEDED
        - Retry-After header present
        - Audit log created for security monitoring
        - Guideline compliance: product-guidelines/08-api-contracts.md:369
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 101 after increment (limit exceeded)
        # With increment-first approach: was at 100, incremented by 1 → 101 (exceeds limit)
        # First execute() is increment pipeline (INCRBY, EXPIRE) → [101, True]
        # Second execute() is rollback pipeline (DECRBY, EXPIRE, GET) → [100, True, "100"]
        mock_redis.execute.side_effect = [
            [101, True],  # Increment pipeline result
            [100, True, "100"],  # Rollback pipeline result
        ]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "100" in data["error"]["message"]
        assert "retry_after_seconds" in data["error"]["details"]
        assert data["error"]["details"]["limit"] == 100

        # Verify audit log for security monitoring
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "rate_limit.exceeded"
        assert call_args["metadata"]["limit_type"] == "upload"
        assert call_args["metadata"]["current_count"] == 100

        # Verify decrby was called to rollback the increment
        assert mock_redis.decrby.called

    def test_rate_limit_allows_99_uploads(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test rate limit allows 99th upload.

        Acceptance Criteria:
        - Returns 201 Created
        - Upload succeeds
        - Redis counter incremented
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 99 after increment (below limit)
        # With increment-first approach: was at 98, incremented by 1 → 99 (below limit)
        mock_redis.execute.return_value = [99, True]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 201

        # Verify Redis counter incremented
        assert mock_redis.pipeline.called
        assert mock_redis.incrby.called
        assert mock_redis.expire.called

    def test_rate_limit_allows_exactly_100th_upload(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test that exactly 100th upload succeeds (boundary test).

        Boundary case: Verifies off-by-one error prevention.
        The rate limit is 100 uploads per hour, so the 100th upload should succeed.
        Only the 101st upload should be rejected.

        Acceptance Criteria:
        - Returns 201 Created (upload succeeds)
        - X-RateLimit-Remaining header is "0" (at capacity but allowed)
        - Redis counter incremented to exactly 100
        - Verifies condition uses > not >= (new_count > limit, not new_count >= limit)
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 100 after increment (exactly at limit)
        # With increment-first approach: was at 99, incremented by 1 → 100 (exactly at limit)
        mock_redis.execute.return_value = [100, True]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        # Upload should succeed (100th upload is allowed, only 101st is rejected)
        assert response.status_code == 201

        # Verify rate limit headers show remaining capacity is 0
        assert response.headers["X-RateLimit-Remaining"] == "0"
        assert response.headers["X-RateLimit-Limit"] == "100"

        # Verify Redis counter incremented
        assert mock_redis.pipeline.called
        assert mock_redis.incrby.called
        assert mock_redis.expire.called

    def test_rate_limit_per_user_isolation(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test rate limit is per-user (User A limit doesn't affect User B).

        Acceptance Criteria:
        - User A at 100 uploads returns 429
        - User B at 0 uploads returns 201
        - Rate limit keys include user_id
        """
        pdf_content = b"%PDF-1.4 Test PDF"

        # Use valid UUIDs for user isolation testing
        from uuid import uuid4

        user_a_id = str(uuid4())
        user_b_id = str(uuid4())

        # User A at limit (101 after increment → exceeds limit)
        token_a = create_test_token(organization_id=TEST_ORG_A_ID, user_id=user_a_id)
        # First execute() is increment pipeline → [101, True]
        # Second execute() is rollback pipeline → [100, True, "100"]
        # Third execute() is User B's increment pipeline → [1, True]
        mock_redis.execute.side_effect = [
            [101, True],  # User A increment
            [100, True, "100"],  # User A rollback
            [1, True],  # User B increment
        ]

        response_a = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token_a}"},
            files={"files": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )

        assert response_a.status_code == 429

        # User B under limit (1 after increment → well under limit)
        token_b = create_test_token(organization_id=TEST_ORG_A_ID, user_id=user_b_id)

        response_b = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token_b}"},
            files={"files": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )

        assert response_b.status_code == 201

    def test_rate_limit_headers_present_on_success(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test X-RateLimit-* headers present on successful upload.

        Acceptance Criteria:
        - X-RateLimit-Limit header = 100
        - X-RateLimit-Remaining header shows remaining uploads
        - X-RateLimit-Reset header shows reset timestamp
        - Guideline compliance: product-guidelines/08-api-contracts.md:838-846
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 50 after increment
        mock_redis.execute.return_value = [50, True]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 201

        # Verify rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "100"

        assert "X-RateLimit-Remaining" in response.headers
        assert int(response.headers["X-RateLimit-Remaining"]) == 50  # 100 - 50 used

        assert "X-RateLimit-Reset" in response.headers
        # Reset timestamp should be a valid Unix timestamp
        reset_timestamp = int(response.headers["X-RateLimit-Reset"])
        assert reset_timestamp > 0

    def test_rate_limit_counter_increments_correctly(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test Redis counter increments on each upload.

        Acceptance Criteria:
        - Redis INCRBY called for rate limit key
        - Redis EXPIRE called with 3600 seconds TTL
        - Pipeline used for atomicity
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 11 after increment (was 10, +1)
        mock_redis.execute.return_value = [11, True]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 201

        # Verify Redis pipeline operations
        assert mock_redis.pipeline.called
        assert mock_redis.incrby.called

        # Verify EXPIRE called with 3600 seconds (1 hour)
        assert mock_redis.expire.called
        expire_call_args = mock_redis.expire.call_args
        assert expire_call_args[0][1] == 3600  # TTL in seconds

        # Verify execute called (pipeline execution)
        assert mock_redis.execute.called

    def test_rate_limit_batch_upload_counts_all_files(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test batch upload counts each file toward rate limit.

        Acceptance Criteria:
        - 5-file batch counts as 5 uploads (not 1 upload)
        - User at 96 uploads can upload 4 files (total 100)
        - User at 96 uploads cannot upload 5 files (would be 101)
        - Guideline: "20 files = 20 uploads" (not request count)
        """
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Test 1: User at 96, uploading 5 files = 101 total (should fail)
        # After increment-first: 96 + 5 = 101 (exceeds limit)
        files_data_5 = [(f"file{i}.pdf", b"%PDF-1.4 content") for i in range(1, 6)]
        file_objects_5 = [
            ("files", (name, io.BytesIO(content), "application/pdf"))
            for name, content in files_data_5
        ]

        # First execute() is increment pipeline → [101, True]
        # Second execute() is rollback pipeline → [96, True, "96"]
        # Third execute() is Test 2's increment pipeline → [100, True]
        mock_redis.execute.side_effect = [
            [101, True],  # Test 1 increment (96 + 5 = 101)
            [96, True, "96"],  # Test 1 rollback
            [100, True],  # Test 2 increment (96 + 4 = 100)
        ]

        response_fail = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files=file_objects_5,
        )

        assert response_fail.status_code == 429
        assert response_fail.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

        # Test 2: User at 96, uploading 4 files = 100 total (should succeed)
        # After increment-first: 96 + 4 = 100 (exactly at limit, allowed)
        files_data_4 = [(f"file{i}.pdf", b"%PDF-1.4 content") for i in range(1, 5)]
        file_objects_4 = [
            ("files", (name, io.BytesIO(content), "application/pdf"))
            for name, content in files_data_4
        ]

        response_success = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files=file_objects_4,
        )

        assert response_success.status_code == 201

    def test_rate_limit_redis_unavailable_allows_upload(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
    ):
        """
        Test graceful degradation when Redis unavailable.

        Acceptance Criteria:
        - Returns 201 Created (upload succeeds)
        - Warning logged about Redis unavailability
        - Fail-open for availability over strict enforcement
        - Guideline: Graceful degradation pattern
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock get_redis to return None (Redis unavailable)
        with patch("app.core.dependencies.get_redis", return_value=iter([None])):
            response = client.post(
                "/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                files={"files": ("test.pdf", pdf_file, "application/pdf")},
            )

        # Upload should succeed despite Redis unavailable (graceful degradation)
        assert response.status_code == 201

    def test_rate_limit_retry_after_header_accurate(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test Retry-After header shows seconds until rate limit resets.

        Acceptance Criteria:
        - Retry-After header present in 429 response
        - Value is seconds until next hour
        - Value between 1 and 3599 seconds
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 101 after increment (limit exceeded)
        mock_redis.execute.side_effect = [
            [101, True],  # Increment pipeline
            [100, True, "100"],  # Rollback pipeline
        ]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 429
        data = response.json()

        # Verify retry_after_seconds in error details
        assert "retry_after_seconds" in data["error"]["details"]
        retry_after = data["error"]["details"]["retry_after_seconds"]

        # Should be between 1 and 3600 seconds (up to 1 hour)
        assert 1 <= retry_after <= 3600

    def test_rate_limit_response_format_compliance(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test 429 error response follows API contract format.

        Acceptance Criteria:
        - Standard error format with code, message, details, request_id
        - Error code is RATE_LIMIT_EXCEEDED (SCREAMING_SNAKE_CASE)
        - Details include limit, current_count, retry_after_seconds, reset_time
        - Guideline compliance: CLAUDE.md error response format
        """
        pdf_content = b"%PDF-1.4 Test PDF"
        pdf_file = io.BytesIO(pdf_content)

        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock Redis to return count of 101 after increment (limit exceeded)
        mock_redis.execute.side_effect = [
            [101, True],  # Increment pipeline
            [100, True, "100"],  # Rollback pipeline
        ]

        response = client.post(
            "/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"files": ("test.pdf", pdf_file, "application/pdf")},
        )

        assert response.status_code == 429
        data = response.json()

        # Verify standard error format
        assert "error" in data
        error = data["error"]

        # Required fields
        assert "code" in error
        assert "message" in error
        assert "details" in error
        assert "request_id" in error

        # Error code format (SCREAMING_SNAKE_CASE)
        assert error["code"] == "RATE_LIMIT_EXCEEDED"
        assert error["code"].isupper()
        assert "_" in error["code"]

        # Details structure
        details = error["details"]
        assert "limit" in details
        assert "current_count" in details
        assert "retry_after_seconds" in details
        assert "reset_time" in details

        # Values correctness
        assert details["limit"] == 100
        assert details["current_count"] == 100

    def test_rate_limit_concurrent_requests_race_condition(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_magic,
        mock_audit_service,
        mock_redis,
        mock_dependencies,
    ):
        """
        Test rate limiting under concurrent load (verifies increment-first pattern prevents race conditions).

        Acceptance Criteria:
        - Concurrent requests at edge of limit are handled correctly
        - Increment-first pattern ensures no requests slip through when limit is reached
        - Redis pipeline atomicity prevents TOCTOU race conditions
        - Exactly the right number of requests succeed (no over/under enforcement)

        Scenario: User at 98 uploads, two concurrent requests each uploading 2 files
        - Old approach (check-then-increment): Both see 98, both increment to 100, both succeed (102 total - BUG)
        - New approach (increment-first): First increments to 100 (succeeds), second increments to 102 then rolls back (fails)

        This test verifies the new approach is implemented correctly.
        """
        import threading
        import time
        from collections import Counter

        pdf_content = b"%PDF-1.4 Test PDF"
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Shared counter to simulate Redis behavior
        redis_counter = {"count": 98}  # Start at 98 uploads
        redis_lock = threading.Lock()

        # Track responses
        responses = []

        def mock_redis_atomic_increment(key, amount):
            """Simulate atomic Redis INCRBY operation with lock."""
            with redis_lock:
                redis_counter["count"] += amount
                return redis_counter["count"]

        def mock_redis_decrement(key, amount):
            """Simulate Redis DECRBY operation."""
            with redis_lock:
                redis_counter["count"] -= amount
                return redis_counter["count"]

        # Configure mock to use our atomic counter
        # Track state for each pipeline call
        last_increment_result = {"value": None}

        def execute_side_effect():
            # Check if this is a rollback pipeline call
            # Rollback happens when last increment exceeded limit (> 100)
            if last_increment_result["value"] is not None and last_increment_result["value"] > 100:
                # This is a rollback pipeline (DECRBY, EXPIRE, GET)
                current_count = mock_redis_decrement("test_key", 2)
                last_increment_result["value"] = None  # Reset for next request
                return [current_count, True, str(current_count)]
            else:
                # This is an increment pipeline (INCRBY, EXPIRE)
                new_count = mock_redis_atomic_increment("test_key", 2)  # 2 files per request
                last_increment_result["value"] = new_count
                return [new_count, True]

        mock_redis.execute.side_effect = execute_side_effect

        def upload_request():
            """Simulate concurrent upload request."""
            try:
                # Upload 2 files
                files_data = [
                    ("files", (f"file1.pdf", io.BytesIO(pdf_content), "application/pdf")),
                    ("files", (f"file2.pdf", io.BytesIO(pdf_content), "application/pdf")),
                ]
                response = client.post(
                    "/v1/documents",
                    headers={"Authorization": f"Bearer {token}"},
                    files=files_data,
                )
                responses.append(response.status_code)
            except Exception as e:
                responses.append(f"error: {e}")

        # Fire two concurrent requests
        thread1 = threading.Thread(target=upload_request)
        thread2 = threading.Thread(target=upload_request)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Verify results
        status_counts = Counter(responses)

        # Expected behavior with increment-first pattern:
        # - Request 1: 98 + 2 = 100 (SUCCESS - at limit)
        # - Request 2: 100 + 2 = 102 (REJECTED - exceeds limit, rolls back to 100)
        # OR vice versa (order not guaranteed in threading)

        # Verify exactly 1 succeeded and 1 failed
        assert (
            status_counts[201] == 1
        ), f"Expected exactly 1 success (201), got {status_counts[201]}"
        assert (
            status_counts[429] == 1
        ), f"Expected exactly 1 rejection (429), got {status_counts[429]}"

        # Verify final count is 100 (one request succeeded, one rolled back)
        assert (
            redis_counter["count"] == 100
        ), f"Expected final count 100, got {redis_counter['count']}"


class TestDocumentDownload:
    """Tests for GET /v1/documents/:id endpoint (STORY-018)."""

    @pytest.fixture
    def mock_blob_storage(self):
        """Mock Vercel Blob storage service."""
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:
            # Mock get_download_url to return a signed URL
            mock_service.get_download_url = AsyncMock(
                return_value="https://blob.vercel-storage.com/documents/signed-url-123.pdf?token=abc"
            )
            yield mock_service

    @pytest.fixture
    def test_document_in_org_a(self):
        """Mock database with test document."""
        from uuid import uuid4
        from app.models import Document

        mock_db = MagicMock()
        mock_query = MagicMock()

        # Create mock document
        test_document = MagicMock(spec=Document)
        test_document.id = uuid4()
        test_document.organization_id = TEST_ORG_A_ID
        test_document.file_name = "test-document.pdf"
        test_document.file_size = 1024000
        test_document.mime_type = "application/pdf"
        test_document.storage_key = "https://blob.vercel-storage.com/documents/test.pdf"

        # Setup query mock chain
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = test_document

        return mock_db, test_document

    def test_download_success(
        self,
        client: TestClient,
        mock_blob_storage,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test successful document download.

        Acceptance Criteria:
        - Returns 307 Temporary Redirect
        - Location header contains Vercel Blob signed URL
        - Content-Type header matches document MIME type
        - Content-Disposition header contains filename
        - Audit log created
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        response = client.get(
            f"/v1/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=False,
        )

        assert response.status_code == 307
        assert "Location" in response.headers
        assert response.headers["Location"].startswith("https://blob.vercel-storage.com/")
        assert response.headers["Content-Type"] == "application/pdf"
        assert "test-document.pdf" in response.headers["Content-Disposition"]

        # Verify audit log
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "document.download.success"

    def test_download_with_page_parameter(
        self,
        client: TestClient,
        mock_blob_storage,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test download with page parameter for PDF viewing.

        Acceptance Criteria:
        - Returns 307 Temporary Redirect
        - X-PDF-Page header present with page number
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        response = client.get(
            f"/v1/documents/{test_doc.id}?page=8",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=False,
        )

        assert response.status_code == 307
        assert "X-PDF-Page" in response.headers
        assert response.headers["X-PDF-Page"] == "8"

    def test_download_not_found(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_audit_service,
    ):
        """
        Test download of non-existent document.

        Acceptance Criteria:
        - Returns 404 Not Found
        - Error code RESOURCE_NOT_FOUND
        - Audit log created for security monitoring
        """
        from uuid import uuid4

        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Document not found

        token = create_test_token(organization_id=TEST_ORG_A_ID)
        nonexistent_id = uuid4()

        response = client.get(
            f"/v1/documents/{nonexistent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

        # Verify audit log
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "document.download.failed"

    def test_download_multi_tenancy_enforcement(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_audit_service,
        test_document_in_org_b,
    ):
        """
        Test multi-tenancy: User from Org A cannot download Org B's document.

        Acceptance Criteria:
        - Returns 404 Not Found (not 403 to avoid info leakage)
        - Error code RESOURCE_NOT_FOUND
        - Audit log for security monitoring
        """
        # User from Org A tries to download Org B's document
        token = create_test_token(organization_id=TEST_ORG_A_ID)
        org_b_document = test_document_in_org_b

        response = client.get(
            f"/v1/documents/{org_b_document.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should return 404 (not 403) to avoid leaking document existence
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_download_no_authentication(
        self,
        client: TestClient,
        mock_blob_storage,
    ):
        """
        Test download without authentication token.

        Acceptance Criteria:
        - Returns 401 Unauthorized
        """
        from uuid import uuid4

        response = client.get(
            f"/v1/documents/{uuid4()}",
        )

        assert response.status_code == 401

    def test_download_blob_storage_failure(
        self,
        client: TestClient,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test handling of Vercel Blob URL generation failure.

        Acceptance Criteria:
        - Returns 500 Internal Server Error
        - Error code DOWNLOAD_URL_FAILED
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock blob storage failure
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:

            async def url_error(*args, **kwargs):
                raise Exception("Blob storage connection timeout")

            mock_service.get_download_url = AsyncMock(side_effect=url_error)

            response = client.get(
                f"/v1/documents/{test_doc.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "DOWNLOAD_URL_FAILED"


class TestDocumentDeletion:
    """Tests for DELETE /v1/documents/:id endpoint (STORY-019)."""

    @pytest.fixture
    def mock_blob_storage(self):
        """Mock Vercel Blob storage service."""
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:
            # Mock successful async delete
            mock_service.delete_file = AsyncMock(return_value=True)
            yield mock_service

    def test_delete_document_not_in_assessment_success(
        self,
        client: TestClient,
        mock_blob_storage,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test successful deletion of document not in any assessment.

        Acceptance Criteria:
        - Returns 204 No Content
        - Document deleted from Vercel Blob storage
        - Document deleted from database
        - Audit log created
        """
        from app.models import Document, AssessmentDocument

        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Setup query chain for AssessmentDocument to return None (no assessment)
        def mock_query_handler(model):
            if model == Document:
                # Return the mocked document query
                return test_document_in_org_a[0].query.return_value
            elif model == AssessmentDocument:
                # Return empty result for assessment documents
                mock_assessment_query = MagicMock()
                mock_join = MagicMock()
                mock_filter = MagicMock()
                mock_filter.first.return_value = None
                mock_join.filter.return_value = mock_filter
                mock_assessment_query.join.return_value = mock_join
                return mock_assessment_query
            else:
                return MagicMock()

        mock_db.query.side_effect = mock_query_handler

        response = client.delete(
            f"/v1/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify blob storage delete called
        assert mock_blob_storage.delete_file.called

        # Verify database delete called
        assert mock_db.delete.called
        assert mock_db.commit.called

        # Verify audit log
        assert mock_audit_service["log_event"].called
        success_logs = [
            call
            for call in mock_audit_service["log_event"].call_args_list
            if call[1].get("action") == "document.delete.success"
        ]
        assert len(success_logs) == 1

    def test_delete_document_in_pending_assessment_allowed(
        self,
        client: TestClient,
        mock_blob_storage,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test deletion of document in pending assessment is allowed.

        Acceptance Criteria:
        - Returns 204 No Content
        - Safe to delete documents in pending assessments
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock assessment_documents query to return document with pending status
        from app.models import Assessment

        mock_assessment_doc = MagicMock()
        mock_assessment_doc.assessment = MagicMock(spec=Assessment)
        mock_assessment_doc.assessment.status = "pending"

        # First query is for document, second is for assessment_documents
        mock_assessment_query = MagicMock()
        mock_assessment_query.first.return_value = None  # No completed/processing assessment
        mock_db.query.side_effect = [test_document_in_org_a[0].query.return_value, mock_assessment_query]

        response = client.delete(
            f"/v1/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

    def test_delete_document_in_completed_assessment_conflict(
        self,
        client: TestClient,
        mock_blob_storage,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test rejection of deleting document in completed assessment.

        Acceptance Criteria:
        - Returns 409 Conflict
        - Error code DOCUMENT_IN_USE
        - Error message indicates assessment status
        - Audit log created
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock assessment_documents query to return document in completed assessment
        from uuid import uuid4
        from app.models import Assessment, AssessmentDocument

        mock_assessment = MagicMock(spec=Assessment)
        mock_assessment.status = "completed"
        mock_assessment.id = uuid4()

        mock_assessment_doc = MagicMock(spec=AssessmentDocument)
        mock_assessment_doc.assessment_id = mock_assessment.id
        mock_assessment_doc.assessment = mock_assessment
        mock_assessment_doc.storage_key = test_doc.storage_key

        # Setup queries
        mock_assessment_query = MagicMock()
        mock_assessment_query.first.return_value = mock_assessment_doc
        mock_db.query.side_effect = [
            test_document_in_org_a[0].query.return_value,  # Document query
            mock_assessment_query,  # AssessmentDocument query
        ]

        response = client.delete(
            f"/v1/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "DOCUMENT_IN_USE"
        assert "completed" in data["error"]["message"]
        assert data["error"]["details"]["assessment_status"] == "completed"

        # Verify NO blob delete or database delete
        assert not mock_blob_storage.delete_file.called
        assert not mock_db.delete.called

        # Verify audit log for failed deletion
        assert mock_audit_service["log_event"].called
        fail_logs = [
            call
            for call in mock_audit_service["log_event"].call_args_list
            if call[1].get("action") == "document.delete.failed"
        ]
        assert len(fail_logs) == 1

    def test_delete_document_in_processing_assessment_conflict(
        self,
        client: TestClient,
        mock_blob_storage,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test rejection of deleting document in processing assessment.

        Acceptance Criteria:
        - Returns 409 Conflict
        - Error code DOCUMENT_IN_USE
        - Error message indicates assessment is processing
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock assessment_documents query to return document in processing assessment
        from uuid import uuid4
        from app.models import Assessment, AssessmentDocument

        mock_assessment = MagicMock(spec=Assessment)
        mock_assessment.status = "processing"
        mock_assessment.id = uuid4()

        mock_assessment_doc = MagicMock(spec=AssessmentDocument)
        mock_assessment_doc.assessment_id = mock_assessment.id
        mock_assessment_doc.assessment = mock_assessment
        mock_assessment_doc.storage_key = test_doc.storage_key

        # Setup queries
        mock_assessment_query = MagicMock()
        mock_assessment_query.first.return_value = mock_assessment_doc
        mock_db.query.side_effect = [test_document_in_org_a[0].query.return_value, mock_assessment_query]

        response = client.delete(
            f"/v1/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "DOCUMENT_IN_USE"
        assert "processing" in data["error"]["message"]

    def test_delete_nonexistent_document_not_found(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_audit_service,
    ):
        """
        Test deletion of non-existent document.

        Acceptance Criteria:
        - Returns 404 Not Found
        - Error code RESOURCE_NOT_FOUND
        - Audit log created for security monitoring
        """
        from uuid import uuid4

        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Document not found

        token = create_test_token(organization_id=TEST_ORG_A_ID)
        nonexistent_id = uuid4()

        response = client.delete(
            f"/v1/documents/{nonexistent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

        # Verify audit log
        assert mock_audit_service["log_event"].called
        call_args = mock_audit_service["log_event"].call_args[1]
        assert call_args["action"] == "document.delete.failed"

    def test_delete_document_different_org_not_found(
        self,
        client: TestClient,
        mock_blob_storage,
        mock_audit_service,
    ):
        """
        Test multi-tenancy: User from Org A cannot delete Org B's document.

        Acceptance Criteria:
        - Returns 404 Not Found (not 403 to avoid info leakage)
        - Error code RESOURCE_NOT_FOUND
        - Audit log for security monitoring
        """
        from uuid import uuid4

        mock_db = MagicMock()
        mock_query = MagicMock()

        # Setup query to return no document (multi-tenancy filter blocks it)
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Filtered out

        # User from Org A tries to delete Org B's document
        token = create_test_token(organization_id=TEST_ORG_A_ID)
        org_b_doc_id = uuid4()

        response = client.delete(
            f"/v1/documents/{org_b_doc_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should return 404 (not 403) to avoid leaking document existence
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_delete_blob_failure_still_deletes_db(
        self,
        client: TestClient,
        test_document_in_org_a,
        mock_audit_service,
    ):
        """
        Test graceful degradation when blob deletion fails.

        Acceptance Criteria:
        - Returns 204 No Content
        - Database record deleted even if blob fails
        - Error logged but operation continues
        - Audit log shows blob_deleted: false
        """
        test_doc = test_document_in_org_a
        token = create_test_token(organization_id=TEST_ORG_A_ID)

        # Mock blob storage failure
        with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock_service:

            async def delete_error(*args, **kwargs):
                raise Exception("Blob storage connection timeout")

            mock_service.delete_file = AsyncMock(side_effect=delete_error)

            # Mock assessment query to return None
            mock_assessment_query = MagicMock()
            mock_assessment_query.first.return_value = None
            mock_db.query.side_effect = [
                test_document_in_org_a[0].query.return_value,
                mock_assessment_query,
            ]

            response = client.delete(
                f"/v1/documents/{test_doc.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        # Should still succeed despite blob deletion failure
        assert response.status_code == 204

        # Database delete should still be called
        assert mock_db.delete.called
        assert mock_db.commit.called

        # Verify audit log shows blob deletion failed
        success_logs = [
            call
            for call in mock_audit_service["log_event"].call_args_list
            if call[1].get("action") == "document.delete.success"
        ]
        assert len(success_logs) == 1
        assert success_logs[0][1]["metadata"]["blob_deleted"] == False

    def test_delete_unauthenticated_returns_401(
        self,
        client: TestClient,
        mock_blob_storage,
    ):
        """
        Test deletion without authentication token.

        Acceptance Criteria:
        - Returns 401 Unauthorized
        - No deletion performed
        """
        from uuid import uuid4

        response = client.delete(
            f"/v1/documents/{uuid4()}",
        )

        assert response.status_code == 401

        # Verify NO blob delete called
        assert not mock_blob_storage.delete_file.called
