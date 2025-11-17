# Database Schema: Qteria

> **Generated**: November 2025
> **Database**: PostgreSQL 15+
> **ORM**: SQLAlchemy + Alembic (Python/FastAPI)
> **ID Strategy**: UUID (non-guessable, distributed-safe)
> **Multi-Tenancy**: Organization-based isolation

---

## Overview

This schema supports the AI-powered document validation workflow for TIC (Testing, Inspection, Certification) notified bodies. The design prioritizes:
- **Journey alignment**: Every table serves specific journey steps
- **Data privacy**: SOC2/ISO 27001 compliant (audit logs, encryption support)
- **Query performance**: Indexed for common access patterns
- **Flexibility**: JSONB for AI results (schema evolves)
- **Multi-tenancy**: Organization-level data isolation

**Entity Count**: 9 core tables
**Key Relationships**: 7 one-to-many, 2 many-to-many (via junction tables)
**Indexes**: 18 strategic indexes for query optimization

---

## How This Traces to User Journey

| Journey Step | Tables Used | Purpose |
|--------------|-------------|---------|
| **Step 1: Create Workflow** | `workflows`, `buckets`, `criteria` | Store workflow definitions (buckets + validation criteria) |
| **Step 2: Upload Documents** | `assessment_documents` | Track uploaded PDFs/DOCX files per bucket |
| **Step 3: AI Validation** | `assessments`, `assessment_results` | Store processing status, AI output, evidence links |
| **Step 4: Review Results** | `assessment_results` | Display pass/fail per criteria with evidence |
| **Step 5: Export Report** | `assessments`, `assessment_results` | Generate PDF reports from stored results |
| **All Steps** | `users`, `organizations`, `audit_logs` | Authentication, multi-tenancy, compliance audit trails |

---

## Entity Relationship Diagram

```
┌────────────────┐
│ Organizations  │
└────────┬───────┘
         │ 1:N
    ┌────▼─────┐
    │  Users   │
    └────┬─────┘
         │ 1:N
    ┌────▼──────────┐
    │   Workflows   │
    └────┬──────────┘
         │ 1:N
    ┌────▼─────────┐         ┌───────────┐
    │   Buckets    │         │ Criteria  │◄─┐
    └──────────────┘         └─────┬─────┘  │
                                   │ 1:N    │ M:N
                             ┌─────▼─────┐  │ (applies_to)
                             │Assessments│  │
                             └─────┬─────┘  │
                                   │ 1:N    │
                    ┌──────────────┼────────┘
                    │              │
         ┌──────────▼─┐     ┌─────▼──────────────┐
         │Assessment  │     │Assessment          │
         │Documents   │     │Results             │
         └────────────┘     └────────────────────┘
                                   │ 1:N (evidence)


┌────────────────┐
│  Audit Logs    │  (All user actions)
└────────────────┘
```

**Legend**:
- 1:N = One-to-Many relationship
- M:N = Many-to-Many (via junction table or JSONB array)
- Foreign keys enforce referential integrity with CASCADE/RESTRICT

---

## Table Definitions

### 1. organizations

**Purpose**: Multi-tenant data isolation. Each notified body (TÜV SÜD, BSI, DEKRA) is an organization.

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Organization name (e.g., "TÜV SÜD") |
| subscription_tier | VARCHAR(50) | NOT NULL, DEFAULT 'trial', CHECK | Pricing tier (trial, professional, enterprise) |
| subscription_status | VARCHAR(50) | NOT NULL, DEFAULT 'active', CHECK | Status (active, cancelled, suspended) |
| subscription_start_date | DATE | NULLABLE | When subscription began |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last modification timestamp |

**Indexes**:
- Primary key (id) - auto-indexed
- `idx_organizations_status`: ON (subscription_status) - billing queries

**Relationships**:
- Has many: `users`, `workflows`

**Design Decisions**:
- **UUID**: Non-guessable IDs (security), supports distributed systems
- **subscription_tier**: Stored here (not separate table) - simple pricing model (3 tiers only)
- **TIMESTAMPTZ**: Timezone-aware for global customers
- **CHECK constraints**: Enforce valid tier/status at database level

**Journey Connection**: Organizations own all workflows and assessments (Step 1-5 isolation)

---

### 2. users

**Purpose**: User accounts (Process Managers, Project Handlers, Admins). Auth handled by Auth.js/Clerk.

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| organization_id | UUID | NULLABLE, REFERENCES organizations(id) ON DELETE CASCADE | Organization membership |
| auth_provider_id | VARCHAR(255) | UNIQUE, NOT NULL | Auth.js/Clerk user ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email (for notifications) |
| name | VARCHAR(255) | NULLABLE | Display name |
| role | VARCHAR(50) | NOT NULL, DEFAULT 'project_handler', CHECK | User role (process_manager, project_handler, admin) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last modification |

**Indexes**:
- Primary key (id)
- `idx_users_org_id`: ON (organization_id) - frequent joins
- `idx_users_auth_id`: UNIQUE ON (auth_provider_id) - login lookups
- `idx_users_email`: UNIQUE ON (email) - email lookups

**Relationships**:
- Belongs to: `organizations` (nullable for initial signup flow)
- Has many: `workflows`, `assessments`, `audit_logs`

