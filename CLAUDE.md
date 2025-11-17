# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Repository Overview

This is a **Stack-Driven v2.0** repository - an AI-powered product development framework that guides users through creating products via a cascading series of 14 strategic sessions. The framework helps users go from user journey to production-ready system in 8-10 hours.

**Current State**: This repository contains a complete cascade output for **Qteria** - an AI-driven document pre-assessment SaaS for the TIC (Testing, Inspection, Certification) industry. The cascade has been completed through Session 14.

**Key Principle**: Everything flows from the user journey. Tech stack, architecture, design, and backlog are all **derived** from understanding user needs, not prescribed templates.

---

## Core Concepts

### The Cascade Flow

The framework uses 14 progressive sessions where each builds on previous outputs:

1. `/refine-journey` → Define user journey through progressive interrogation
2. `/create-product-strategy` → Market validation and strategic positioning
3. `/choose-tech-stack` → Derive optimal tech from journey requirements
4. `/generate-strategy` → Create mission, metrics, monetization, architecture
5. `/create-brand-strategy` → Brand strategy foundation
6. `/create-design` → Design system optimized for journey
7. `/design-database-schema` → Database schema with ERD
8. `/generate-api-contracts` → API contracts with OpenAPI specs
9. `/create-test-strategy` → Comprehensive testing strategy
10. `/generate-backlog` → Prioritized user stories with RICE scoring
11. `/create-gh-issues` → Push backlog to GitHub
12. `/scaffold-project` → Generate working development environment
13. `/plan-deployment` → Deployment strategy and CI/CD
14. `/design-observability` → Monitoring, alerting, SLO strategy

**Check progress**: Use `/cascade-status` to see what's been completed.

### Directory Structure

```
qteria/
├── .claude/commands/        # Slash command definitions (framework prompts)
├── product-guidelines/      # Generated cascade outputs (gitignored per user)
│   ├── 00-user-journey.md
│   ├── 01-product-strategy.md
│   ├── 02-tech-stack.md
│   ├── 03-mission.md
│   ├── 04-*.md            # metrics, monetization, architecture
│   ├── 05-brand-strategy.md
│   ├── 06-design-system.md
│   ├── 07-database-schema.md
│   ├── 08-api-contracts.md
│   ├── 09-test-strategy.md
│   ├── 10-backlog/        # Generated user stories
│   ├── 12-project-scaffold/  # Actual code/config files
│   ├── 13-deployment-plan.md
│   └── 14-observability-strategy.md
├── templates/              # Blank templates used by slash commands
└── README.md              # Framework documentation
```

---

## Tech Stack (Qteria Example)

The current cascade generated this stack (derived from journey requirements):

- **Frontend**: Next.js 14+ (TypeScript, App Router)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with JSONB
- **Cache/Queue**: Redis (Upstash)
- **Storage**: Vercel Blob → AWS S3
- **AI**: Claude 3.5 Sonnet (Anthropic)
- **Auth**: Auth.js (NextAuth) → Clerk (when revenue allows)
- **Hosting**: Vercel (frontend) + Railway/Render (backend)

**Why these choices**: See `product-guidelines/02-tech-stack.md` for detailed reasoning traced to user journey requirements (fast PDF processing, AI validation, data privacy).

---

## Development Commands

### Scaffold Development (if using generated scaffold)

Located in `product-guidelines/12-project-scaffold/`:

```bash
# Start local services (PostgreSQL + Redis)
npm run docker:up

# Install dependencies
npm install
cd apps/api && pip install -r requirements-dev.txt && cd ../..

# Run database migrations
npm run db:migrate

# Start development servers
npm run dev        # Next.js frontend (port 3000)
npm run dev:api    # FastAPI backend (port 8000)

# Testing
npm run test       # All tests
npm run test:unit  # Unit tests only
npm run test:e2e   # E2E tests (Playwright)

# Code quality
npm run lint       # Lint all code
npm run format     # Format all code

# Database
npm run db:seed    # Seed development data
npm run db:reset   # Reset database (destructive)
```

### Framework Development

```bash
# Check cascade progress
/cascade-status

# Run full cascade automatically
/run-cascade

# Individual sessions (run in order)
/refine-journey
/create-product-strategy
/choose-tech-stack
# ... etc

# Post-cascade sessions (optional)
/design-user-experience
/discover-naming
/define-messaging
/design-brand-identity
/create-financial-model
/design-growth-strategy
/setup-analytics
```

---

## Architecture Principles

Derived from the cascade (see `product-guidelines/04-architecture.md`):

