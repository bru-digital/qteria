# Tech Stack: Qteria

> **Derived from**: product-guidelines/00-user-journey.md, product-guidelines/01-product-strategy.md
> **Optimized for**: Fast PDF processing, AI validation, data privacy, solo founder constraints

---

## Core Stack

**Frontend**: Next.js 14+ (React, TypeScript)
**Backend**: Python (FastAPI)
**Database**: PostgreSQL with JSONB
**Cache**: Redis (Upstash) - for background jobs
**Storage**: Vercel Blob (or AWS S3)
**AI**: Claude 3.5 Sonnet (Anthropic) with zero-retention agreement
**Auth**: Auth.js (NextAuth) → migrate to Clerk when revenue allows
**Hosting**: Vercel (frontend) + Railway/Render (backend)

---

## Why This Stack (Journey-Driven Decisions)

### Frontend: Next.js 14+ (React, TypeScript)

**Journey Requirements**:

- Step 1: Process Manager creates workflows (complex form builder UI for buckets + criteria)
- Step 2: Project Handler uploads documents (drag-drop interface, progress indicators)
- Step 3: Results page (evidence-based display with document links, interactive)
- Step 5: Export validation reports (may want shareable public links in future)
- Strategy: Exceptional UX principle (minimalist, fast, intuitive)

