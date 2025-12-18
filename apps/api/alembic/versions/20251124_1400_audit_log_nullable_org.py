"""Make audit_logs.organization_id nullable for auth events

Revision ID: c1a2b3d4e5f6
Revises: 339026f16129
Create Date: 2025-11-24 14:00:00.000000

This migration allows organization_id to be nullable in audit_logs
to support logging authentication/authorization failures that occur
before the organization context is known (e.g., invalid token attempts).

This is required for SOC2/ISO 27001 compliance to track all security events.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1a2b3d4e5f6"
down_revision: Union[str, None] = "339026f16129"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make organization_id nullable in audit_logs."""
    op.alter_column(
        "audit_logs",
        "organization_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    """Revert organization_id to NOT NULL (will fail if NULL values exist)."""
    # Note: This will fail if there are rows with NULL organization_id
    op.alter_column(
        "audit_logs",
        "organization_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
