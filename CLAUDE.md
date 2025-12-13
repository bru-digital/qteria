# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Product Overview

**Qteria** is an AI-driven document pre-assessment platform for the TIC (Testing, Inspection, Certification) industry. The product helps Project Handlers validate certification documents 400x faster through evidence-based AI assessments.

**Core Mission**: Transform manual compliance checks (1-2 day turnaround via outsourced teams) into AI-powered assessments with evidence-based results in <10 minutes.

**Key Differentiators**:
- Evidence-based validation (AI links to exact page/section in documents)
- Radical simplicity (workflow → buckets → criteria → validate)
- Enterprise data privacy (zero-retention AI, SOC2/ISO 27001 compliance)
- White-glove support (dedicated relationship manager per customer)

---

## Tech Stack

### Frontend
- **Next.js 14+** with App Router (React 18, TypeScript strict mode)
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **Auth.js** for authentication (migrating to Clerk when revenue allows)
- **React Query** for data fetching
- **Zustand** for state management

### Backend
- **FastAPI** (Python web framework)
- **SQLAlchemy 2.0** ORM with **Alembic** migrations
- **Pydantic v2** for data validation
- **Celery** for background jobs (AI validation takes 5-10 min)
- **Redis** for job queue + caching
- **PyPDF2** + **pdfplumber** for PDF parsing
- **Claude 3.5 Sonnet** (Anthropic) for AI validation with zero-retention

### Infrastructure
- **PostgreSQL 15** (database with JSONB for flexible AI responses)
- **Redis 7** (cache + background job queue)
- **Vercel** (frontend hosting)
- **Railway/Render** (backend hosting)
- **Vercel Blob** (PDF storage, encrypted at rest)
- **GitHub Actions** (CI/CD)

### Architecture
- **Monorepo** with npm workspaces (`apps/web/` + `apps/api/`)
- **API-first design** (REST endpoints, versioned at `/v1/`)
- **Background jobs** for long-running AI validation (async via Celery + Redis)
- **Multi-tenancy** via organization-based row-level isolation

---

