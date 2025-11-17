# Architecture Principles: Qteria

> **Derived from**: product-guidelines/02-tech-stack.md and journey requirements

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER (Browser)                         │
│                     Project Handler / Process Manager           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14+)                       │
│                                                                 │
│  • Workflow Builder UI (create buckets + criteria)             │
│  • Document Upload (drag-drop PDFs)                            │
│  • Results Display (evidence-based pass/fail)                  │
│  • Auth (Auth.js → Clerk when revenue)                         │
│                                                                 │
│  Hosted on: Vercel                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API (HTTPS)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                    │
│                                                                 │
│  • Workflow CRUD API                                           │
│  • Document Processing (PDF parsing, validation)               │
│  • Assessment Engine (triggers AI validation)                  │
│  • Results API (serve evidence-based results)                  │
│                                                                 │
│  Hosted on: Railway / Render                                   │
└─────┬─────────────┬─────────────┬────────────────┬──────────────┘
      │             │             │                │
      │             │             │                │
      ▼             ▼             ▼                ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌─────────────┐
│PostgreSQL│  │  Redis   │  │ Vercel Blob  │  │   Claude    │
│          │  │(Upstash) │  │  (Storage)   │  │ 3.5 Sonnet  │
│          │  │          │  │              │  │  (AI API)   │
│Workflows │  │Background│  │  PDFs        │  │             │
│Criteria  │  │Job Queue │  │  Encrypted   │  │ Evidence-   │
│Results   │  │(Celery)  │  │              │  │ based       │
│Users     │  │          │  │              │  │ Validation  │
└──────────┘  └──────────┘  └──────────────┘  └─────────────┘
   Vercel       Upstash        Vercel            Anthropic
   Postgres     Redis          Blob              API
