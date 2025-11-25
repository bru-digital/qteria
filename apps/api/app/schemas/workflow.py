"""
Pydantic schemas for Workflow model.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class WorkflowBase(BaseModel):
    """Base schema for Workflow with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    is_active: bool = Field(default=True, description="Whether workflow is active")


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new workflow."""

    pass


class WorkflowUpdate(BaseModel):
    """Schema for updating an existing workflow."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    """Schema for workflow response."""

    id: UUID = Field(..., description="Workflow ID")
    organization_id: UUID = Field(..., description="Organization ID")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    archived: bool = Field(..., description="Whether workflow is archived")
    archived_at: Optional[datetime] = Field(None, description="Archive timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True  # Formerly orm_mode in Pydantic v1