**Design Decisions**:
- **auth_provider_id**: External auth (Auth.js), not passwords (security best practice)
- **organization_id NULLABLE**: Allows user creation before org assignment (onboarding flow)
- **role CHECK**: Enum enforcement at DB level (process_manager, project_handler, admin)
- **ON DELETE CASCADE**: If org deleted, users deleted (GDPR compliance - right to be forgotten)

**Journey Connection**: Process Managers create workflows (Step 1), Project Handlers run assessments (Step 2-5)

---

### 3. workflows

**Purpose**: Validation workflow definitions created by Process Managers (Step 1).

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| organization_id | UUID | NOT NULL, REFERENCES organizations(id) ON DELETE CASCADE | Organization ownership |
| created_by | UUID | NOT NULL, REFERENCES users(id) ON DELETE SET NULL | Creator (Process Manager) |
| name | VARCHAR(255) | NOT NULL | Workflow name (e.g., "Medical Device - Class II") |
| description | TEXT | NULLABLE | Optional description |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft-enable/disable (not delete) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last modification |

**Indexes**:
- Primary key (id)
- `idx_workflows_org_id`: ON (organization_id) - "show all workflows for org"
- `idx_workflows_created_by`: ON (created_by) - "my workflows"
- `idx_workflows_active`: ON (is_active) WHERE is_active = TRUE - partial index for active workflows

**Relationships**:
- Belongs to: `organizations`, `users` (creator)
- Has many: `buckets`, `criteria`, `assessments`

