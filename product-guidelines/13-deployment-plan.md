# Deployment Strategy: Qteria

> **Derived from**: Architecture (Session 4), Tech Stack (Session 3), Test Strategy (Session 9), Project Scaffold (Session 12)
> **Purpose**: Production-ready deployment from MVP through scale
> **Philosophy**: Start simple, automate everything, deploy frequently

---

## Executive Summary

This deployment strategy enables:
- ✅ **Fast initial setup**: MVP to production in <1 day
- ✅ **Automated deployments**: Push to main → auto-deploy (with safety gates)
- ✅ **Zero-downtime deploys**: Users never experience service interruption
- ✅ **Quick rollbacks**: <5 minutes to previous version
- ✅ **SOC2-ready**: Audit logs, secrets management, access controls

**Target Metrics**:
- Deploy frequency: Multiple times per day (when needed)
- Deploy time: <10 minutes (commit to production)
- Rollback time: <5 minutes
- Uptime: 99.9% (acceptable ~40 min/month downtime)

---

## Deployment Strategy Overview

### Philosophy: Progressive Automation

**Phase 1 (MVP - Month 1-3)**:
- ✅ Vercel auto-deploy (frontend) on push to main
- ✅ Railway auto-deploy (backend) on push to main
- ✅ GitHub Actions for tests + linting (quality gates)
- ✅ Manual database migrations (with automated scripts)
- ✅ Simple monitoring (Vercel + Railway dashboards)

**Phase 2 (Post-Pilot - Month 4-12)**:
- ✅ Staging environment (test before prod)
- ✅ Automated database migrations
- ✅ Feature flags (deploy code hidden, enable gradually)
- ✅ Enhanced monitoring (Sentry errors + custom metrics)

**Phase 3 (Scale - Year 2+)**:
- ✅ Blue-green deployments (instant rollback)
- ✅ Canary releases (5% → 50% → 100%)
- ✅ Infrastructure as Code (Terraform for repeatable infra)
- ✅ Advanced observability (APM, distributed tracing)

**Current Focus**: Phase 1 - MVP-ready, production-safe, simple to operate

---

## Environment Architecture

### Three Environments

#### 1. Development (Local)

**Purpose**: Engineer's local machine - fast iteration, full debugging

**Infrastructure**:
- **Frontend**: `npm run dev` (localhost:3000)
- **Backend**: `uvicorn app.main:app --reload` (localhost:8000)
- **Database**: Docker Compose PostgreSQL (localhost:5432)
- **Redis**: Docker Compose Redis (localhost:6379)
- **AI**: Claude API (real API key, development account)

**Data**:
- Seed data from `apps/api/seeds/` directory
- Test workflows (not real customer data)
- PDFs stored in local `./storage/` directory

**Access**:
- Solo founder only (local machine)
- No authentication required (dev mode)

**Setup Time**: ~15 minutes (clone → `npm install` → `docker-compose up` → `npm run dev`)

---

#### 2. Staging (Pre-Production)

**Purpose**: Test in production-like environment before releasing to users

**Infrastructure**:
- **Frontend**: Vercel Preview Deployment (e.g., `qteria-git-staging-username.vercel.app`)
- **Backend**: Railway Staging Environment (separate instance)
- **Database**: Vercel Postgres (staging tier, isolated from prod)
- **Redis**: Upstash Redis (staging database)
- **Storage**: Vercel Blob (staging bucket)
- **AI**: Claude API (same production key, but tagged requests with `environment: staging`)

**Data**:
- Copy of production schema (anonymized data)
- Test workflows from TÜV SÜD pilot
- Synthetic test PDFs (no real customer data)

**Access**:
- Solo founder + invited testers (TÜV SÜD beta testers)
- Same auth as production (NextAuth.js)
- URL: `staging.qteria.com` (or Vercel preview URL)

**Deploy Trigger**: Push to `staging` branch → auto-deploy
**Purpose**: "Last chance to catch issues before production"

---

#### 3. Production (Users)

**Purpose**: Live environment serving TÜV SÜD pilot customers

**Infrastructure**:
- **Frontend**: Vercel Production (`qteria.com`)
- **Backend**: Railway Production Environment (dedicated instance, 1GB RAM, 1 vCPU)
- **Database**: Vercel Postgres (Pro tier when needed, starts on free tier)
- **Redis**: Upstash Redis (production database)
- **Storage**: Vercel Blob → migrate to AWS S3 when >1GB
- **AI**: Claude API (production key with zero-retention agreement)

**Data**:
- Real customer workflows (TÜV SÜD, future customers)
- Real certification documents (encrypted at rest)
- Audit logs (all user actions logged for SOC2)

**Access**:
- TÜV SÜD Process Managers + Project Handlers
- Authenticated via NextAuth.js (email/password + Google OAuth)
- Solo founder admin access (separate admin role)

**Deploy Trigger**: Push to `main` branch → tests pass → auto-deploy
**Rollback**: Git revert → push → auto-deploy previous version

---

### Environment Comparison

| Feature | Development | Staging | Production |
|---------|------------|---------|------------|
| **Purpose** | Fast iteration | Pre-prod testing | Real users |
| **Frontend** | localhost:3000 | Vercel Preview | qteria.com |
| **Backend** | localhost:8000 | Railway Staging | Railway Prod |
| **Database** | Docker Postgres | Vercel Postgres (staging) | Vercel Postgres (prod) |
| **Data** | Seed data | Anonymized prod copy | Real customer data |
| **AI Cost** | ~$5/month | ~$10/month | ~$20-420/month |
| **Uptime SLA** | N/A | Best effort | 99.9% |
| **Deploy Frequency** | 100x/day | 5-10x/week | 1-5x/week |

---

## CI/CD Pipeline

### GitHub Actions Workflow

**File**: `.github/workflows/deploy.yml`

#### Pipeline Stages