```

**Key Design Decisions**:
1. **Monolith architecture** (Next.js + FastAPI) - not microservices (solo founder, simpler deployment)
2. **Background jobs** (Celery + Redis) - AI validation takes <10 min, async processing required
3. **API-first backend** (FastAPI REST endpoints) - enables future integrations, mobile app
4. **Evidence-based storage** (PostgreSQL stores exact page/section references from AI)
5. **Data privacy by design** (PDFs encrypted in Blob, AI with zero-retention, audit logs in PostgreSQL)

---

## Core Architectural Principles

### 1. Journey-Step Optimization (Optimize Critical Path, Not Theoretical Scale)

**Principle**: Optimize architecture for **Step 3** (AI validation in <10 minutes), not for scale we don't have.

**Application**:

**Step 1** (Process Manager Creates Workflow):
- **Requirement**: Simple CRUD (create workflow, add buckets, define criteria)
- **Architecture**: FastAPI REST endpoints → PostgreSQL relational tables (workflows, buckets, criteria)
- **Why**: Relational structure natural for workflow → buckets → criteria hierarchy. JSONB for flexible criteria definitions (different types of checks).
- **Optimization**: Not needed - CRUD is fast enough. Focus elsewhere.

**Step 2** (Project Handler Uploads Documents):
- **Requirement**: Drag-drop PDFs (50+ pages), upload to storage, validate formats
- **Architecture**: Next.js file upload → Vercel Blob (encrypted storage) → FastAPI (parse PDF metadata)
- **Why**: Vercel Blob handles large files, encryption at rest. FastAPI validates file type/size before storing.
- **Optimization**: Streaming upload (don't block browser), progress indicators, chunked upload for large files (>10MB)

**Step 3** (AI Validates & Returns Evidence-Based Results) ⭐ **CRITICAL PATH**:
- **Requirement**: <10 min processing, extract text from PDFs, validate against criteria, link evidence to exact pages/sections
- **Architecture**: FastAPI triggers Celery background job → PDF parsing (PyPDF2/pdfplumber) → Claude API (validate each criteria) → Store results in PostgreSQL with evidence metadata → Notify frontend (email or polling)
- **Why**: AI validation can take 5-10 min (Claude processes 50-page PDFs). Background job prevents frontend timeout. Celery + Redis queue handles retries, monitoring.
- **Optimization**:
  - **PDF parsing parallelization**: Parse all docs in assessment concurrently (not sequential)
  - **Claude batch API**: Send multiple criteria checks in single prompt (reduce API round-trips from 10 calls → 1 call)
  - **Caching**: Store parsed PDF text in PostgreSQL (if re-assessment, don't re-parse, just re-validate)
  - **Target**: P95 processing time <10 min (95% of assessments complete in <10 min)

**Step 4** (Re-Run Assessment):
- **Requirement**: Replace document, trigger new validation
- **Architecture**: Frontend replaces file in Vercel Blob → FastAPI triggers new Celery job (reuses workflow, new docs)
- **Why**: Same flow as Step 3, but faster (workflows already exist, users know what to expect)
- **Optimization**: Partial re-assessment (only re-check criteria for replaced document, not all docs) - saves AI cost and time

**Step 5** (Export Validation Report):
- **Requirement**: Generate PDF summary (pass/fail per criteria, evidence links)
- **Architecture**: FastAPI generates PDF using ReportLab/WeasyPrint → Store in Vercel Blob → Return download link
- **Why**: Backend generates PDFs (Next.js could do it, but FastAPI has better Python PDF libraries)
- **Optimization**: Not critical (happens after validation). Cache generated reports (if same assessment requested twice, serve cached PDF)

**Anti-Pattern**: Don't optimize Step 1/2/5 prematurely. 99% of value is Step 3 speed and accuracy.

---

### 2. Boring Technology + Strategic Innovation

**Principle**: Use proven tech (90%), innovate only where differentiated (10%).

**Boring (Proven) Technology**:
- ✅ **Next.js**: Battle-tested React framework, millions of apps
- ✅ **FastAPI**: Modern Python framework, widely adopted for APIs
- ✅ **PostgreSQL**: 30+ years mature, handles billions of rows
- ✅ **Redis**: Industry standard for queues and caching
- ✅ **Vercel/Railway hosting**: Managed platforms, proven reliability

**Strategic Innovation** (Where We Differentiate):
- 🚀 **Evidence-based AI prompting**: Custom prompt engineering to make Claude return `{pass: false, page: 8, section: "3.2", reason: "..."}` - not generic AI usage
- 🚀 **PDF section detection**: Parse PDFs to identify section boundaries (not just page numbers) - enables precise evidence links
- 🚀 **Confidence scoring algorithm**: Classify AI responses into green/yellow/red based on uncertainty markers in text
- 🚀 **Feedback loop for AI improvement**: Store user corrections (false positives/negatives), use to refine prompts over time

**Why This Balance**:
- Boring tech reduces operational risk (fewer surprises, easier hiring, abundant Stack Overflow answers)
- Strategic innovation focuses energy on differentiation (evidence-based validation, not reinventing databases)
- Solo founder can move fast (don't waste time debugging obscure frameworks)

**Anti-Pattern**: Don't use bleeding-edge tech (Rust, Deno, edge databases, etc.) unless journey explicitly requires it. We don't.

---

### 3. API-First Design (Enable Future Integrations)

**Principle**: Backend exposes clean REST API, frontend is one client (not tightly coupled).

**Application**:

**Backend API Structure** (FastAPI):
```
POST   /api/v1/workflows              # Create workflow
GET    /api/v1/workflows/:id          # Get workflow details
PUT    /api/v1/workflows/:id          # Update workflow
DELETE /api/v1/workflows/:id          # Delete workflow

POST   /api/v1/assessments            # Start assessment
GET    /api/v1/assessments/:id        # Get assessment status
GET    /api/v1/assessments/:id/results # Get results (evidence)

POST   /api/v1/documents              # Upload document
GET    /api/v1/documents/:id          # Download document
DELETE /api/v1/documents/:id          # Delete document