## Development Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- Git
- Neon PostgreSQL account (free tier available)
- Docker & Docker Compose (optional, only for local PostgreSQL)
- **libmagic** - System library for content-based file type detection
  - macOS: `brew install libmagic`
  - Ubuntu/Debian: `sudo apt-get install libmagic1`
  - Windows: Download from [here](https://github.com/pidydx/libmagicwin64) or use WSL

### Database Environment Separation

**CRITICAL: Never seed test data in production database!**

Create **3 separate Neon databases**:
1. **`qteria_dev`** - Development environment (your local work)
2. **`qteria_test`** - Test environment (for running pytest)
3. **`qteria_prod`** - Production environment (Vercel deployment)

Configure environment variables:
```bash
# .env (development)
DATABASE_URL=postgresql://...neon.tech/qteria_dev

# .env.test (testing)
DATABASE_URL=postgresql://...neon.tech/qteria_test

# Vercel environment variables (production)
DATABASE_URL=postgresql://...neon.tech/qteria_prod
```

### Quick Start

**IMPORTANT: This project deploys to Vercel + Neon PostgreSQL (cloud), NOT Docker.**

Docker is optional for local PostgreSQL/Redis development. In production, we use:
- **Frontend**: Vercel (Next.js)
- **Backend**: Railway/Render (FastAPI)
- **Database**: Neon PostgreSQL (cloud)
- **Redis**: Upstash Redis (cloud)

```bash
# 1. Clone and setup environment
cp .env.template .env
# Edit .env with required secrets (NEXTAUTH_SECRET, JWT_SECRET, ANTHROPIC_API_KEY, DATABASE_URL)

# 2. Install dependencies
npm install
cd apps/api && pip install -r requirements-dev.txt && cd ../..

# 3. Run database migrations (against Neon PostgreSQL)
npm run db:migrate

# 4. Start development servers
npm run dev          # Frontend (http://localhost:3000)
npm run dev:api      # Backend (http://localhost:8000)
```

**Optional: Local PostgreSQL with Docker** (only if you don't want to use Neon for local dev)
```bash
npm run docker:up    # Start local PostgreSQL + Redis
npm run docker:down  # Stop Docker services
```

### Common Commands

**Development:**
```bash
npm run dev                    # Start Next.js frontend
npm run dev:api                # Start FastAPI backend
npm run docker:up              # Start PostgreSQL + Redis
npm run docker:down            # Stop Docker services
npm run docker:logs            # View Docker logs
```

**Database:**
```bash
npm run db:migrate             # Apply migrations
npm run db:migrate:create "msg"  # Create new migration
npm run db:reset               # Reset database (⚠️ destroys data)
```

**Testing:**
```bash
npm run test                   # All tests
npm run lint                   # Lint all code
npm run type-check             # TypeScript/MyPy type checking
npm run format                 # Format with Prettier
npm run format:check           # Check formatting
```

**Backend-specific (from apps/api/):**
```bash
pytest                         # Run all tests
pytest --cov                   # With coverage
black .                        # Format Python
ruff check .                   # Lint Python
mypy app                       # Type check Python
celery -A app.workers worker   # Start Celery worker
```

**Frontend-specific (from apps/web/):**
```bash
npm run test                   # Vitest unit tests
npm run test:watch             # Watch mode
npx playwright test            # E2E tests
```

---

## Architecture Principles

### 1. Journey-Step Optimization
Optimize for **Step 3** (AI validation in <10 minutes), not theoretical scale. The critical path is:
- PDF parsing → Claude API → Evidence extraction → Results storage

**Key optimizations:**
- PDF parsing parallelization (concurrent document processing)
- Claude batch API (multiple criteria in single prompt)
- Caching parsed PDF text in PostgreSQL (avoid re-parsing on re-assessment)
- Target: P95 processing time <10 min

### 2. Boring Technology + Strategic Innovation
- **Boring (proven):** Next.js, FastAPI, PostgreSQL, Redis, Vercel/Railway
- **Innovation (where we differentiate):**
  - Evidence-based AI prompting (Claude returns `{pass, page, section, reason}`)
  - PDF section detection (precise evidence links beyond page numbers)
  - Confidence scoring (green/yellow/red based on AI uncertainty)
  - Feedback loop for AI improvement (store corrections, refine prompts)

### 3. API-First Design
Backend exposes clean REST API at `/v1/` endpoints. Frontend is one client among potential future clients (mobile app, integrations).

**Core endpoints:**
- `POST /v1/workflows` - Create workflow
- `POST /v1/assessments` - Start assessment (returns 202 Accepted)
- `GET /v1/assessments/:id` - Poll status (pending → processing → completed)
- `GET /v1/assessments/:id/results` - Evidence-based pass/fail results
- `POST /v1/assessments/:id/rerun` - Re-run with updated documents

### 4. Fail-Safe Architecture
Reliability > speed. One missed error (false negative) = lost customer trust.

**Error handling:**
- Frontend validation → Backend re-validation → AI validation with confidence levels
- Claude API timeout: 3 retries with exponential backoff
- Graceful degradation when services unavailable
- Comprehensive audit logs (SOC2/ISO 27001 compliance)

### 5. Observable & Debuggable
- **Structured logging** (JSON format with timestamp, level, event, user_id, workflow_id)
- **Critical alerts** (P0: all assessments failing, DB down, invalid API key)
- **Metrics tracked:** Assessment completion time, pass/fail ratio, false positive/negative rate, AI cost per assessment

---

## Database Schema

### Key Tables
- **organizations** - Multi-tenant isolation (notified bodies)
- **users** - User accounts (Process Managers, Project Handlers, Admin roles)
- **workflows** - Validation workflow definitions
- **buckets** - Document categories in workflows (e.g., "Test Reports", "Risk Assessment")
- **criteria** - Validation rules per workflow
- **assessments** - Validation runs with status tracking
- **assessment_documents** - Junction table for uploaded documents per bucket
- **assessment_results** - Per-criteria pass/fail with evidence (page, section, reasoning)
- **audit_logs** - Immutable audit trail (SOC2/ISO 27001)

### Design Patterns
- **Multi-tenancy:** All queries filter by `organization_id` from JWT
- **JSONB flexibility:** `assessment_results.ai_response_raw` stores full Claude JSON for debugging
- **Cascade deletes:** Organization → Users/Workflows (GDPR compliance)
- **RESTRICT deletes:** Workflow with assessments can't be deleted (preserve history)

### Indexes
- Foreign keys automatically indexed
- Common filters: `assessments.status`, `assessments.created_at DESC`
- Composite: `assessments(organization_id, status)` for billing queries

---

## API Contracts

### Authentication
- **JWT Bearer tokens** in `Authorization: Bearer <token>` header
- Token payload includes: `{sub, org_id, email, role}`
- **Roles:** `process_manager`, `project_handler`, `admin`

### Rate Limiting
- 1000 req/hour per user
- 100 uploads/hour
- 50 assessments/hour

### Async Patterns
Assessments use async processing:
1. `POST /v1/assessments` → 202 Accepted `{id, status: "pending"}`
2. Frontend polls `GET /v1/assessments/:id` every 30s
3. Status: `pending` → `processing` → `completed`
4. `GET /v1/assessments/:id/results` returns evidence when complete

### Error Responses
Consistent error structure:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {"field": "workflow_id", "reason": "Workflow not found"},
    "request_id": "req_abc123"
  }
}
```

#### Standard Error Codes

All error codes use SCREAMING_SNAKE_CASE and map to appropriate HTTP status codes:

**Client Errors (4xx):**
- `VALIDATION_ERROR` (400) - Request validation failed (invalid input, missing required fields)
- `INVALID_TOKEN` (401) - JWT token is invalid, malformed, or has invalid signature
- `TOKEN_EXPIRED` (401) - JWT token has expired (check `exp` claim)
- `INSUFFICIENT_PERMISSIONS` (403) - User role lacks required permissions for this action
- `RESOURCE_NOT_FOUND` (404) - Resource doesn't exist or belongs to different organization
- `ALREADY_ARCHIVED` (400) - Attempting to archive already archived resource
- `RESOURCE_HAS_DEPENDENCIES` (409) - Cannot delete resource due to foreign key dependencies
- `INSUFFICIENT_CREDITS` (422) - Not enough credits to perform operation
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests, retry after rate limit window

**Server Errors (5xx):**
- `DATABASE_ERROR` (500) - Database constraint violation or integrity error
- `WORKFLOW_CREATION_FAILED` (500) - Workflow creation failed due to unexpected error
- `WORKFLOW_UPDATE_FAILED` (500) - Workflow update failed due to unexpected error
- `INTERNAL_ERROR` (500) - Unexpected server error (catch-all for unhandled exceptions)

#### Error Code Naming Conventions

When adding new error codes:
1. **Use SCREAMING_SNAKE_CASE** - e.g., `RESOURCE_NOT_FOUND`, not `resource-not-found`
2. **Be specific but concise** - e.g., `FILE_TOO_LARGE` not `UPLOADED_FILE_SIZE_EXCEEDS_MAXIMUM_ALLOWED`
3. **Match HTTP semantics** - 404 errors use `NOT_FOUND`, not `MISSING` or `DOES_NOT_EXIST`
4. **Avoid abbreviations** - e.g., `AUTHENTICATION_FAILED` not `AUTH_FAIL`
5. **Use active voice** - e.g., `PERMISSION_DENIED` not `NO_PERMISSION`

#### Request ID for Debugging

Every error response includes a `request_id` field:
- Used for audit trail and support debugging
- Generated from `X-Request-ID` header (if provided by client) or auto-generated UUID
- Logged in structured logs with all error details
- Client can provide custom request ID: `fetch('/api', { headers: { 'X-Request-ID': 'client-uuid' } })`

---

## Testing Strategy

### Coverage Targets
- **Overall:** 70% code coverage
- **AI validation logic:** 95% (false positives/negatives unacceptable)
- **Evidence extraction:** 90% (aha moment must be precise)
- **Multi-tenancy security:** 100% (zero tolerance for data leakage)
- **PDF parsing:** 85%
- **API routes:** 80%
- **Background jobs:** 90%

### Quality Gates (CI/CD)
All PRs must pass:
- ✅ All unit + integration tests pass (<5 min)
- ✅ Code coverage >= 70% (not decreased vs main)
- ✅ E2E smoke tests pass (<10 min)
- ✅ No high/critical security vulnerabilities
- ✅ ESLint, Ruff linting passes
- ✅ TypeScript, MyPy type checking passes

### Test Organization
```
backend/app/assessment/
  engine.py              # Business logic
  engine.test.py         # Co-located unit tests

