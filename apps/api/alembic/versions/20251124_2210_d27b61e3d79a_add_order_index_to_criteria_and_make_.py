"""Add order_index to criteria and make description nullable

Revision ID: d27b61e3d79a
Revises: c1a2b3d4e5f6
Create Date: 2025-11-24 22:10:41.107191+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d27b61e3d79a"
down_revision: Union[str, Sequence[str], None] = "c1a2b3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add order_index to criteria and make description nullable."""
    # Add order_index column to criteria table
    op.add_column("criteria", sa.Column("order_index", sa.Integer(), nullable=True))

    # Make description field nullable on criteria table
    op.alter_column("criteria", "description", existing_type=sa.TEXT(), nullable=True)

    # Add composite index for efficient sorting of criteria within a workflow
    op.create_index("ix_criteria_workflow_order", "criteria", ["workflow_id", "order_index"])


def downgrade() -> None:
    """Downgrade schema: Remove order_index and revert description to non-nullable."""
    # Remove composite index
    op.drop_index("ix_criteria_workflow_order", table_name="criteria")

    # Revert description to non-nullable
    op.alter_column("criteria", "description", existing_type=sa.TEXT(), nullable=False)

    # Remove order_index column
    op.drop_column("criteria", "order_index")
