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
from datetime import datetime
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
    def _generate_storage_key(
        filename: str,
        organization_id: UUID,
        document_id: Optional[str] = None
    ) -> str:
        """
        Generate unique storage key for document.

        Format: documents/{org_id}/{timestamp}_{document_id}_{filename}

        Args:
            filename: Original filename
            organization_id: Organization ID for data isolation
            document_id: Optional document ID for additional uniqueness

        Returns:
            str: Unique storage key path
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = filename.replace(" ", "_")

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
                    "filename": filename,
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
                    "filename": filename,
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