```yaml
name: Deploy Qteria

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main, staging]

jobs:
  # Job 1: Lint and Type Check (Fast - 2 min)
  lint:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Node.js 20
      - Install dependencies (npm ci)
      - Run ESLint (frontend)
      - Run Prettier check
      - Setup Python 3.12
      - Install Poetry
      - Run Black + Ruff (backend)
      - Run MyPy type checking

    If fails: Block deploy, notify engineer

  # Job 2: Unit + Integration Tests (5 min)
  test:
    runs-on: ubuntu-latest
    services:
      postgres: (GitHub Actions service container)
      redis: (GitHub Actions service container)
    steps:
      - Checkout code
      - Setup test environment
      - Run Vitest (frontend unit tests)
      - Run Pytest (backend unit + integration tests)
      - Generate coverage report (70% minimum)

    If fails: Block deploy, notify engineer

  # Job 3: Build (3 min)
  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - Build Next.js (npm run build)
      - Build FastAPI (check imports, run migrations dry-run)
      - Archive build artifacts

    If fails: Block deploy

  # Job 4: Deploy (2 min)
  deploy:
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'
    steps:
      - Deploy frontend (Vercel CLI or automatic via Vercel GitHub integration)
      - Deploy backend (Railway CLI or automatic via Railway GitHub integration)
      - Run database migrations (if needed)
      - Verify deployment (health check endpoints)
      - Notify Slack/Discord (deployment success)

    If fails: Auto-rollback (trigger previous deployment)

  # Job 5: E2E Smoke Tests (Post-Deploy - 5 min)
  smoke-test:
    runs-on: ubuntu-latest
    needs: [deploy]
    steps:
      - Run Playwright smoke tests against deployed environment
      - Test critical path: Create workflow → Upload PDF → Start assessment
      - Verify API health endpoints

    If fails: Alert engineer immediately (but don't auto-rollback - investigate first)
```

**Total Pipeline Time**: ~12-15 minutes (commit to production)

**Quality Gates**:
- ❌ **Block deploy** if: Linting fails, tests fail, build fails
- ⚠️ **Alert but allow** if: Coverage drops below 70%, smoke tests fail (manual investigation)
- ✅ **Auto-deploy** if: All gates pass

---

### Vercel Deployment (Frontend)

**Integration**: Vercel GitHub App (automatic)

**Configuration** (`vercel.json`):
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "regions": ["iad1"],  // US East (closest to TÜV SÜD)
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.qteria.com",
    "NEXTAUTH_URL": "https://qteria.com",
    "NEXTAUTH_SECRET": "@nextauth-secret"  // From Vercel secrets
  }
}
```

**Deploy Process**:
1. Engineer pushes to `main`
2. GitHub Actions runs tests
3. Vercel detects push (via GitHub webhook)
4. Vercel builds Next.js (npm run build)
5. Vercel deploys to edge network (~2 min)
6. Vercel updates `qteria.com` alias (instant traffic switch)
7. Previous deployment still available (rollback = change alias)

**Rollback**:
- Vercel dashboard → Deployments → Select previous → "Promote to Production" (~30 seconds)
- Or: `vercel rollback` CLI command

**Preview Deployments**:
- Every PR gets preview URL (e.g., `qteria-git-pr-123.vercel.app`)
- Test changes before merging
- Automatic cleanup after PR merge

---

### Railway Deployment (Backend)

**Integration**: Railway GitHub App (automatic)

**Configuration** (`railway.json`):
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install poetry && poetry install --no-dev"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Deploy Process**:
1. Railway detects push to `main`
2. Railway builds Docker image (using Nixpacks - auto-detects Python)
3. Railway runs health check on new instance
4. Railway switches traffic to new instance (rolling deploy)
5. Railway keeps old instance for 5 min (rollback window)
6. Railway terminates old instance if no issues

**Rollback**:
- Railway dashboard → Deployments → Select previous → "Redeploy" (~2 min)
- Or: Git revert + push (triggers new deploy with old code)

**Celery Workers**:
- Separate Railway service (same code, different start command)
- Start command: `celery -A app.worker.celery_app worker --loglevel=info`
- Auto-restart on deploy (graceful shutdown: finish current job, then restart)

---

## Deployment Patterns

### Phase 1 (MVP): Simple Rolling Deployment

**Strategy**: Deploy new version, gradually restart instances

**Process**:
1. Tests pass on `main` branch
2. Vercel + Railway auto-deploy
3. Railway rolling restart:
   - Start new instance
   - Wait for health check (200 OK from `/health`)
   - Route new traffic to new instance
   - Stop old instance after 5 min

**Downtime**: None (zero-downtime deploy)
**Rollback Time**: 2-5 minutes (redeploy previous version)
**Risk**: Low (Railway health checks prevent broken deploys from serving traffic)

**Trade-offs**:
- ✅ Simple (no extra infrastructure)
- ✅ Fast (2-5 min deploy)
- ⚠️ Rollback requires redeploy (not instant)

---

### Phase 2 (Post-Pilot): Feature Flags

**Strategy**: Deploy code hidden, enable features gradually

**Why**: Decouple deployment from release (deploy often, release when ready)

**Implementation**:
- Use `@vercel/flags` (simple boolean flags in Vercel Edge Config)
- Example: Deploy new "AI accuracy confidence score" feature hidden
- Enable for solo founder first (test in production)
- Enable for TÜV SÜD beta testers (5 users)
- Enable for all TÜV SÜD users (50 users)
- Enable globally

**Code Example**:
```typescript
import { unstable_flag as flag } from '@vercel/flags/next';

