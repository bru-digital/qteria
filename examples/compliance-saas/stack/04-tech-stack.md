# Tech Stack: Compliance Assessment Platform

> **Context**: This is a completed example showing journey-driven tech decisions. Different journeys = different stacks!

---

## Core Stack

**Frontend**: Next.js 14 (React, TypeScript, Tailwind CSS)
**Backend**: FastAPI (Python 3.11)
**Database**: PostgreSQL 15
**Cache**: Redis 7
**Storage**: AWS S3
**AI**: Claude Sonnet 4 (Anthropic API)
**Auth**: Clerk
**Queue**: Redis + BullMQ
**Hosting**: Vercel (frontend) + Railway (backend + database)
**Monitoring**: Sentry + PostHog

---

## Why This Stack (Journey-Driven Decisions)

### Frontend: Next.js

**Journey Requirements**:
- Step 4: Shareable compliance reports need SEO
- Step 5: Public report links for stakeholders
- Step 1-2: Fast, responsive upload/config UX

**Why Next.js**:
✅ SSR for shareable reports (compliance officers share links with leadership)
✅ File-based routing (simple, fast development)
✅ API routes for backend proxy (avoid CORS complexity)
✅ Vercel deployment (zero-config, fast)
✅ React ecosystem (rich component libraries for document viewers)

**Alternatives Considered**:
- ❌ SvelteKit: Smaller ecosystem, team less familiar
- ❌ Vanilla SPA: No SSR for shareable reports
- ✅ Next.js: Best fit for requirements

### Backend: FastAPI (Python)

**Journey Requirements**:
- Step 3: AI assessment requires Claude API (Python SDK best-in-class)
- Step 1: PDF text extraction (strong Python libraries)
- Step 3: Async processing of long-running assessments

**Why FastAPI**:
✅ Python ecosystem for document processing (PyPDF2, pdfplumber, python-docx)
✅ Anthropic Python SDK (official, well-maintained)
✅ Async by default (handles concurrent assessments efficiently)
✅ Auto-generated OpenAPI docs (useful for enterprise API customers)
✅ Type hints = automatic validation (reduce bugs)

**Alternatives Considered**:
- ❌ Node/Express: Weaker document processing libraries
- ❌ Django: Too heavy, REST framework overhead
- ✅ FastAPI: Perfect for AI + document processing

### Database: PostgreSQL

**Journey Requirements**:
- Step 2: Store user frameworks, preferences, history
- Step 3: Complex assessment results (nested JSON)
- Step 5: Audit trail for regulatory compliance
- Business need: User data, billing, teams

**Why PostgreSQL**:
✅ JSONB for flexible assessment results (structure evolves)
✅ Full-text search for document content
✅ ACID compliance (critical for compliance use case)
✅ Excellent at joins (users, teams, assessments, frameworks)
✅ Proven at scale (billions of rows)

**Alternatives Considered**:
- ❌ MongoDB: Weak relational integrity, overkill for our schema
- ❌ DynamoDB: Serverless not needed, harder local dev
- ✅ PostgreSQL: Best balance of features and reliability

### Cache: Redis

**Journey Requirements**:
- Step 2: Cache framework definitions (reduce latency)
- Step 3: Rate limiting for API (prevent abuse)
- Business need: Session storage, background jobs

**Why Redis**:
✅ Sub-millisecond latency (framework lookups feel instant)
✅ Built-in pub/sub (real-time progress updates for Step 3)
✅ Job queue (BullMQ for background processing)
✅ Rate limiting primitives (protect API)

### Storage: AWS S3

**Journey Requirements**:
- Step 1: Store uploaded PDF documents (could be 100+ MB)
- Step 5: Store generated reports
- Business need: Audit retention (7+ years for compliance)

**Why S3**:
✅ Presigned URLs (users upload directly, no backend bottleneck)
✅ Unlimited scalability
✅ 99.999999999% durability (regulatory requirement)
✅ Lifecycle policies (archive old documents to Glacier)
✅ Industry standard (customers trust it)

**Alternatives Considered**:
- ❌ Database storage: Files too large, expensive
- ✅ S3: Purpose-built for this

### AI: Claude Sonnet 4

**Journey Requirements**:
- Step 3: Deep reasoning about compliance requirements
- Step 3: 100-page documents (long context)
- Step 4: Structured output (findings by framework)

**Why Claude**:
✅ Best reasoning capabilities (compliance requires nuance)
✅ 200K token context window (fits large documents)
✅ Strong instruction following (structured output format)
✅ Citations (can reference specific document sections)
✅ Reasonable cost ($3/M tokens)

**Alternatives Considered**:
- ❌ GPT-4: Good reasoning but higher cost, less consistent structured output
- ❌ GPT-3.5: Too weak for compliance reasoning
- ✅ Claude Sonnet: Best balance of capability, cost, reliability

### Auth: Clerk

**Journey Requirements**:
- Step 1: Quick signup (reduce friction)
- Business need: Team management
- Enterprise need: SSO (for Enterprise tier)

