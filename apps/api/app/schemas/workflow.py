"""
Pydantic schemas for Workflow API endpoints.

This module defines request/response schemas for workflow creation and management.
Supports nested bucket and criteria creation in a single transaction.

Journey Step 1: Process Manager creates validation workflows with document buckets
and validation criteria.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class BucketCreate(BaseModel):
    """
    Schema for creating a document bucket within a workflow.

    Buckets categorize documents (e.g., "Technical Documentation", "Test Reports").
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Bucket name (e.g., 'Technical Documentation')",
        examples=["Technical Documentation", "Test Reports", "Risk Assessment"],
    )
    required: bool = Field(
        default=True,
        description="Whether documents in this bucket are required for assessment",
    )
    order_index: int = Field(
        default=0, ge=0, description="Display order (0-indexed, for UI sorting)"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate bucket name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Bucket name cannot be empty or whitespace")
        return v.strip()


class CriteriaCreate(BaseModel):
    """
    Schema for creating validation criteria within a workflow.

    Criteria define validation rules that AI will check (e.g., "All documents must be signed").
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Criteria name (brief description of validation rule)",
        examples=[
            "All documents must be signed",
            "Test report must include pass/fail summary",
            "Risk matrix must be complete",
        ],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description of validation rule for AI context",
    )
    applies_to_bucket_ids: List[int] = Field(
        default_factory=list,
        description="Bucket indexes this criteria applies to (empty = applies to all buckets)",
        examples=[[0, 1], [2], []],
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate criteria name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Criteria name cannot be empty or whitespace")
        return v.strip()


class WorkflowCreate(BaseModel):
    """
    Schema for creating a workflow with nested buckets and criteria.

    This schema supports creating the complete workflow structure in a single request:
    - Workflow metadata (name, description)
    - Document buckets (categories for uploaded documents)
    - Validation criteria (rules AI will check)

    Journey Step 1: Process Manager defines validation workflow in one atomic operation.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Workflow name (e.g., 'Medical Device - Class II')",
        examples=["Medical Device - Class II", "Machinery Directive 2006/42/EC"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional workflow description",
    )
    buckets: List[BucketCreate] = Field(
        ...,
        min_length=1,
        description="Document buckets (at least one required)",
    )
    criteria: List[CriteriaCreate] = Field(
        ...,
        min_length=1,
        description="Validation criteria (at least one required)",
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate workflow name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode='after')
    def validate_unique_bucket_names(self) -> 'WorkflowCreate':
        """
        Validate that bucket names are unique within the workflow (case-insensitive).

        This prevents UX confusion where multiple buckets have the same name.
        """
        bucket_names_lower = [bucket.name.lower() for bucket in self.buckets]
        unique_names = set(bucket_names_lower)

        if len(bucket_names_lower) != len(unique_names):
            # Find duplicates for better error message
            seen = set()
            duplicates = []
            for name in bucket_names_lower:
                if name in seen and name not in duplicates:
                    duplicates.append(name)
                seen.add(name)

            raise ValueError(
                f"Bucket names must be unique (case-insensitive). "
                f"Duplicate names found: {', '.join(duplicates)}"
            )

        return self

    @field_validator("criteria")
    @classmethod
    def validate_bucket_references(cls, v: List[CriteriaCreate], values) -> List[CriteriaCreate]:
        """
        Validate that criteria bucket references are valid indexes.

        Criteria can reference buckets by index in the buckets array.
        This validates that all referenced indexes exist.
        """
        # Get buckets from values (Pydantic v2 uses info.data)
        buckets = values.data.get("buckets", [])
        bucket_count = len(buckets) if buckets else 0

        for criteria in v:
            for bucket_index in criteria.applies_to_bucket_ids:
                if bucket_index < 0 or bucket_index >= bucket_count:
                    raise ValueError(
                        f"Criteria '{criteria.name}' references invalid bucket index {bucket_index}. "
                        f"Valid range: 0-{bucket_count - 1}"
                    )

        return v


class BucketResponse(BaseModel):
    """
    Schema for bucket in API responses.
    """

    id: UUID
    name: str
    required: bool
    order_index: int

    class Config:
        from_attributes = True  # Pydantic v2: enable ORM mode


class CriteriaResponse(BaseModel):
    """
    Schema for criteria in API responses.
    """

    id: UUID
    name: str
    description: Optional[str]
    applies_to_bucket_ids: Optional[List[UUID]] = None  # None = applies to all buckets
    order_index: int

    class Config:
        from_attributes = True


class WorkflowResponse(BaseModel):
    """
    Schema for workflow in API responses.

    Includes full workflow details with nested buckets and criteria.
    """

    id: UUID
    name: str
    description: Optional[str]
    organization_id: UUID
    created_by: UUID
    is_active: bool
    archived: bool = Field(default=False, description="Whether workflow is archived")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    created_at: datetime
    updated_at: datetime
    buckets: List[BucketResponse]
    criteria: List[CriteriaResponse]

    class Config:
        from_attributes = True


class WorkflowListItem(BaseModel):
    """
    Schema for workflow in list responses (lighter than full response).
    """

    id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    archived: bool = Field(default=False, description="Whether workflow is archived")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    created_at: datetime
    buckets_count: int
    criteria_count: int

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """
    Schema for pagination metadata in list responses.

    Provides information about the current page, total items, and total pages.
    """

    total_count: int = Field(
        ...,
        ge=0,
        description="Total number of items across all pages"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)"
    )
    per_page: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages"
    )
    has_next_page: bool = Field(
        ...,
        description="Whether there is a next page available"
    )
    has_prev_page: bool = Field(
        ...,
        description="Whether there is a previous page available"
    )