GET    /api/v1/users/me               # Current user
GET    /api/v1/users/:id/workflows    # User's workflows
```

**Why API-First**:
- ✅ **Future mobile app**: React Native app can consume same API (no backend rewrite)
- ✅ **Customer integrations**: Notified bodies can integrate Qteria with project management tools (call our API)
- ✅ **Marketplace**: Consultants publishing workflows hit same API (consistent interface)
- ✅ **Testing**: API endpoints testable independent of frontend (Pytest can test FastAPI without browser)

**Frontend as Client**:
- Next.js calls FastAPI endpoints (not direct database access)
- Auth tokens (JWT) passed in headers
- Frontend doesn't know about PostgreSQL, Redis, Blob - just API contracts

**Versioning**:
- `/api/v1/` prefix allows breaking changes in `/api/v2/` later without breaking existing clients
- Start with v1, only introduce v2 if major changes needed (rare for B2B SaaS)

**Anti-Pattern**: Don't tightly couple Next.js to FastAPI internals (e.g., Next.js calling Python functions directly via RPC). Keep clean HTTP boundary.

---

### 4. Fail-Safe Architecture (Reliability Over Performance)

**Principle**: In compliance/certification, reliability > speed. One missed error (false negative) = lost customer trust.

**Application**:

**Error Handling**:
- ✅ **PDF parsing fails**: Return clear error to user ("Document format not supported"), don't fail silently
- ✅ **Claude API timeout**: Retry 3x with exponential backoff, then fail gracefully ("Assessment timed out, please try again")
- ✅ **Database connection lost**: Queue writes in Redis, replay when DB reconnects (no data loss)

**Validation Layers**:
1. **Frontend validation**: Check file type (PDF, DOCX only), file size (<50MB), required fields filled
2. **Backend validation**: Re-validate on server (don't trust frontend), scan for malicious files, check user permissions
3. **AI validation**: If Claude returns malformed JSON, parse it conservatively (mark as "uncertain" yellow, don't assume pass/fail)

**Graceful Degradation**:
- **Claude API down**: Show user "AI service temporarily unavailable, please try again in 10 min" (don't silently fail or return wrong results)
- **Vercel Blob down**: Queue uploads in backend, retry when storage recovers
- **Redis down**: Fall back to PostgreSQL-based queue (slower but works), alert founder to fix Redis

**Audit Trails**:
- **Every assessment logged**: Workflow ID, user ID, documents uploaded, criteria checked, AI responses, timestamp
- **Every AI call logged**: Prompt sent to Claude, response received, processing time, cost
- **Every error logged**: Sentry (error tracking), include user context, request details
- **Why**: SOC2/ISO 27001 require audit trails. Also helps debug false positives/negatives.

**Uptime Target**: 99.9% (not 99.99% - over-engineering for MVP). Allows ~40 min downtime/month.

**Anti-Pattern**: Don't prioritize "blazing fast" over "correct and reliable." Users tolerate 10-min processing, not incorrect results.

---

### 5. Observable & Debuggable (Measure Everything)

**Principle**: Can't improve what we don't measure. Solo founder needs visibility into system health.

**Application**:

**Metrics Collection**:
- **Business metrics**: Active Assessments, Completion Rate, AI Accuracy → track in PostgreSQL + weekly dashboard
- **Performance metrics**: API response time (P50, P95, P99), background job duration → Vercel Analytics, Railway metrics
- **Cost metrics**: Claude API spend per assessment, storage costs, database size → track in spreadsheet, set budget alerts
- **Error metrics**: Error rate (%), top 10 error types → Sentry

**Logging**:
- **Structured logs** (JSON format): `{"timestamp": "...", "level": "INFO", "event": "assessment_started", "user_id": "...", "workflow_id": "...", "duration_ms": 120}`
- **Log levels**: DEBUG (development only), INFO (assessment lifecycle), WARN (retries, degraded mode), ERROR (failures)
- **Log aggregation**: Vercel logs (frontend), Railway logs (backend), centralize in future if needed (Logtail, Datadog)

**Alerts**:
- **Critical**: P0 errors (all assessments failing, database down, Claude API key invalid) → Email + SMS to founder
- **Warning**: P1 issues (error rate >5%, slow processing >15 min, AI accuracy drop below 90%) → Email to founder
- **Info**: Daily summary (assessments run, revenue, top workflows used) → Email to founder

**Dashboards**:
- **Daily dashboard** (founder checks each morning):
  - Assessments completed yesterday
  - Error rate last 24 hours
  - AI accuracy last 7 days
  - Uptime last 24 hours
- **Weekly dashboard** (Monday review):
  - North Star trend (Assessments per Month)
  - Customer health scores (usage, NPS, support tickets)
  - Cost metrics (burn rate, gross margin)

**Anti-Pattern**: Don't collect metrics you won't act on. Focus on actionable insights (assessment speed, accuracy, errors), not vanity metrics (page views).

---

## Data Flow: Critical Journey Step (Step 3 - AI Validation)

### Detailed Step 3 Flow

```
1. User clicks "Start Assessment"
   ↓
