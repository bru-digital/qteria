# [STORY-002] Database Migration System

**Type**: Story
**Epic**: EPIC-01 (Database & Infrastructure)
**Journey Step**: Foundation
**Priority**: P0 (Blocks Everything)
**RICE Score**: 200 (R:100 × I:2 × C:100% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When developers need to evolve the database schema over time, they need a reliable migration system with version control, so they can safely deploy schema changes without data loss.

**Value Delivered**: Enables safe, reversible database schema changes with full version control and rollback capability.

**Success Metric**: 100% successful migrations with zero rollbacks required in production.

---

## Acceptance Criteria

- [ ] Alembic installed and configured for PostgreSQL
- [ ] Initial migration (v001_initial_schema) created from STORY-001 schema
- [ ] Migration can upgrade (apply schema changes)
- [ ] Migration can downgrade (rollback schema changes)
- [ ] Migration versioning works correctly (sequential version numbers)
- [ ] Migration history tracked in alembic_version table
- [ ] Migration script documented with clear instructions
- [ ] Tested on local PostgreSQL and Vercel Postgres
- [ ] Migration runs successfully in CI/CD pipeline

---

## Technical Approach

**Tech Stack Components Used**:
- Migrations: Alembic (Python)
- Database: PostgreSQL 15+ (Vercel Postgres)
- ORM: SQLAlchemy

**Implementation Notes**:
- Initialize Alembic with `alembic init alembic`
- Configure alembic.ini with database connection string (use environment variables)
- Create initial migration from STORY-001 schema
- Use Alembic auto-generate for future migrations
- Store migrations in `alembic/versions/` directory

**Migration Structure**:
```python
# alembic/versions/v001_initial_schema.py
def upgrade():
    # Create all 9 tables from STORY-001
    op.create_table('organizations', ...)
    op.create_table('users', ...)
    # ... etc

def downgrade():
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('assessment_results')
    # ... etc
```

**Commands**:
```bash
# Create migration
alembic revision -m "initial schema"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Dependencies

- **Blocked By**: STORY-001 (Database Schema Setup) - need schema definition first
- **Blocks**: All future schema changes - migration system must exist before evolving schema

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:
- Alembic setup: 0.25 days (config, initialization)
- Initial migration creation: 0.25 days (convert STORY-001 schema to migration)
- Testing upgrade/downgrade: 0.25 days (test on local + Vercel Postgres)
- Documentation: 0.25 days (migration guide, commands)

---

## Definition of Done

- [ ] Alembic configured with PostgreSQL connection
- [ ] Initial migration (v001) creates all 9 tables
- [ ] `alembic upgrade head` applies schema successfully
- [ ] `alembic downgrade -1` removes schema successfully
- [ ] `alembic upgrade head` (after downgrade) reapplies schema
- [ ] alembic_version table tracks current version
- [ ] Migration tested on Vercel Postgres (production database)
- [ ] Migration documentation added to README
- [ ] CI/CD pipeline runs migrations automatically
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests** (70% coverage target):
- [ ] Run upgrade → verify all 9 tables exist
- [ ] Run downgrade → verify all tables removed
- [ ] Run upgrade again → verify tables recreated
- [ ] Check alembic_version table shows correct version
- [ ] Test with empty database (fresh install)
- [ ] Test with existing database (upgrade scenario)

**Edge Cases**:
- [ ] Migration fails mid-execution → rollback transaction
- [ ] Run migration twice → idempotent (no errors)
- [ ] Concurrent migrations → handled gracefully (alembic lock)

---

## Risks & Mitigations

**Risk**: Migration fails in production, database left in inconsistent state
- **Mitigation**: Use database transactions, test migrations thoroughly on staging, enable backups before migration

**Risk**: Downgrade loses data (destructive operations)
- **Mitigation**: Document which migrations are destructive, require manual confirmation for data-loss migrations

**Risk**: Alembic auto-generate creates incorrect migrations
- **Mitigation**: Always review auto-generated migrations manually, test upgrade/downgrade before committing

---

## Notes

- This is the **second highest priority story** after STORY-001
- All future schema changes will use this migration system
- Keep migrations linear (no branches) to avoid merge conflicts
- Document breaking changes clearly in migration comments
- After completing this story, proceed to STORY-003 (Seed Data)