1. **Monolith First**: Single Next.js + FastAPI codebase. Split when revenue validates need.
2. **Background Jobs**: Long AI operations (10 min) run async via Celery + Redis
3. **API-First**: FastAPI exposes REST API, Next.js consumes it
4. **Data Privacy by Design**: Encrypted storage, zero-retention AI, audit logs
5. **Boring Technology**: Proven stack (no bleeding-edge experiments)

### Key Backend Patterns

- **Database**: SQLAlchemy ORM with Alembic migrations
- **Multi-tenancy**: Organization-based isolation (all queries filtered by org_id)
- **Error Handling**: Structured exceptions with user-friendly messages
- **Validation**: Pydantic models for request/response validation
- **Background Jobs**: Celery tasks for AI processing with retry logic

### Key Frontend Patterns

- **Routing**: Next.js App Router with server actions
- **State Management**: React Context for global state, server state with React Query
- **UI Components**: shadcn/ui + Tailwind CSS
- **Forms**: React Hook Form + Zod validation
- **File Upload**: Direct to blob storage with progress tracking

---

## Database Schema

See `product-guidelines/07-database-schema.md` for complete schema.

**Core Tables**:
- `organizations` - Multi-tenant isolation
- `users` - Authentication (via Auth.js)
- `workflows` - Validation workflow definitions
- `buckets` - Document categories in workflows
- `criteria` - Validation rules
- `assessments` - Document validation jobs
- `assessment_documents` - Uploaded files
- `assessment_results` - AI validation outputs
- `audit_logs` - Compliance audit trail

**Key Design Decisions**:
- UUID primary keys (non-guessable, distributed-safe)
- JSONB for flexible AI results storage
- Strategic indexes for common query patterns
- Foreign keys with CASCADE/RESTRICT for data integrity

---

## API Structure

See `product-guidelines/08-api-contracts.md` for complete API specification.

**Key Endpoints**:
- `POST /api/v1/workflows` - Create validation workflow
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/assessments` - Start document assessment
- `GET /api/v1/assessments/{id}/status` - Poll assessment progress
- `GET /api/v1/assessments/{id}/results` - Retrieve validation results

**API Conventions**:
- RESTful design with standard HTTP verbs
- JSON request/response bodies
- JWT authentication (Bearer tokens)
- Pagination: `?page=1&limit=20`
- Filtering: `?status=completed&created_after=2025-01-01`
- Standard error format: `{error: string, details?: object}`

---

## Testing Strategy

See `product-guidelines/09-test-strategy.md` for complete strategy.

**Coverage Targets**:
- Backend: 80% line coverage (Pytest)
- Frontend: 70% line coverage (Vitest)
- E2E: Critical user flows (Playwright)

**Test Organization**:
```
apps/api/tests/
├── unit/           # Pure functions, utilities
├── integration/    # API endpoints, database
└── e2e/           # Full user flows

apps/web/tests/
├── unit/          # Components, hooks
└── e2e/           # Playwright flows
```

**Running Tests**:
```bash
# Backend
cd apps/api
pytest                    # All tests
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest --cov             # With coverage

