"""Add section_patterns to workflows table for custom regex patterns

Revision ID: d4e5f6g7h8i0
Revises: c3d4e5f6g7h9
Create Date: 2025-12-16 10:00:00.000000

This migration adds the section_patterns column to workflows table to support
custom regex patterns for section detection during PDF parsing. This allows
Process Managers to define domain-specific section detection patterns (e.g.,
medical device documentation patterns vs industrial certification patterns).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i0'
down_revision: Union[str, None] = 'c3d4e5f6g7h9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add section_patterns JSON column to workflows table."""
    op.add_column(
        'workflows',
        sa.Column(
            'section_patterns',
            sa.JSON(),
            nullable=True,
            comment='Custom regex patterns for PDF section detection (array of strings)'
        )
    )


def downgrade() -> None:
    """Remove section_patterns column from workflows table."""
    op.drop_column('workflows', 'section_patterns')
