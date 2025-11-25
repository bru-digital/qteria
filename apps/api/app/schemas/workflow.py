"""
Pydantic schemas for Workflow API endpoints.

These schemas define the request and response models for workflow-related operations.
Following the API contracts defined in product-guidelines/08-api-contracts.md.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BucketDetail(BaseModel):
    """
    Bucket details in workflow response.

    Buckets represent document categories (e.g., "Test Reports", "Risk Assessment").
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique bucket identifier")
    name: str = Field(..., description="Bucket name (e.g., 'Technical Documentation')")
    required: bool = Field(..., description="Whether documents in this bucket are required")
    order_index: int = Field(..., description="Display order (0-based)")


class CriteriaDetail(BaseModel):
    """
    Criteria details in workflow response.

    Criteria represent validation rules that AI checks during assessment.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique criteria identifier")
    name: str = Field(..., description="Criteria name (e.g., 'All documents must be signed')")
    description: str = Field(..., description="Detailed criteria description for AI validation")
    applies_to_bucket_ids: List[UUID] = Field(
        ...,
        description="List of bucket IDs this criteria applies to"
    )


class WorkflowStats(BaseModel):
    """
    Workflow statistics for quick overview.
    """

    bucket_count: int = Field(..., description="Number of buckets in workflow")
    criteria_count: int = Field(..., description="Number of criteria in workflow")


class WorkflowDetailResponse(BaseModel):
    """
    Complete workflow details with nested buckets and criteria.

    This is the response for GET /v1/workflows/:id endpoint.
    Journey Step 1: Users view complete workflow structure before assessment.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name (e.g., 'Medical Device - Class II')")
    description: Optional[str] = Field(None, description="Workflow description")
    organization_id: UUID = Field(..., description="Organization that owns this workflow")
    created_by: Optional[UUID] = Field(None, description="User ID who created this workflow")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether workflow is active or archived")

    buckets: List[BucketDetail] = Field(
        ...,
        description="Document categories (sorted by order_index on client side)"
    )
    criteria: List[CriteriaDetail] = Field(
        ...,
        description="Validation rules that AI checks"
    )
    stats: WorkflowStats = Field(
        ...,
        description="Workflow statistics"
    )


class WorkflowListItem(BaseModel):
    """
    Workflow summary for list endpoint.

    This is used for GET /v1/workflows endpoint (future story).
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    is_active: bool = Field(..., description="Whether workflow is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    bucket_count: int = Field(0, description="Number of buckets")
    criteria_count: int = Field(0, description="Number of criteria")