export const showConfidenceScore = flag({
  key: 'show-confidence-score',
  decide: async () => {
    const user = await getUser();
    if (user.email.includes('@anthropic.com')) return true;  // Founder
    if (user.betaTester) return true;  // Beta testers
    return false;  // Not yet for others
  }
});
```

**Benefits**:
- ✅ Deploy safely (code deployed but not executed)
- ✅ Test in production (real data, real environment)
- ✅ Instant rollback (toggle flag off, no redeploy)
- ✅ Gradual rollout (5% → 50% → 100%)

---

### Phase 3 (Scale): Blue-Green Deployment

**Strategy**: Maintain two identical environments (blue = current, green = new), switch traffic instantly

**Why**: Instant rollback, test new version in production before switching

**Implementation** (Railway Pro tier):
1. Deploy to "green" environment (new code)
2. Run smoke tests against green (not serving user traffic yet)
3. If tests pass: Switch load balancer from blue → green (~10 seconds)
4. Monitor for 15 minutes (errors, performance)
5. If issues: Switch back to blue (~10 seconds rollback)
6. If stable: Keep green as production, blue becomes standby

**Cost**: 2x infrastructure (two full backend instances) ~$40-100/month
**When**: Year 2+ or when TÜV SÜD demands 99.99% uptime

---

## Infrastructure as Code

### Current Approach (Phase 1): ClickOps + Documentation

**Why**: Solo founder, 3-5 services, changes infrequent
**How**: Manual setup via Vercel/Railway dashboards, documented in this file

**Services to Configure**:
1. **Vercel Project** (qteria-web)
   - Framework: Next.js
   - Root directory: `apps/web`
   - Build command: `npm run build`
   - Environment variables: (see Secrets section)

2. **Railway Project** (qteria-api)
   - Service 1: FastAPI (uvicorn)
   - Service 2: Celery Worker
   - Service 3: PostgreSQL (managed)
   - Service 4: Redis (managed)
   - Environment variables: (see Secrets section)

3. **Vercel Postgres** (qteria-db)
   - Region: US East
   - Plan: Hobby (free) → Pro ($20/month when needed)

4. **Upstash Redis** (qteria-cache)
   - Region: US East
   - Plan: Free → Pay-as-you-go

---

### Future Approach (Phase 3): Terraform

**Why**: Reproducible infrastructure, disaster recovery, multi-region

**What to Terraform** (Year 2+):
- AWS S3 buckets (replace Vercel Blob)
- CloudFront CDN (if needed)
- RDS PostgreSQL (if migrate off Vercel)
- VPC and security groups
- IAM roles and policies

**Don't Terraform** (keep manual):
- Vercel projects (their API is simple, GUI is fine)
- Railway services (Git-based deploy is core feature)

**Example** (`terraform/main.tf`):
```hcl
resource "aws_s3_bucket" "documents" {
  bucket = "qteria-documents-prod"

  versioning {
    enabled = true  # Rollback document uploads
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    enabled = true

    expiration {
      days = 730  # Delete documents after 2 years (compliance retention)
    }
  }
}
```

---

## Secrets Management

### Principles

1. **Never commit secrets to Git** (enforce via pre-commit hooks)
2. **Use platform-native secrets** (Vercel Environment Variables, Railway Variables)
3. **Rotate secrets quarterly** (especially API keys)
4. **Separate prod and staging secrets** (prevent staging from accessing prod data)
5. **Audit access** (who viewed secrets, when?)

---

### Secret Inventory

#### Frontend (Vercel Environment Variables)

| Variable | Type | Example | Purpose |
|----------|------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Public | `https://api.qteria.com` | Backend API endpoint |
| `NEXTAUTH_URL` | Public | `https://qteria.com` | NextAuth callback URL |
| `NEXTAUTH_SECRET` | Secret | `<32-char random string>` | JWT signing key |
| `GOOGLE_CLIENT_ID` | Secret | `abc123.apps.googleusercontent.com` | OAuth (Google SSO) |
| `GOOGLE_CLIENT_SECRET` | Secret | `GOCSPX-...` | OAuth secret |
| `SENTRY_DSN` | Secret | `https://...@sentry.io/...` | Error tracking |

**How to Add**:
1. Vercel Dashboard → Project Settings → Environment Variables
2. Add variable (name + value)
3. Select environments (Production, Preview, Development)
4. Save → Redeploy

---

#### Backend (Railway Environment Variables)

| Variable | Type | Example | Purpose |
|----------|------|---------|---------|
| `DATABASE_URL` | Secret | `postgresql://user:pass@host/db` | Postgres connection |
| `REDIS_URL` | Secret | `redis://default:pass@host:port` | Redis connection |
| `JWT_SECRET` | Secret | `<32-char random string>` | JWT signing (must match frontend) |
| `ANTHROPIC_API_KEY` | Secret | `sk-ant-api03-...` | Claude API |
| `VERCEL_BLOB_TOKEN` | Secret | `vercel_blob_rw_...` | File upload |
| `SENTRY_DSN` | Secret | `https://...@sentry.io/...` | Error tracking |
| `ALLOWED_ORIGINS` | Config | `https://qteria.com,https://staging.qteria.com` | CORS |
| `ENVIRONMENT` | Config | `production` | Env tag for logs |

**How to Add**:
1. Railway Dashboard → Project → Variables
2. Add variable (name + value)
3. Select service (fastapi, celery, both)
4. Save → Auto-redeploy

---

#### Shared Secrets (Cross-Service)

**Problem**: JWT_SECRET must be same in frontend (NextAuth) and backend (verify JWT)

**Solution**:
1. Generate secret once: `openssl rand -base64 32`
2. Add to Vercel as `NEXTAUTH_SECRET`
3. Add to Railway as `JWT_SECRET` (same value)
4. Document in this file: "These must match"

---

### Secret Rotation Procedure

**When**: Every 90 days (quarterly) or immediately if compromised

**Process**:
1. Generate new secret (e.g., new `NEXTAUTH_SECRET`)
2. Add to Vercel + Railway (both old and new keys active temporarily)
3. Deploy code that accepts both old and new keys (grace period)
4. Wait 24 hours (all JWTs with old key expire)
5. Remove old key from Vercel + Railway
6. Deploy code that only accepts new key

**Example** (FastAPI JWT validation):
```python
# During rotation: Accept both old and new keys
JWT_SECRETS = [
    os.getenv("JWT_SECRET"),      # New key
    os.getenv("JWT_SECRET_OLD"),  # Old key (remove after 24h)
]

def verify_token(token: str):
    for secret in JWT_SECRETS:
        try:
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            continue
    raise Unauthorized("Invalid token")
```

