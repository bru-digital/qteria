"""Add section_patterns column to workflows table

Revision ID: d4e5f6g7h8i0
Revises: c3d4e5f6g7h9
Create Date: 2025-12-17 14:00:00.000000

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
    """Add section_patterns column to workflows table."""
    # Add section_patterns column as JSON (nullable, defaults to NULL)
    op.add_column(
        'workflows',
        sa.Column('section_patterns', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )


def downgrade() -> None:
    """Remove section_patterns column from workflows table."""
    op.drop_column('workflows', 'section_patterns')
