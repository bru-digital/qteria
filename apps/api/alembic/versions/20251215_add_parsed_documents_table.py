"""Add parsed_documents table for PDF parsing cache

Revision ID: c3d4e5f6g7h9
Revises: 20251214_documents
Create Date: 2025-12-15 18:00:00.000000

This migration adds the parsed_documents table to cache parsed PDF text with
page boundaries and section detection. This avoids re-parsing the same document
multiple times and stores results in JSON format for the AI validation engine.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h9'
down_revision: Union[str, None] = '20251214_documents'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parsed_documents table with indexes."""
    op.create_table(
        'parsed_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parsed_data', sa.JSON(), nullable=False),
        sa.Column('parsing_method', sa.String(length=50), nullable=False),
        sa.Column('parsed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', name='uq_parsed_documents_document_id')
    )

    # Create indexes for efficient querying
    # Note: document_id index is created automatically by the unique constraint above
    op.create_index('idx_parsed_documents_parsed_at', 'parsed_documents', ['parsed_at'], unique=False)
    op.create_index('idx_parsed_documents_organization_id', 'parsed_documents', ['organization_id'], unique=False)


def downgrade() -> None:
    """Remove parsed_documents table and indexes."""
    op.drop_index('idx_parsed_documents_organization_id', table_name='parsed_documents')
    op.drop_index('idx_parsed_documents_parsed_at', table_name='parsed_documents')
    # document_id index is dropped automatically by the unique constraint
    op.drop_table('parsed_documents')