# Frontend
npm run test             # All tests
npm run test:unit        # Unit tests only
npm run test:e2e         # E2E tests
npm run test:coverage    # With coverage
```

---

## Working with Slash Commands

Slash commands are located in `.claude/commands/*.md`. Each command:
1. Reads previous cascade outputs from `product-guidelines/`
2. Applies framework templates from `templates/`
3. Generates new outputs in `product-guidelines/`

**Modifying Commands**:
- Edit `.claude/commands/{name}.md` to change prompts
- Test with `/cascade-status` to verify command is recognized
- Commands should maintain traceability to user journey

**Creating New Commands**:
1. Add `.claude/commands/new-command.md`
2. Follow existing patterns (read inputs, apply framework, write outputs)
3. Update cascade flow documentation if adding to core 14 sessions

---

## Important Constraints

### Data Privacy

The Qteria product handles sensitive certification documents:
- **Zero-retention AI**: Anthropic enterprise agreement required
- **Encryption at rest**: All blob storage encrypted
- **Audit logs**: Track all document access
- **Multi-tenant isolation**: Row-level security via organization_id

### Performance Requirements

From user journey (Step 3 - "AHA MOMENT"):
- **Assessment completion**: <10 minutes target
- **Evidence linking**: Must show exact page/section in PDF
- **False positive rate**: <5% (target)
- **False negative rate**: <1% (critical - can't miss real issues)

### Solo Founder Constraints

Stack optimized for single developer:
- **Simple deployment**: Vercel + Railway (no Kubernetes)
- **Boring technology**: Proven tools, no experiments
- **Monolith architecture**: Split only when revenue validates
- **Managed services**: PostgreSQL, Redis, blob storage all managed

---

## Migration Paths

### When to Scale Up

Defined in product strategy (see `product-guidelines/01-product-strategy.md`):

- **Auth.js → Clerk**: At $30K ARR (first paying customer)
- **Vercel Blob → AWS S3**: When storage limits hit (~50GB)
- **Monolith → Microservices**: At $500K+ ARR (not before)
- **API AI → Self-hosted**: Only if customers require (expensive)

### When NOT to Optimize

- **Don't add Kubernetes**: Not until $1M+ ARR
- **Don't split services**: Monolith handles 10 customers easily
- **Don't self-host AI**: API is 10-50x cheaper for MVP scale
- **Don't add GraphQL**: REST works fine for this use case

---

## Common Patterns

### Adding a New API Endpoint

1. Define route in `apps/api/app/api/v1/` (if scaffold exists)
2. Create Pydantic request/response models
3. Add business logic in service layer
4. Write tests (unit + integration)
5. Update OpenAPI spec in `product-guidelines/08-api-contracts.md`

### Adding a New UI Component

1. Create component in `apps/web/src/components/` (if scaffold exists)
2. Follow shadcn/ui patterns (Tailwind CSS)
3. Add to Storybook (if implemented)
4. Write tests (unit + integration)
5. Update design system docs in `product-guidelines/06-design-system.md`

### Running a Background Job

1. Define Celery task in `apps/api/app/tasks/` (if scaffold exists)
2. Trigger from API endpoint: `task.delay(params)`
3. Store job ID in database for status polling
4. Implement status endpoint: `GET /api/v1/jobs/{id}/status`
5. Handle retries and error states

---

## Philosophy

When working in this repository, remember:

1. **User journey first**: Every decision traces back to `product-guidelines/00-user-journey.md`
2. **Generative, not prescriptive**: Tech choices are derived from requirements, not templates
3. **Cascading decisions**: Each session builds on previous outputs
4. **Boring is beautiful**: Proven tech > exotic tech
5. **Ship fast**: Solo founder needs velocity, not complexity

**Before adding complexity**, ask:
- Does this serve a specific user journey step?
- Is this needed now, or premature optimization?
- Can we defer this until revenue validates the need?

---

## Deployment

See `product-guidelines/13-deployment-plan.md` for complete strategy.

**Environments**:
- **Local**: Docker Compose (PostgreSQL + Redis)
- **Staging**: Vercel Preview + Railway staging
- **Production**: Vercel Production + Railway production

**CI/CD** (via GitHub Actions):
```bash
# Defined in .github/workflows/ci.yml (if scaffold exists)
# Triggered on: push to main, pull requests

# Pipeline steps:
# 1. Lint (ESLint, Black, Ruff)
# 2. Type check (TypeScript, MyPy)
# 3. Test (Pytest, Vitest)
# 4. Build (Next.js, FastAPI)
# 5. Deploy (Vercel, Railway)
```

**Deployment Commands**:
```bash
# Preview deployment (automatic on PR)
# - Vercel creates preview URL
# - Railway creates staging backend

# Production deployment (automatic on merge to main)
# - Vercel deploys to production
# - Railway deploys to production
# - Run migrations: npm run db:migrate
```

---

## Monitoring & Observability

See `product-guidelines/14-observability-strategy.md` for complete strategy.

**Key Metrics**:
- **Golden Signals**: Latency, traffic, errors, saturation
- **Business Metrics**: Assessments/day, validation accuracy, user retention
- **SLOs**: 99.5% uptime, <10 min assessment completion

**Tools**:
- **Error Tracking**: Sentry
- **Logging**: Structured logs (JSON) to stdout
- **Metrics**: Vercel Analytics + custom metrics
- **APM**: Consider Datadog when revenue allows

---

## Support & Resources

- **Cascade Status**: Run `/cascade-status` to see progress
- **Framework Docs**: See `README.md` for full Stack-Driven documentation
- **Product Guidelines**: All strategic decisions in `product-guidelines/`
- **Backlog**: Generated user stories in `product-guidelines/10-backlog/`
- **GitHub Issues**: If `/create-gh-issues` was run, issues are on GitHub

**When Stuck**:
1. Check `/cascade-status` - are you missing a prerequisite session?
2. Read `product-guidelines/00-user-journey.md` - does this serve the journey?
3. Consult `product-guidelines/02-tech-stack.md` - why was this tech chosen?
4. Review `product-guidelines/01-product-strategy.md` - is this aligned with strategy?
