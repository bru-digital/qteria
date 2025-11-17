# [EPIC-01] Database & Infrastructure Setup

**Type**: Epic
**Journey Step**: Foundation (Enables All)
**Priority**: P0 (Critical - Blocks Everything)

---

## Epic Overview

Set up PostgreSQL database schema, infrastructure foundation, and deployment pipeline. This epic is the foundation for the entire application - no other work can begin until the database and API infrastructure are operational.

**Value**: Enables secure, multi-tenant data storage and API infrastructure for all application features.

---

## Success Criteria

- [ ] PostgreSQL database deployed and accessible
- [ ] All tables created with proper relationships, indexes, constraints
- [ ] Alembic migrations working (can upgrade/downgrade schema)
- [ ] Seed data loaded for development/testing
- [ ] FastAPI backend deployed and responding to health checks
- [ ] Multi-tenancy enforced at database level (row-level security via organization_id)

---

## Stories in This Epic

### STORY-001: Database Schema Setup [P0, 2 days]
Create complete PostgreSQL schema with all 9 core tables (organizations, users, workflows, buckets, criteria, assessments, assessment_documents, assessment_results, audit_logs) with proper foreign keys, indexes, and constraints.

**RICE**: R:100 × I:3 × C:100% ÷ E:2 = **150** (Highest priority - blocks everything)

### STORY-002: Database Migration System [P0, 1 day]
Set up Alembic for database migrations, create initial migration (v001_initial_schema), and test upgrade/downgrade workflows.

**RICE**: R:100 × I:2 × C:100% ÷ E:1 = **200**

### STORY-003: Seed Data for Development [P0, 0.5 days]
Create seed data script (1 organization "TÜV SÜD Demo", 2 users, 2 sample workflows with buckets/criteria) for local development and testing.

**RICE**: R:50 × I:1 × C:100% ÷ E:0.5 = **100**

### STORY-004: FastAPI Infrastructure & Health Checks [P0, 1.5 days]
Set up FastAPI application structure, database connection pool (SQLAlchemy), health check endpoint, CORS configuration, and deploy to Railway.

**RICE**: R:100 × I:2 × C:100% ÷ E:1.5 = **133**

---

## Total Estimated Effort

**5 person-days** (1 week for solo founder)

**Breakdown**:
- Backend: 4 days (schema, migrations, API setup)
- DevOps: 0.5 days (deployment)
- Testing: 0.5 days (schema validation, connection tests)

---

## Dependencies

**Blocks**:
- EPIC-02: Authentication (needs users, organizations tables)
- EPIC-03: Workflow Management (needs workflows, buckets, criteria tables)
- EPIC-04: Document Processing (needs assessment_documents table)
- EPIC-05: AI Validation (needs assessment_results table)
- ALL other epics (every feature needs database)

**Blocked By**: Nothing - this is the starting point

---

## Technical Approach

**Tech Stack**:
- Database: PostgreSQL 15+ (Vercel Postgres free tier)
- Backend: FastAPI + SQLAlchemy (ORM)
- Migrations: Alembic
- Deployment: Railway (backend), Vercel Postgres (database)

**Key Design Decisions**:
- UUID primary keys (non-guessable, distributed-safe)
- Multi-tenancy via organization_id (row-level isolation)
- JSONB for flexible AI responses (future-proof schema)
- Audit logs (immutable, SOC2 compliance)
- Foreign key cascades (org deleted → users deleted, workflow deleted → buckets/criteria deleted)

**Reference**: `product-guidelines/07-database-schema.md` for complete schema

---

## Success Metrics

**Technical Metrics**:
- Database query P95 latency: <100ms
- Connection pool never exhausted (max 20 connections)
- Zero data integrity errors (foreign key violations)

**Operational Metrics**:
- Database uptime: 99.9%
- Successful migrations: 100% (no rollbacks required)
- Seed data load time: <5 seconds

---

## Definition of Done

- [ ] All 9 tables created with indexes and constraints
- [ ] Alembic migrations tested (upgrade + downgrade)
- [ ] Seed data script creates valid test data
- [ ] FastAPI health check returns 200 OK
- [ ] Database connection pool configured correctly
- [ ] Integration tests pass (CRUD operations work)
- [ ] Deployed to Railway + Vercel Postgres
- [ ] Multi-tenancy validated (org_a cannot see org_b data)
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: PostgreSQL free tier limits (256MB storage)
- **Mitigation**: Monitor storage usage, upgrade to Pro ($20/month) when >80% full

**Risk**: Alembic migration conflicts (if schema changes rapidly)
- **Mitigation**: Run migrations in linear order, test before merging

**Risk**: Foreign key cascades delete data unintentionally
- **Mitigation**: Test cascade behavior thoroughly, use RESTRICT for critical relationships (assessments preserve history)

---

## Testing Requirements

**Integration Tests** (70% coverage target):
- [ ] Create organization → users → workflows (cascade insert)
- [ ] Delete organization → users/workflows deleted (cascade delete)
- [ ] Delete user → workflows stay, created_by set NULL (SET NULL)
- [ ] Multi-tenant isolation (user A cannot query user B's data)
- [ ] All indexes exist and speed up queries (EXPLAIN ANALYZE)
- [ ] All constraints enforced (CHECK, UNIQUE, FOREIGN KEY)

**Performance Tests**:
- [ ] Insert 1000 workflows: <10 seconds
- [ ] Query workflows by organization: <50ms
- [ ] Join workflows + buckets + criteria: <100ms

---

## Next Epic

After completing this epic, proceed to **EPIC-02: Authentication & Authorization** to secure API endpoints and implement role-based access control.