**Why Next.js**:
✅ **Vercel deployment** (user's explicit preference for fast deployment)
✅ **Rich UI capabilities** (React ecosystem for complex workflow builder, drag-drop, results display)
✅ **TypeScript support** (type safety for solo founder - catch errors early)
✅ **App Router** (better structure for multi-page SaaS - workflows, assessments, results, settings)
✅ **Future-proof for SSR** (if we need shareable validation reports with preview links, already set up)
✅ **Server actions** (simplify form handling for workflow creation)

**Alternatives Considered**:

- ❌ **React SPA (Vite)**: Could work, but Next.js provides better structure + Vercel integration. No downside since we want Vercel anyway.
- ❌ **SvelteKit**: Smaller bundle, but React ecosystem richer for UI components (drag-drop, PDF viewers, etc.). Team familiarity matters.
- ✅ **Next.js**: Best fit for Vercel + complex UI + future flexibility

**Trade-offs**:

- Slightly more complex than SPA, but journey needs structured multi-page app
- React is heavier than Svelte, but ecosystem + component libraries worth it

---

### Backend: Python (FastAPI)

**Journey Requirements**:

- Step 2: Upload PDFs (parse, validate formats, store)
- Step 3: AI validates documents (<10 min processing, extract text, identify pages/sections)
- Step 3: Evidence linking (must parse PDFs to link to page X, section Y)
- Step 4: Re-run assessments (background job processing)
- Strategy: Data privacy (need strong control over document handling, encryption)

**Why Python + FastAPI**:
✅ **PDF processing libraries** (PyPDF2, pdfplumber, python-docx are best-in-class for Python - critical for Step 3)
✅ **AI SDK excellence** (OpenAI and Anthropic Python SDKs are first-class, well-maintained)
✅ **Document parsing** (Python excels at text extraction, section detection, page linking)
✅ **FastAPI performance** (async/await for concurrent AI requests, modern type hints)
✅ **Background jobs** (Celery + Redis for long-running AI validation, or FastAPI background tasks for simpler MVP)
✅ **Familiar ecosystem** (solo founder can move fast with Python's simplicity)

**Alternatives Considered**:

- ❌ **Node.js (Express/Fastify)**: Great for real-time, but Python's PDF/AI libraries are superior. Journey needs PDF processing more than real-time collaboration.
- ❌ **Go**: Fast, but ecosystem for PDF processing + AI is weaker than Python. Overkill for MVP scale.
- ✅ **Python (FastAPI)**: Best fit for PDF-heavy, AI-heavy workload

**Trade-offs**:

- Python slower than Go/Node for pure I/O, but PDF/AI processing is the bottleneck (not framework speed)
- FastAPI async mitigates Python's I/O limitations

---

### Database: PostgreSQL with JSONB

**Journey Requirements**:

- Step 1: Store workflows (relational: workflow → buckets → criteria)
- Step 1: Flexible criteria definitions (different types of checks: signatures, summaries, risk matrices)
- Step 3: Store assessment results (relational: assessment → criteria results → evidence links)
- Step 4: Re-assessment history (track changes, versions)
- Strategy: Scale to 10 customers, 2000 assessments/month by Year 3 (relational queries for analytics)

**Why PostgreSQL + JSONB**:
✅ **Relational structure** (workflows have buckets, buckets have criteria, assessments reference workflows)
✅ **Flexible criteria storage** (JSONB for variable criteria definitions without rigid schema)
✅ **Full-text search** (for searching workflows, criteria by name)
✅ **ACID guarantees** (critical for audit trails, assessment integrity - SOC2 requirement)
✅ **Proven scalability** (handles millions of rows, 2000 assessments/month is trivial)
✅ **Vercel Postgres integration** (easy deployment with Vercel frontend)

**Alternatives Considered**:

- ❌ **MongoDB**: Flexible, but lose relational integrity (workflow → bucket → criteria relationships matter). PostgreSQL JSONB gives flexibility WITHOUT losing relations.
- ❌ **MySQL**: Works, but PostgreSQL JSONB + full-text search better for this use case.
- ❌ **SQLite**: Too limited for multi-user SaaS, no cloud hosting.
- ✅ **PostgreSQL**: Best of both worlds (relational + flexible)

**Trade-offs**:

- Slightly more complex than pure document DB, but relational structure matches journey's data model

---

### Cache: Redis (Upstash)

**Journey Requirements**:

- Step 3: Background job queue (AI validation takes <10 min - need async processing)
- Step 4: Re-assessment (track job status, show progress to user)

**Why Redis (Upstash)**:
✅ **Job queue** (Celery + Redis for background AI validation tasks)
✅ **Serverless-friendly** (Upstash Redis works with Vercel/Railway hosting)
✅ **Session caching** (optional: cache user sessions, workflow metadata for speed)

**Alternatives Considered**:

- ❌ **No cache (FastAPI background tasks)**: Could work for MVP, but Celery + Redis more robust for 10-min jobs (retry logic, monitoring)
- ❌ **PostgreSQL as queue**: Possible, but Redis purpose-built for queues
- ✅ **Redis (Upstash)**: Industry standard, easy setup

**Trade-offs**:

- Adds complexity (another service), but 10-min background jobs need proper queue

---

### Storage: Vercel Blob (or AWS S3)

**Journey Requirements**:

- Step 2: Store uploaded PDFs (50+ page documents, potentially confidential)
- Step 3: Retrieve PDFs for AI processing
- Step 5: Serve PDFs for download/export
- Strategy: Data privacy (encryption at rest, audit logs)

**Why Vercel Blob**:
✅ **Vercel integration** (seamless with Next.js frontend)
✅ **Simple API** (upload, retrieve, delete)
✅ **Encryption at rest** (built-in)
✅ **Free tier** (1GB - enough for MVP pilot)

**Fallback: AWS S3**:
✅ **Industry standard** (if Vercel Blob limits hit)
✅ **SOC2 compliant** (critical for notified body customers)
✅ **Lifecycle policies** (auto-delete old assessments to save cost)

**Alternatives Considered**:

- ❌ **Store in PostgreSQL (bytea)**: Bad idea for large files (bloats DB, slow queries)
- ❌ **Local filesystem**: Doesn't work with Vercel/Railway (ephemeral)
- ✅ **Vercel Blob → S3 if needed**: Start simple, migrate if volume requires

**Trade-offs**:

- Vercel Blob less mature than S3, but simpler for MVP

---

### AI: Claude 3.5 Sonnet (Anthropic)

**Journey Requirements**:

- Step 3: Validate documents against criteria in <10 min
- Step 3: Evidence-based results (link to page X, section Y)
- Strategy: Data privacy non-negotiable (zero-retention, SOC2/ISO 27001 path)
- Strategy: AI accuracy <5% false positive, <1% false negative

**Why Claude 3.5 Sonnet (Anthropic)**:
✅ **Zero-retention agreements** (Anthropic offers enterprise privacy - no training on user data)
✅ **Document understanding** (Claude excels at long-context PDF reasoning - 200K tokens)
✅ **Structured output** (can return JSON with evidence: {pass: false, page: 8, section: "3.2"})
✅ **Cost-effective** (Claude Sonnet cheaper than GPT-4, faster than Opus)
✅ **Reasoning quality** (strong at compliance-style validation: "Does this document have X?")

**Alternatives Considered**:

- ✅ **GPT-4**: Also excellent, offers enterprise zero-retention. Backup if Claude doesn't perform well.
- ❌ **GPT-3.5**: Cheaper, but less accurate for compliance validation (can't risk false negatives)
- ❌ **Self-hosted open-source (Llama, Mistral)**: User's concern about data privacy. **Evaluation**: Too expensive for MVP ($500-2000/month for GPU infra). Revisit when revenue validates ($150K+ ARR). Start with Claude enterprise agreement.
- ✅ **Claude 3.5 Sonnet**: Best balance (accuracy + privacy + cost)

**Pricing Reality Check**:

- Claude Sonnet: ~$3 per million input tokens, ~$15 per million output tokens
- Assume 50-page PDF = ~15K tokens per doc × 3 docs per assessment = 45K tokens input
- Assume 10 criteria checks × 500 tokens output = 5K tokens output
- Cost per assessment: (45K × $3/1M) + (5K × $15/1M) = $0.135 + $0.075 = **~$0.21 per assessment**
- 100 assessments/month (TÜV SÜD pilot) = **$21/month AI cost**
- 2000 assessments/month (Year 3) = **$420/month AI cost**
- Still cheaper than India team ($8,333/month for $100K/year)!

**Trade-offs**:

- API dependency (if Anthropic has downtime, service impacted)
- Data privacy relies on vendor contract (but zero-retention agreement mitigates this)
- Self-hosting would give more control but costs 10-20x more for MVP

---

### Auth: Auth.js (NextAuth) → Clerk (when revenue allows)

**Journey Requirements**:

- Step 1: Process Managers and Project Handlers need different permissions (RBAC)
- Step 2: Workflow sharing (team access control)
- Strategy Goal 4: SOC2/ISO 27001 (audit logs, MFA support)
- Strategy: White-glove support (relationship manager needs admin access for customer debugging)

**Why Auth.js (NextAuth) for MVP**:
✅ **Free** (critical for bootstrapped MVP)
✅ **Next.js integration** (built for Next.js, server actions support)
✅ **OAuth providers** (Google, Microsoft - easy SSO for enterprise trial)
✅ **Session management** (JWT or database sessions)
✅ **RBAC possible** (can implement roles: ProcessManager, ProjectHandler, Admin)

**Why Clerk (when revenue allows)**:
✅ **Better UX** (polished auth UI, user management dashboard)
✅ **B2B features** (organizations, team invites, SSO built-in)
✅ **SOC2 compliant** (audit logs, MFA, SAML SSO for enterprise)
✅ **Relationship manager admin** (Clerk dashboard for customer debugging)

**Migration Path**:

- Start with Auth.js (free, functional)
- At $30K ARR (TÜV SÜD signed), migrate to Clerk ($25/month)
- Clerk enables enterprise SSO when selling to BSI, DEKRA, etc.

**Alternatives Considered**:

- ❌ **Roll your own**: Security risk, slow to build, hard to maintain (SOC2 audit nightmare)
- ❌ **Supabase Auth**: Good, but if not using Supabase for DB, less compelling
- ✅ **Auth.js → Clerk**: Start free, upgrade when revenue validates

**Trade-offs**:

- Auth.js less polished than Clerk, but functional for MVP
- Migration effort later, but worth saving $300/year until revenue

---

## Stack Mapping to Journey

| Journey Step                  | Technical Requirement                                    | Technology Solution                                                                                  |
| ----------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Step 1: Create Workflow**   | Form builder UI (buckets + criteria)                     | Next.js (React form components) + FastAPI (CRUD API) + PostgreSQL (relational storage)               |
| **Step 2: Upload Documents**  | Drag-drop PDFs, progress indicator                       | Next.js (file upload UI) + Vercel Blob (storage) + FastAPI (parse, validate)                         |
| **Step 3: AI Validation**     | Extract text, validate criteria, link evidence (<10 min) | FastAPI (PDF parsing with PyPDF2) + Claude Sonnet (AI reasoning) + Celery + Redis (background jobs)  |
| **Step 3: Evidence Display**  | Show pass/fail with page/section links                   | Next.js (results UI) + PostgreSQL (store evidence metadata) + Vercel Blob (serve PDFs)               |
| **Step 4: Re-run Assessment** | Update docs, re-validate                                 | Next.js (replace document) + FastAPI (trigger new job) + Celery (re-run AI validation)               |
| **Step 5: Export Report**     | Generate PDF summary                                     | FastAPI (generate PDF with ReportLab or WeasyPrint) + Vercel Blob (serve download)                   |
| **Auth & Permissions**        | RBAC (Process Manager vs Project Handler)                | Auth.js (session + roles) → Clerk (when revenue)                                                     |
| **Data Privacy**              | Encryption, audit logs, zero-retention AI                | Vercel Blob (encryption at rest) + Claude enterprise (zero-retention) + PostgreSQL (audit log table) |

---

## Cost Estimate (MVP Phase)

**Scenario**: TÜV SÜD pilot - 100 assessments/month, 5 active users

| Service                           | Cost             | Notes                                                   |
| --------------------------------- | ---------------- | ------------------------------------------------------- |
| **Vercel** (Frontend hosting)     | $0               | Hobby plan (free), upgrade to Pro ($20/month) if needed |
| **Railway** (Backend hosting)     | $5-10/month      | Starter plan, Python + FastAPI                          |
| **Vercel Postgres** (Database)    | $0               | Free tier (256MB), upgrade to Pro ($20/month) if needed |
| **Upstash Redis** (Job queue)     | $0               | Free tier (10K commands/day), enough for MVP            |
| **Vercel Blob** (PDF storage)     | $0               | Free tier (1GB), ~20-50 assessments before upgrade      |
| **Claude AI** (Anthropic)         | $20-30/month     | 100 assessments × $0.21 each = ~$21/month               |
| **Auth.js** (Authentication)      | $0               | Open source, free                                       |
| **Monitoring** (Sentry/LogRocket) | $0               | Free tier for MVP                                       |
| **Domain** (qteria.com)           | $12/year         | ~$1/month                                               |
|                                   |                  |                                                         |
| **Total (MVP)**                   | **$25-40/month** | **~$300-480/year**                                      |

**At Scale (Year 3: 2000 assessments/month, 10 customers)**:

| Service            | Cost           | Notes                                 |
| ------------------ | -------------- | ------------------------------------- |
| Vercel Pro         | $20/month      | Pro plan for better performance       |
| Railway (Backend)  | $20-50/month   | Scale up for concurrent AI jobs       |
| Vercel Postgres    | $20/month      | Pro plan for more storage             |
| Upstash Redis      | $10/month      | Paid tier for higher throughput       |
| Vercel Blob        | $20/month      | ~5GB storage for PDFs                 |
| Claude AI          | $420/month     | 2000 assessments × $0.21 = $420/month |
| Clerk              | $25/month      | B2B plan for SSO, MFA                 |
| Monitoring         | $50/month      | Paid tier for SOC2 compliance         |
|                    |                |                                       |
| **Total (Year 3)** | **$585/month** | **~$7,020/year**                      |

**Revenue Context**:

- Year 3 revenue: $300K ARR (10 customers × $30K)
- Infrastructure cost: $7K/year
- **Gross margin: 97.7%** (SaaS dream!)

---

## Development Stack (Tools & Workflow)

**Version Control**: Git + GitHub
**CI/CD**: Vercel (frontend auto-deploy on push) + Railway (backend auto-deploy)
**Package Management**: npm (frontend) + Poetry (Python backend)
**Type Safety**: TypeScript (frontend) + Pydantic (backend FastAPI models)
**Code Quality**: ESLint + Prettier (frontend) + Black + Ruff (Python)
**Testing**: Vitest (frontend unit) + Pytest (backend unit) + Playwright (E2E)
**Monitoring**: Sentry (error tracking) + Vercel Analytics (web vitals)

---

## What We DIDN'T Choose (And Why)

### Kubernetes / Docker Orchestration

**Why Not**: Over-engineering for MVP and Year 3 scale (10 customers, 2000 assessments/month). Vercel + Railway handle this scale trivially. Monolith scales to millions of requests before needing microservices. Add complexity only when $1M+ ARR validates need.

**Journey Reality**: Solo founder needs speed, not DevOps complexity. K8s adds weeks of setup for zero MVP benefit.

---

### GraphQL

**Why Not**: REST is simpler. Journey doesn't show complex relational queries from frontend (no "fetch workflow + nested buckets + criteria + last 10 assessments in one query"). FastAPI REST endpoints with Pydantic models are fast to build and maintain.

**Journey Reality**: Frontend knows what data it needs for each page (workflow list, workflow detail, assessment results). No over-fetching problem GraphQL solves.

---

### MongoDB / NoSQL

**Why Not**: Journey has clear relational structure (workflows → buckets → criteria, assessments → results). PostgreSQL JSONB gives flexibility for variable criteria definitions WITHOUT losing relational integrity.

**Journey Reality**: Need to query "all assessments for workflow X" (relational) but also store flexible criteria types (JSONB). PostgreSQL does both.

---

### React Native / Mobile App

**Why Not**: Journey is web-first. Process Managers and Project Handlers work at desks (office computers). No mobile requirement. Don't build mobile until users explicitly request it.

**Journey Reality**: Step 2 shows "drag-drop documents" (desktop interaction). No mobile-first signals.

---

### Microservices Architecture

**Why Not**: Monolith (Next.js frontend + FastAPI backend) is simpler and faster to build. Journey doesn't require independent scaling of services. PDF processing and AI validation happen in same backend flow - no reason to split.

**Journey Reality**: Solo founder. Microservices mean more repos, more deploys, more complexity. Monolith until $500K+ ARR.

---

### Self-Hosted AI (Llama, Mistral)

**Why Not**: User's key concern about data privacy is valid, BUT:

- **Cost**: Self-hosted GPUs cost $500-2000/month (vs. $20-420/month for Claude API)
- **Accuracy**: Open-source models (Llama 3, Mistral) lag GPT-4/Claude for reasoning quality (critical for <1% false negative goal)
- **Enterprise agreements**: Claude and OpenAI offer zero-retention contracts for enterprise customers
- **Migration path**: Start with API + zero-retention, validate product-market fit with TÜV SÜD, THEN invest in self-hosted if customers demand it (when revenue justifies $500-2K/month infra cost)

**Journey Reality**: $30K/year revenue in Year 1 can't support $24K/year self-hosted AI cost. Claude API at $21-420/month is 10-50x cheaper. Revisit at $150K+ ARR.

**Recommendation**: Negotiate zero-retention agreement with Anthropic (they offer this for enterprise). If TÜV SÜD rejects API even with zero-retention, THEN explore self-hosted as blocker removal.

---

### Serverless Functions (AWS Lambda, etc.) for Backend

**Why Not**: FastAPI on Railway/Render is simpler for long-running AI validation (10 min jobs). Lambda has 15-minute timeout, but cold starts + complexity not worth it for MVP.

**Journey Reality**: Background jobs (Celery + Redis) easier to reason about than chaining Lambda functions. Serverless shines for spiky traffic (not our pattern - steady assessment flow).

---

## Architecture Principles (Preview of Session 4)

Based on this tech stack, architecture will follow:

1. **Monolith First**: Next.js frontend + FastAPI backend. Split when revenue validates need.
2. **Background Jobs**: Long AI validation (10 min) runs async via Celery + Redis. User gets notification when done.
3. **API-First**: FastAPI backend exposes REST API. Next.js frontend consumes it. Future: third-party integrations possible.
4. **Data Privacy by Design**: PDFs stored encrypted (Vercel Blob), AI with zero-retention (Claude enterprise), audit logs in PostgreSQL.
5. **Boring Technology**: Proven stack (Next.js, FastAPI, PostgreSQL, Redis). No bleeding-edge experiments.

---

## Migration Risks & Mitigations

**Risk: Claude API doesn't meet TÜV SÜD data privacy requirements**

- **Mitigation**: Have GPT-4 enterprise agreement as backup. If both rejected, budget $500-1K/month for self-hosted Llama 3 (delay launch 1-2 months to set up GPU infra).

**Risk: Vercel Blob limits hit (storage/bandwidth)**

- **Mitigation**: Migrate to AWS S3 (straightforward code change, similar API).

**Risk: FastAPI backend too slow for concurrent AI jobs**

- **Mitigation**: Scale Railway/Render vertically (more RAM/CPU). If still bottleneck, add horizontal scaling (multiple backend instances behind load balancer).

**Risk: PostgreSQL query performance degrades at scale**

- **Mitigation**: Add indexes on common queries (workflow_id, user_id). If still slow, add Redis caching layer. PostgreSQL handles millions of rows easily.

---

## Next in Cascade

With tech stack defined, next sessions will:

- **Session 4 (`/generate-strategy`)**: Define mission, metrics, monetization, architecture principles
- **Session 6 (`/create-design`)**: Design system optimized for this stack (Next.js components, Tailwind CSS, shadcn/ui)
- **Session 7 (`/design-database-schema`)**: PostgreSQL schema for workflows, buckets, criteria, assessments, results
- **Session 8 (`/generate-api-contracts`)**: FastAPI endpoints for CRUD operations, assessment execution

This stack enables fast iteration (Vercel deploy), strong AI capabilities (Claude), and data privacy (zero-retention + encryption) - all optimized for YOUR journey.

---

**Stack Summary**: Next.js + FastAPI + PostgreSQL + Claude. Boring, proven, fast to ship. Optimized for PDF processing, AI validation, data privacy, and solo founder velocity.