**Design Decisions**:
- **is_active**: Soft disable (don't delete workflows with assessment history)
- **ON DELETE SET NULL** for created_by: Keep workflow if creator leaves (orphaned workflows stay)
- **name + organization_id**: No UNIQUE constraint (allow duplicate names across orgs, even within org)

**Journey Connection**: Step 1 - Process Manager defines validation workflow structure

---

### 4. buckets

**Purpose**: Document categories within workflows (e.g., "Technical Documentation", "Test Reports").

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| workflow_id | UUID | NOT NULL, REFERENCES workflows(id) ON DELETE CASCADE | Parent workflow |
| name | VARCHAR(255) | NOT NULL | Bucket name (e.g., "Technical Documentation") |
| required | BOOLEAN | NOT NULL, DEFAULT TRUE | Must upload documents? |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | Display order (for UI sorting) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- Primary key (id)
- `idx_buckets_workflow_id`: ON (workflow_id) - "get all buckets for workflow"
- `idx_buckets_order`: ON (workflow_id, order_index) - sorted display

**Relationships**:
- Belongs to: `workflows`
- Has many: `assessment_documents` (documents uploaded to this bucket)

**Design Decisions**:
- **required**: Boolean (not nullable) - explicit true/false, no ambiguity
- **order_index**: UI sorting without string sorting (drag-drop reorder)
- **ON DELETE CASCADE**: If workflow deleted, buckets deleted (no orphans)
- **No UNIQUE on name**: Same bucket name allowed in different workflows

**Journey Connection**: Step 1 - Process Manager creates document buckets (2-5 per workflow typical)

---

### 5. criteria

**Purpose**: Validation rules defined by Process Managers (e.g., "All documents must be signed").

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| workflow_id | UUID | NOT NULL, REFERENCES workflows(id) ON DELETE CASCADE | Parent workflow |
| name | VARCHAR(255) | NOT NULL | Criteria name (e.g., "Signature Required") |
| description | TEXT | NOT NULL | Detailed validation rule |
| applies_to_bucket_ids | UUID[] | NULLABLE | Array of bucket IDs (or NULL = all buckets) |
| example_text | TEXT | NULLABLE | Optional example for AI context |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- Primary key (id)
- `idx_criteria_workflow_id`: ON (workflow_id) - "get all criteria for workflow"
- `idx_criteria_order`: ON (workflow_id, order_index) - sorted display
- `idx_criteria_bucket_gin`: USING GIN (applies_to_bucket_ids) - array containment queries

**Relationships**:
- Belongs to: `workflows`
- Applies to: `buckets` (via UUID array - many-to-many without junction table)
- Has many: `assessment_results` (results per criteria)

**Design Decisions**:
- **UUID[]**: PostgreSQL array (many-to-many without junction table) - simpler than `criteria_buckets` table
- **applies_to_bucket_ids NULLABLE**: NULL = applies to ALL buckets (common case)
- **GIN index**: Fast containment queries (`WHERE bucket_id = ANY(applies_to_bucket_ids)`)
- **example_text**: Optional AI context (helps Claude understand nuanced criteria)

**Journey Connection**: Step 1 - Process Manager defines what to validate (10-20 criteria typical per workflow)

---

### 6. assessments

**Purpose**: Assessment runs (Step 2-5). Tracks processing status, timing, results.

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| organization_id | UUID | NOT NULL, REFERENCES organizations(id) ON DELETE CASCADE | Organization ownership (billing) |
| workflow_id | UUID | NOT NULL, REFERENCES workflows(id) ON DELETE RESTRICT | Workflow used (prevent delete if assessments exist) |
| created_by | UUID | NOT NULL, REFERENCES users(id) ON DELETE SET NULL | Project Handler who started |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'pending', CHECK | Processing status (pending, processing, completed, failed) |
| error_message | TEXT | NULLABLE | Error details if failed |
| started_at | TIMESTAMPTZ | NULLABLE | When AI processing began |
| completed_at | TIMESTAMPTZ | NULLABLE | When processing finished |
| duration_ms | INTEGER | NULLABLE | Processing time in milliseconds |
| ai_cost_cents | INTEGER | NULLABLE, DEFAULT 0 | Claude API cost (for billing/analytics) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Assessment creation |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last status update |

**Indexes**:
- Primary key (id)
- `idx_assessments_org_id`: ON (organization_id) - billing queries
- `idx_assessments_workflow_id`: ON (workflow_id) - "assessments per workflow"
- `idx_assessments_created_by`: ON (created_by) - "my assessments"
- `idx_assessments_status`: ON (status) - filter by status
- `idx_assessments_created`: ON (created_at DESC) - recent assessments first
- `idx_assessments_org_status`: ON (organization_id, status) - composite (common query pattern)

**Relationships**:
- Belongs to: `organizations`, `workflows`, `users` (creator)
- Has many: `assessment_documents`, `assessment_results`

**Design Decisions**:
- **status CHECK**: Enforce valid states (pending, processing, completed, failed)
- **duration_ms**: Milliseconds (more precise than seconds) for performance monitoring
- **ai_cost_cents**: Cents not dollars (avoid float precision issues), tracks Claude API spend
- **ON DELETE RESTRICT** for workflow: Can't delete workflow with assessment history (data integrity)
- **ON DELETE SET NULL** for created_by: Keep assessment if user deleted

**Journey Connection**: Step 2-5 - Central entity for entire validation process

---

### 7. assessment_documents

**Purpose**: Junction table linking assessments to uploaded documents per bucket.

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| assessment_id | UUID | NOT NULL, REFERENCES assessments(id) ON DELETE CASCADE | Parent assessment |
| bucket_id | UUID | NOT NULL, REFERENCES buckets(id) ON DELETE RESTRICT | Document category |
| file_name | VARCHAR(255) | NOT NULL | Original filename (e.g., "technical-spec.pdf") |
| file_size_bytes | INTEGER | NOT NULL, CHECK | File size (validation: max 50MB) |
| file_type | VARCHAR(50) | NOT NULL, CHECK | MIME type (application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document) |
| storage_key | TEXT | NOT NULL, UNIQUE | Vercel Blob / S3 key for retrieval |
| uploaded_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Upload timestamp |

**Indexes**:
- Primary key (id)
- `idx_assessment_docs_assessment_id`: ON (assessment_id) - "get all docs for assessment"
- `idx_assessment_docs_bucket_id`: ON (bucket_id) - "docs per bucket"
- `idx_assessment_docs_storage_key`: UNIQUE ON (storage_key) - fast retrieval

**Relationships**:
- Belongs to: `assessments`, `buckets`

**Design Decisions**:
- **storage_key UNIQUE**: Prevent duplicate uploads, fast blob retrieval
- **file_size_bytes CHECK**: Enforce max size at DB level (> 0, < 52428800 = 50MB)
- **file_type CHECK**: Only allow PDF, DOCX (application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- **ON DELETE RESTRICT** for bucket: Can't delete bucket with uploaded documents (referential integrity)

**Journey Connection**: Step 2 - Project Handler uploads documents to buckets

---

### 8. assessment_results

**Purpose**: Per-criteria validation results with AI evidence (Step 3 output, Step 4 display).

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| assessment_id | UUID | NOT NULL, REFERENCES assessments(id) ON DELETE CASCADE | Parent assessment |
| criteria_id | UUID | NOT NULL, REFERENCES criteria(id) ON DELETE RESTRICT | Validated criteria |
| pass | BOOLEAN | NOT NULL | Pass (true) or Fail (false) |
| confidence | VARCHAR(50) | NOT NULL, DEFAULT 'high', CHECK | Confidence level (high, medium, low) |
| evidence_document_id | UUID | NULLABLE, REFERENCES assessment_documents(id) ON DELETE SET NULL | Document containing evidence |
| evidence_page | INTEGER | NULLABLE | Page number (for PDFs) |
| evidence_section | TEXT | NULLABLE | Section reference (e.g., "3.2 Test Results") |
| reasoning | TEXT | NOT NULL | AI explanation (why pass/fail) |
| ai_response_raw | JSONB | NULLABLE | Full Claude JSON response (debugging) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Result timestamp |

**Indexes**:
- Primary key (id)
- `idx_assessment_results_assessment_id`: ON (assessment_id) - "get all results for assessment"
- `idx_assessment_results_criteria_id`: ON (criteria_id) - "results per criteria across assessments"
- `idx_assessment_results_pass`: ON (assessment_id, pass) - "failed criteria" queries
- `idx_assessment_results_confidence`: ON (confidence) WHERE confidence IN ('medium', 'low') - filter uncertain results

**Relationships**:
- Belongs to: `assessments`, `criteria`, `assessment_documents` (evidence source)

**Design Decisions**:
- **pass NOT NULL**: Always boolean (no "uncertain" - use confidence for that)
- **confidence CHECK**: Enforce valid levels (high, medium, low)
- **evidence_* columns**: All nullable (some criteria don't have document evidence, e.g., "workflow completeness")
- **ai_response_raw JSONB**: Store full Claude response (helps debug false positives/negatives)
- **JSONB not JSON**: Binary format, faster queries, supports indexing
- **ON DELETE RESTRICT** for criteria: Can't delete criteria with historical results

**Journey Connection**: Step 3 - AI generates results, Step 4 - Display to user with evidence

---

### 9. audit_logs

**Purpose**: SOC2/ISO 27001 compliance audit trail. Every user action logged.

**Columns**:
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| organization_id | UUID | NOT NULL, REFERENCES organizations(id) ON DELETE CASCADE | Organization context |
| user_id | UUID | NULLABLE, REFERENCES users(id) ON DELETE SET NULL | Actor (nullable for system actions) |
| action | VARCHAR(100) | NOT NULL | Action type (workflow_created, assessment_started, document_uploaded, etc.) |
| resource_type | VARCHAR(50) | NOT NULL | Resource affected (workflow, assessment, document, user) |
| resource_id | UUID | NULLABLE | Specific resource (if applicable) |
| metadata | JSONB | NULLABLE | Additional context (e.g., {changed_fields: ["name", "description"]}) |
| ip_address | VARCHAR(45) | NULLABLE | IPv4 (15 chars) or IPv6 (45 chars) |
| user_agent | TEXT | NULLABLE | Browser/client info |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When action occurred |

**Indexes**:
- Primary key (id)
- `idx_audit_logs_org_id`: ON (organization_id) - org-specific audits
- `idx_audit_logs_user_id`: ON (user_id) - user activity reports
- `idx_audit_logs_created`: ON (created_at DESC) - recent activity
- `idx_audit_logs_action`: ON (action) - filter by action type
- `idx_audit_logs_resource`: ON (resource_type, resource_id) - "audit trail for resource X"

**Relationships**:
- Belongs to: `organizations`, `users` (nullable)

**Design Decisions**:
- **Immutable**: No UPDATE or DELETE (audit logs never change) - enforce via app logic or triggers
- **user_id NULLABLE**: System actions (e.g., scheduled jobs) have no user
- **metadata JSONB**: Flexible structure (different actions need different context)
- **ip_address VARCHAR(45)**: Supports IPv6 (max 39 chars + padding)
- **created_at only**: No updated_at (immutable records)
- **No ON DELETE CASCADE**: Keeps audit logs even if user deleted (compliance requirement)

**Journey Connection**: All steps - Track every action for security audits, debugging, compliance

---

## Query Patterns & Performance

### Common Queries (with indexes)

**1. Show all workflows for organization (Step 1 dashboard)**:
```sql
SELECT * FROM workflows
WHERE organization_id = $1 AND is_active = TRUE
ORDER BY created_at DESC;
```
- Uses: `idx_workflows_org_id`, `idx_workflows_active`

**2. Get workflow with buckets and criteria (Step 1 detail)**:
```sql
-- Workflow
SELECT * FROM workflows WHERE id = $1;

-- Buckets (ordered)
SELECT * FROM buckets
WHERE workflow_id = $1
ORDER BY order_index ASC;

-- Criteria (ordered)
SELECT * FROM criteria
WHERE workflow_id = $1
ORDER BY order_index ASC;
```
- Uses: Primary keys, `idx_buckets_workflow_id`, `idx_criteria_workflow_id`

**3. Get assessment with results (Step 4 display)**:
```sql
-- Assessment
SELECT * FROM assessments WHERE id = $1;

-- Results with criteria details
SELECT ar.*, c.name AS criteria_name, c.description
FROM assessment_results ar
JOIN criteria c ON ar.criteria_id = c.id
WHERE ar.assessment_id = $1
ORDER BY c.order_index ASC;
```
- Uses: Primary keys, `idx_assessment_results_assessment_id`

**4. Recent assessments for user (dashboard)**:
```sql
SELECT a.*, w.name AS workflow_name
FROM assessments a
JOIN workflows w ON a.workflow_id = w.id
WHERE a.created_by = $1
ORDER BY a.created_at DESC
LIMIT 20;
```
- Uses: `idx_assessments_created_by`, `idx_assessments_created`

**5. Billing: Count assessments per org per month**:
```sql
SELECT
  organization_id,
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS assessment_count,
  SUM(ai_cost_cents) AS total_cost_cents
FROM assessments
WHERE organization_id = $1
  AND created_at >= $2 AND created_at < $3
GROUP BY organization_id, month;
```
- Uses: `idx_assessments_org_id`, `idx_assessments_created`

**6. Performance monitoring: Average processing time**:
```sql
SELECT
  AVG(duration_ms) AS avg_duration_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_duration_ms
FROM assessments
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '7 days';
```
- Uses: `idx_assessments_status`, `idx_assessments_created`

---

## Data Types Rationale

**UUID vs BIGINT for Primary Keys**:
- ✅ **Chose UUID**:
  - Non-guessable (security: can't enumerate assessments by incrementing ID)
  - Distributed-safe (can generate IDs in frontend, multiple backend instances)
  - Merge-friendly (no ID conflicts across environments)
- ❌ **Not BIGINT**:
  - Guessable (easy to scrape all assessments)
  - Requires central ID generation (not distributed)
  - 16 bytes vs 8 bytes (storage cost acceptable for security benefits)

**TIMESTAMPTZ vs TIMESTAMP**:
- ✅ **Chose TIMESTAMPTZ** (timezone-aware):
  - Global customers (notified bodies in different timezones)
  - Server timezone changes don't affect data
  - Converts to user's timezone in application
- ❌ **Not TIMESTAMP**: Timezone-naive, ambiguous for global apps

**JSONB vs JSON**:
- ✅ **Chose JSONB** (binary format):
  - Faster queries (pre-parsed)
  - Supports indexing (`CREATE INDEX ON assessment_results USING GIN (ai_response_raw)`)
  - Removes duplicate keys, enforces valid JSON
- ❌ **Not JSON**: Text storage, slower queries, no indexing

**VARCHAR(255) vs TEXT**:
- **VARCHAR(255)**: Short strings with known max length (name, email, role)
- **TEXT**: Long strings with unknown length (description, reasoning, error messages)
- PostgreSQL treats them similarly (no performance difference), but VARCHAR documents intent

**UUID[] vs Junction Table** (criteria → buckets):
- ✅ **Chose UUID[] array**:
  - Simpler (1 table instead of 3: criteria, buckets, criteria_buckets)
  - Fewer joins (array containment query)
  - Typical use case: 2-3 buckets per criteria (small arrays)
- ❌ **Not junction table**: More tables, more joins, overkill for small M:N
- **When to reconsider**: If criteria apply to >10 buckets (array gets large)

**INTEGER vs NUMERIC** (money, measurements):
- **INTEGER (cents)**: Use for money (ai_cost_cents, file_size_bytes) - no float precision issues
- **NUMERIC(precision, scale)**: Use for measurements with decimals (not needed in this schema)

---

## Constraints & Data Integrity

### CHECK Constraints (DB-level validation)

**Status enums** (prevent invalid states):
```sql
-- Organizations
subscription_tier CHECK (subscription_tier IN ('trial', 'professional', 'enterprise'))
subscription_status CHECK (subscription_status IN ('active', 'cancelled', 'suspended'))

-- Users
role CHECK (role IN ('process_manager', 'project_handler', 'admin'))

-- Assessments
status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))

-- Assessment Results
confidence CHECK (confidence IN ('high', 'medium', 'low'))
```

**Positive integers** (prevent negative values):
```sql
file_size_bytes CHECK (file_size_bytes > 0)
duration_ms CHECK (duration_ms >= 0)
ai_cost_cents CHECK (ai_cost_cents >= 0)
order_index CHECK (order_index >= 0)
```

**File types** (whitelist):
```sql
file_type CHECK (file_type IN ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
```

### Foreign Key Constraints (referential actions)

**CASCADE** (child deleted when parent deleted):
- `organizations.id` → `users.organization_id`: Delete users when org deleted (GDPR)
- `workflows.id` → `buckets.workflow_id`: Delete buckets when workflow deleted
- `assessments.id` → `assessment_results.assessment_id`: Delete results when assessment deleted

**SET NULL** (child orphaned when parent deleted):
- `users.id` → `workflows.created_by`: Keep workflow if creator leaves
- `users.id` → `assessments.created_by`: Keep assessment if creator leaves
- `assessment_documents.id` → `assessment_results.evidence_document_id`: Keep result if doc deleted

**RESTRICT** (prevent delete if child exists):
- `workflows.id` → `assessments.workflow_id`: Can't delete workflow with assessment history
- `criteria.id` → `assessment_results.criteria_id`: Can't delete criteria with results
- `buckets.id` → `assessment_documents.bucket_id`: Can't delete bucket with uploaded docs

**Rationale**:
- CASCADE: Use when child is meaningless without parent
- SET NULL: Use when child should survive parent deletion (historical records)
- RESTRICT: Use to prevent accidental data loss (audit trail preservation)

---

## Scaling Considerations

### Current Capacity (Year 1-3)

**Expected Load**:
- 5 organizations × 50 users each = 250 users
- 10 workflows per org × 5 = 50 workflows
- 2,000 assessments/month × 12 = 24,000 assessments/year
- 10 criteria per assessment × 24,000 = 240,000 results/year

**PostgreSQL Handles**:
- Millions of rows easily (current scale: 250K rows/year)
- Vercel Postgres free tier: 256MB storage (sufficient for Year 1)
- Upgrade to Pro ($20/month): 10GB storage (sufficient through Year 5)

### Bottlenecks & Solutions (Year 5+)

**If assessments table > 1M rows**:
- **Partition by month**: `CREATE TABLE assessments_2026_01 PARTITION OF assessments FOR VALUES FROM ('2026-01-01') TO ('2026-02-01')`
- **Archive old assessments**: Move completed assessments >2 years old to cold storage (S3 + restore on demand)

**If assessment_results > 10M rows**:
- **Partition with assessments**: Same monthly partitioning (child table follows parent)
- **Partial indexes**: Only index recent data (`WHERE created_at > NOW() - INTERVAL '1 year'`)

**If query latency > 1 second**:
- **Read replicas**: PostgreSQL streaming replication (1 write, N read replicas)
- **Caching layer**: Redis cache for frequent queries (workflows, criteria)
- **Materialized views**: Pre-compute dashboard stats (`REFRESH MATERIALIZED VIEW CONCURRENTLY`)

**If writes > 1000/second**:
- **Connection pooling**: PgBouncer (reuse connections, reduce overhead)
- **Batch inserts**: Insert 100 assessment_results at once (reduce round-trips)
- **Async writes**: Use message queue (Celery) for non-critical writes (audit logs)

---

## Migration Files

### Alembic (Python/FastAPI)

**Initial Migration**:

File: `alembic/versions/001_initial_schema.py`

```python
"""Initial Qteria schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-17 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subscription_tier', sa.String(50), server_default='trial', nullable=False),
        sa.Column('subscription_status', sa.String(50), server_default='active', nullable=False),
        sa.Column('subscription_start_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("subscription_tier IN ('trial', 'professional', 'enterprise')", name='check_subscription_tier'),
        sa.CheckConstraint("subscription_status IN ('active', 'cancelled', 'suspended')", name='check_subscription_status'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_organizations_status', 'organizations', ['subscription_status'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=True),
        sa.Column('auth_provider_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), server_default='project_handler', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('process_manager', 'project_handler', 'admin')", name='check_user_role'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('auth_provider_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_org_id', 'users', ['organization_id'])
    op.create_index('idx_users_auth_id', 'users', ['auth_provider_id'], unique=True)
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('created_by', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workflows_org_id', 'workflows', ['organization_id'])
    op.create_index('idx_workflows_created_by', 'workflows', ['created_by'])
    op.create_index('idx_workflows_active', 'workflows', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create buckets table
    op.create_table(
        'buckets',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('required', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('order_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('order_index >= 0', name='check_bucket_order_positive'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_buckets_workflow_id', 'buckets', ['workflow_id'])
    op.create_index('idx_buckets_order', 'buckets', ['workflow_id', 'order_index'])

    # Create criteria table
    op.create_table(
        'criteria',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('applies_to_bucket_ids', postgresql.ARRAY(postgresql.UUID()), nullable=True),
        sa.Column('example_text', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('order_index >= 0', name='check_criteria_order_positive'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_criteria_workflow_id', 'criteria', ['workflow_id'])
    op.create_index('idx_criteria_order', 'criteria', ['workflow_id', 'order_index'])
    op.create_index('idx_criteria_bucket_gin', 'criteria', ['applies_to_bucket_ids'], postgresql_using='gin')

    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(), nullable=False),
        sa.Column('created_by', postgresql.UUID(), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('ai_cost_cents', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name='check_assessment_status'),
        sa.CheckConstraint('duration_ms >= 0', name='check_duration_positive'),
        sa.CheckConstraint('ai_cost_cents >= 0', name='check_cost_positive'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_assessments_org_id', 'assessments', ['organization_id'])
    op.create_index('idx_assessments_workflow_id', 'assessments', ['workflow_id'])
    op.create_index('idx_assessments_created_by', 'assessments', ['created_by'])
    op.create_index('idx_assessments_status', 'assessments', ['status'])
    op.create_index('idx_assessments_created', 'assessments', [sa.text('created_at DESC')])
    op.create_index('idx_assessments_org_status', 'assessments', ['organization_id', 'status'])

    # Create assessment_documents table
    op.create_table(
        'assessment_documents',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(), nullable=False),
        sa.Column('bucket_id', postgresql.UUID(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('storage_key', sa.Text(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('file_size_bytes > 0', name='check_file_size_positive'),
        sa.CheckConstraint("file_type IN ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')", name='check_file_type'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bucket_id'], ['buckets.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_key')
    )
    op.create_index('idx_assessment_docs_assessment_id', 'assessment_documents', ['assessment_id'])
    op.create_index('idx_assessment_docs_bucket_id', 'assessment_documents', ['bucket_id'])
    op.create_index('idx_assessment_docs_storage_key', 'assessment_documents', ['storage_key'], unique=True)

    # Create assessment_results table
    op.create_table(
        'assessment_results',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(), nullable=False),
        sa.Column('criteria_id', postgresql.UUID(), nullable=False),
        sa.Column('pass', sa.Boolean(), nullable=False),
        sa.Column('confidence', sa.String(50), server_default='high', nullable=False),
        sa.Column('evidence_document_id', postgresql.UUID(), nullable=True),
        sa.Column('evidence_page', sa.Integer(), nullable=True),
        sa.Column('evidence_section', sa.Text(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('ai_response_raw', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("confidence IN ('high', 'medium', 'low')", name='check_confidence_level'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['criteria_id'], ['criteria.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['evidence_document_id'], ['assessment_documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_assessment_results_assessment_id', 'assessment_results', ['assessment_id'])
    op.create_index('idx_assessment_results_criteria_id', 'assessment_results', ['criteria_id'])
    op.create_index('idx_assessment_results_pass', 'assessment_results', ['assessment_id', 'pass'])
    op.create_index('idx_assessment_results_confidence', 'assessment_results', ['confidence'], postgresql_where=sa.text("confidence IN ('medium', 'low')"))

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_org_id', 'audit_logs', ['organization_id'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_created', 'audit_logs', [sa.text('created_at DESC')])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('assessment_results')
    op.drop_table('assessment_documents')
    op.drop_table('assessments')
    op.drop_table('criteria')
    op.drop_table('buckets')
    op.drop_table('workflows')
    op.drop_table('users')
    op.drop_table('organizations')
```

**Apply Migration**:
```bash
# Initialize Alembic (if not already)
alembic init alembic

# Copy migration file
cp product-guidelines/07-database-schema/alembic/versions/001_initial_schema.py alembic/versions/

# Run migration
alembic upgrade head

# Verify
psql $DATABASE_URL -c "\dt"  # List tables
```

---

## What We DIDN'T Choose (And Why)

### 1. NoSQL / MongoDB

**What it is**: Schema-less document database, stores JSON documents, no fixed structure

**Why not**:
- **Journey has stable entities**: workflows, buckets, criteria have predictable structure (won't change weekly)
- **Relationships matter**: user → workflows → assessments is naturally relational (clearer in SQL)
- **ACID transactions needed**: Billing calculations (can't lose assessment records for invoicing)
- **PostgreSQL JSONB provides flexibility**: Store AI results in JSONB (variable structure) while keeping relational benefits for core data
- **Team expertise**: Tech stack shows FastAPI + PostgreSQL (team comfortable with SQL)

**When to reconsider**:
- IF schema changes weekly (product pivoting constantly, entities unstable)
- IF documents have highly variable structure per type (e.g., 50 different certification types, each with unique fields)
- IF need horizontal sharding immediately (MongoDB distributes more easily)

**Example where MongoDB wins**: CMS with 100+ content types, each with different fields. Qteria has ~10 tables with stable structure.

---

### 2. Soft Deletes (deleted_at column)

**What it is**: Instead of `DELETE`, set `deleted_at = NOW()`, filter with `WHERE deleted_at IS NULL`

**Why not**:
- **GDPR compliance**: Users have "right to be forgotten" - must actually DELETE data, not just hide it
- **Query complexity**: Every query needs `WHERE deleted_at IS NULL` (easy to forget, causes bugs)
- **Index bloat**: Indexes grow with soft-deleted records (slower queries over time)
- **Billing accuracy**: Don't want to accidentally count deleted assessments in billing queries

**When to reconsider**:
- IF undo feature required ("restore deleted workflow for 30 days")
- IF legal requirement to retain deleted data for N months (beyond audit logs)
- IF ORM has built-in soft delete support (handles WHERE clause automatically)

**Current approach**: Hard delete with audit logs (immutable history in `audit_logs` table satisfies compliance)

---

### 3. Event Sourcing / CQRS

**What it is**: Store all changes as events (WorkflowCreated, AssessmentStarted, ResultsGenerated), rebuild state from event log

**Why not**:
- **Journey is CRUD, not event-driven**: Assessments have simple lifecycle (created → processing → completed) - no complex state machine
- **Complexity is massive**: Event store, event handlers, projections, eventual consistency, snapshots
- **Team size is small**: 1-2 engineers can't maintain complex architecture (solo founder initially)
- **No audit requirement justifies complexity**: Simple audit_logs table satisfies SOC2/ISO 27001 (immutable log of actions)

**When to reconsider**:
- IF regulatory requirement for complete audit trail of every field change (financial trading systems)
- IF need to replay history ("what would assessment look like with old AI model?")
- IF team has event sourcing expertise and time to build/maintain infrastructure

**Example where Event Sourcing wins**: Financial trading system where every order change must be auditable and replayable for compliance. Qteria = simpler use case.

---

### 4. Multi-Table Inheritance / Polymorphic Associations

**What it is**: Base `workflows` table + subclasses (`ComplianceWorkflow`, `QualityWorkflow`) with type discriminator, separate tables per type

**Why not**:
- **All workflows are similar**: Compliance workflows have same structure (buckets + criteria) regardless of certification type
- **No type-specific logic**: Assessment process is identical for all workflow types (Step 3 AI validation = same algorithm)
- **Queries become complex**: JOIN across 3+ tables, many NULL fields, harder to reason about
- **JSONB metadata column simpler**: If workflows need type-specific fields, add JSONB column (e.g., `metadata: {certification_type: "ISO13485"}`)

**When to reconsider**:
- IF workflow types have radically different structures (e.g., document workflows vs video workflows vs audio workflows)
- IF type-specific validation logic (each type has completely different assessment algorithm)
- IF querying specific type frequently ("show ONLY medical device workflows, never others")

**Example where polymorphism wins**: Media asset management with images (dimensions, color profile), videos (duration, codec), documents (page count). Each type has unique attributes.

---

### 5. Microservices with Separate Databases

**What it is**: Split into services (workflow-service, assessment-service, billing-service), each with own database

**Why not**:
- **Monolith is simpler**: Single FastAPI app, single PostgreSQL database (fewer moving parts)
- **ACID transactions across entities**: Assessments reference workflows + users + criteria (hard with distributed DBs)
- **Team size is small**: 1-2 engineers can't maintain 5 microservices + inter-service communication
- **No scaling bottleneck**: PostgreSQL handles millions of assessments (current scale: 24K/year = trivial)
- **Network overhead**: Cross-service API calls add latency (monolith = in-memory function calls)

**When to reconsider**:
- IF team grows to 20+ engineers (microservices enable parallel work by different teams)
- IF specific service needs different scaling (e.g., AI validation needs 10x more resources than workflows)
- IF need to deploy services independently (assessment-service update without touching workflow-service)

**Current approach**: Monolith with clear module boundaries (can extract to microservices later if needed). Start simple.

---

### 6. GraphQL with Relay-style Global IDs

**What it is**: GraphQL API with global object IDs (`Base64(typename:id)` like `"V29ya2Zsb3c6MTIz"`) instead of UUIDs

**Why not**:
- **API pattern is REST** (from architecture doc): GraphQL adds complexity without clear benefit for this use case
- **Global IDs obscure relationships**: Harder to debug, harder to write raw SQL, harder to understand data model
- **Team expertise**: Tech stack shows REST + FastAPI (team familiar with REST, not GraphQL)
- **Simpler is better for MVP**: UUIDs work perfectly, no need for encoding layer

**When to reconsider**:
- IF switching to GraphQL API (then global IDs are idiomatic)
- IF building public API for partners (obscure database IDs for security)
- IF need to refactor without breaking API contracts (global IDs allow moving entities between tables)

**Example where GraphQL wins**: Public API with complex nested queries ("fetch user, their workflows, assessment results, all in one request"). Qteria = simple REST endpoints.

---

## Setup Instructions

### Prerequisites

```bash
# Install PostgreSQL (if not using managed service)
brew install postgresql@15  # macOS
# or
sudo apt install postgresql-15  # Ubuntu

# Install Python dependencies
pip install alembic sqlalchemy psycopg2-binary
```

### Apply Migrations

```bash
# 1. Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/qteria"

# 2. Initialize Alembic (if new project)
alembic init alembic

# 3. Copy migration file to your project
# (The migration file is in the documentation above)

# 4. Run migration
alembic upgrade head

# 5. Verify tables created
psql $DATABASE_URL -c "\dt"
# Should see: organizations, users, workflows, buckets, criteria, assessments, assessment_documents, assessment_results, audit_logs

# 6. Verify indexes
psql $DATABASE_URL -c "\di"
# Should see 18+ indexes
```

### Generate SQLAlchemy Models (optional)

```bash
# Install sqlacodegen
pip install sqlacodegen

# Generate models from database
sqlacodegen $DATABASE_URL > app/models.py

# Or manually define models in app/models.py (recommended for control)
```

---

## Testing Strategy

### Seed Data (for development/testing)

```sql
-- Insert test organization
INSERT INTO organizations (id, name, subscription_tier, subscription_status)
VALUES ('00000000-0000-0000-0000-000000000001', 'Test TÜV SÜD', 'professional', 'active');

-- Insert test users
INSERT INTO users (id, organization_id, auth_provider_id, email, name, role)
VALUES
  ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'auth0|test_pm', 'pm@tuv.com', 'Process Manager Test', 'process_manager'),
  ('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'auth0|test_ph', 'ph@tuv.com', 'Project Handler Test', 'project_handler');

-- Insert test workflow
INSERT INTO workflows (id, organization_id, created_by, name, description)
VALUES ('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'Medical Device - Class II', 'Pre-assessment for Class II medical devices');

-- Insert test buckets
INSERT INTO buckets (id, workflow_id, name, required, order_index)
VALUES
  ('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000004', 'Technical Documentation', TRUE, 0),
  ('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000004', 'Test Reports', TRUE, 1),
  ('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000004', 'Risk Assessment', FALSE, 2);

-- Insert test criteria
INSERT INTO criteria (id, workflow_id, name, description, applies_to_bucket_ids, order_index)
VALUES
  ('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000004', 'All documents signed', 'All documents must have authorized signatures', NULL, 0),
  ('00000000-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000004', 'Test summary present', 'Test report must include pass/fail summary section', ARRAY['00000000-0000-0000-0000-000000000006']::UUID[], 1);
```

### Query Tests

```python
# Test: Fetch workflow with related data
import pytest
from sqlalchemy import select
from app.models import Workflow, Bucket, Criteria

def test_fetch_workflow_with_relations(db_session):
    workflow = db_session.query(Workflow).filter_by(
        id='00000000-0000-0000-0000-000000000004'
    ).first()

    assert workflow is not None
    assert workflow.name == 'Medical Device - Class II'
    assert len(workflow.buckets) == 3  # 3 buckets
    assert len(workflow.criteria) == 2  # 2 criteria
```

---

## Document Control

**Status**: Final
**Last Updated**: November 2025
**Next Review**: After MVP launch (Q2 2026), review query performance
**Owner**: Founder
**Database Version**: PostgreSQL 15+
**Migration Status**: v001_initial_schema

---

**Schema Summary**: 9 tables supporting workflow-based document validation. Multi-tenant (organization-based), WCAG/SOC2 compliant (audit logs), optimized for journey (18 strategic indexes), flexible AI results (JSONB), scales to millions of rows (partitioning strategy defined). UUID primary keys, timezone-aware timestamps, CHECK constraints for data integrity.
