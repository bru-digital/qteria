"""
Unit tests for BlobStorageService.

Tests cover:
- Filename sanitization (SECURITY-CRITICAL: path traversal, null bytes, control chars)
- Storage key generation (uniqueness, organization isolation)
- Upload/delete edge cases
"""
import os
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID, uuid4

import pytest

from app.services.blob_storage import BlobStorageService


# ============================================================================
# SECURITY-CRITICAL: Filename Sanitization Tests
# ============================================================================


class TestFilenameSanitization:
    """Test filename sanitization to prevent path traversal and injection attacks."""

    def test_sanitize_filename_path_traversal_unix(self):
        """Test sanitization of Unix path traversal attempts."""
        malicious = "../../etc/passwd"
        sanitized = BlobStorageService._sanitize_filename(malicious)

        # Should remove path components and special chars
        # Path.name extracts only the final component
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert sanitized == "passwd"

    def test_sanitize_filename_path_traversal_windows(self):
        """Test sanitization of Windows path traversal attempts."""
        malicious = "..\\..\\windows\\system32\\config\\sam"
        sanitized = BlobStorageService._sanitize_filename(malicious)

        # Should remove path components and backslashes
        # On Unix systems, backslashes are not path separators, so Path.name
        # returns the whole string, then backslashes are replaced with underscores
        assert ".." not in sanitized
        assert "\\" not in sanitized
        # On Unix/macOS: backslashes are treated as filename chars, then sanitized to underscores
        assert sanitized == "windows_system32_config_sam"

    def test_sanitize_filename_null_byte_injection(self):
        """Test sanitization removes null bytes (classic path traversal technique)."""
        # Null byte can trick path parsers: "test.pdf\0.exe" might pass as PDF
        malicious = "test\x00.pdf.exe"
        sanitized = BlobStorageService._sanitize_filename(malicious)

        # Should remove null bytes
        assert "\x00" not in sanitized
        assert sanitized == "test.pdf.exe"

    def test_sanitize_filename_control_characters(self):
        """Test sanitization removes ASCII control characters (0x00-0x1f, 0x7f)."""
        # Control chars can cause issues in file systems and terminals
        malicious = "test\x01\x02\x03\x1f\x7ffile.pdf"
        sanitized = BlobStorageService._sanitize_filename(malicious)

        # Should remove all control characters
        assert sanitized == "testfile.pdf"

    def test_sanitize_filename_unicode_normalization(self):
        """Test sanitization handles Unicode characters correctly."""
        # Unicode can have multiple representations (NFC, NFD, etc.)
        unicode_name = "café_résumé.pdf"
        sanitized = BlobStorageService._sanitize_filename(unicode_name)

        # Should preserve safe Unicode characters or replace with underscore
        # (Exact behavior depends on \w regex - typically allows Unicode letters)
        assert sanitized.endswith(".pdf")
        assert len(sanitized) > 0

    def test_sanitize_filename_empty_string(self):
        """Test sanitization returns fallback for empty or whitespace-only strings."""
        # Empty filename after sanitization should use fallback
        assert BlobStorageService._sanitize_filename("") == "unnamed_file"
        assert BlobStorageService._sanitize_filename("   ") == "unnamed_file"
        assert BlobStorageService._sanitize_filename("...") == "unnamed_file"
        assert BlobStorageService._sanitize_filename("___") == "unnamed_file"

    def test_sanitize_filename_special_characters(self):
        """Test sanitization of special characters that could cause issues."""
        malicious = "test!@#$%^&*()+=[]{}|;:'\",<>?.pdf"
        sanitized = BlobStorageService._sanitize_filename(malicious)

        # Should replace special chars with underscores, keep dots and filename
        assert sanitized.endswith(".pdf")
        assert all(c.isalnum() or c in "._-" for c in sanitized)

    def test_sanitize_filename_leading_trailing_dots(self):
        """Test sanitization removes leading/trailing dots (hidden files, path issues)."""
        assert BlobStorageService._sanitize_filename(".hidden.pdf") == "hidden.pdf"
        assert BlobStorageService._sanitize_filename("file.pdf.") == "file.pdf"
        assert BlobStorageService._sanitize_filename("..file..pdf..") == "file..pdf"

    def test_sanitize_filename_preserves_safe_filenames(self):
        """Test that safe filenames are preserved unchanged."""
        safe_names = [
            "report.pdf",
            "technical-spec-v2.pdf",
            "Test_Report_2024.pdf",
            "file123.pdf",
        ]
        for safe_name in safe_names:
            sanitized = BlobStorageService._sanitize_filename(safe_name)
            assert sanitized == safe_name


