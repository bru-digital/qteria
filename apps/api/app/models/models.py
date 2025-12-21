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

from typing import Optional

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
    FetchedValue,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
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
    users: Mapped[list["User"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    workflows: Mapped[list["Workflow"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    # Note: No cascade delete - audit logs preserved for SOC2/ISO 27001 compliance
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="organization")


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
    organization: Mapped["Organization"] = relationship(back_populates="users")
    created_workflows: Mapped[list["Workflow"]] = relationship(
        back_populates="creator", foreign_keys="Workflow.created_by"
    )
    created_assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="creator", foreign_keys="Assessment.created_by"
    )
    uploaded_documents: Mapped[list["Document"]] = relationship(
        back_populates="uploader", foreign_keys="Document.uploaded_by"
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
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        server_default=FetchedValue(),
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        server_default=FetchedValue(),
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)
    section_patterns = Column(JSON, nullable=True)  # Custom regex patterns for section detection

    # Workflow status fields:
    # - is_active: Workflow enabled/disabled (can be toggled by user)
    # - archived: Workflow soft deleted (permanent removal from normal operations, preserves audit trail)
    is_active = Column(Boolean, default=True)
    archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="workflows")
    creator: Mapped["User"] = relationship(back_populates="created_workflows", foreign_keys=[created_by])
    buckets: Mapped[list["Bucket"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")
    criteria: Mapped[list["Criteria"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="workflow")

    # Indexes
    __table_args__ = (
        Index("idx_workflow_organization", "organization_id"),
        Index("idx_workflow_active", "is_active"),
        Index(
            "idx_workflow_org_archived", "organization_id", "archived"
        ),  # Composite index for list queries
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
    workflow: Mapped["Workflow"] = relationship(back_populates="buckets")
    documents: Mapped[list["Document"]] = relationship(back_populates="bucket")
    assessment_documents: Mapped[list["AssessmentDocument"]] = relationship(back_populates="bucket")

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
    description = Column(Text)  # Made nullable to match API schema
    applies_to_bucket_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True
    )  # Array of bucket UUIDs
    example_text = Column(Text)
    order_index = Column(Integer, default=0)  # Added for UI sorting
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="criteria")
    assessment_results: Mapped[list["AssessmentResult"]] = relationship(back_populates="criteria")

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
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        server_default=FetchedValue(),
    )
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        server_default=FetchedValue(),
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
    organization: Mapped["Organization"] = relationship(back_populates="assessments")
    workflow: Mapped["Workflow"] = relationship(back_populates="assessments")
    creator: Mapped["User"] = relationship(back_populates="created_assessments", foreign_keys=[created_by])
    assessment_documents: Mapped[list["AssessmentDocument"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    assessment_results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_assessment_organization_status", "organization_id", "status"),
        Index("idx_assessment_status", "status"),
        Index("idx_assessment_workflow", "workflow_id"),  # For workflow archive checks
        Index("idx_assessment_created_at", "started_at"),
    )


class Document(Base):
    """
    Standalone document storage table for uploaded files.

    Documents are uploaded independently and can later be attached to assessments.
    This enables:
    - Multi-tenancy validation at upload time
    - Document reuse across multiple assessments
    - Orphan document cleanup
    - Audit trail for document access
    """

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        server_default=FetchedValue(),
    )
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)  # e.g., "application/pdf"
    storage_key = Column(String(500), nullable=False, unique=True)  # Vercel Blob URL
    bucket_id = Column(
        UUID(as_uuid=True),
        ForeignKey("buckets.id", ondelete="SET NULL"),
        nullable=True,  # Optional - document may not be associated with bucket yet
    )
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        server_default=FetchedValue(),
    )
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="documents")
    bucket: Mapped[Optional["Bucket"]] = relationship(back_populates="documents")
    uploader: Mapped["User"] = relationship(back_populates="uploaded_documents")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_document_organization", "organization_id"),
        Index("idx_document_bucket", "bucket_id"),
        Index("idx_document_uploaded_at", "uploaded_at"),
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
    assessment: Mapped["Assessment"] = relationship(back_populates="assessment_documents")
    bucket: Mapped["Bucket"] = relationship(back_populates="assessment_documents")

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
    criteria_id = Column(UUID(as_uuid=True), ForeignKey("criteria.id"), nullable=False)
    pass_status = Column(Boolean, nullable=False)  # Renamed from 'pass' (reserved keyword)
    confidence = Column(
        String(50),
        CheckConstraint("confidence IN ('high', 'medium', 'low')", name="check_confidence_level"),
    )
    evidence_page = Column(Integer)
    evidence_section = Column(Text)
    reasoning = Column(Text)
    ai_response_raw = Column(JSON)  # Full Claude response for debugging

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    assessment: Mapped["Assessment"] = relationship(back_populates="assessment_results")
    criteria: Mapped["Criteria"] = relationship(back_populates="assessment_results")

    # Indexes
    __table_args__ = (
        Index("idx_result_assessment", "assessment_id"),
        Index("idx_result_criteria", "criteria_id"),
    )


class AuditLog(Base):
    """
    Immutable audit trail for SOC2/ISO 27001 compliance.
    Tracks all critical actions in the system.

    Note: organization_id is nullable to allow logging of security events
    (e.g., invalid token attempts) before organization context is known.
    """

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Nullable to support logging auth failures before org context is known
    # SET NULL on org deletion preserves audit trail for compliance (SOC2/ISO 27001)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
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
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="audit_logs")

    # Indexes for querying audit logs
    __table_args__ = (
        Index("idx_audit_organization", "organization_id"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_created_at", "created_at"),
        Index("idx_audit_action", "action"),
    )


class ParsedDocument(Base):
    """
    Cached parsed text from PDF documents.
    Avoids re-parsing the same document multiple times.
    Stores structured text with page boundaries and detected sections.
    """

    __tablename__ = "parsed_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        server_default=FetchedValue(),
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One parsed result per document
    )
    parsed_data = Column(JSON, nullable=False)  # Array of {page, section, text}
    parsing_method = Column(String(50), nullable=False)  # 'pypdf2' or 'pdfplumber'
    parsed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    # Use selectin loading to prevent N+1 query issues when accessing document.parsed_version
    document: Mapped["Document"] = relationship(backref=backref("parsed_version", lazy="selectin"))

    # Indexes
    # Note: document_id index is created automatically by unique=True constraint
    # Note: organization_id index is created automatically by index=True parameter
    __table_args__ = (Index("idx_parsed_documents_parsed_at", "parsed_at"),)
