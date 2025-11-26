"""add_index_assessment_workflow_id

Revision ID: 25424df7abc9
Revises: b2c3d4e5f6g8
Create Date: 2025-11-26 08:47:33.526113+00:00

Adds an explicit index on assessments.workflow_id to optimize the workflow
archive operation's assessment count query. PostgreSQL does NOT automatically
create indexes for foreign keys (unlike MySQL), so we must explicitly create
this index to ensure optimal performance for COUNT queries.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25424df7abc9'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6g8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index on assessments.workflow_id for archive operation."""
    op.create_index(
        'idx_assessment_workflow',
        'assessments',
        ['workflow_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove index on assessments.workflow_id."""
    op.drop_index('idx_assessment_workflow', table_name='assessments')
