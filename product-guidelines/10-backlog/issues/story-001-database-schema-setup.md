# [STORY-001] Database Schema Setup

**Type**: Story
**Epic**: EPIC-01 (Database & Infrastructure)
**Journey Step**: Foundation
**Priority**: P0 (Blocks Everything)
**RICE Score**: 150 (R:100 × I:3 × C:100% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When developers start building features, they need a complete database schema with all tables, relationships, and constraints, so they can store workflows, assessments, and results reliably.

**Value Delivered**: Foundation for entire application - enables all data storage and retrieval for every feature.

**Success Metric**: Database schema deployed with 100% data integrity (no foreign key violations, constraint violations).

---

## Acceptance Criteria

- [ ] All 9 core tables created: organizations, users, workflows, buckets, criteria, assessments, assessment_documents, assessment_results, audit_logs
- [ ] Foreign keys established with correct ON DELETE behavior (CASCADE for org→users, SET NULL for user→workflows, RESTRICT for workflows→assessments)
- [ ] CHECK constraints enforced (subscription_tier, role, status, confidence enums)
- [ ] Indexes created on foreign keys and common filters (organization_id, status, created_at)
- [ ] UUID primary keys for all tables (non-guessable IDs)
- [ ] JSONB columns for flexible data (ai_response_raw in assessment_results)
- [ ] Timestamps (created_at, updated_at) on all tables
- [ ] Schema deployed to Vercel Postgres (free tier)
- [ ] Can insert and query data successfully

---

## Technical Approach

**Tech Stack Components Used**:
- Database: PostgreSQL 15+ (Vercel Postgres)
- ORM: SQLAlchemy (Python)
- Schema Management: Direct SQL (migrations in STORY-002)

**Implementation Notes**:
- Create tables in dependency order (organizations first, then users, then workflows, etc.)
- Use UUID v4 for primary keys (`id UUID DEFAULT gen_random_uuid()`)
- Multi-tenancy via organization_id on all user-data tables
- Audit logs immutable (no UPDATE/DELETE allowed, only INSERT)

**Database Schema** (from `07-database-schema-essentials.md`):
```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  subscription_tier VARCHAR(50) CHECK (subscription_tier IN ('trial', 'professional', 'enterprise')),
  subscription_status VARCHAR(50) CHECK (subscription_status IN ('trial', 'active', 'cancelled')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50) CHECK (role IN ('process_manager', 'project_handler', 'admin')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- (Continue with all 9 tables from 07-database-schema-essentials.md)
```

**Reference**: `product-guidelines/07-database-schema-essentials.md` for complete schema

---

## Dependencies

- **Blocks**: ALL stories (every feature needs database)
- **Blocked By**: Nothing - this is the starting point

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:
- Schema design: 0.5 days (reference cascade output)
- SQL script writing: 0.5 days (9 tables + indexes + constraints)
- Testing: 0.5 days (insert/query data, validate constraints)
- Documentation: 0.5 days (schema diagram, table descriptions)

---

## Definition of Done

- [ ] SQL script creates all 9 tables successfully
- [ ] Foreign keys enforce relationships (test CASCADE, SET NULL, RESTRICT)
- [ ] CHECK constraints prevent invalid data (test enum validation)
- [ ] Indexes speed up common queries (verify with EXPLAIN ANALYZE)
- [ ] Can insert organization → user → workflow → assessment flow
- [ ] Schema deployed to Vercel Postgres
- [ ] Schema documented (table diagram, column descriptions)
- [ ] Integration tests pass (CRUD operations work)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests** (70% coverage target):
- [ ] Create organization → users → workflows (cascade insert)
- [ ] Delete organization → users/workflows deleted (CASCADE)
- [ ] Delete user → workflows stay, created_by set NULL (SET NULL)
- [ ] Delete workflow with assessments → prevented (RESTRICT)
- [ ] Invalid subscription_tier → rejected (CHECK constraint)
- [ ] Invalid role → rejected (CHECK constraint)
- [ ] Multi-tenant isolation (org A cannot see org B data via organization_id filter)

**Data Integrity Tests**:
- [ ] UUID primary keys are unique and non-guessable
- [ ] Timestamps auto-populate (created_at defaults to NOW())
- [ ] JSONB columns accept valid JSON (ai_response_raw)

---

## Risks & Mitigations

**Risk**: Vercel Postgres free tier limits (256MB storage)
- **Mitigation**: Monitor usage, plan for Pro upgrade ($20/month) when >80% full

**Risk**: Foreign key cascades delete data unintentionally
- **Mitigation**: Test cascade behavior thoroughly, use RESTRICT for history preservation (assessments)

**Risk**: Schema changes required after deployment (migrations complex)
- **Mitigation**: Thorough design review before deployment, use Alembic for future changes (STORY-002)

---

## Notes

- This is the **highest priority story** - nothing else can start without the database
- Complete schema in `07-database-schema.md` (full version with 56% more detail)
- ERD diagram available in `07-database-schema-essentials.md`
- After completing this story, immediately proceed to STORY-002 (Database Migrations) to set up version control for schema changes