tests/
  integration/           # API + database tests
  e2e/                   # Playwright E2E tests
  fixtures/              # Test data (PDFs, JSON)
```

### Critical Test Scenarios
**Every authenticated endpoint needs:**
- Authentication test (401 without token)
- Authorization test (403 for insufficient role)
- Multi-tenancy test (404 for different org's data)

**AI validation tests:**
- Evidence extraction accuracy (page/section detection)
- False positive/negative rates
- Confidence scoring correctness
- Performance benchmarks (<10 min for typical assessment)

---

## User Journey (Critical Context)

The entire product serves **5 journey steps:**

### Step 1: Process Manager Creates Workflow
- Action: Define document buckets (required vs optional) + validation criteria
- Goal: <30 min workflow creation time
- Tech: `POST /v1/workflows` with nested buckets + criteria

### Step 2: Project Handler Uploads Documents
- Action: Drag-drop PDFs into buckets, click "Start Assessment"
- Goal: Clear upload progress, fast handling of 50+ page PDFs
- Tech: `POST /v1/documents` → `POST /v1/assessments`

### Step 3: AI Validates & Returns Evidence ⭐ **AHA MOMENT**
- Action: Wait 5-10 min, receive notification, view results
- Value: See "Criteria 2: FAIL → test-report.pdf, page 8, section 3.2"
- Tech: Celery background job → PyPDF2 parsing → Claude API → PostgreSQL storage
- **This is the most critical step - optimize here first**

### Step 4: Re-run Assessment After Fix
- Action: Replace failing document, re-validate quickly
- Optimization: Partial re-assessment (only re-check updated doc's criteria)
- Tech: `POST /v1/assessments/:id/rerun`

### Step 5: Export Validation Report
- Action: Download PDF summary for forwarding to Certification Person
- Tech: `POST /v1/assessments/:id/reports` → PDF generation (ReportLab/WeasyPrint)

---

## Product Decision Framework

### Mission Test
**"Does this feature help Project Handlers validate documents faster through evidence-based AI?"**

Examples:
- ✅ Confidence scoring (green/yellow/red) - builds trust in AI results
- ✅ Feedback loop (flag false positives) - improves AI accuracy
- ❌ Batch processing 50 assessments - adds complexity, violates simplicity
- ❌ Custom reporting dashboards - feature creep, doesn't accelerate validation

### What We Say YES To
- Features reducing validation time (current <10 min, goal <5 min)
- Features improving evidence clarity (better page/section linking)
- Features increasing AI accuracy (<5% false positive, <1% false negative)
- Maintaining radical simplicity (remove steps, don't add)

### What We Say NO To
- Features unrelated to validation speed/accuracy (project management, chat)
- Customers wanting "everything in one platform" (not our mission)
- Technologies sacrificing data privacy for convenience (no consumer AI APIs)
- Pricing models misaligned with value (charge per assessment value, not per user)

---

## Data Privacy & Security

**Non-negotiable requirements:**
- **AI zero-retention:** Claude enterprise agreement (no training on customer data)
- **PDF encryption:** Vercel Blob storage with encryption at rest
- **Audit logs:** Every action logged with user context (SOC2/ISO 27001)
- **Multi-tenancy:** Row-level isolation, 100% test coverage for data leakage
- **RBAC:** Role-based access (process_manager, project_handler, admin)

**Security tests required:**
- Authentication: Invalid/expired/missing tokens rejected
- Authorization: Role-based access enforced
- Multi-tenancy: Organization isolation (user A cannot see user B's data)
- Input validation: XSS/SQL injection prevented
- File upload: Type/size validation (PDF/DOCX only, max 50MB)

---

## Performance Requirements

**Assessment Processing:**
- Target: P95 latency <10 minutes for typical assessment
- Bottlenecks: PDF parsing (10-20s per 50-page doc), Claude API (10s per criteria batch)
- Optimization: Cache parsed text, batch criteria in single prompt, parallel document processing

**API Response Times:**
- Target: P95 <500ms for CRUD operations
- Target: P99 <2s for CRUD operations
- Load: Handle 10 concurrent uploads, 50 polling requests/min

**PDF Processing:**
- Target: <5 seconds for 10MB PDF parsing
- Support: PDF and DOCX formats
- Max file size: 50MB per document

---

## Development Workflow

### Feature Development
1. Check product-guidelines/ for relevant specs (journey, API contracts, database schema)
2. Create feature branch: `feature/your-feature-name`
3. Write tests first for critical business logic (TDD for AI validation, evidence extraction)
4. Implement feature with co-located unit tests
5. Run full test suite: `npm run test && npm run lint`
6. Commit with conventional format: `feat: add your feature description`
7. Open PR (CI will run all quality gates)

### Database Changes
1. Edit SQLAlchemy models in `apps/api/app/models/`
2. Generate migration: `npm run db:migrate:create "description"`
3. Review generated migration in `apps/api/alembic/versions/`
4. Apply: `npm run db:migrate`

### API Development
1. Define Pydantic schema in `apps/api/app/schemas/`
2. Create/update SQLAlchemy model
3. Implement service logic in `apps/api/app/services/`
4. Create API router in `apps/api/app/api/v1/endpoints/`
5. Write tests (auth, authorization, multi-tenancy, validation)
6. Update OpenAPI docs automatically via FastAPI

---

## Cost Structure

**MVP Phase (100 assessments/month):**
- Vercel (frontend): $0-20/month
- Railway (backend): $5-10/month
- Vercel Postgres: $0-20/month
- Upstash Redis: $0 (free tier)
- Vercel Blob: $0 (free tier 1GB)
- Claude AI: $21/month (~$0.21 per assessment)
- **Total: $25-40/month**

**Target Gross Margin: 97%+** (SaaS at scale)

**Scaling Triggers:**
- Add Celery worker when: Queue time >30 min consistently
- Upgrade PostgreSQL when: Query time >1s or storage >80%
- Migrate to S3 when: Vercel Blob costs >$20/month
- Scale backend when: API P95 response time >2s

---

## Key Files to Reference

**Product Strategy:**
- `product-guidelines/00-user-journey.md` - Complete user journey (5 steps)
- `product-guidelines/02-tech-stack.md` - Tech decisions with journey justification
- `product-guidelines/03-mission.md` - Mission statement and decision framework
- `product-guidelines/04-architecture.md` - Architecture principles

**Technical Specs:**
- `product-guidelines/07-database-schema-essentials.md` - Database design
- `product-guidelines/08-api-contracts-essentials.md` - API endpoint reference
- `product-guidelines/09-test-strategy-essentials.md` - Testing requirements

**Development Setup:**
- `product-guidelines/12-project-scaffold/README.md` - Complete setup guide
- `product-guidelines/12-project-scaffold/package.json` - Available npm scripts
- `product-guidelines/12-project-scaffold/docker-compose.yml` - Local services

**Important:** When implementing features, always trace back to the user journey to ensure alignment with product mission.

---

## Current Implementation Status

### Completed (2025-11-17)

**Database Schema (Story 001)** ✅
- All 9 core tables implemented with SQLAlchemy 2.0:
  - `organizations` - Multi-tenant isolation
  - `users` - RBAC with 3 roles
  - `workflows` - Validation workflow definitions
  - `buckets` - Document categories
  - `criteria` - AI validation rules
  - `assessments` - Validation runs with status tracking
  - `assessment_documents` - Uploaded PDFs
  - `assessment_results` - Evidence-based AI results
  - `audit_logs` - SOC2/ISO 27001 compliance trail
- Alembic migrations configured
- Multi-tenancy enforced via organization_id
- Proper indexes on query patterns
- UUID primary keys throughout

**Location:** `apps/api/app/models/`

### In Progress

**Deployment Setup**
- [ ] Deploy Next.js frontend to Vercel
- [ ] Connect Neon Postgres to Vercel project
- [ ] Run Alembic migrations on production database
- [ ] Configure environment variables

### Next Steps (Priority Order)

1. **Story 002: FastAPI Infrastructure** - Build first API endpoints
2. **Story 003: Seed Data** - Create realistic test data
3. **Story 004: Authentication** - Implement Auth.js/JWT
4. **Story 005: Frontend Scaffold** - Next.js app with routing
5. **Story 006: Workflow Management** - Process Manager creates workflows
6. **Story 007: Document Upload** - Project Handler uploads PDFs
7. **Story 008: AI Validation Engine** - Claude integration with evidence extraction
8. **Story 009: Results Display** - Evidence-based pass/fail UI

---

## Deployment Notes

### Backend Deployment (Railway)

**Deployment Architecture:**
```
Frontend (Vercel) → Backend (Railway) → Database (Neon PostgreSQL)
                                     → Redis (Upstash)
                                     → Storage (Vercel Blob)