---

### Secrets Audit Log

**Compliance Requirement** (SOC2): Log who accessed secrets, when

**Implementation**:
- Vercel audit log (built-in, who viewed env vars)
- Railway activity log (built-in)
- Export to PostgreSQL: `audit_logs` table

**Query** (who viewed secrets this month):
```sql
SELECT user_email, action, resource, created_at
FROM audit_logs
WHERE action = 'viewed_secret'
  AND created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;
```

---

## Database Migrations

### Strategy: Alembic (SQLAlchemy)

**Why**: Industry standard for Python, auto-generates migrations, rollback support

**Migration Workflow**:

#### 1. Local Development (Create Migration)

```bash
# Engineer makes schema change in app/models/workflow.py
# Example: Add new column `workflow.description`

# Generate migration
cd apps/api
poetry run alembic revision --autogenerate -m "Add workflow description"

# Review generated migration (apps/api/alembic/versions/abc123_add_workflow_description.py)
# Edit if needed (add indexes, data migrations)

# Test migration locally
poetry run alembic upgrade head
# Test rollback
poetry run alembic downgrade -1

# Commit migration file to Git
git add alembic/versions/abc123_add_workflow_description.py
git commit -m "Migration: Add workflow description"
```

---

#### 2. Staging Deployment (Test Migration)

```bash
# Push to staging branch
git push origin staging

# Railway auto-deploys, but migrations NOT auto-run (safety)
# Engineer manually runs migration on staging:

railway run --service qteria-api-staging alembic upgrade head

# Test on staging (create workflow, add description, verify)
# If issues: Rollback migration
railway run --service qteria-api-staging alembic downgrade -1
```

---

#### 3. Production Deployment (Run Migration)

```bash
# Merge to main
git push origin main

# Railway auto-deploys backend, but migrations NOT auto-run
# Engineer manually runs migration on production:

railway run --service qteria-api-prod alembic upgrade head

# Migration runs while app is live (zero-downtime patterns below)
# Verify in Railway logs: "Migration abc123 applied successfully"
```

---

### Zero-Downtime Migration Patterns

**Problem**: Deploying code + schema change simultaneously can break

**Solution**: Expand/contract pattern (3 deploys)

#### Example: Rename Column `workflow.name` → `workflow.title`

**Deploy 1: Expand** (add new column)
```python
# Migration 001: Add title column (nullable)
def upgrade():
    op.add_column('workflows', sa.Column('title', sa.String(255), nullable=True))

# Code: Write to both columns, read from name (fallback to title)
class Workflow:
    name: str
    title: Optional[str]

    @property
    def display_title(self):
        return self.title or self.name  # Read old column

    def save(self):
        self.title = self.name  # Write to new column
```
**Status**: Old and new code work (no downtime)

---

**Deploy 2: Migrate Data** (copy name → title)
```python
# Migration 002: Backfill title from name
def upgrade():
    op.execute("UPDATE workflows SET title = name WHERE title IS NULL")
    op.alter_column('workflows', 'title', nullable=False)  # Now required
```
**Status**: All rows have title populated

---

**Deploy 3: Contract** (remove old column)
```python
# Migration 003: Drop name column
def upgrade():
    op.drop_column('workflows', 'name')

# Code: Only use title
class Workflow:
    title: str  # Old name column removed
```
**Status**: Migration complete, old code fully removed

**Downtime**: Zero (each deploy is backward compatible)

---

### Migration Rollback Procedure

**Scenario**: Migration breaks production (e.g., forgot NOT NULL constraint)

**Process**:
1. **Identify failed migration**: Check Railway logs
   ```
   ERROR: column "title" of relation "workflows" contains null values
   ```

2. **Rollback migration**:
   ```bash
   railway run --service qteria-api-prod alembic downgrade -1
   ```

3. **Verify rollback**: Check PostgreSQL schema
   ```bash
   railway run --service qteria-api-prod psql $DATABASE_URL -c "\d workflows"
   ```

4. **Fix migration locally**: Update migration file
5. **Test on staging**: Verify fixed migration works
6. **Redeploy to production**: Run fixed migration