# ============================================================================
# Storage Key Generation Tests
# ============================================================================


class TestStorageKeyGeneration:
    """Test storage key generation for uniqueness and organization isolation."""

    def test_generate_storage_key_format(self):
        """Test storage key follows expected format."""
        org_id = uuid4()
        filename = "report.pdf"

        storage_key = BlobStorageService._generate_storage_key(
            filename=filename,
            organization_id=org_id
        )

        # Format: documents/{org_id}/{timestamp}_{filename}
        assert storage_key.startswith(f"documents/{org_id}/")
        assert storage_key.endswith("_report.pdf")
        assert "_" in storage_key  # timestamp separator

    def test_generate_storage_key_with_document_id(self):
        """Test storage key includes document_id when provided."""
        org_id = uuid4()
        doc_id = "doc_123"
        filename = "report.pdf"

        storage_key = BlobStorageService._generate_storage_key(
            filename=filename,
            organization_id=org_id,
            document_id=doc_id
        )

        # Format: documents/{org_id}/{timestamp}_{document_id}_{filename}
        assert storage_key.startswith(f"documents/{org_id}/")
        assert f"_{doc_id}_" in storage_key
        assert storage_key.endswith("_report.pdf")

    def test_generate_storage_key_organization_isolation(self):
        """Test that different organizations get different storage paths."""
        org1 = uuid4()
        org2 = uuid4()
        filename = "report.pdf"

        key1 = BlobStorageService._generate_storage_key(filename, org1)
        key2 = BlobStorageService._generate_storage_key(filename, org2)

        # Different organizations should have different paths
        assert str(org1) in key1
        assert str(org2) in key2
        assert key1 != key2

    def test_generate_storage_key_uniqueness_over_time(self):
        """Test that keys generated at different times are unique."""
        org_id = uuid4()
        filename = "report.pdf"

        # Generate two keys with slight time difference
        key1 = BlobStorageService._generate_storage_key(filename, org_id)
        # Ensure timestamp changes (microsecond precision)
        import time
        time.sleep(0.001)  # 1ms delay
        key2 = BlobStorageService._generate_storage_key(filename, org_id)

        # Keys should be different due to timestamp
        assert key1 != key2

    def test_generate_storage_key_sanitizes_filename(self):
        """Test that storage key sanitizes malicious filenames."""
        org_id = uuid4()
        malicious = "../../etc/passwd"

        storage_key = BlobStorageService._generate_storage_key(
            filename=malicious,
            organization_id=org_id
        )

        # Should not contain path traversal
        # Path.name extracts only the final component
        assert ".." not in storage_key
        assert "passwd" in storage_key
        assert "etc" not in storage_key  # Path components should be removed


# ============================================================================
# Upload File Tests
# ============================================================================