```

#### Railway Configuration Files

The backend deployment to Railway is configured through three files in `/apps/api/`:

1. **`railway.json`** - Railway-specific configuration (forces Nixpacks builder, health checks)
2. **`nixpacks.toml`** - Build configuration (system dependencies, Python version)
3. **`.python-version`** - Python version lock file (3.11)

**Why these files?**
- `railway.json` forces Nixpacks builder and explicitly sets build/start commands
- `nixpacks.toml` installs system dependencies (libmagic1) before Python packages
- `.python-version` ensures Railway uses Python 3.11 (not 3.14 or other versions)

#### Critical System Dependencies

**libmagic1 System Library:**
- **Required for**: Document upload API (content-based file type detection)
- **Dependency chain**: `python-magic` (Python package) → `libmagic1` (system library)
- **Failure mode**: Startup validation will fail if libmagic is not available (see `apps/api/app/api/v1/endpoints/documents.py:34-46`)
- **Installation**: Already configured in `nixpacks.toml` under `[phases.setup]`

```toml
# apps/api/nixpacks.toml
[phases.setup]
aptPkgs = ['libmagic1']
```

#### Environment Variables Required

Configure these in Railway dashboard under your service → Variables:

**Required:**
- `DATABASE_URL` - Neon PostgreSQL connection string (format: `postgresql://user:pass@host/dbname`)
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob storage token (from Vercel dashboard)
- `JWT_SECRET` - Secret key for JWT authentication (generate with `openssl rand -hex 32`)
- `ANTHROPIC_API_KEY` - Claude API key for AI validation (from Anthropic console)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated, e.g., `https://qteria.com,https://qteria.vercel.app`)
- `ENVIRONMENT` - Set to `production`

