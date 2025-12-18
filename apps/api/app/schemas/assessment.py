"""
Pydantic schemas for Assessment API endpoints.

This module defines request/response schemas for starting and managing assessments.
Assessments represent the AI validation process where uploaded documents are checked
against workflow criteria.

Journey Step 2→3: Project Handler starts assessment → AI validates documents.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DocumentMapping(BaseModel):
    """
    Schema for mapping uploaded documents to workflow buckets.

    Each document must be assigned to a specific bucket for validation.
    Multiple documents can be assigned to the same bucket.

    The document details (filename, storage_key, size) come from the DocumentResponse
    returned by the document upload API.
    """

    bucket_id: UUID = Field(..., description="Bucket UUID to assign document to")
    document_id: UUID = Field(..., description="Document UUID from document upload API")
    file_name: str = Field(..., description="Original filename from upload response")
    storage_key: str = Field(..., description="Vercel Blob storage URL from upload response")
    file_size: int = Field(..., gt=0, description="File size in bytes from upload response")


class AssessmentCreate(BaseModel):
    """
    Schema for creating/starting a new assessment.

    This triggers the background AI validation process:
    1. Validates all required buckets have documents
    2. Creates assessment record with status "pending"
    3. Creates assessment_documents join records
    4. Enqueues Celery background job for AI validation (STORY-023)

    Journey Step 2: Project Handler uploads documents and starts assessment.
    """

    workflow_id: UUID = Field(
        ...,
        description="Workflow UUID to run assessment against",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    documents: List[DocumentMapping] = Field(
        ...,
        min_length=1,
        description="Document-to-bucket mappings (at least one document required)",
        examples=[
            [
                {
                    "bucket_id": "660e8400-e29b-41d4-a716-446655440001",
                    "document_id": "770e8400-e29b-41d4-a716-446655440002",
                    "file_name": "technical-spec.pdf",
                    "storage_key": "https://blob.vercel-storage.com/...",
                    "file_size": 2048576,
                },
                {
                    "bucket_id": "660e8400-e29b-41d4-a716-446655440003",
                    "document_id": "880e8400-e29b-41d4-a716-446655440004",
                    "file_name": "test-report.pdf",
                    "storage_key": "https://blob.vercel-storage.com/...",
                    "file_size": 1536000,
                },
            ]
        ],
    )

    @field_validator("documents")
    @classmethod
    def validate_unique_documents(cls, v: List[DocumentMapping]) -> List[DocumentMapping]:
        """
        Validate that each document is assigned to only one bucket.

        A document can only be in one bucket per assessment to avoid
        duplicate validation.
        """
        document_ids = [doc.document_id for doc in v]
        unique_document_ids = set(document_ids)

        if len(document_ids) != len(unique_document_ids):
            # Find duplicates for better error message
            seen = set()
            duplicates = []
            for doc_id in document_ids:
                if doc_id in seen and doc_id not in duplicates:
                    duplicates.append(str(doc_id))
                seen.add(doc_id)

            raise ValueError(
                f"Each document can only be assigned to one bucket. "
                f"Duplicate document IDs found: {', '.join(duplicates)}"
            )

        return v


class AssessmentResponse(BaseModel):
    """
    Schema for assessment in API responses.

    Returns assessment details after creation and during status polling.
    """

    id: UUID = Field(..., description="Assessment unique identifier")
    workflow_id: UUID = Field(..., description="Workflow being assessed")
    status: str = Field(
        ..., description="Processing status: pending, processing, completed, failed"
    )
    started_at: datetime = Field(..., description="Assessment creation timestamp (UTC)")
    estimated_completion_at: datetime = Field(..., description="Estimated completion time (UTC)")
    document_count: int = Field(..., ge=0, description="Number of documents in this assessment")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "990e8400-e29b-41d4-a716-446655440005",
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "started_at": "2024-11-17T14:45:00Z",
                "estimated_completion_at": "2024-11-17T14:55:00Z",
                "document_count": 3,
            }
        }
