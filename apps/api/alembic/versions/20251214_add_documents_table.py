"""add_documents_table

Revision ID: 20251214_documents
Revises: 25424df7abc9
Create Date: 2025-12-14 00:00:00.000000+00:00

Adds documents table for standalone document storage with multi-tenancy.
This table stores uploaded documents before they're associated with assessments,
enabling:
- Multi-tenancy validation at upload time
- Document reuse across multiple assessments
- Orphan document cleanup
- Audit trail for document access

Required for STORY-018 (Document Download API) to query documents by ID.
Completes missing database persistence from STORY-015 (Document Upload API).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "20251214_documents"
down_revision: Union[str, Sequence[str], None] = "25424df7abc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create documents table with multi-tenancy and indexes."""
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column(
            "bucket_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buckets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create indexes for common query patterns
    op.create_index("idx_document_organization", "documents", ["organization_id"], unique=False)
    op.create_index("idx_document_bucket", "documents", ["bucket_id"], unique=False)
    op.create_index("idx_document_uploaded_at", "documents", ["uploaded_at"], unique=False)


def downgrade() -> None:
    """Drop documents table and indexes."""
    op.drop_index("idx_document_uploaded_at", table_name="documents")
    op.drop_index("idx_document_bucket", table_name="documents")
    op.drop_index("idx_document_organization", table_name="documents")
    op.drop_table("documents")