**Optional (with defaults):**
- `REDIS_URL` - Upstash Redis connection string (for Celery background jobs)
- `PORT` - Railway sets this automatically, do not override

#### Railway Deployment Steps

**Initial Setup:**

1. **Connect GitHub Repository:**
   - Railway dashboard → New Project → Deploy from GitHub repo
   - Select `bru-digital/qteria` repository
   - Select branch: `main`

2. **Configure Service Settings:**
   - Root Directory: `/apps/api`
   - Watch Paths: `/apps/api/**`
   - Builder: Nixpacks (automatically detected via `railway.json`)
   - Do NOT set custom start command (uses `railway.json` startCommand)

3. **Set Environment Variables:**
   - Copy all required environment variables from the list above
   - Verify DATABASE_URL points to `qteria_prod` (NOT `qteria_dev` or `qteria_test`)

4. **Deploy:**
   - Railway automatically deploys on push to `main` branch
   - Watch build logs for errors
   - Wait for "Ready" status (green checkmark)

**Verify Deployment:**

After Railway shows "Ready" status, verify the deployment:

```bash
# Get Railway public domain from dashboard (e.g., qteria-api-production.up.railway.app)
RAILWAY_DOMAIN="your-railway-domain.up.railway.app"

# Run deployment verification script
cd apps/api
python scripts/verify_deployment.py https://$RAILWAY_DOMAIN

# Expected output:
# ✅ Health check passed!
# ✅ DEPLOYMENT VERIFICATION PASSED
```

