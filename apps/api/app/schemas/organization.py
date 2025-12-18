"""
Pydantic schemas for Organization model.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    """Base schema for Organization with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    subscription_tier: str = Field(
        default="trial",
        pattern="^(trial|professional|enterprise)$",
        description="Subscription tier",
    )
    subscription_status: str = Field(
        default="trial",
        pattern="^(trial|active|cancelled)$",
        description="Subscription status",
    )


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""

    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an existing organization."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    subscription_tier: Optional[str] = Field(None, pattern="^(trial|professional|enterprise)$")
    subscription_status: Optional[str] = Field(None, pattern="^(trial|active|cancelled)$")


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    id: UUID = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True  # Formerly orm_mode in Pydantic v1