class WorkflowListResponse(BaseModel):
    """
    Schema for paginated workflow list responses.

    Includes both workflow data and pagination metadata for client-side pagination UI.
    """

    workflows: List[WorkflowListItem] = Field(
        ...,
        description="List of workflows for the current page"
    )
    pagination: PaginationMeta = Field(
        ...,
        description="Pagination metadata"
    )


class BucketUpdate(BaseModel):
    """
    Schema for updating a document bucket within a workflow.

    Supports add/update/delete operations via optional ID:
    - id=None: Create new bucket
    - id=UUID: Update existing bucket
    - Omit from request: Delete bucket
    """

    id: Optional[UUID] = Field(
        default=None,
        description="Bucket UUID (None for new buckets, UUID for existing buckets)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Bucket name (e.g., 'Technical Documentation')",
        examples=["Technical Documentation", "Test Reports", "Risk Assessment"],
    )
    required: bool = Field(
        default=True,
        description="Whether documents in this bucket are required for assessment",
    )
    order_index: int = Field(
        default=0, ge=0, description="Display order (0-indexed, for UI sorting)"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate bucket name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Bucket name cannot be empty or whitespace")
        return v.strip()


class CriteriaUpdate(BaseModel):
    """
    Schema for updating validation criteria within a workflow.

    Supports add/update/delete operations via optional ID:
    - id=None: Create new criteria
    - id=UUID: Update existing criteria
    - Omit from request: Delete criteria
    """

    id: Optional[UUID] = Field(
        default=None,
        description="Criteria UUID (None for new criteria, UUID for existing criteria)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Criteria name (brief description of validation rule)",
        examples=[
            "All documents must be signed",
            "Test report must include pass/fail summary",
            "Risk matrix must be complete",
        ],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description of validation rule for AI context",
    )
    applies_to_bucket_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Bucket UUIDs this criteria applies to (None = applies to all buckets)",
        examples=[],
    )
    order_index: int = Field(
        default=0, ge=0, description="Display order (0-indexed, for UI sorting)"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate criteria name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Criteria name cannot be empty or whitespace")
        return v.strip()


class WorkflowUpdate(BaseModel):
    """
    Schema for updating a workflow with nested buckets and criteria.

    This schema supports differential updates:
    - Update workflow metadata (name, description)
    - Add new buckets (id=None)
    - Update existing buckets (id=UUID)
    - Delete buckets (omit from request)
    - Add new criteria (id=None)
    - Update existing criteria (id=UUID)
    - Delete criteria (omit from request)

    All changes occur in a single database transaction with rollback on error.

    Journey Step 1: Process Manager refines validation workflow based on feedback.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Workflow name (e.g., 'Medical Device - Class II')",
        examples=["Medical Device - Class II", "Machinery Directive 2006/42/EC"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional workflow description",
    )
    buckets: List[BucketUpdate] = Field(
        ...,
        min_length=1,
        description="Document buckets (at least one required)",
    )
    criteria: List[CriteriaUpdate] = Field(
        ...,
        min_length=1,
        description="Validation criteria (at least one required)",
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate workflow name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode='after')
    def validate_unique_bucket_names(self) -> 'WorkflowUpdate':
        """
        Validate that bucket names are unique within the workflow (case-insensitive).

        This prevents UX confusion where multiple buckets have the same name.
        """
        bucket_names_lower = [bucket.name.lower() for bucket in self.buckets]
        unique_names = set(bucket_names_lower)

        if len(bucket_names_lower) != len(unique_names):
            # Find duplicates for better error message
            seen = set()
            duplicates = []
            for name in bucket_names_lower:
                if name in seen and name not in duplicates:
                    duplicates.append(name)
                seen.add(name)

            raise ValueError(
                f"Bucket names must be unique (case-insensitive). "
                f"Duplicate names found: {', '.join(duplicates)}"
            )

        return self

    # Note: Bucket reference validation removed as per PR review #82
    # The validator only checked references within the request payload, which incorrectly
    # rejected valid scenarios where criteria reference existing buckets not being updated.
    # Database-level validation (IntegrityError) handles truly invalid references.