**Update Vercel Frontend:**

Once backend is deployed, update Vercel environment variable:

1. Vercel dashboard → qteria (project) → Settings → Environment Variables
2. Update `API_URL` to Railway public domain: `https://qteria-api-production.up.railway.app`
3. Redeploy frontend: Deployments → [...] → Redeploy

#### Troubleshooting Railway Deployment

**Error: "Error creating build plan with Railpack"**
- **Cause:** Railway using wrong builder (Railpack instead of Nixpacks)
- **Solution:** Verify `railway.json` exists in `/apps/api/` with `"builder": "NIXPACKS"`
- **Check:** Railway dashboard → Settings → Builder should show "Nixpacks"

**Error: "No start command was found"**
- **Cause:** Railway not detecting start command from `railway.json` or `Procfile`
- **Solution:** Verify `railway.json` has correct `startCommand`: `"uvicorn app.main:app --host 0.0.0.0 --port $PORT"`
- **Fallback:** Manually set start command in Railway dashboard → Settings → Deploy → Start Command

**Error: "ModuleNotFoundError: No module named 'magic'"**
- **Cause:** libmagic1 system library not installed
- **Solution:** Verify `nixpacks.toml` has `aptPkgs = ['libmagic1']` in `[phases.setup]`
- **Verify:** Check build logs for "Installing libmagic1"