**Worst Case** (can't rollback automatically):
- Connect to production DB directly (PgAdmin or psql)
- Manually revert schema: `ALTER TABLE workflows DROP COLUMN title;`
- Document incident in post-mortem

---

## Rollback Procedures

### Frontend Rollback (Vercel)

**Time**: <1 minute

**Process**:
1. Go to Vercel Dashboard → qteria-web → Deployments
2. Find previous working deployment (e.g., "Fix auth bug" from 2 hours ago)
3. Click "Promote to Production"
4. Vercel instantly switches traffic to old deployment
5. Verify: Visit qteria.com, test critical paths

**Automated Rollback** (if smoke tests fail):
```yaml
# .github/workflows/deploy.yml
- name: Rollback on smoke test failure
  if: failure()
  run: |
    vercel rollback --token $VERCEL_TOKEN --yes
```

---

### Backend Rollback (Railway)

**Time**: 2-5 minutes

**Manual Process**:
1. Go to Railway Dashboard → qteria-api → Deployments
2. Find previous working deployment
3. Click "Redeploy"
4. Railway builds + deploys old code (~2-3 min)
5. Verify: `curl https://api.qteria.com/health`

**Git Revert Process** (preferred):
```bash
# Identify bad commit
git log --oneline -10

# Revert bad commit
git revert abc123

# Push (triggers auto-deploy of reverted code)
git push origin main
```

**Why Git Revert > Railway Redeploy**:
- ✅ Git history preserved (audit trail)
- ✅ Redeploy reverted code to staging first (verify fix)
- ✅ Team sees revert in Git log (communication)

---

### Database Rollback (Alembic)

**Time**: 1-5 minutes (depends on data volume)

**Process**:
```bash
# Rollback last migration
railway run --service qteria-api-prod alembic downgrade -1

# Rollback to specific version
railway run --service qteria-api-prod alembic downgrade abc123

# View migration history
railway run --service qteria-api-prod alembic history
```

**Destructive Migrations** (can't rollback):
- Dropping columns with data
- Deleting rows
- Changing data types (lossy conversions)

**Solution**: Take database backup before risky migrations
```bash
# Before migration
railway run --service qteria-postgres pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# If migration fails, restore backup
railway run --service qteria-postgres psql $DATABASE_URL < backup_20240315_143022.sql
```

---

### Full System Rollback (All Components)

**Scenario**: Deploy breaks everything (frontend + backend + DB)

**Process**:
1. **Rollback database first** (most critical, preserves data)
   ```bash
   railway run --service qteria-api-prod alembic downgrade -1
   ```

2. **Rollback backend** (restore API functionality)
   ```bash
   git revert abc123 && git push origin main
   ```

3. **Rollback frontend** (restore UI)
   ```
   Vercel Dashboard → Promote previous deployment
   ```

4. **Verify** (smoke tests):
   ```bash
   curl https://api.qteria.com/health  # Backend OK
   curl https://qteria.com             # Frontend OK
   # Manually test: Create workflow, upload PDF
   ```

5. **Post-mortem** (within 24 hours):
   - What broke?
   - Why didn't staging catch it?
   - How to prevent in future?
   - Document in `docs/incidents/2024-03-15-deploy-rollback.md`

---

## Pre-Deployment Checklist

**Use this checklist before every production deploy**

### Code Quality
- [ ] All tests pass (`npm test` + `pytest`)
- [ ] Linting passes (ESLint, Black, Ruff)
- [ ] Type checking passes (TypeScript, MyPy)
- [ ] Code reviewed (if team >1, otherwise solo founder self-review)
- [ ] No console.log or print() statements in critical paths
- [ ] No TODO comments marked "BLOCKER"

### Database
- [ ] Migrations tested on staging
- [ ] Migrations are backward compatible (expand/contract pattern)
- [ ] Database backup taken (if destructive migration)
- [ ] Migration rollback tested locally

### Configuration
- [ ] Environment variables set correctly (prod vs staging)
- [ ] Secrets rotated if needed (quarterly rotation)
- [ ] CORS origins updated (if adding new domains)
- [ ] Feature flags configured (if using Vercel Flags)

### Dependencies
- [ ] No vulnerable dependencies (`npm audit`, `poetry audit`)
- [ ] Dependencies up-to-date (especially security patches)
- [ ] Lock files committed (package-lock.json, poetry.lock)

### Monitoring
- [ ] Sentry configured (error tracking enabled)
- [ ] Logs reviewed (no repeated errors in staging)
- [ ] Alerts configured (if adding new critical paths)

### Communication
- [ ] Team notified (if deploying during business hours)
- [ ] Customers notified (if breaking changes or downtime expected)
- [ ] Rollback plan documented (how to revert if breaks)

### Testing
- [ ] Smoke tests pass on staging
- [ ] Critical user journey tested manually (create workflow → upload PDF → get results)
- [ ] Performance tested (if changes affect Step 3: AI validation)

### Documentation
- [ ] CHANGELOG.md updated
- [ ] API docs updated (if endpoints changed)
- [ ] Runbooks updated (if new failure modes introduced)

---

## Post-Deployment Verification

**After deployment, verify these within 15 minutes**

### Automated Checks (CI/CD)
- [ ] GitHub Actions pipeline succeeded
- [ ] Vercel deployment succeeded (green checkmark)
- [ ] Railway deployment succeeded (green checkmark)
- [ ] Smoke tests passed (Playwright E2E)

### Manual Checks (Solo Founder)
- [ ] Frontend loads: Visit https://qteria.com
- [ ] Backend healthy: `curl https://api.qteria.com/health` returns 200 OK
- [ ] Authentication works: Log in as test user
- [ ] Critical path works:
  - [ ] Create new workflow
  - [ ] Upload PDF document
  - [ ] Start assessment (triggers background job)
  - [ ] View results (evidence-based pass/fail)
- [ ] Database responsive: Check Vercel Postgres dashboard (query time <100ms)
- [ ] Background jobs running: Railway logs show Celery worker processing jobs
- [ ] No errors in logs: Check Sentry (no new error spikes)

### Monitoring (First Hour)
- [ ] Error rate <1% (Sentry dashboard)
- [ ] Response time P95 <2 seconds (Vercel Analytics)
- [ ] API uptime 100% (Railway metrics)
- [ ] Database CPU <50% (Vercel Postgres metrics)
- [ ] No customer complaints (email, support tickets)

### If Issues Detected
- **Minor issues** (non-blocking): Create bug ticket, fix in next deploy
- **Major issues** (broken critical path): **ROLLBACK IMMEDIATELY** (see Rollback Procedures)
- **Data issues** (wrong results, data loss): **ROLLBACK + INCIDENT** (page on-call engineer)

---

## Runbooks

### Runbook 1: "All Assessments Failing"

**Symptoms**:
- Users report assessments stuck in "pending" status
- Railway logs show Celery errors: `AuthenticationError: Invalid API key`

**Diagnosis**:
```bash
# Check Celery worker logs
railway logs --service qteria-celery-prod --tail 100

# Common error: "anthropic.AuthenticationError: Invalid API key"
```

**Cause**: Claude API key expired or invalid

**Fix**:
1. Verify API key:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

2. If invalid: Get new key from Anthropic dashboard
3. Update Railway secret: `ANTHROPIC_API_KEY`
4. Restart Celery workers: Railway dashboard → Redeploy celery service
5. Retry failed assessments: PostgreSQL → UPDATE assessments SET status='pending' WHERE status='failed'

**Prevention**: Set calendar reminder to rotate API keys quarterly

---

### Runbook 2: "Frontend Can't Reach Backend (CORS Error)"

**Symptoms**:
- Frontend shows errors: "Network request failed"
- Browser console: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Diagnosis**:
```javascript
// Browser console
fetch('https://api.qteria.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)

// Error: "CORS policy: No 'Access-Control-Allow-Origin' header"
```

**Cause**: Backend `ALLOWED_ORIGINS` missing frontend URL

**Fix**:
1. Check Railway environment variable: `ALLOWED_ORIGINS`
2. Should include: `https://qteria.com,https://staging.qteria.com`
3. If missing: Add to Railway variables
4. Restart backend: Railway → Redeploy fastapi service
5. Verify: `curl -H "Origin: https://qteria.com" https://api.qteria.com/health -I`
   - Should see: `Access-Control-Allow-Origin: https://qteria.com`

**Prevention**: Document ALLOWED_ORIGINS in `.env.template`, add to pre-deploy checklist

---

### Runbook 3: "Database Connection Pool Exhausted"

**Symptoms**:
- API returns 500 errors: "OperationalError: connection pool exhausted"
- Railway logs: "FATAL: remaining connection slots reserved for non-replication superuser connections"

**Diagnosis**:
```bash
# Check active connections
railway run --service qteria-postgres psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# If >20 connections (Vercel Postgres free tier limit): Problem
```

**Cause**: Too many concurrent requests, connection leaks

**Fix** (Immediate):
1. Restart backend: Railway → Redeploy fastapi service (closes all connections)
2. Upgrade database: Vercel Postgres Hobby → Pro (256 connections)

**Fix** (Long-term):
1. Reduce connection pool size in FastAPI:
   ```python
   # app/database.py
   engine = create_engine(
       DATABASE_URL,
       pool_size=5,  # Max 5 connections per backend instance
       max_overflow=10,
       pool_pre_ping=True  # Verify connections before use
   )
   ```

2. Add connection pooling middleware (PgBouncer):
   - Railway → Add PgBouncer service
   - Update DATABASE_URL to point to PgBouncer (not direct Postgres)

**Prevention**: Monitor database connections in Vercel dashboard (alert if >80% pool)

---

### Runbook 4: "Deployment Succeeded But Site Shows Old Version"

**Symptoms**:
- GitHub Actions shows deploy succeeded
- Vercel/Railway shows new deployment live
- But users (and founder) see old version of site

**Diagnosis**:
```bash
# Check deployed version
curl https://qteria.com/api/version
# Expected: {"version": "1.2.3", "commit": "abc123"}
# Actual: {"version": "1.2.2", "commit": "old123"}
```

**Cause**: Browser cache or CDN cache

**Fix**:
1. **Hard refresh browser**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear Vercel edge cache**:
   ```bash
   vercel --prod --purge
   ```
3. **Verify latest deployment active**: Vercel dashboard → Deployments → Production (check timestamp)

**Prevention**:
- Add cache-busting headers in Next.js:
  ```javascript
  // next.config.js
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=0, must-revalidate',  // Always revalidate
          },
        ],
      },
    ]
  }
  ```

---

### Runbook 5: "Celery Worker Crashed (Memory Exhaustion)"

**Symptoms**:
- Assessments stuck in "processing" status
- Railway logs: "Killed" or "OOMKilled"
- Railway metrics: Memory usage 100%

**Diagnosis**:
```bash
# Check Celery worker logs
railway logs --service qteria-celery-prod --tail 200

# Look for: "Killed" or "MemoryError" or "OOMKilled"
```

**Cause**: PDF parsing loads entire 50-page PDF into memory (300MB+ per PDF)

**Fix** (Immediate):
1. Restart Celery worker: Railway → Redeploy celery service
2. Increase memory: Railway → Settings → 1GB RAM (from 512MB)
3. Retry stuck assessments: PostgreSQL → UPDATE assessments SET status='pending' WHERE status='processing'

**Fix** (Long-term):
1. Stream PDF parsing (don't load entire PDF):
   ```python
   # Before (loads entire file)
   with open("document.pdf", "rb") as f:
       pdf = PyPDF2.PdfReader(f)

   # After (streams pages)
   with open("document.pdf", "rb") as f:
       for page_num, page in enumerate(PyPDF2.PdfReader(f).pages):
           text = page.extract_text()
           process_page(text)  # Process incrementally
   ```

2. Add memory monitoring:
   ```python
   import psutil

   @celery.task
   def validate_assessment(assessment_id):
       process = psutil.Process()
       logger.info(f"Memory before: {process.memory_info().rss / 1024 / 1024:.2f} MB")
       # ... process PDFs ...
       logger.info(f"Memory after: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

**Prevention**: Set Railway alert (notify if memory >80% for 5 min)

---

### Runbook 6: "Users Can't Log In (NextAuth Error)"

**Symptoms**:
- Users click "Sign In with Google"
- Redirected back with error: "Configuration error"
- NextAuth logs: "OAUTH_CALLBACK_ERROR: redirect_uri mismatch"

**Diagnosis**:
```bash
# Check NextAuth configuration
curl https://qteria.com/api/auth/providers

# Check Google OAuth console (https://console.cloud.google.com/apis/credentials)
# Authorized redirect URIs should include:
#   https://qteria.com/api/auth/callback/google
#   https://staging.qteria.com/api/auth/callback/google
```

**Cause**: Google OAuth `redirect_uri` not matching configured URIs

**Fix**:
1. Go to Google Cloud Console → Credentials → OAuth 2.0 Client IDs
2. Edit "Qteria Web App" client
3. Add missing redirect URI: `https://qteria.com/api/auth/callback/google`
4. Save (takes ~5 min to propagate)
5. Test login: https://qteria.com/auth/signin

**Prevention**:
- Document OAuth setup in `docs/auth-setup.md`
- Add to deploy checklist: "Verify OAuth redirect URIs for new domains"

---

## Security and Compliance

### SOC2 Readiness (Required for Enterprise Customers)

**Deployment Security Requirements**:

1. **Access Control**:
   - ✅ Only authorized personnel can deploy (GitHub branch protection, Railway RBAC)
   - ✅ Production secrets isolated from staging
   - ✅ Audit log of all deployments (GitHub commits + Railway logs)

2. **Change Management**:
   - ✅ All changes reviewed (GitHub PRs, even if solo founder self-reviews)
   - ✅ Deployment checklist followed (documented above)
   - ✅ Rollback procedure tested quarterly

3. **Data Protection**:
   - ✅ Secrets never committed to Git (pre-commit hooks enforce)
   - ✅ Database encrypted at rest (Vercel Postgres default)
   - ✅ Connections encrypted in transit (TLS 1.2+)
   - ✅ Backup retention 30 days (Vercel Postgres automatic)

4. **Monitoring & Incident Response**:
   - ✅ Error tracking (Sentry)
   - ✅ Uptime monitoring (Vercel + Railway built-in)
   - ✅ Incident response runbooks (documented above)
   - ✅ Post-mortem process (template in `docs/incident-template.md`)

---

### Pre-Commit Hooks (Prevent Secrets Leaks)

**File**: `.husky/pre-commit`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Check for secrets before allowing commit
npx secretlint **/*

# Block if secrets detected
if [ $? -ne 0 ]; then
  echo "❌ SECRET DETECTED - Commit blocked!"
  echo "Remove secrets from code before committing."
  exit 1
fi

# Also check with gitleaks
gitleaks protect --staged --verbose

echo "✅ No secrets detected - commit allowed"
```

**Setup**:
```bash
npm install --save-dev husky secretlint gitleaks
npx husky install
npx husky add .husky/pre-commit "npm run check-secrets"
```

---

### Dependency Scanning (Detect Vulnerabilities)

**GitHub Actions** (runs weekly):

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday midnight
  push:
    branches: [main]

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run npm audit
        run: npm audit --audit-level=high

      - name: Run poetry audit
        run: |
          cd apps/api
          poetry install
          poetry run safety check

      - name: Notify if vulnerabilities found
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "🚨 Security vulnerabilities detected in dependencies - review required"
            }
```

**Fix Vulnerabilities**:
```bash
# Update dependencies
npm audit fix
cd apps/api && poetry update

# Test after updates
npm test
pytest

# Deploy updated dependencies
git commit -m "Security: Update dependencies (fix CVE-2024-1234)"
git push origin main
```

---

## Cost Optimization

### Infrastructure Cost Breakdown (MVP → Scale)

#### Phase 1: MVP (Month 1-3, TÜV SÜD Pilot)

| Service | Plan | Cost/Month | Notes |
|---------|------|------------|-------|
| Vercel (Frontend) | Hobby | $0 | Free tier sufficient |
| Railway (Backend) | Starter | $5 | 512MB RAM, 0.5 vCPU |
| Railway (Celery) | Starter | $5 | Separate worker instance |
| Vercel Postgres | Hobby | $0 | 256MB, 60 hours compute/month |
| Upstash Redis | Free | $0 | 10K commands/day |
| Vercel Blob | Free | $0 | 1GB storage (~20-50 assessments) |
| Claude API | Pay-as-you-go | $20 | 100 assessments × $0.21 |
| Sentry | Developer | $0 | 5K errors/month |
| GitHub Actions | Free | $0 | 2,000 minutes/month |
| **Total** | | **$30/month** | **$360/year** |

**Revenue**: $30K/year (TÜV SÜD) → Infrastructure = 1.2% of revenue

---

#### Phase 2: Post-Pilot (Month 4-12, 5 Customers)

| Service | Plan | Cost/Month | Notes |
|---------|------|------------|-------|
| Vercel (Frontend) | Pro | $20 | Better performance, analytics |
| Railway (Backend) | Pro | $20 | 1GB RAM, scale to 2 instances |
| Railway (Celery) | Pro | $20 | 3 workers for concurrency |
| Vercel Postgres | Pro | $20 | 10GB storage, 1000 hours compute |
| Upstash Redis | Pay-as-you-go | $10 | Higher throughput |
| AWS S3 | Pay-as-you-go | $5 | 10GB storage (migrated from Blob) |
| Claude API | Pay-as-you-go | $420 | 2,000 assessments × $0.21 |
| Clerk | B2B | $25 | Replace Auth.js (SSO, MFA) |
| Sentry | Team | $26 | 50K errors/month |
| GitHub Actions | Free | $0 | Still within free tier |
| **Total** | | **$566/month** | **$6,792/year** |

**Revenue**: $150K/year (5 customers × $30K) → Infrastructure = 4.5% of revenue

---

#### Phase 3: Scale (Year 2+, 10-20 Customers)

| Service | Plan | Cost/Month | Notes |
|---------|------|------------|-------|
| Vercel (Frontend) | Pro | $20 | Same, scales automatically |
| Railway (Backend) | Pro | $50 | 5 instances (load balanced) |
| Railway (Celery) | Pro | $50 | 10 workers (concurrency) |
| Vercel Postgres | Pro | $60 | 100GB storage, more compute |
| Upstash Redis | Pay-as-you-go | $30 | Higher volume |
| AWS S3 | Pay-as-you-go | $20 | 100GB storage |
| Claude API | Pay-as-you-go | $840 | 4,000 assessments × $0.21 |
| Clerk | Enterprise | $50 | SAML SSO, custom domains |
| Sentry | Business | $89 | Full APM |
| GitHub Actions | Team | $4 | Slightly over free tier |
| **Total** | | **$1,213/month** | **$14,556/year** |

**Revenue**: $500K/year (15 customers × $33K avg) → Infrastructure = 2.9% of revenue

---

### Cost Optimization Strategies

**1. Reduce Claude API Costs** (~50% of infrastructure spend at scale):

- **Batch criteria validation** (10 calls → 1 call):
  ```python
  # Before: 10 API calls per assessment
  for criteria in workflow.criteria:
      result = claude.validate(document, criteria)

  # After: 1 API call per assessment
  prompt = f"""
  Validate document against these 10 criteria:
  {json.dumps([c.to_dict() for c in workflow.criteria])}

  Return JSON array: [{{"criteria_id": "1", "pass": true, ...}}, ...]
  """
  results = claude.validate_batch(document, prompt)
  ```
  **Savings**: 90% fewer API calls (10 → 1) = ~$380/month at scale

- **Cache common validations**:
  ```python
  # If same workflow + same document type → likely same result
  cache_key = f"{workflow_id}:{document_hash}"
  if cached_result := redis.get(cache_key):
      return cached_result
  ```
  **Savings**: ~10-20% fewer API calls (repeated assessments)

- **Negotiate volume discount**: At $500K ARR, negotiate with Anthropic for enterprise pricing

---

**2. Optimize Database Storage**:

- **Archive old assessments** (delete after 2 years):
  ```sql
  -- Move to cold storage (S3) after 1 year
  SELECT * FROM assessments WHERE created_at < NOW() - INTERVAL '1 year'
  -- Archive to S3, then DELETE

  -- Reclaim space
  VACUUM FULL assessments;
  ```
  **Savings**: ~$10-20/month (reduce Postgres storage tier)

- **Compress PDFs before storage**:
  ```python
  # Compress PDFs using Ghostscript
  subprocess.run([
      "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
      "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
      f"-sOutputFile={output_path}", input_path
  ])
  ```
  **Savings**: ~50-70% smaller files → less S3 cost

---

**3. Right-Size Infrastructure**:

- **Monitor resource usage** (Railway dashboard):
  - If CPU <30%: Downgrade instance (save $10-20/month)
  - If Memory <50%: Downgrade instance
  - If Celery queue always empty: Reduce workers

- **Auto-scaling** (Phase 3):
  - Railway Pro supports auto-scaling (scale up during peak hours, down at night)
  - Saves ~30-40% vs. running max capacity 24/7

---

## Future Improvements

### Year 1 (MVP → Post-Pilot)

**Q1-Q2: Get to Production**
- [x] Basic CI/CD (GitHub Actions + Vercel/Railway auto-deploy)
- [x] Staging environment (test before prod)
- [ ] Automated database migrations (Alembic)
- [ ] Pre-commit hooks (block secrets)
- [ ] Monitoring (Sentry + basic dashboards)

**Q3-Q4: Stabilize + Scale**
- [ ] Feature flags (Vercel Flags or LaunchDarkly)
- [ ] Advanced monitoring (custom metrics, P95 latency)
- [ ] Load testing (Locust - simulate 100 concurrent assessments)
- [ ] Database performance tuning (indexes, query optimization)
- [ ] Runbook for every incident (documentation culture)

---

### Year 2 (5-10 Customers)

**Q1-Q2: Enterprise Features**
- [ ] Blue-green deployments (zero-downtime, instant rollback)
- [ ] Multi-region failover (if EU customers require data residency)
- [ ] Advanced secrets rotation (automated quarterly rotation)
- [ ] Compliance automation (SOC2 continuous compliance, not annual audit)

**Q3-Q4: Scaling Infrastructure**
- [ ] Canary releases (5% → 50% → 100% rollout)
- [ ] Infrastructure as Code (Terraform for AWS resources)
- [ ] Database read replicas (if query latency increases)
- [ ] CDN for documents (CloudFront or Cloudflare - faster PDF downloads)
- [ ] Advanced monitoring (Datadog APM, distributed tracing)

---

### Year 3+ (10-50 Customers)

**Multi-Region Architecture**:
- Deploy backend to EU (for EU customers - data residency requirement)
- Route traffic geographically (CloudFront + Route53)
- Replicate PostgreSQL across regions (read replicas)

**Advanced Reliability**:
- 99.99% uptime SLA (requires redundancy at every layer)
- Chaos engineering (test failure scenarios monthly)
- On-call rotation (if team grows beyond solo founder)

**Cost at Scale**:
- $50K/year infrastructure (at $2M ARR) = 2.5% of revenue
- Gross margin: 75-80% (including AI costs + support team)

---

## Summary: Deployment Checklist

### Initial Setup (One-Time)

- [ ] Set up Vercel project (connect GitHub repo, configure build)
- [ ] Set up Railway project (backend + Celery + PostgreSQL + Redis)
- [ ] Configure environment variables (Vercel + Railway secrets)
- [ ] Set up GitHub Actions (CI/CD pipeline from `.github/workflows/deploy.yml`)
- [ ] Configure domains (qteria.com → Vercel, api.qteria.com → Railway)
- [ ] Set up monitoring (Sentry, Vercel Analytics)
- [ ] Test deployment pipeline (push to staging, verify auto-deploy)
- [ ] Document rollback procedure (save in `docs/runbooks/`)
- [ ] Create incident response template (`docs/incident-template.md`)

### Every Deploy (Ongoing)

- [ ] Run pre-deployment checklist (tests, migrations, secrets)
- [ ] Push to `staging` branch (verify in staging environment)
- [ ] Merge to `main` (triggers auto-deploy to production)
- [ ] Run post-deployment verification (smoke tests, manual checks)
- [ ] Monitor for 1 hour (Sentry, Railway logs, user reports)
- [ ] If issues: Rollback immediately (see Runbook procedures)
- [ ] If stable: Update CHANGELOG.md, celebrate

---

## Conclusion

This deployment strategy enables Qteria to ship fast (multiple deploys/day) while maintaining reliability (99.9% uptime) and safety (rollback in <5 min).

**Key Principles**:
1. **Automate everything** - No manual steps (except database migrations, for safety)
2. **Deploy frequently** - Small changes = low risk
3. **Monitor constantly** - Know when things break before users complain
4. **Rollback quickly** - Assume deploys will fail, plan for it
5. **Document thoroughly** - Runbooks save 2am debugging

**Next Steps**:
1. Complete initial setup (Vercel + Railway + GitHub Actions)
2. Deploy MVP to production (first real user)
3. Test rollback procedure (practice before you need it)
4. Build monitoring dashboards (daily health check)
5. Write first runbook (after first incident)

Deployment is not a one-time event - it's a continuous practice. Start simple, automate incrementally, and learn from every deploy.

**Ready to ship to production? Let's go!**

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Owner**: Solo Founder
**Review Cadence**: Monthly (update after incidents or major changes)
