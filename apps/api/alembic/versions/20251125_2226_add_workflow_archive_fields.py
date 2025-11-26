"""Add workflow archive fields

Revision ID: a1b2c3d4e5f7
Revises: d27b61e3d79a
Create Date: 2025-11-25 22:26:00.000000

This migration adds archived and archived_at columns to the workflows table
to support soft delete functionality. Archived workflows are hidden from
list endpoints by default but remain accessible for audit trail purposes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'd27b61e3d79a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add archived and archived_at columns to workflows table."""
    # Add archived column (non-nullable with default False)
    op.add_column(
        'workflows',
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='false')
    )

    # Add archived_at column (nullable timestamp)
    op.add_column(
        'workflows',
        sa.Column('archived_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Remove archived and archived_at columns from workflows table."""
    # Drop columns
    op.drop_column('workflows', 'archived_at')
    op.drop_column('workflows', 'archived')
