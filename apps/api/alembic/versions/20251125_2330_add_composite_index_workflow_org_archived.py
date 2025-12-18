"""Add composite index for workflow org_archived

Revision ID: b2c3d4e5f6g8
Revises: a1b2c3d4e5f7
Create Date: 2025-11-25 23:30:00.000000

This migration adds a composite index on (organization_id, archived) columns
to the workflows table for efficient filtering of archived workflows per organization.
This improves performance for list queries that filter by both fields together.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g8"
down_revision: Union[str, None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite index on (organization_id, archived) for workflows table."""
    op.create_index(
        "idx_workflow_org_archived", "workflows", ["organization_id", "archived"], unique=False
    )


def downgrade() -> None:
    """Remove composite index on (organization_id, archived) from workflows table."""
    op.drop_index("idx_workflow_org_archived", table_name="workflows")