2. Frontend → Backend: POST /api/v1/assessments
   {
     workflow_id: "abc123",
     document_ids: ["doc1", "doc2", "doc3"]
   }
   ↓
3. Backend (FastAPI):
   - Create assessment record in PostgreSQL (status: "pending")
   - Enqueue Celery background job (job_id: "xyz789")
   - Return to frontend: {assessment_id: "assess123", status: "pending", estimated_time: "5-10 min"}
   ↓
4. Frontend:
   - Show progress UI ("Assessment in progress... typically completes in 5-10 minutes")
   - Poll every 30 seconds: GET /api/v1/assessments/assess123
   ↓
5. Background Job (Celery worker):
   a. Fetch workflow (buckets + criteria) from PostgreSQL
   b. Download PDFs from Vercel Blob
   c. Parse PDFs (PyPDF2/pdfplumber):
      - Extract full text
      - Detect page boundaries
      - Identify sections (heuristics: headings, numbering, whitespace)
   d. For each criteria:
      - Build Claude prompt:
        """
        Validate this document against the following criteria:
        Criteria: "Test report must include pass/fail summary"
        Applies to: Bucket 2 (Test Reports)

        Document text: [extracted text from test-report.pdf]

        Return JSON:
        {
          "pass": true/false,
          "confidence": "high"/"medium"/"low",
          "evidence_page": 8,
          "evidence_section": "3.2 Test Results",
          "reasoning": "..."
        }
        """
      - Call Claude API (POST https://api.anthropic.com/v1/messages)
      - Parse response, store in memory
   e. Store all results in PostgreSQL:
      - assessment_results table: {assessment_id, criteria_id, pass, confidence, evidence_page, evidence_section, reasoning}
   f. Update assessment status: "completed"
   g. Send notification (email or in-app)
   ↓
6. Frontend (polling detects status change):
   - GET /api/v1/assessments/assess123/results
   - Display results page:
     ✅ GREEN: "Criteria 1: Signatures present - PASS"
     ❌ RED: "Criteria 2: Test summary missing - FAIL → [Link: test-report.pdf, page 8, section 3.2]"
   ↓
7. User clicks evidence link:
   - GET /api/v1/documents/doc2?page=8
   - Backend serves PDF with #page=8 anchor
   - Browser opens PDF at page 8
```

**Why This Architecture**:
- ✅ **Async processing**: Doesn't block frontend (user can navigate away, check back later)
- ✅ **Celery retries**: If Claude API times out, Celery retries 3x automatically
- ✅ **Polling vs. WebSocket**: Polling simpler for MVP (WebSocket adds complexity, not needed for 5-10 min jobs)
- ✅ **Evidence precision**: PDF parsing enables page + section linking (not just "page 8" but "page 8, section 3.2")
- ✅ **Structured AI output**: Claude returns JSON (not free text), easier to parse and display

**Bottlenecks**:
- **PDF parsing**: 50-page PDFs take 10-20 seconds to parse. **Mitigation**: Cache parsed text in PostgreSQL (if same document in future assessments, skip parsing)
- **Claude API**: 10 criteria × 10 seconds each = 100 seconds. **Mitigation**: Batch criteria in single prompt (reduce 10 calls → 1 call)
- **Celery workers**: 1 worker can process 1 assessment at a time. **Mitigation**: Scale to 3-5 workers on Railway (handles 3-5 concurrent assessments)

---

## Database Schema (Key Tables)

### Workflows
```sql
CREATE TABLE workflows (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Buckets
```sql
CREATE TABLE buckets (
  id UUID PRIMARY KEY,
  workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  required BOOLEAN DEFAULT TRUE,
  order_index INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Criteria
```sql
CREATE TABLE criteria (
  id UUID PRIMARY KEY,
  workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  applies_to_buckets UUID[], -- Array of bucket IDs
  example_text TEXT, -- Optional example for AI
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Assessments
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY,
  workflow_id UUID REFERENCES workflows(id),
  created_by UUID REFERENCES users(id),
  status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  estimated_duration_seconds INTEGER
);
```

### Assessment Documents (Junction Table)
```sql
CREATE TABLE assessment_documents (
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  bucket_id UUID REFERENCES buckets(id),
  document_id UUID, -- Vercel Blob file ID
  document_name VARCHAR(255),
  uploaded_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (assessment_id, bucket_id, document_id)
);
```

### Assessment Results
```sql
CREATE TABLE assessment_results (
  id UUID PRIMARY KEY,
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  criteria_id UUID REFERENCES criteria(id),
  pass BOOLEAN NOT NULL,
  confidence VARCHAR(50), -- high, medium, low
  evidence_page INTEGER,
  evidence_section TEXT,
  reasoning TEXT, -- AI explanation
  ai_response_raw JSONB, -- Full Claude response for debugging
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50), -- ProcessManager, ProjectHandler, Admin
  organization_id UUID REFERENCES organizations(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Organizations (Notified Bodies)
```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  subscription_tier VARCHAR(50), -- Pilot, Professional, Enterprise
  subscription_status VARCHAR(50), -- trial, active, cancelled
  subscription_start_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Audit Logs (SOC2/ISO 27001)
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR(100), -- workflow_created, assessment_started, document_uploaded, etc.
  resource_type VARCHAR(50),
  resource_id UUID,
  metadata JSONB, -- Additional context
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

**Why This Schema**:
- ✅ **Relational integrity**: Workflows → Buckets → Criteria (cascading deletes prevent orphaned data)
- ✅ **JSONB for flexibility**: `ai_response_raw` stores full Claude JSON (for debugging false positives)
- ✅ **Audit trail**: Every action logged with user context (SOC2 requirement)
- ✅ **Indexes**: Fast queries on common patterns (user_id, created_at, workflow_id)

---

## Scaling Strategy

### Current Capacity (MVP - Year 1)

**Expected Load** (TÜV SÜD pilot):
- 1 customer
- 5-10 active users
- 100-500 assessments/month
- ~3-15 concurrent assessments during peak hours

**Current Architecture Handles**:
- **Frontend (Vercel)**: Scales automatically, no limit for this traffic
- **Backend (Railway)**: 1 instance, 512MB RAM, 0.5 vCPU - handles 5-10 concurrent API requests
- **Celery workers**: 1 worker - processes 1 assessment at a time (queue others)
- **PostgreSQL (Vercel)**: Free tier (256MB) - handles 10K assessments easily
- **Vercel Blob**: 1GB free tier - ~20-50 assessments before paid tier
- **Claude API**: No rate limit concern at 100-500 assessments/month

**Bottleneck**: Celery (1 worker) - if 10 assessments start simultaneously, 9 wait in queue

**Solution**: Add 2-3 more Celery workers on Railway ($5-10/month each) - handles 3-4 concurrent assessments

---

### Bottlenecks & Solutions (Year 3 - 5 Customers)

**Expected Load**:
- 5 customers
- 25-50 active users
- 2,000 assessments/month (~66/day, ~3-5 concurrent during peak)

**Potential Bottlenecks**:

1. **Celery Workers**:
   - **Problem**: 1 worker can't process 3-5 concurrent assessments
   - **Solution**: Scale to 5 workers (1 per concurrent assessment) - Railway auto-scaling or manual replicas
   - **Cost**: $25-50/month (5 workers × $5-10 each)

2. **PostgreSQL**:
   - **Problem**: 2,000 assessments/month × 10 criteria each = 20K result rows/month = 240K rows/year (free tier limited)
   - **Solution**: Upgrade to Vercel Postgres Pro ($20/month) - handles millions of rows
   - **Cost**: $20/month

3. **Vercel Blob**:
   - **Problem**: 2,000 assessments × 3 docs each × 5MB avg = 30GB/month (exceeds 1GB free tier)
   - **Solution**: Migrate to AWS S3 ($0.023/GB = ~$0.70/month storage + $0.09/GB egress) or pay Vercel Blob ($0.15/GB)
   - **Cost**: $5-10/month

4. **Claude API**:
   - **Problem**: 2,000 assessments × $0.21 each = $420/month AI cost
   - **Solution**: Optimize prompts (batch criteria, cache common validations), or negotiate volume discount with Anthropic
   - **Cost**: $400-500/month (acceptable at $150K ARR)

5. **Backend API**:
   - **Problem**: More users → more API requests (CRUD workflows, fetch results)
   - **Solution**: Scale Railway backend horizontally (2-3 instances behind load balancer)
   - **Cost**: $20-50/month

**Total Infrastructure Cost (Year 3)**: $585/month (from earlier estimate)

**Scaling Triggers**:
- **Add Celery worker** when: Assessment queue time >30 min consistently
- **Upgrade PostgreSQL** when: Query time >1 second or storage >80% full
- **Migrate to S3** when: Vercel Blob costs >$20/month
- **Scale backend** when: API response time P95 >2 seconds

---

### Future Scale (Year 5+ - 20-50 Customers)

**Expected Load**:
- 20-50 customers
- 100-250 active users
- 10,000 assessments/month (~333/day, ~15-20 concurrent during peak)

**Architecture Evolution**:

1. **Horizontal Scaling**:
   - 10-20 Celery workers (handle 15-20 concurrent assessments)
   - 3-5 FastAPI backend instances (load balanced)
   - PostgreSQL read replicas (if query latency increases)

2. **Caching Layer**:
   - Redis for frequently accessed workflows (reduce PostgreSQL reads)
   - CDN for static assets (Vercel already does this)

3. **Database Optimization**:
   - Partition `assessment_results` table by month (archiving old assessments)
   - Indexes on common queries (workflow_id, user_id, created_at)
   - Query optimization (EXPLAIN ANALYZE slow queries)

4. **Monitoring & Observability**:
   - Upgrade to Datadog or New Relic (full APM)
   - Distributed tracing (track requests across frontend → backend → Claude API)
   - Cost monitoring (track spend per customer, gross margin per assessment)

**When to Consider Microservices** (Probably Never):
- If specific bottleneck emerges (e.g., PDF parsing is separate service)
- If team grows to 10+ engineers (separate teams own services)
- If compliance requires isolated services (e.g., PCI DSS for payments)

**For Now**: Monolith is correct choice. Optimize monolith before considering microservices.

---

**Connection to Journey**: Architecture optimizes **Step 3** (AI validation in <10 minutes) - the critical path where value is delivered. Background jobs (Celery) + evidence-based storage (PostgreSQL) + PDF parsing (PyPDF2) all serve Step 3 performance and accuracy.
