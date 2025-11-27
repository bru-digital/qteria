"""
Vercel Blob storage service for document uploads.

This module provides file upload functionality to Vercel Blob storage with
encryption at rest and unique key generation.

Usage:
    from app.services.blob_storage import BlobStorageService

    # Upload file
    storage_url = await BlobStorageService.upload_file(
        file_content=pdf_bytes,
        filename="technical-spec.pdf",
        content_type="application/pdf",
        organization_id="org_123"
    )
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class BlobStorageService:
    """
    Service for uploading and managing documents in Vercel Blob storage.

    All methods are static for ease of use across the application.
    Files are stored with unique keys to prevent collisions and include
    organization context for potential data isolation.
    """

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to remove problematic characters.

        Removes:
        - Path traversal characters (../, ..\\, /)
        - Null bytes
        - Control characters
        - Special characters that could cause issues

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename safe for storage
        """
        # Get just the filename (remove any path components)
        safe_name = Path(filename).name

        # Remove null bytes
        safe_name = safe_name.replace("\0", "")

        # Remove control characters (ASCII 0-31 and 127)
        safe_name = re.sub(r'[\x00-\x1f\x7f]', '', safe_name)

        # Replace problematic characters with underscore
        # Keep only alphanumeric, dash, underscore, dot
        safe_name = re.sub(r'[^\w\-.]', '_', safe_name)

        # Remove leading/trailing dots and underscores
        safe_name = safe_name.strip('._')

        # Ensure filename is not empty after sanitization
        if not safe_name:
            safe_name = "unnamed_file"

        return safe_name

    @staticmethod
    def _generate_storage_key(
        filename: str,
        organization_id: UUID,
        document_id: Optional[str] = None
    ) -> str:
        """
        Generate unique storage key for document.

        Format: documents/{org_id}/{timestamp}_{document_id}_{filename}

        Args:
            filename: Original filename (will be sanitized)
            organization_id: Organization ID for data isolation
            document_id: Optional document ID for additional uniqueness

        Returns:
            str: Unique storage key path
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = BlobStorageService._sanitize_filename(filename)

        if document_id:
            return f"documents/{organization_id}/{timestamp}_{document_id}_{safe_filename}"
        return f"documents/{organization_id}/{timestamp}_{safe_filename}"

    @staticmethod
    async def upload_file(
        file_content: bytes,
        filename: str,
        content_type: str,
        organization_id: UUID,
        document_id: Optional[str] = None
    ) -> str:
        """
        Upload file to Vercel Blob storage.

        Args:
            file_content: Binary file content
            filename: Original filename
            content_type: MIME type (e.g., "application/pdf")
            organization_id: Organization ID for data isolation
            document_id: Optional document ID for tracking

        Returns:
            str: Blob storage URL

        Raises:
            Exception: If upload fails (network, authentication, etc.)
        """
        try:
            # Import vercel_blob here to avoid issues if package not installed
            from vercel_blob import put
        except ImportError:
            logger.error("vercel-blob package not installed")
            raise ImportError(
                "vercel-blob package required. Install with: pip install vercel-blob"
            )

        blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")
        if not blob_token:
            logger.error("BLOB_READ_WRITE_TOKEN environment variable not set")
            raise ValueError(
                "BLOB_READ_WRITE_TOKEN environment variable is required"
            )

        # Generate unique storage key
        storage_key = BlobStorageService._generate_storage_key(
            filename=filename,
            organization_id=organization_id,
            document_id=document_id
        )

        try:
            # Upload to Vercel Blob with encryption and private access
            response = await put(
                storage_key,
                file_content,
                {
                    "access": "private",  # Requires authentication
                    "contentType": content_type,
                    "addRandomSuffix": True,  # Additional collision prevention
                },
                token=blob_token
            )

            logger.info(
                "File uploaded to Vercel Blob",
                extra={
                    "file_name": filename,
                    "storage_key": storage_key,
                    "organization_id": str(organization_id),
                    "file_size": len(file_content),
                    "content_type": content_type,
                }
            )

            return response["url"]

        except Exception as e:
            logger.error(
                "Failed to upload file to Vercel Blob",
                extra={
                    "file_name": filename,
                    "organization_id": str(organization_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise Exception(f"Failed to upload file to Vercel Blob: {str(e)}")

    @staticmethod
    async def delete_file(storage_url: str) -> bool:
        """
        Delete file from Vercel Blob storage.

        Args:
            storage_url: Full URL of the blob to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            from vercel_blob import delete
        except ImportError:
            logger.error("vercel-blob package not installed")
            raise ImportError(
                "vercel-blob package required. Install with: pip install vercel-blob"
            )

        blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")
        if not blob_token:
            logger.error("BLOB_READ_WRITE_TOKEN environment variable not set")
            raise ValueError(
                "BLOB_READ_WRITE_TOKEN environment variable is required"
            )

        try:
            await delete(storage_url, token=blob_token)
            logger.info(
                "File deleted from Vercel Blob",
                extra={"storage_url": storage_url}
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to delete file from Vercel Blob",
                extra={"storage_url": storage_url, "error": str(e)},
                exc_info=True
            )
            return False
