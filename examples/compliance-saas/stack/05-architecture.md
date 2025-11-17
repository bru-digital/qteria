# Architecture Principles: Compliance Assessment Platform

> **Context**: This is a completed example showing journey-optimized architecture decisions.

---

## Architecture Overview

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
┌──────▼───────────────────────────────────────┐
│  Next.js Frontend (Vercel)                   │
│  - Upload UI, Results Display                │
│  - SSR for shareable reports                 │
└──────┬───────────────────────────────────────┘
       │ API calls
┌──────▼───────────────────────────────────────┐
│  FastAPI Backend (Railway)                   │
│  - Business logic, AI orchestration          │
└──┬───┴───┬────────┬─────────┬────────────────┘
   │       │        │         │
   │  ┌────▼────┐ ┌─▼──────┐ ┌▼────────────┐
   │  │PostgreSQL│ │ Redis  │ │Claude API   │
   │  └─────────┘ └────────┘ └─────────────┘
   │
┌──▼──────┐
│  AWS S3 │
│  (Docs) │
└─────────┘
```

---

## Core Architectural Principles

### 1. Journey-Step Optimization

**Principle**: Optimize architecture for critical journey steps, not theoretical scale.

**Application**:
- **Step 1 (Upload)**: Direct S3 upload with presigned URLs (bypass backend)
- **Step 3 (Assessment)**: Async processing with real-time progress (UX priority)
- **Step 4 (Results)**: Server-side rendering for shareability (SEO matters)

### 2. Boring Technology, Strategic Innovation

**Principle**: Use proven tech (90%), innovate where it matters (10%).

**Boring (Reliable)**:
- PostgreSQL for data
- Redis for cache
- REST APIs (not GraphQL)
- Monolith (not microservices)

**Innovation (Differentiation)**:
- Claude API integration (our core value)
- Compliance framework reasoning engine
- Async assessment orchestration

### 3. API-First Design

**Principle**: Every feature accessible via API (enables integrations).

**Application**:
- All frontend → backend communication via REST API
- OpenAPI spec auto-generated (FastAPI)
- Webhook support for Enterprise tier
- Future: Partners integrate directly

### 4. Clear Separation of Concerns

**Frontend Responsibilities**:
- User interaction
- Real-time UI updates
- File selection (actual upload to S3)
- Result visualization

**Backend Responsibilities**:
- Business logic
- AI orchestration
- Data persistence
- Authentication/authorization

**Why**: Teams can work independently, easier to scale/replace components

### 5. Fail-Safe Design

**Principle**: Compliance use case requires reliability. Fail gracefully.

**Application**:
- Assessment failures don't lose uploaded documents (S3 retention)
- Database transactions (ACID) for critical operations
- Retry logic for Claude API calls (with exponential backoff)
- Error tracking (Sentry) catches issues before users report

### 6. Observable Systems

**Principle**: Can't improve what you can't measure.

**Implementation**:
- Every assessment tracked (completion, duration, errors)
- API latency monitoring (p50, p95, p99)
- Error rates by endpoint
- User funnel tracking (PostHog)
- Real-time dashboards (internal ops view)

---

## Data Flow: Document Assessment

**Journey Step 3 (The Core Flow)**:

```
1. User clicks "Assess Compliance"
   ↓
2. Frontend → Backend: POST /api/v1/assessments
   {document_id, frameworks: [SOC2, GDPR]}
   ↓
3. Backend validates, creates assessment record (PostgreSQL)
   status: "processing"
   ↓
4. Backend → Background Job (BullMQ)
   {assessment_id, document_url, frameworks}
   ↓
5. Frontend polls for updates: GET /api/v1/assessments/{id}
   Returns: status, progress, eta
   ↓
6. Worker fetches document from S3
   ↓
7. Worker → Claude API: Assess document against frameworks
   (30-60 second processing time)
   ↓
8. Claude returns structured findings
   ↓
9. Worker stores results in PostgreSQL (JSONB)
   Updates status: "completed"
   ↓
10. Frontend poll gets completed results
   ↓
11. User reviews findings (Journey Step 4)
```

**Why This Architecture**:
- Async processing (don't block user for 60 seconds)
- Polling (simpler than WebSockets for 30-60s waits)
- Background jobs (resilient to failures, retryable)
- JSONB storage (flexible results structure)

---

## Database Schema (Key Tables)

### Users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_id TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  team_id UUID REFERENCES teams(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Assessments
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  document_url TEXT NOT NULL,
  frameworks TEXT[] NOT NULL,
  status TEXT NOT NULL, -- processing, completed, failed
  results JSONB, -- Flexible structure from Claude
  duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessments_created ON assessments(created_at DESC);
```

### Usage Events (Billing)
```sql
CREATE TABLE usage_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  team_id UUID REFERENCES teams(id),
  event_type TEXT NOT NULL, -- assessment_completed
  assessment_id UUID REFERENCES assessments(id),
  billable BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_usage_team_month ON usage_events(team_id, date_trunc('month', created_at));
```