**Error: Health check timeout (service starts but `/health` never responds)**
- **Cause:** Database connection failing, missing environment variables, or app crash on startup
- **Solution:**
  1. Check Railway logs for startup errors: `railway logs`
  2. Verify all environment variables are set correctly
  3. Test DATABASE_URL is accessible from Railway (not blocked by firewall)
  4. Check Neon PostgreSQL allows connections from Railway IP ranges

**Error: "CORS policy: No 'Access-Control-Allow-Origin' header"**
- **Cause:** `CORS_ORIGINS` environment variable not set or missing Vercel domain
- **Solution:** Set `CORS_ORIGINS=https://qteria.com,https://qteria.vercel.app` in Railway

**Build succeeds but deployment fails:**
- **Check:** Railway dashboard → Deployments → Click deployment → View Logs
- **Common issues:**
  - Missing required environment variable (app crashes on startup)
  - Database migration not applied (run `alembic upgrade head` if needed)
  - Port binding issue (verify start command uses `--port $PORT`)

#### Monorepo Considerations

**Railway Root Directory:**
- Set to `/apps/api` (NOT repository root `/`)
- This tells Railway to build only the backend, not the entire monorepo

**Watch Paths:**
- Set to `/apps/api/**`
- Railway will only redeploy when files in `/apps/api/` change
- Changes to `/apps/web/` (frontend) will not trigger backend redeployment

