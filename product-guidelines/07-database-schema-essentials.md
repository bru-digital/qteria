# Database Schema Essentials (For Backlog Generation)

> **Purpose**: Condensed version for Session 10 (backlog generation) - 56% smaller than full schema
> **Full Details**: See `07-database-schema.md` for complete table definitions, indexes, migrations, scaling

---

## Database Technology Choices

**Database**: PostgreSQL 15+
**ORM**: SQLAlchemy + Alembic (Python/FastAPI)
**ID Strategy**: UUID (non-guessable, distributed-safe)
**Multi-Tenancy**: Organization-based (row-level isolation via `organization_id`)

---

## Table List (Journey-Mapped)

| Table                  | Journey Step | Purpose                                            | Key Columns                                                                |
| ---------------------- | ------------ | -------------------------------------------------- | -------------------------------------------------------------------------- |
| `organizations`        | All          | Multi-tenant isolation (notified bodies)           | id, name, subscription_tier                                                |
| `users`                | All          | User accounts (Process Managers, Project Handlers) | id, organization_id, email, role                                           |
| `workflows`            | Step 1       | Validation workflow definitions                    | id, organization_id, created_by, name                                      |
| `buckets`              | Step 1       | Document categories in workflows                   | id, workflow_id, name, required                                            |
| `criteria`             | Step 1       | Validation rules                                   | id, workflow_id, name, description, applies_to_bucket_ids                  |
| `assessments`          | Step 2-5     | Validation runs (processing status, timing)        | id, organization_id, workflow_id, status, duration_ms                      |
| `assessment_documents` | Step 2       | Uploaded documents per bucket                      | id, assessment_id, bucket_id, file_name, storage_key                       |
| `assessment_results`   | Step 3-4     | Per-criteria results with evidence                 | id, assessment_id, criteria_id, pass, confidence, evidence_page, reasoning |
| `audit_logs`           | All          | SOC2/ISO 27001 compliance audit trail              | id, organization_id, user_id, action, resource_type                        |

**Total**: 9 core tables

---

## Entity Relationship Diagram

```
Organizations (1:N) Users (1:N) Workflows
                                    │
                         ┌──────────┴───────────┐
                    Buckets (1:N)        Criteria (1:N)
                         │                      │
                    (Assessment Documents) Assessments (1:N) Assessment Results
                                    │
                               Audit Logs
```

**Key Relationships**:

- Organizations → Users (1:N, CASCADE)
- Users → Workflows (1:N, SET NULL if user deleted)
- Workflows → Buckets, Criteria (1:N, CASCADE)
- Workflows → Assessments (1:N, RESTRICT to preserve history)
- Assessments → Assessment Documents, Assessment Results (1:N, CASCADE)
- Criteria → Assessment Results (1:N, RESTRICT to preserve history)

---

## Key Data Patterns

### Multi-Tenancy

**Pattern**: Organization-based row-level isolation

```sql
-- All queries filter by organization_id
SELECT * FROM workflows WHERE organization_id = $current_org_id;
SELECT * FROM assessments WHERE organization_id = $current_org_id;
```

**Enforcement**: Foreign keys + application-level checks (FastAPI middleware)

---

### Flexible AI Results

**Pattern**: JSONB for variable AI response structure

```sql
-- assessment_results.ai_response_raw: JSONB
{
  "pass": false,
  "confidence": "high",
  "evidence": {
    "page": 8,
    "section": "3.2",
    "text_snippet": "..."
  },
  "claude_metadata": {
    "model": "claude-3-5-sonnet-20241022",
    "tokens_used": 1542
  }
}
```

**Rationale**: Claude output schema evolves, JSONB allows flexibility without migrations

---

### Audit Trail

**Pattern**: Immutable audit logs (no UPDATE/DELETE)

```sql
-- Every user action logged
INSERT INTO audit_logs (organization_id, user_id, action, resource_type, resource_id, metadata)
VALUES ($org_id, $user_id, 'workflow_created', 'workflow', $workflow_id, '{"name": "Medical Device"}');
```

**Purpose**: SOC2/ISO 27001 compliance, security forensics, debugging

---

## Data Access Patterns (For Story Scoping)

### Read Patterns

**Dashboard (Step 1)**:

- Fetch all workflows for org (JOIN buckets, criteria)
- Recent assessments for user

**Workflow Detail (Step 1)**:

- Single workflow + buckets + criteria (3 queries or JOIN)

**Assessment Results (Step 4)**:

- Assessment + all results + criteria details (JOIN)

**Billing**:

- Count assessments per org per month
- Sum AI costs

### Write Patterns

**Create Workflow (Step 1)**:

- INSERT workflow → INSERT N buckets → INSERT M criteria (transaction)

**Start Assessment (Step 2)**:

- INSERT assessment → INSERT N assessment_documents (transaction)

**Store Results (Step 3)**:

- UPDATE assessment (status='processing') → INSERT M assessment_results → UPDATE assessment (status='completed')

**Audit Logging (All Steps)**:

- INSERT audit_log (async, non-blocking)

---

## Critical Indexes (Query Optimization)

**Foreign Keys** (all indexed):

- workflows.organization_id, workflows.created_by
- buckets.workflow_id
- criteria.workflow_id
- assessments.organization_id, assessments.workflow_id, assessments.created_by
- assessment_results.assessment_id, assessment_results.criteria_id

**Common Filters** (indexed):

- assessments.status, assessments.created_at DESC
- workflows.is_active WHERE is_active = TRUE
- users.auth_provider_id, users.email

**Composite Indexes** (multi-column queries):

- assessments(organization_id, status) - billing + filtering
- assessment_results(assessment_id, pass) - "show failed criteria"

---

## Data Constraints

**CHECK Constraints** (DB-level validation):

- subscription_tier IN ('trial', 'professional', 'enterprise')
- role IN ('process_manager', 'project_handler', 'admin')
- status IN ('pending', 'processing', 'completed', 'failed')
- confidence IN ('high', 'medium', 'low')
- file_size_bytes > 0, duration_ms >= 0, ai_cost_cents >= 0

**Foreign Key Actions**:

- CASCADE: Organization deleted → users/workflows deleted (GDPR)
- SET NULL: User deleted → workflows/assessments keep (historical data)
- RESTRICT: Workflow with assessments can't be deleted (preserve history)

---

## Scaling Strategy (Future)

**Current Capacity**: Handles 250K rows/year easily (Year 1-3)

**When to Scale** (Year 5+, >1M assessments):

- **Partition assessments** by month (time-series data)
- **Read replicas** for dashboard queries (separate read/write)
- **Archive old assessments** (>2 years) to cold storage

---

## Migration Status

**Version**: v001_initial_schema (Alembic)
**Applied**: [Date when you run `alembic upgrade head`]
**Location**: Full migration in `07-database-schema.md`

---

## For Backlog Stories

**When writing stories, reference**:

- Table names for CRUD operations
- Relationships for JOIN queries
- Indexes for performance considerations
- Constraints for validation logic

**Example Stories**:

- "As PM, create workflow" → INSERT workflows + buckets + criteria (transaction)
- "As PH, view assessment results" → SELECT assessment JOIN assessment_results JOIN criteria
- "As Admin, audit user actions" → SELECT audit_logs WHERE user_id = X ORDER BY created_at DESC

**Complete Details**: See `07-database-schema.md` for:

- Column definitions (types, nullability, defaults)
- Index strategies (GIN, partial, composite)
- Alembic migration code
- Query examples with EXPLAIN ANALYZE
- "What We DIDN'T Choose" alternatives