class TestUploadFile:
    """Test file upload functionality and edge cases."""

    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        """Test successful file upload to Vercel Blob."""
        org_id = uuid4()
        file_content = b"PDF content here"
        filename = "report.pdf"
        content_type = "application/pdf"

        mock_response = {"url": "https://blob.vercel-storage.com/test-abc123.pdf"}

        with patch("app.services.blob_storage.put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                url = await BlobStorageService.upload_file(
                    file_content=file_content,
                    filename=filename,
                    content_type=content_type,
                    organization_id=org_id
                )

                assert url == mock_response["url"]

                # Verify put was called with correct parameters
                mock_put.assert_called_once()
                args, kwargs = mock_put.call_args

                # First arg is storage key
                assert args[0].startswith(f"documents/{org_id}/")
                # Second arg is file content
                assert args[1] == file_content
                # Third arg is options dict
                assert kwargs["token"] == "test_token"
                assert args[2]["access"] == "private"
                assert args[2]["contentType"] == content_type
                assert args[2]["addRandomSuffix"] is True

    @pytest.mark.asyncio
    async def test_upload_file_missing_token(self):
        """Test upload fails gracefully when BLOB_READ_WRITE_TOKEN is missing."""
        org_id = uuid4()

        with patch.dict(os.environ, {}, clear=True):  # Clear env vars
            with pytest.raises(ValueError) as exc_info:
                await BlobStorageService.upload_file(
                    file_content=b"content",
                    filename="test.pdf",
                    content_type="application/pdf",
                    organization_id=org_id
                )

            assert "BLOB_READ_WRITE_TOKEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_invalid_response(self):
        """Test upload fails when Vercel Blob returns invalid response (no URL)."""
        org_id = uuid4()

        # Mock response without 'url' field
        mock_response = {"error": "Something went wrong"}

        with patch("app.services.blob_storage.put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                with pytest.raises(Exception) as exc_info:
                    await BlobStorageService.upload_file(
                        file_content=b"content",
                        filename="test.pdf",
                        content_type="application/pdf",
                        organization_id=org_id
                    )

                assert "Invalid response" in str(exc_info.value)
                assert "missing URL" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_network_error(self):
        """Test upload handles network/API errors gracefully."""
        org_id = uuid4()

        with patch("app.services.blob_storage.put", new_callable=AsyncMock) as mock_put:
            mock_put.side_effect = Exception("Network error")

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                with pytest.raises(Exception) as exc_info:
                    await BlobStorageService.upload_file(
                        file_content=b"content",
                        filename="test.pdf",
                        content_type="application/pdf",
                        organization_id=org_id
                    )

                assert "Failed to upload file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_with_document_id(self):
        """Test upload includes document_id in storage key when provided."""
        org_id = uuid4()
        doc_id = "doc_abc123"

        mock_response = {"url": "https://blob.vercel-storage.com/test.pdf"}

        with patch("app.services.blob_storage.put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                await BlobStorageService.upload_file(
                    file_content=b"content",
                    filename="test.pdf",
                    content_type="application/pdf",
                    organization_id=org_id,
                    document_id=doc_id
                )

                # Check storage key includes document_id
                args, _ = mock_put.call_args
                storage_key = args[0]
                assert f"_{doc_id}_" in storage_key


# ============================================================================
# Delete File Tests
# ============================================================================


class TestDeleteFile:
    """Test file deletion functionality and edge cases."""

    @pytest.mark.asyncio
    async def test_delete_file_success(self):
        """Test successful file deletion from Vercel Blob."""
        storage_url = "https://blob.vercel-storage.com/test-abc123.pdf"

        with patch("app.services.blob_storage.delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = None  # delete returns nothing on success

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                result = await BlobStorageService.delete_file(storage_url)

                assert result is True
                mock_delete.assert_called_once_with(storage_url, token="test_token")

    @pytest.mark.asyncio
    async def test_delete_file_missing_token(self):
        """Test delete fails gracefully when BLOB_READ_WRITE_TOKEN is missing."""
        storage_url = "https://blob.vercel-storage.com/test.pdf"

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                await BlobStorageService.delete_file(storage_url)

            assert "BLOB_READ_WRITE_TOKEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_file_api_error(self):
        """Test delete returns False on API errors (instead of raising)."""
        storage_url = "https://blob.vercel-storage.com/test.pdf"

        with patch("app.services.blob_storage.delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.side_effect = Exception("Not found")

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                result = await BlobStorageService.delete_file(storage_url)

                # Should return False instead of raising
                assert result is False

    @pytest.mark.asyncio
    async def test_delete_file_invalid_url(self):
        """Test delete handles invalid URLs gracefully."""
        invalid_url = "not-a-valid-url"

        with patch("app.services.blob_storage.delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.side_effect = Exception("Invalid URL")

            with patch.dict(os.environ, {"BLOB_READ_WRITE_TOKEN": "test_token"}):
                result = await BlobStorageService.delete_file(invalid_url)

                assert result is False
