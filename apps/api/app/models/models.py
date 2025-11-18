"""
SQLAlchemy models for Qteria database schema.

This module defines all 9 core tables:
- organizations: Multi-tenant isolation
- users: User accounts with RBAC
- workflows: Validation workflow definitions
- buckets: Document categories in workflows
- criteria: Validation rules per workflow
- assessments: Validation runs with status tracking
- assessment_documents: Uploaded documents per bucket
- assessment_results: Per-criteria pass/fail with evidence
- audit_logs: Immutable audit trail (SOC2/ISO 27001)
"""
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    TIMESTAMP,
    ForeignKey,
    CheckConstraint,
    Text,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .base import Base


class Organization(Base):
    """
    Multi-tenant organization table.
    All data is isolated by organization_id for data privacy.
    """

    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    subscription_tier = Column(
        String(50),
        CheckConstraint(
            "subscription_tier IN ('trial', 'professional', 'enterprise')",
            name="check_subscription_tier",
        ),
        default="trial",
    )
    subscription_status = Column(
        String(50),
        CheckConstraint(
            "subscription_status IN ('trial', 'active', 'cancelled')",
            name="check_subscription_status",
        ),
        default="trial",
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    users = relationship(
        "User", back_populates="organization", cascade="all, delete-orphan"
    )
    workflows = relationship("Workflow", back_populates="organization")
    assessments = relationship("Assessment", back_populates="organization")
    audit_logs = relationship("AuditLog", back_populates="organization")


class User(Base):
    """
    User accounts with role-based access control (RBAC).
    Roles: process_manager, project_handler, admin
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    password_hash = Column(String(255))  # bcrypt hashed password
    role = Column(
        String(50),
        CheckConstraint(
            "role IN ('process_manager', 'project_handler', 'admin')",
            name="check_user_role",
        ),
        nullable=False,
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_workflows = relationship(
        "Workflow", back_populates="creator", foreign_keys="Workflow.created_by"
    )
    created_assessments = relationship(
        "Assessment", back_populates="creator", foreign_keys="Assessment.created_by"
    )

    # Indexes
    __table_args__ = (Index("idx_user_organization", "organization_id"),)


class Workflow(Base):
    """
    Validation workflow definitions created by Process Managers.
    Contains buckets (document categories) and criteria (validation rules).
    """

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    organization = relationship("Organization", back_populates="workflows")
    creator = relationship(
        "User", back_populates="created_workflows", foreign_keys=[created_by]
    )
    buckets = relationship(
        "Bucket", back_populates="workflow", cascade="all, delete-orphan"
    )
    criteria = relationship(
        "Criteria", back_populates="workflow", cascade="all, delete-orphan"
    )
    assessments = relationship("Assessment", back_populates="workflow")

    # Indexes
    __table_args__ = (
        Index("idx_workflow_organization", "organization_id"),
        Index("idx_workflow_active", "is_active"),
    )


class Bucket(Base):
    """
    Document categories within a workflow (e.g., "Test Reports", "Risk Assessment").
    Can be required or optional.
    """

    __tablename__ = "buckets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    required = Column(Boolean, default=True)
    order_index = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    workflow = relationship("Workflow", back_populates="buckets")
    assessment_documents = relationship(
        "AssessmentDocument", back_populates="bucket"
    )

    # Indexes
    __table_args__ = (Index("idx_bucket_workflow", "workflow_id"),)


class Criteria(Base):
    """
    Validation rules that AI checks during assessment.
    Each criteria can apply to specific buckets.
    """

    __tablename__ = "criteria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    applies_to_bucket_ids = Column(
        ARRAY(UUID(as_uuid=True))
    )  # Array of bucket UUIDs
    example_text = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    workflow = relationship("Workflow", back_populates="criteria")
    assessment_results = relationship(
        "AssessmentResult", back_populates="criteria"
    )

    # Indexes
    __table_args__ = (Index("idx_criteria_workflow", "workflow_id"),)


class Assessment(Base):
    """
    Validation runs by Project Handlers.
    Status: pending -> processing -> completed/failed
    """

    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    workflow_id = Column(
        UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False
    )
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    status = Column(
        String(50),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="check_assessment_status",
        ),
        default="pending",
        nullable=False,
    )
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))
    duration_ms = Column(Integer)

    # Relationships
    organization = relationship("Organization", back_populates="assessments")
    workflow = relationship("Workflow", back_populates="assessments")
    creator = relationship(
        "User", back_populates="created_assessments", foreign_keys=[created_by]
    )
    assessment_documents = relationship(
        "AssessmentDocument",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    assessment_results = relationship(
        "AssessmentResult",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_assessment_organization_status", "organization_id", "status"),
        Index("idx_assessment_status", "status"),
        Index("idx_assessment_created_at", "started_at"),
    )


class AssessmentDocument(Base):
    """
    Junction table for uploaded documents in an assessment.
    Links assessments -> buckets -> actual document files.
    """

    __tablename__ = "assessment_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )
    bucket_id = Column(UUID(as_uuid=True), ForeignKey("buckets.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    storage_key = Column(String(500), nullable=False)  # Vercel Blob or S3 key
    file_size_bytes = Column(Integer)
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="assessment_documents")
    bucket = relationship("Bucket", back_populates="assessment_documents")

    # Indexes
    __table_args__ = (Index("idx_assessment_document", "assessment_id"),)


class AssessmentResult(Base):
    """
    Per-criteria validation results with evidence-based AI assessment.
    This is the "aha moment" - showing EXACTLY where validation passed/failed.
    """

    __tablename__ = "assessment_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )
    criteria_id = Column(
        UUID(as_uuid=True), ForeignKey("criteria.id"), nullable=False
    )
    pass_status = Column(
        Boolean, nullable=False
    )  # Renamed from 'pass' (reserved keyword)
    confidence = Column(
        String(50),
        CheckConstraint(
            "confidence IN ('high', 'medium', 'low')", name="check_confidence_level"
        ),
    )
    evidence_page = Column(Integer)
    evidence_section = Column(Text)
    reasoning = Column(Text)
    ai_response_raw = Column(JSON)  # Full Claude response for debugging

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="assessment_results")
    criteria = relationship("Criteria", back_populates="assessment_results")

    # Indexes
    __table_args__ = (
        Index("idx_result_assessment", "assessment_id"),
        Index("idx_result_criteria", "criteria_id"),
    )


class AuditLog(Base):
    """
    Immutable audit trail for SOC2/ISO 27001 compliance.
    Tracks all critical actions in the system.
    """

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    action_metadata = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")

    # Indexes for querying audit logs
    __table_args__ = (
        Index("idx_audit_organization", "organization_id"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_created_at", "created_at"),
        Index("idx_audit_action", "action"),
    )
