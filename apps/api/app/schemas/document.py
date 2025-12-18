"""
Pydantic schemas for document upload API.

This module defines request/response models for document upload endpoints,
including validation rules and error responses.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """
    Response schema for uploaded document.

    Returns document metadata after successful upload to Vercel Blob storage.
    """

    id: UUID = Field(..., description="Unique document identifier")
    file_name: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type (e.g., application/pdf)")
    storage_key: str = Field(..., description="Storage URL/key for retrieval")
    bucket_id: Optional[UUID] = Field(
        None, description="Associated bucket ID (if specified during upload)"
    )
    uploaded_at: datetime = Field(..., description="Upload timestamp (UTC)")
    uploaded_by: UUID = Field(..., description="User ID who uploaded the document")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "file_name": "technical-spec.pdf",
                "file_size": 2048576,
                "mime_type": "application/pdf",
                "storage_key": "https://blob.vercel-storage.com/documents/...",
                "bucket_id": "660e8400-e29b-41d4-a716-446655440001",
                "uploaded_at": "2024-11-17T14:30:00Z",
                "uploaded_by": "770e8400-e29b-41d4-a716-446655440002",
            }
        }


class DocumentListResponse(BaseModel):
    """Response schema for listing documents (future endpoint)."""

    data: list[DocumentResponse]
    total: int
    page: int = 1
    limit: int = 20


class DocumentErrorResponse(BaseModel):
    """Error response for document upload failures."""

    error: dict[str, Any] = Field(
        ...,
        description="Error details",
        json_schema_extra={
            "example": {
                "code": "INVALID_FILE_TYPE",
                "message": "Invalid file type: image/jpeg. Only PDF, DOCX, and XLSX allowed.",
                "details": {
                    "detected_mime_type": "image/jpeg",
                    "allowed_types": [
                        "application/pdf",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.ms-excel",
                    ],
                },
            }
        },
    )


# Validation constants
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
    "application/vnd.ms-excel",  # XLS (legacy)
}

# SECURITY: Explicitly reject macro-enabled files to prevent malicious code execution
# These file types can contain embedded macros that pose security risks
REJECTED_MIME_TYPES = {
    "application/vnd.ms-excel.sheet.macroEnabled.12",  # XLSM (macro-enabled Excel)
    "application/vnd.ms-word.document.macroEnabled.12",  # DOCM (macro-enabled Word)
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12",  # PPTM (macro-enabled PowerPoint)
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB


def validate_file_type(mime_type: str) -> bool:
    """
    Validate if MIME type is allowed.

    SECURITY: Explicitly rejects macro-enabled files (XLSM, DOCM) to prevent
    malicious code execution. Even if not in allowed list, explicit rejection
    provides clear security intent and better error messages.

    Args:
        mime_type: MIME type to validate

    Returns:
        bool: True if allowed, False otherwise
    """
    # Explicitly reject dangerous file types first (security defense-in-depth)
    if mime_type in REJECTED_MIME_TYPES:
        return False

    return mime_type in ALLOWED_MIME_TYPES


def validate_file_size(file_size: int) -> bool:
    """
    Validate if file size is within limits.

    Args:
        file_size: File size in bytes

    Returns:
        bool: True if within limits, False otherwise
    """
    return 0 < file_size <= MAX_FILE_SIZE_BYTES