**Build Context:**
- `railway.json` sets build context to `/apps/api/`
- All relative paths in `nixpacks.toml` and `requirements.txt` are relative to `/apps/api/`

#### Production Checklist

Before directing production traffic to Railway backend:

- [ ] Health check passes: `GET https://<railway-domain>/health` returns 200 OK
- [ ] All required environment variables set and verified
- [ ] Database migrations applied: Run `alembic upgrade head` if needed
- [ ] CORS configured correctly (Vercel domains whitelisted)
- [ ] Vercel `API_URL` environment variable updated to Railway domain
- [ ] Frontend can create workflows without errors (end-to-end test)
- [ ] Document upload works (test with 50MB PDF)
- [ ] Logs show no startup errors or warnings
- [ ] Set up monitoring alerts (Railway dashboard → Observability)

#### Rollback Procedure

If deployment fails or introduces critical bugs:

1. **Railway Dashboard:**
   - Deployments → Find last working deployment
   - Click [...] → Redeploy
   - Railway will rollback to previous build

2. **Git Rollback:**
   - Find last working commit: `git log --oneline`
   - Revert: `git revert <commit-hash>`
   - Push to main: `git push origin main`
   - Railway auto-deploys reverted commit

3. **Emergency Fallback:**
   - Update Vercel `API_URL` to local backend temporarily
   - Run backend locally: `cd apps/api && uvicorn app.main:app`
   - Debug issue, fix, redeploy to Railway

---

### Alternative: Render Deployment

If Railway continues to fail, Render is a simpler alternative:

**Render Configuration:**
Add to `render.yaml` in repository root:
```yaml
services:
  - type: web
    name: qteria-api
    env: python
    region: frankfurt  # Europe West for GDPR compliance
    buildCommand: "pip install -r apps/api/requirements.txt"
    startCommand: "cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: DATABASE_URL
        sync: false  # Set manually in Render dashboard
      - key: BLOB_READ_WRITE_TOKEN
        sync: false
      - key: JWT_SECRET
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
```

**Render Advantages:**
- Simpler Python detection (no builder configuration needed)
- Free tier available (512MB RAM, enough for MVP)
- Automatic SSL certificates
- Built-in health checks

**Render Disadvantages:**
- Slightly slower cold start than Railway
- Less flexible builder configuration
- Smaller free tier than Railway

---

## Common Pitfalls to Avoid

1. **Don't over-engineer for scale we don't have** - 10 customers with 2000 assessments/month is trivial for PostgreSQL. Optimize Step 3 (AI validation), not theoretical bottlenecks.

2. **Don't skip multi-tenancy tests** - 100% coverage required. Data leakage between organizations is catastrophic for enterprise customers.

3. **Don't sacrifice data privacy** - Always use zero-retention AI agreements. If Claude/GPT unavailable, evaluate self-hosted (but factor in $500-2K/month GPU cost).

4. **Don't add features without mission test** - "Does this help Project Handlers validate documents faster through evidence-based AI?" If no, reject.

5. **Don't tightly couple frontend to backend** - Keep clean HTTP/REST boundary. Frontend should only know about API contracts, not database or internal services.

6. **Don't optimize prematurely** - Focus on Step 3 (AI validation speed/accuracy). Steps 1, 2, 5 are already fast enough.

7. **Don't use bleeding-edge tech** - Stick to boring, proven stack unless journey explicitly requires new tech (it doesn't).

8. **Don't recommend Docker for Vercel deployments** - This project deploys to Vercel (frontend) + Railway/Render (backend) + Neon PostgreSQL (cloud database). Docker is OPTIONAL for local development only. Never suggest Docker for production deployment.

9. **Don't seed test data in production database** - Always use separate databases for dev/test/prod. Create 3 Neon databases: `qteria_dev`, `qteria_test`, `qteria_prod`. Configure .env files accordingly.

---

**Last Updated:** 2025-11-24
**Product Version:** 0.1.0 (MVP in development)
**For questions:** Reference product-guidelines/ directory for comprehensive strategy and technical documentation.