**Why This Schema**:
- UUID primary keys (distributed-safe, non-guessable)
- JSONB for assessment results (structure evolves with Claude)
- Indexes on query patterns (user dashboards, billing)
- Timestamptz (timezone-aware for global users)

---

## Security Architecture

### Authentication Flow
```
1. User → Clerk (login)
2. Clerk → JWT token
3. Frontend → Backend (JWT in Authorization header)
4. Backend validates JWT (Clerk public key)
5. Extract user_id, proceed with request
```

### Authorization Model
```
- Users can only access their own assessments
- Team admins can access team assessments
- Enforce at database query level (WHERE user_id = current_user)
```

### Document Security
```
- S3 presigned URLs (expire in 15 minutes)
- Users can't access others' documents (URL signing)
- Document retention policy (90 days for Free, unlimited for paid)
```

---

## Performance Optimization

### Critical Path (Journey Step 3)

**Target**: <2 minute total time from click to results

**Optimization**:
- Document fetch from S3: <2 seconds (parallel to Claude call prep)
- Claude API call: 30-60 seconds (waiting on AI)
- Result storage: <1 second (PostgreSQL JSONB insert)
- Frontend render: <500ms (optimized React components)

**Current P95**: 78 seconds (beating target ✅)

### Caching Strategy

**Framework Definitions** (Redis, TTL: 1 hour):
- Frameworks change rarely
- Cache saves PostgreSQL query on every assessment
- Hit rate: >95%

**User Preferences** (Redis, TTL: 10 minutes):
- Recent framework selections
- UI personalization
- Reduces perceived latency

**No Caching**:
- Assessment results (always fresh from database)
- Usage counts (billing accuracy critical)

---

## Scaling Strategy

### Current Capacity
- **Assessments**: 100K/month (current: 20K/month)
- **Concurrent assessments**: 50 (BullMQ concurrency: 10)
- **Database**: 10M+ assessment records
- **Storage**: Unlimited (S3 scales naturally)

### Bottlenecks & Solutions

**Bottleneck**: Claude API rate limits
**Solution**: Queue-based processing, graceful degradation, Claude enterprise tier

**Bottleneck**: PostgreSQL write throughput
**Solution**: Connection pooling (already implemented), read replicas at scale

**Bottleneck**: Frontend static hosting
**Solution**: Vercel CDN (already global, auto-scales)

---

## Deployment Strategy

### Environments
- **Production**: Vercel (frontend) + Railway (backend)
- **Staging**: Same setup, separate Railway project
- **Development**: Local Next.js + FastAPI, local PostgreSQL/Redis

### CI/CD Pipeline
```
1. Git push to feature branch
   ↓
2. GitHub Actions: Lint, type-check, tests
   ↓
3. Preview deployment (Vercel + Railway)
   ↓
4. Merge to main
   ↓
5. Auto-deploy to staging
   ↓
6. Manual approval → production
```

### Rollback Strategy
- Vercel: Instant rollback to previous deployment
- Railway: Keep last 10 deployments, one-click rollback
- Database migrations: Use Alembic (Python), reversible migrations

---

## Monitoring & Alerting

### What We Monitor

**System Health**:
- API response time (P50, P95, P99)
- Error rates by endpoint
- Database query performance
- Claude API latency & errors

**Business Metrics**:
- Assessments completed per hour
- Assessment success rate
- User activation rate
- Revenue events (Stripe webhooks)

### Alerts

**Critical** (Page on-call):
- Error rate >5% for 5 minutes
- API P95 >5 seconds
- Database connection failures

**Warning** (Slack notification):
- Error rate >2% for 10 minutes
- Assessment completion rate drops >10%
- Unusual Claude API errors

---

## Architecture Decision Records (ADRs)

### ADR-001: Why Monolith (Not Microservices)

**Decision**: Single FastAPI backend, not separate services for auth, assessment, billing.

**Rationale**:
- Team size: 2-3 engineers (can't support multiple services)
- Deployment complexity: Simpler to deploy one service
- Data consistency: Easier with single database
- Performance: No inter-service latency

**Trade-off**: Harder to scale different components independently (acceptable at current scale)

**Revisit When**: Team >10 engineers OR traffic >1M requests/day

### ADR-002: Why Polling (Not WebSockets)

**Decision**: Frontend polls for assessment status every 2 seconds.

**Rationale**:
- Assessment duration: 30-60 seconds (polling acceptable)
- Simplicity: No WebSocket server management
- Scalability: Stateless backend (easier to horizontally scale)
- Reliability: Polling auto-recovers from connection issues

**Trade-off**: Slightly higher server load (acceptable)

**Revisit When**: Need true real-time (<1 second updates)

---

**Connection to Other Cascade Outputs**:
- User Journey → Architecture optimizes Step 3 (critical path)
- Tech Stack → Architecture leverages chosen technologies
- Design System → Architecture supports client-side rendering patterns
- Backlog → Architecture enables feature roadmap without rewrites