**Why Clerk**:
✅ Beautiful, pre-built UI (fast implementation)
✅ Social login + magic links (quick signup)
✅ Organization/team features (built-in)
✅ SSO ready (for Enterprise tier)
✅ Generous free tier (10K MAU)

**Alternatives Considered**:
- ❌ Build our own: Not our core value
- ❌ Auth0: More complex, less modern UX
- ✅ Clerk: Best DX for React/Next.js

### Hosting: Vercel + Railway

**Frontend (Vercel)**:
✅ Next.js native (zero config)
✅ Global CDN (fast everywhere)
✅ Automatic HTTPS + previews
✅ Generous free tier

**Backend (Railway)**:
✅ Git push to deploy
✅ Built-in PostgreSQL + Redis
✅ Fair pricing ($20/month includes database)
✅ Easy scaling (when needed)

**Alternatives Considered**:
- ❌ AWS: Too complex for MVP, over-engineering
- ❌ Heroku: Expensive, less modern
- ✅ Railway: Best balance of simplicity and power

---

## Stack Mapping to Journey

| Journey Step | Technical Requirement | Technology Solution |
|--------------|----------------------|---------------------|
| 1. Upload | Large file handling | S3 presigned URLs, Next.js client |
| 2. Frameworks | Fast lookups | Redis cache, PostgreSQL storage |
| 3. Assessment | AI reasoning, async processing | Claude API, FastAPI async, BullMQ |
| 4. Results | Rich display, sharing | Next.js SSR, PostgreSQL queries |
| 5. Export | PDF generation, storage | Python libraries, S3 |
| Business | Auth, billing, teams | Clerk, Stripe, PostgreSQL |

---

## Cost Estimate (1,000 users, 10,000 assessments/month)

| Service | Cost | Notes |
|---------|------|-------|
| Vercel | $0 | Free tier sufficient |
| Railway | $25 | Hobby plan + database |
| S3 | $8 | Storage + transfer |
| Clerk | $0 | Free tier (under 10K MAU) |
| Claude API | $120 | ~40M tokens/month (mostly Sonnet) |
| Sentry | $0 | Free tier |
| PostHog | $0 | Free tier |
| **Total** | **~$153/month** | |

**Revenue at scale**: 10,000 assessments × $0.10 = $1,000/month
**Margin**: 85% (~$850 profit on $1,000 revenue)

---

## Decision Framework Applied

For each technology choice, we asked:

1. **Does this serve a user journey step?** ✅ (All choices map to journey)
2. **Can we use boring/proven technology?** ✅ (No exotic tech)
3. **Do we have expertise?** ✅ (Team knows Python + React)
4. **What's operational burden?** ✅ (Managed services, simple deploy)
5. **Generous free tier?** ✅ (MVP costs <$200/month)
6. **Scales to 1M users?** ✅ (All tech proven at scale)

---

## What We DIDN'T Choose (And Why)

### Kubernetes / Microservices
**Why Not**: Over-engineering. Monolith scales to millions of requests. Add complexity only when needed.

### GraphQL
**Why Not**: REST is simpler. We don't have complex relational queries from frontend. KISS.

### MongoDB
**Why Not**: PostgreSQL JSONB gives us flexibility where needed, strong typing where it matters. Best of both worlds.

### AWS Lambda / Serverless
**Why Not**: Assessment processing is long-running (30-60 seconds). Traditional servers are simpler and more cost-effective for our pattern.

### WebSockets (for real-time)
**Why Not**: HTTP polling is sufficient for 30-60 second waits. WebSockets add complexity without meaningful UX improvement for our use case.

---

## Integration Points

### Stripe Integration (Monetization)
- **Why**: Best-in-class billing for PAYG + subscriptions
- **How**: Stripe webhook → FastAPI → PostgreSQL usage tracking

### PostHog Integration (Metrics)
- **Why**: Track North Star metric (assessments completed)
- **How**: Client + server-side events, funnel analysis

### Sentry Integration (Reliability)
- **Why**: Catch errors before users report them
- **How**: Frontend + backend SDKs, release tracking

---

## Upgrade Path (When We Outgrow Current Stack)

**At 100K assessments/month**:
- Move from Railway to AWS/GCP for better scaling
- Add read replicas for PostgreSQL
- Consider CDN for uploaded documents

**At 1M assessments/month**:
- Horizontal scaling of FastAPI workers
- Redis cluster (current single instance sufficient until then)
- Dedicated Claude quota (faster rate limits)

**At 10M+ assessments/month**:
- Consider microservices (if team structure demands it)
- Multi-region deployment
- Custom ML models for common assessment patterns

**Philosophy**: Don't pre-optimize. Current stack handles 100K assessments/month easily. Cross optimization bridge when we get there.

---

**Next in Cascade**: This tech stack enables our architecture principles (stack/05-architecture.md) and design system implementation (design/06-design-system.md).
