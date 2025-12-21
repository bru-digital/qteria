"""Add ondelete SET NULL to audit_logs.organization_id for compliance

Revision ID: a7b8c9d0e1f2
Revises: (latest revision)
Create Date: 2025-12-20 21:22:00.000000

This migration modifies the foreign key constraint on audit_logs.organization_id
to use ON DELETE SET NULL. This ensures that when an organization is deleted,
the audit logs are preserved with NULL organization_id for SOC2/ISO 27001 compliance.

Without this change, cascade deleting audit logs would violate compliance requirements
for maintaining immutable audit trails.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "d4e5f6g7h8i0"  # 20251217_add_section_patterns_to_workflows
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ON DELETE SET NULL to audit_logs.organization_id foreign key."""
    # Drop existing foreign key constraint
    op.drop_constraint("audit_logs_organization_id_fkey", "audit_logs", type_="foreignkey")

    # Recreate foreign key with ON DELETE SET NULL
    op.create_foreign_key(
        "audit_logs_organization_id_fkey",
        "audit_logs",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Remove ON DELETE SET NULL from audit_logs.organization_id foreign key."""
    # Drop existing foreign key constraint
    op.drop_constraint("audit_logs_organization_id_fkey", "audit_logs", type_="foreignkey")

    # Recreate foreign key without ON DELETE clause (defaults to NO ACTION)
    op.create_foreign_key(
        "audit_logs_organization_id_fkey",
        "audit_logs",
        "organizations",
        ["organization_id"],
        ["id"],
    )
