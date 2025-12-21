# Observability Strategy: Qteria

> **Derived from**: Architecture (Session 4), Metrics (Session 4), Test Strategy (Session 9), Deployment Plan (Session 13)
> **Purpose**: Monitor, measure, and maintain production reliability
> **Philosophy**: You can't improve what you can't measure - observability enables continuous delivery of journey value

---

## Executive Summary

This observability strategy ensures Qteria can:

- ✅ **Detect issues before users** - Alert on symptoms (errors, latency) not just downtime
- ✅ **Debug production incidents** - Logs + metrics + traces answer "what happened and why"
- ✅ **Measure reliability** - SLOs define user expectations with error budgets
- ✅ **Drive improvements** - Data informs where to optimize (Step 3: AI validation speed)
- ✅ **Meet compliance** - SOC2 requires logging, monitoring, incident response

**Key Metrics**:

- **Availability SLO**: 99.9% uptime (43 min downtime/month allowed)
- **Performance SLO**: P95 assessment processing time <10 minutes
- **Accuracy SLO**: <5% false positives, <1% false negatives
- **Error Budget**: 0.1% failure rate = room to experiment and deploy

**Three Pillars**:

1. **Metrics** (What is happening?) - Latency, traffic, errors, saturation
2. **Logs** (Why is it happening?) - Structured events for debugging
3. **Traces** (Where is it happening?) - Request flow across services

---

## Observability Philosophy

### Principles

**1. Alert on Symptoms, Not Causes**

- ❌ Don't alert: "CPU >80%" (cause)
- ✅ Do alert: "API errors >1%" (symptom users experience)
- **Why**: CPU can be high without affecting users. Alert on user-facing impact.

**2. Observe User Journeys, Not Just Services**

- ❌ Don't just monitor: "Frontend responded in 200ms"
- ✅ Do monitor: "Step 3 (AI validation) completed in 8 minutes"
- **Why**: Journey critical path (Step 3) is what users care about, not individual service response time.

**3. SLOs Over SLAs**

- **SLA**: Contract with customer (99.9% uptime or refund)
- **SLO**: Internal target (99.95% uptime → 0.05% error budget)
- **Why**: SLO stricter than SLA creates safety margin. Burn error budget before violating SLA.

**4. Dashboards Answer Questions**

- ❌ Don't create: "Database dashboard" (what data?)
- ✅ Do create: "Is the system healthy?" dashboard (answers specific question)
- **Why**: Dashboards are tools for decision-making, not data dumps.

**5. Runbooks Save 2am Debugging**

- First incident: Debug and fix (could take hours)
- Document solution in runbook
- Second incident: Refer to runbook (5-10 min fix)
- **Why**: Most incidents repeat. Runbooks compress response time 10-100x.

**6. Post-Mortems Without Blame**

- Incidents happen (error budget exists for this reason)
- Post-mortem asks: "How to prevent?" not "Who caused it?"
- Action items with owners and deadlines
- **Why**: Blame culture hides incidents. Blameless culture prevents future incidents.

**7. Cost-Aware Observability**

- Observability can cost >$1,000/month if unconstrained
- Start lean (structured logs + basic metrics + critical alerts)
- Add complexity when revenue validates spend
- **Why**: Observability ROI is reliability, but over-monitoring has diminishing returns.

---

## Golden Signals (Four Key Metrics Per Service)

### What Are Golden Signals?

**Four metrics that reveal service health**:

1. **Latency**: How long requests take (P50, P95, P99)
2. **Traffic**: How many requests (requests/sec, or domain-specific like assessments/day)
3. **Errors**: How many requests fail (% error rate)
4. **Saturation**: How close to capacity (CPU, memory, queue depth)

**Why These Four**: Cover user experience (latency, errors) and capacity (traffic, saturation)

---

### Frontend (Next.js on Vercel)

**Service**: qteria.com

**1. Latency**:

- **Metric**: P95 page load time
- **Target**: <2 seconds (industry standard for web apps)
- **Why**: Users notice slow page loads, abandon if >3 seconds
- **How to measure**: Vercel Analytics (built-in Web Vitals)

**2. Traffic**:

- **Metric**: Requests per minute (page views)
- **Target**: ~500 requests/day at MVP (5 users × 100 requests/day), grow to 5,000/day at scale
- **Why**: Traffic spikes indicate growth or issues (DDOS, bot traffic)
- **How to measure**: Vercel Analytics

**3. Errors**:

- **Metric**: Frontend error rate (%)
- **Target**: <1% (99% of user actions succeed)
- **Why**: Errors = broken UX (can't create workflow, upload fails)
- **How to measure**: Sentry error tracking (JS errors, API call failures)

**4. Saturation**:

- **Metric**: Vercel edge function invocations per second
- **Target**: <10,000 invocations/sec (Vercel Pro tier limit)
- **Why**: Vercel scales automatically, but check for runaway functions
- **How to measure**: Vercel dashboard

**Critical Alert**:

- Frontend error rate >5% for 5 minutes → Page founder immediately

---

### Backend API (FastAPI on Railway)

**Service**: api.qteria.com

**1. Latency**:

- **Metric**: P95 API response time
- **Target**: <500ms for CRUD endpoints (GET /workflows, POST /assessments)
- **Why**: Fast API = snappy UX. Slow API = users perceive app as broken.
- **How to measure**: Custom middleware logging (FastAPI request duration)

**2. Traffic**:

- **Metric**: Requests per second (RPS)
- **Target**: ~0.5 RPS at MVP (5 users × ~500 requests/day), grow to 5 RPS at scale
- **Why**: Traffic patterns reveal usage (spike during work hours, drop at night)
- **How to measure**: Railway metrics (HTTP requests count)

**3. Errors**:

- **Metric**: API error rate (%)
- **Target**: <0.5% (99.5% of API calls succeed)
- **Why**: API errors = broken features (can't save workflow, assessment fails)
- **How to measure**: Sentry + custom metrics (count 5xx responses / total responses)

**4. Saturation**:

- **Metric**: Railway instance CPU %
- **Target**: <70% average, <90% P95
- **Why**: High CPU = slow responses, eventual crashes
- **How to measure**: Railway metrics dashboard

**Critical Alerts**:

- API error rate >1% for 5 minutes → Page founder
- API P95 latency >2 seconds for 10 minutes → Page founder
- Railway CPU >90% for 10 minutes → Alert founder (scale up instance)

---

### Background Jobs (Celery Workers on Railway)

**Service**: Celery workers (AI validation processing)

**1. Latency** (Job Duration):

- **Metric**: P95 assessment processing time
- **Target**: <10 minutes (user expectation: "results in 5-10 min")
- **Why**: Core journey (Step 3) - slow processing = users abandon
- **How to measure**: Custom metric (log job start/end time, calculate duration)

**2. Traffic** (Job Queue Depth):

- **Metric**: Assessments queued (waiting to start)
- **Target**: <10 jobs in queue (low wait time)
- **Why**: Queue depth >50 = users wait 30+ min (poor experience)
- **How to measure**: Redis queue length (Celery inspect active/scheduled)

**3. Errors** (Job Failure Rate):

- **Metric**: % of assessments that fail (status='failed')
- **Target**: <2% (98% success rate - some failures expected from bad PDFs)
- **Why**: Failed assessments = no results = users re-upload = wasted time
- **How to measure**: PostgreSQL query (failed assessments / total assessments)

**4. Saturation** (Worker Capacity):

- **Metric**: Active workers / max workers
- **Target**: <80% utilization (room for spikes)
- **Why**: 100% utilization = queue grows, long wait times
- **How to measure**: Celery inspect stats (active workers)

**Critical Alerts**:

- Assessment failure rate >10% for 15 minutes → Page founder (AI API down?)
- Queue depth >50 jobs for 30 minutes → Alert founder (add workers)
- P95 processing time >15 minutes for 1 hour → Alert founder (AI slow, optimize)

---

### Database (PostgreSQL on Vercel)

**Service**: Vercel Postgres

**1. Latency** (Query Duration):

- **Metric**: P95 query time
- **Target**: <100ms for SELECT, <500ms for complex queries
- **Why**: Slow queries = slow API = slow UX
- **How to measure**: PostgreSQL `pg_stat_statements` extension (log slow queries)

**2. Traffic** (Query Rate):

- **Metric**: Queries per second (QPS)
- **Target**: ~5-10 QPS at MVP, grow to 50-100 QPS at scale
- **Why**: Sudden drop = outage, sudden spike = runaway query or attack
- **How to measure**: Vercel Postgres dashboard

**3. Errors** (Connection Failures):

- **Metric**: Database connection errors per minute
- **Target**: 0 errors (database should always be reachable)
- **Why**: Connection errors = API fails = users see 500 errors
- **How to measure**: Sentry (catch SQLAlchemy connection errors)

**4. Saturation** (Connection Pool):

- **Metric**: Active connections / max connections
- **Target**: <80% (Vercel free tier = 20 connections, Pro = 256)
- **Why**: Pool exhaustion = API hangs, timeouts, 500 errors
- **How to measure**: PostgreSQL query (`SELECT count(*) FROM pg_stat_activity`)

**Critical Alerts**:

- Database connection errors >5 in 5 minutes → Page founder (DB down?)
- Connection pool >90% for 10 minutes → Alert founder (connection leak or scale up)
- P95 query time >1 second for 10 minutes → Alert founder (missing index or bad query)

---

### AI Service (Claude API via Anthropic)

**Service**: Claude 3.5 Sonnet API (external dependency)

**1. Latency** (API Response Time):

- **Metric**: P95 Claude API response time
- **Target**: <30 seconds per API call (for 50-page PDF validation)
- **Why**: Claude latency directly impacts Step 3 processing time
- **How to measure**: Custom metric (log API call start/end)

**2. Traffic** (API Calls Per Day):

- **Metric**: Claude API calls per day
- **Target**: ~100-200 calls/day at MVP (100 assessments × 1-2 calls each), grow to 2,000+/day
- **Why**: Track cost (Claude charges per API call)
- **How to measure**: Custom counter (increment on each API call)

**3. Errors** (API Failure Rate):

- **Metric**: % of Claude API calls that fail (rate limit, timeout, auth error)
- **Target**: <1% (Claude is reliable, but occasional timeouts happen)
- **Why**: API failures = assessment fails = users frustrated
- **How to measure**: Sentry (catch anthropic.APIError exceptions)

**4. Saturation** (Rate Limits):

- **Metric**: API calls per minute (check against rate limit)
- **Target**: <80% of rate limit (Claude Tier 1 = 50 requests/min)
- **Why**: Hit rate limit = API calls rejected = assessments fail
- **How to measure**: Custom counter (API calls per minute, compare to limit)

**Critical Alerts**:

- Claude API error rate >5% for 10 minutes → Page founder (AI down, rotate key)
- Claude API latency P95 >60 seconds for 30 minutes → Alert founder (AI slow, contact Anthropic)

---

## Logging Strategy

### Philosophy: Structured Logs for Debugging

**Why Structured Logs**:

- ❌ Unstructured: `"User abc123 started assessment at 2024-03-15 14:30"` (hard to query)
- ✅ Structured: `{"event": "assessment_started", "user_id": "abc123", "timestamp": "2024-03-15T14:30:00Z"}` (easy to query)

**Benefits**:

- Query by field: "Show all assessments that failed for user abc123"
- Aggregate: "Count assessments started per hour"
- Alert: "Trigger alert if error_count >10 in 5 min"

---

### Log Levels (When to Use Each)

| Level        | When to Use                          | Example                                                       |
| ------------ | ------------------------------------ | ------------------------------------------------------------- |
| **DEBUG**    | Development only (verbose details)   | `"Parsed PDF page 15, extracted 2,453 characters"`            |
| **INFO**     | Normal operations (lifecycle events) | `"Assessment started: assessment_id=abc123, user_id=user456"` |
| **WARN**     | Recoverable issues (retry succeeded) | `"Claude API timeout, retrying (attempt 2 of 3)"`             |
| **ERROR**    | Failures requiring attention         | `"Assessment failed: PDF parsing error, document corrupted"`  |
| **CRITICAL** | System-wide failures                 | `"Database connection pool exhausted, API unavailable"`       |

**Production Log Level**: INFO (DEBUG too verbose, increases cost)

---

### Structured Log Format (JSON)

**Standard Fields** (every log entry):

```json
{
  "timestamp": "2024-03-15T14:30:00.123Z", // ISO 8601 format
  "level": "INFO", // DEBUG, INFO, WARN, ERROR, CRITICAL
  "service": "api", // frontend, api, celery
  "environment": "production", // development, staging, production
  "version": "1.2.3", // Git commit SHA or version tag
  "message": "Assessment started", // Human-readable summary
  "event": "assessment_started", // Machine-readable event type
  "user_id": "user_abc123", // Who triggered this
  "request_id": "req_xyz789", // Trace requests across services
  "duration_ms": 1234 // How long operation took (if applicable)
}
```

**Event-Specific Fields** (add context):

**Assessment Started**:

```json
{
  "event": "assessment_started",
  "assessment_id": "assess_123",
  "workflow_id": "workflow_456",
  "document_count": 3,
  "estimated_duration_sec": 600
}
```

**Assessment Completed**:

```json
{
  "event": "assessment_completed",
  "assessment_id": "assess_123",
  "status": "success",
  "duration_sec": 485,
  "criteria_checked": 10,
  "criteria_passed": 8,
  "criteria_failed": 2
}
```

**API Request**:

```json
{
  "event": "api_request",
  "method": "POST",
  "path": "/api/v1/assessments",
  "status_code": 201,
  "duration_ms": 245,
  "user_id": "user_abc123",
  "ip_address": "192.168.1.1"
}
```

**Claude API Call**:

```json
{
  "event": "ai_api_call",
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "prompt_tokens": 15234,
  "completion_tokens": 567,
  "cost_usd": 0.05,
  "duration_ms": 12345,
  "success": true
}
```

**Error Log**:

```json
{
  "event": "error",
  "error_type": "PDFParsingError",
  "error_message": "Invalid PDF: Missing page tree",
  "stack_trace": "...",
  "assessment_id": "assess_123",
  "document_id": "doc_789",
  "user_id": "user_abc123"
}
```

---

### Log Retention Policy

| Environment     | Retention | Why                                                   |
| --------------- | --------- | ----------------------------------------------------- |
| **Development** | 7 days    | Short-term debugging, not compliance-critical         |
| **Staging**     | 30 days   | Test deployments, verify logging works before prod    |
| **Production**  | 90 days   | SOC2 compliance (audit trail), incident investigation |

**Cost**:

- Railway logs: Free (30 days retention built-in)
- Vercel logs: Free (30 days retention)
- If need longer retention: Export to AWS S3 (~$1-5/month for 90 days)

**After Retention**: Archive to S3 Glacier ($0.004/GB/month for compliance, rarely accessed)

---

### What to Log (Comprehensive Checklist)

**✅ Do Log**:

- User actions (create workflow, upload document, start assessment)
- API requests (method, path, status, duration, user)
- Assessment lifecycle (started, processing, completed, failed)
- AI API calls (prompt size, response size, cost, duration, success/failure)
- Errors (with stack trace, user context, request ID)
- Background job lifecycle (queued, started, completed, failed, retried)
- Database queries >1 second (slow query log)
- Authentication events (login, logout, failed login attempts)
- Configuration changes (environment variable updated, feature flag toggled)
- Deployment events (version deployed, rollback triggered)

**❌ Don't Log**:

- Passwords or API keys (security risk)
- Full document content (privacy + storage cost)
- Credit card numbers or PII (compliance violation)
- Excessive DEBUG logs in production (cost, noise)
- Duplicate logs (same event logged multiple times)

**⚠️ Log with Caution** (redact sensitive parts):

- User emails (log `user_id` instead, lookup email if needed)
- Document titles (may contain confidential info - log `document_id` instead)
- AI prompts (log prompt hash or length, not full text - can contain customer data)

---

### Logging Implementation

**Frontend (Next.js)**:

```typescript
// lib/logger.ts
export function logEvent(event: string, data: object) {
  const log = {
    timestamp: new Date().toISOString(),
    level: 'INFO',
    service: 'frontend',
    environment: process.env.NODE_ENV,
    version: process.env.NEXT_PUBLIC_VERSION,
    event,
    ...data,
  }

  // Console log (Vercel captures this)
  console.log(JSON.stringify(log))

  // Also send to Sentry breadcrumb (for error context)
  Sentry.addBreadcrumb({
    category: event,
    data,
    level: 'info',
  })
}

// Usage
logEvent('assessment_started', {
  assessment_id: 'assess_123',
  workflow_id: 'workflow_456',
  user_id: session.user.id,
})
```

**Backend (FastAPI)**:

```python
# app/logger.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, service='api'):
        self.service = service
        self.logger = logging.getLogger(service)

    def info(self, event: str, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': 'INFO',
            'service': self.service,
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'version': os.getenv('GIT_SHA', 'unknown'),
            'event': event,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

    def error(self, event: str, error: Exception, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': 'ERROR',
            'service': self.service,
            'event': event,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            **kwargs
        }
        self.logger.error(json.dumps(log_entry))

logger = StructuredLogger('api')

# Usage
logger.info('assessment_started', assessment_id=str(assessment.id), user_id=str(user.id))
```

**Celery Worker**:

```python
# app/worker/tasks.py
from app.logger import StructuredLogger

logger = StructuredLogger('celery')

@celery.task(bind=True)
def process_assessment(self, assessment_id: str):
    start_time = time.time()

    logger.info('job_started', task_id=self.request.id, assessment_id=assessment_id)

    try:
        # ... process assessment ...
        duration = time.time() - start_time
        logger.info('job_completed', task_id=self.request.id, assessment_id=assessment_id, duration_sec=duration)
    except Exception as e:
        logger.error('job_failed', error=e, task_id=self.request.id, assessment_id=assessment_id)
        raise
```

---

## Distributed Tracing

### What Is Tracing?

**Problem**: Request touches multiple services (Frontend → API → Database → AI API). When it fails, where did it break?

**Solution**: Trace request across all services with a `request_id`

**Example Flow**:

1. User clicks "Start Assessment" (frontend generates `request_id: req_xyz789`)
2. Frontend → POST /api/v1/assessments (passes `request_id` in header)
3. API logs: `{"event": "api_request", "request_id": "req_xyz789", "path": "/assessments"}`
4. API → Database: SELECT workflow (logs: `{"event": "db_query", "request_id": "req_xyz789"}`)
5. API → Celery: Enqueue job (logs: `{"event": "job_queued", "request_id": "req_xyz789"}`)
6. Celery worker → Claude API (logs: `{"event": "ai_api_call", "request_id": "req_xyz789"}`)

**Now**: Search logs for `request_id: req_xyz789` → see full request flow, identify bottleneck

---

### Tracing Implementation (Simple - Phase 1)

**Generate Request ID** (Frontend):

```typescript
// lib/api.ts
import { v4 as uuidv4 } from 'uuid'

export async function apiCall(endpoint: string, options: RequestInit) {
  const requestId = uuidv4()

  const response = await fetch(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      'X-Request-ID': requestId, // Pass to backend
    },
  })

  // Log frontend API call
  logEvent('api_call', {
    request_id: requestId,
    endpoint,
    status: response.status,
  })

  return response
}
```

**Propagate Request ID** (Backend):

```python
# app/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response

# app/main.py
app.add_middleware(RequestIDMiddleware)

# In route handlers
@app.post('/api/v1/assessments')
def create_assessment(request: Request):
    request_id = request.state.request_id
    logger.info('assessment_created', request_id=request_id, ...)
```

---

### Distributed Tracing (Advanced - Phase 3)

**Tool**: OpenTelemetry (industry standard)

**Why**: Auto-instrument code, visualize traces in Grafana Tempo or Datadog APM

**When**: Year 2+ when debugging complex multi-service issues (not needed for MVP)

**Cost**: OpenTelemetry free (open source), Grafana Tempo self-hosted (~$50/month), Datadog APM ($15-30/host/month)

---

## Metrics Architecture

### RED Method (Requests, Errors, Duration)

**What**: Three key metrics for every API endpoint

**Why**: Cover user experience (errors, latency) and capacity (traffic)

**Metrics**:

1. **R**ate: Requests per second (RPS)
2. **E**rrors: Error rate (%)
3. **D**uration: P95 response time (ms)

**Example** (POST /api/v1/assessments endpoint):

- **Rate**: 0.5 RPS at MVP (5 users × ~100 requests/day ÷ 86,400 sec/day)
- **Errors**: <0.5% error rate (99.5% success)
- **Duration**: P95 <500ms (API creates assessment record, enqueues job, returns)

---

### Custom Metrics (Business-Specific)

Beyond RED, track domain-specific metrics:

**Assessment Metrics**:

- `assessments_started_total` (counter) - Total assessments started
- `assessments_completed_total` (counter) - Total assessments completed (status='completed')
- `assessments_failed_total` (counter) - Total assessments failed (status='failed')
- `assessment_duration_seconds` (histogram) - Time to process assessment (Step 3 duration)
- `assessment_queue_depth` (gauge) - Number of assessments waiting in Celery queue

**AI Metrics**:

- `ai_api_calls_total` (counter) - Total Claude API calls
- `ai_api_errors_total` (counter) - Failed API calls
- `ai_api_cost_usd_total` (counter) - Cumulative AI cost
- `ai_api_duration_seconds` (histogram) - Claude API response time
- `ai_tokens_used_total` (counter) - Total tokens consumed (input + output)

**Business Metrics**:

- `active_users_daily` (gauge) - Unique users per day (WAU ÷ 7)
- `workflows_created_total` (counter) - Total workflows created
- `revenue_mrr_usd` (gauge) - Monthly Recurring Revenue

---

### Metrics Collection (Prometheus Format)

**Backend (FastAPI)**:

```python
# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
assessments_started = Counter('assessments_started_total', 'Total assessments started')
assessments_completed = Counter('assessments_completed_total', 'Total assessments completed')
assessment_duration = Histogram('assessment_duration_seconds', 'Assessment processing duration')
queue_depth = Gauge('assessment_queue_depth', 'Assessments waiting in queue')

# Increment metrics
@app.post('/api/v1/assessments')
def create_assessment():
    assessments_started.inc()
    # ... create assessment ...

# Celery task
@celery.task
def process_assessment(assessment_id):
    start = time.time()
    # ... process ...
    duration = time.time() - start
    assessments_completed.inc()
    assessment_duration.observe(duration)

# Expose metrics endpoint
@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type='text/plain')
```

**Scraping Metrics**:

- **Railway**: No built-in Prometheus scraping (use Grafana Cloud or self-hosted Prometheus)
- **Alternative**: Push metrics to Grafana Cloud (free tier: 10K series, 50GB logs)

---

## Dashboards

### Dashboard 1: System Health (Is Everything Working?)

**Purpose**: First dashboard to check each morning - "Is the system healthy?"

**Panels**:

1. **Uptime** (last 24 hours): Green if 100%, red if <99.9%
2. **API Error Rate** (last 1 hour): <0.5% = green, 0.5-1% = yellow, >1% = red
3. **Frontend Error Rate** (last 1 hour): <1% = green, >1% = yellow
4. **Assessment Queue Depth** (current): <10 = green, 10-50 = yellow, >50 = red
5. **Database Connection Pool** (% used): <80% = green, 80-95% = yellow, >95% = red
6. **Railway CPU/Memory** (% used): <70% = green, 70-90% = yellow, >90% = red
7. **Recent Errors** (last 10 errors from Sentry with links)

**Alert**: If any panel is red for >10 minutes, send alert

**View**: Grafana dashboard (1 page, auto-refresh every 30 seconds)

---

### Dashboard 2: User Journey (Step 3 - AI Validation)

**Purpose**: Monitor the critical path - "How fast are assessments completing?"

**Panels**:

1. **Assessments Started** (today vs. yesterday): Show trend
2. **Assessments Completed** (today): Show count + completion rate
3. **P50/P95/P99 Processing Time** (last 24 hours): Line chart, target P95 <10 min
4. **Assessment Failure Rate** (last 7 days): <2% = green, 2-5% = yellow, >5% = red
5. **Failure Reasons** (pie chart): PDF parsing errors, AI timeouts, etc.
6. **Queue Wait Time** (P95): How long assessments wait before processing starts

**Goal**: Optimize Step 3 speed and reliability (core journey value)

**View**: Grafana dashboard, review weekly

---

### Dashboard 3: Business Metrics (Are We Growing?)

**Purpose**: Track North Star and input metrics - "Is the product succeeding?"

**Panels**:

1. **Active Assessments Per Month** (North Star): Current vs. target
2. **Active Customers** (gauge): Count of customers with >1 assessment in last 30 days
3. **Assessments Per Customer** (bar chart): Distribution across customers
4. **Daily Active Users** (line chart, last 30 days): Trend
5. **Workflows Created** (cumulative, last 90 days): Growth curve
6. **AI Accuracy** (last 30 days): % of assessments with no user-flagged errors

**Audience**: Founder reviews weekly, shares with team monthly

**View**: Grafana dashboard or Metabase (if SQL-based BI preferred)

---

### Dashboard 4: Cost & Usage (What's This Costing?)

**Purpose**: Track infrastructure and AI costs - "Are we spending efficiently?"

**Panels**:

1. **Claude API Cost** (last 30 days): Total USD spent
2. **Cost Per Assessment** (last 30 days): Total cost ÷ total assessments
3. **Token Usage** (input vs. output tokens, stacked area chart)
4. **Railway Costs** (backend + Celery, last 30 days)
5. **Vercel Costs** (frontend + Postgres + Blob, last 30 days)
6. **Total Infrastructure Cost** (sum, last 30 days)
7. **Revenue Per Assessment** (MRR ÷ assessments per month)

**Goal**: Ensure gross margin stays healthy (>75%)

**View**: Spreadsheet or Grafana dashboard, review monthly

---

### Dashboard 5: Errors & Debugging (What's Breaking?)

**Purpose**: Drill into errors - "Where are errors happening and why?"

**Panels**:

1. **Error Rate by Endpoint** (last 24 hours): Which API endpoints failing?
2. **Top 10 Errors** (last 7 days, by count): Most frequent error types
3. **Error Trend** (last 30 days, line chart): Improving or degrading?
4. **Errors by User** (last 24 hours): One user hitting errors repeatedly = bug in their data
5. **Sentry Issues** (embedded): Link to Sentry dashboard

**Audience**: Engineer debugging production issues

**View**: Grafana + Sentry integration

---

### Dashboard 6: Infrastructure (Railway/Vercel Health)

**Purpose**: Monitor platform resources - "Do we need to scale?"

**Panels**:

1. **Railway CPU** (backend + Celery, last 24 hours): <70% = healthy
2. **Railway Memory** (backend + Celery, last 24 hours): <80% = healthy
3. **Vercel Edge Function Invocations** (last 24 hours): Approaching limits?
4. **Database Connections** (active vs. max): Connection pool status
5. **Redis Memory** (Upstash, last 24 hours): Queue size healthy?
6. **Deployment History** (last 10 deploys with status): Did recent deploy correlate with errors?

**Audience**: Engineer on-call, reviewing during incidents

**View**: Railway dashboard + Vercel dashboard (built-in, no custom dashboard needed for MVP)

---

## Alerts & SLOs

### SLOs (Service Level Objectives)

**Definition**: Internal reliability targets (stricter than customer-facing SLAs)

**Purpose**: Define "what is good enough" and create error budget for experimentation

---

#### SLO 1: Availability (Uptime)

**Metric**: % of time API is reachable and returning 200 OK

**Target**: 99.9% availability over 30 days

**Calculation**:

- 99.9% = 43.2 minutes of downtime allowed per month
- Measured via: Health check endpoint (`GET /health`) polled every 1 minute

**Error Budget**:

- 0.1% = 43.2 minutes/month
- If burn through error budget early (20 min downtime in first week), pause feature work and focus on reliability

**Why 99.9% (not 99.99%)**:

- 99.99% = 4.3 min downtime/month = requires redundancy, load balancing, blue-green deploys
- MVP doesn't need 99.99% (TÜV SÜD pilot can tolerate 40 min downtime/month during business hours)
- Cost: 99.99% costs 5-10x more in infrastructure

**Alerting**:

- If downtime >10 minutes in 1 day → Page founder
- If monthly downtime >30 minutes (approaching budget) → Alert founder to freeze deploys

---

#### SLO 2: Latency (Assessment Processing Time)

**Metric**: P95 assessment processing time (Step 3 duration)

**Target**: 95% of assessments complete in <10 minutes

**Calculation**:

- Measure: `assessment.completed_at - assessment.started_at` for all completed assessments
- P95: 95th percentile (5% of assessments can take longer)

**Error Budget**:

- 5% of assessments can exceed 10 minutes
- Example: 100 assessments/month → 5 can take 10-15 min

**Why 10 minutes**:

- User journey testing showed "5-10 min is acceptable, >15 min feels broken"
- P95 <10 min = most users get results fast enough

**Alerting**:

- If P95 >15 minutes for 1 hour → Alert founder (investigate AI slowness, PDF size, etc.)
- If P95 >10 minutes for 1 day → Warning (approaching SLO violation)

---

#### SLO 3: Error Rate (Assessment Success Rate)

**Metric**: % of assessments that complete successfully (not status='failed')

**Target**: >98% success rate (2% error budget)

**Calculation**:

- Success rate = (completed assessments / total assessments started) × 100%
- Failed assessments expected (bad PDFs, user error, occasional AI timeout)

**Error Budget**:

- 2% = 2 failures per 100 assessments
- 100 assessments/month → 2 failures allowed

**Why 98%**:

- Some failures unavoidable (corrupted PDFs, user uploads wrong file type)
- 98% success = 49/50 assessments succeed (good enough for MVP)

**Alerting**:

- If error rate >5% for 1 hour → Page founder (systemic issue, AI down?)
- If error rate >2% for 1 day → Warning (approaching SLO violation)

---

#### SLO 4: AI Accuracy (False Positive/Negative Rate)

**Metric**: % of assessments where user flags incorrect AI results

**Target**:

- <5% false positive rate (AI wrongly flags pass as fail)
- <1% false negative rate (AI wrongly flags fail as pass)

**Calculation**:

- Requires user feedback: "Was this result correct?" (thumbs up/down)
- False positive rate = (assessments flagged as wrong fail / total fail results) × 100%

**Error Budget**:

- 5% false positive = 5 per 100 fail results can be wrong
- 1% false negative = 1 per 100 pass results can be wrong

**Why These Targets**:

- False negatives (missed issues) = certification person catches error later = embarrassment = lost trust
- False positives (extra work) = user double-checks = time wasted but not dangerous
- <1% false negative is critical, <5% false positive is acceptable

**Alerting**:

- If false negative rate >1% for 1 week → Alert founder (retrain AI, improve prompts)
- If false positive rate >10% for 1 week → Warning (users losing trust)

---

### Alert Definitions

#### Critical Alerts (Page Founder Immediately - 2am Wake-Up)

**When to Page**: User-facing impact, requires immediate action

**Alert 1: API Down**

- **Condition**: Health check fails for 5 consecutive minutes
- **Impact**: Users can't create workflows, upload documents, view results
- **Action**: Check Railway status, restart backend, rollback if recent deploy
- **Runbook**: Link to "API Down" runbook

**Alert 2: High Error Rate**

- **Condition**: API error rate >1% for 5 minutes
- **Impact**: Users see errors when trying to use product
- **Action**: Check Sentry for error patterns, rollback if recent deploy
- **Runbook**: Link to "High Error Rate" runbook

**Alert 3: All Assessments Failing**

- **Condition**: Assessment failure rate >50% for 15 minutes
- **Impact**: Core journey (Step 3) broken, users get no results
- **Action**: Check Celery worker logs, check Claude API status, restart workers
- **Runbook**: Link to "Assessments Failing" runbook

**Alert 4: Database Connection Pool Exhausted**

- **Condition**: Active connections >95% of max for 5 minutes
- **Impact**: API hangs, timeouts, 500 errors
- **Action**: Restart backend (closes connections), upgrade database tier
- **Runbook**: Link to "Database Connection Pool" runbook

**Alert 5: Payment Failed (Claude API)**

- **Condition**: Claude API returns 402 Payment Required
- **Impact**: All assessments fail, AI unavailable
- **Action**: Update payment method in Anthropic dashboard immediately
- **Runbook**: Link to "Payment Failed" runbook

---

#### Warning Alerts (Email Founder - Check Within 1 Hour)

**When to Alert**: Degrading performance, not yet user-facing

**Alert 6: High Latency**

- **Condition**: API P95 latency >2 seconds for 10 minutes
- **Impact**: Slow UX, users perceive app as sluggish
- **Action**: Check slow queries, check Railway CPU, scale up if needed

**Alert 7: Queue Depth Growing**

- **Condition**: Assessment queue >50 for 30 minutes
- **Impact**: Users wait longer for results (>15 min)
- **Action**: Add Celery workers, check if workers crashed

**Alert 8: High CPU/Memory**

- **Condition**: Railway CPU >90% for 10 minutes
- **Impact**: Slow responses, potential crashes
- **Action**: Scale up instance size, optimize code

**Alert 9: Approaching Error Budget**

- **Condition**: Monthly downtime >30 minutes (70% of 43 min budget)
- **Impact**: Risk violating SLO, need to pause deploys
- **Action**: Freeze feature deploys, focus on stability

**Alert 10: AI Cost Spike**

- **Condition**: Claude API cost >$50/day (expected: $1-10/day at MVP)
- **Impact**: Budget burn, possible runaway job
- **Action**: Check for retry loops, check assessment queue

---

#### Info Alerts (Slack/Email - Good to Know)

**When to Alert**: Non-urgent, informational

**Alert 11: Deployment Success**

- **Condition**: GitHub Actions deploy succeeds
- **Impact**: None (positive signal)
- **Action**: None (celebrate!)

**Alert 12: Daily Summary**

- **Condition**: Every day at 8am
- **Impact**: None
- **Action**: Review metrics (assessments completed, errors, uptime)

**Alert 13: Weekly Metrics Report**

- **Condition**: Every Monday at 9am
- **Impact**: None
- **Action**: Review North Star trend, input metrics, SLOs

---

### Alert Routing

**Critical Alerts**:

- PagerDuty → SMS + Phone Call (2am wake-up if needed)
- Fallback: Email if founder doesn't acknowledge in 5 minutes

**Warning Alerts**:

- Email + Slack DM
- Founder checks within 1 hour during business hours

**Info Alerts**:

- Slack channel (#qteria-alerts)
- Review when convenient

**Escalation**:

- If founder doesn't acknowledge critical alert in 15 minutes → Call backup (co-founder or senior engineer if team grows)

---

## Incident Response

### Incident Severity Levels

| Severity          | Definition                                | Example                      | Response Time            | Escalation                       |
| ----------------- | ----------------------------------------- | ---------------------------- | ------------------------ | -------------------------------- |
| **P0 (Critical)** | Complete service outage, data loss risk   | API down, database corrupted | Immediate (page on-call) | Founder + all hands              |
| **P1 (High)**     | Core feature broken, many users affected  | Assessments failing, AI down | <15 minutes              | Founder                          |
| **P2 (Medium)**   | Minor feature broken, some users affected | Export PDF broken, UI bug    | <2 hours                 | Engineer (during business hours) |
| **P3 (Low)**      | Cosmetic issue, workaround exists         | Typo, minor UI glitch        | <1 day                   | Fix in next deploy               |

---

### Incident Response Process

**Step 1: Detect**

- Alert fires (PagerDuty, Slack, Sentry)
- User reports issue (email, support ticket)
- Engineer notices anomaly (dashboard red)

**Step 2: Acknowledge**

- On-call engineer acknowledges alert in PagerDuty (stops escalation)
- Post in Slack: "Investigating API errors, will update in 15 min"

**Step 3: Assess**

- Check dashboards (System Health, Errors)
- Check Sentry (recent errors)
- Check Railway logs (backend + Celery)
- Determine severity (P0-P3)

**Step 4: Mitigate**

- **If recent deploy**: Rollback immediately (see Deployment Plan runbook)
- **If infrastructure**: Restart service, scale up, check cloud status
- **If external dependency** (Claude API down): Wait, implement fallback, notify users

**Step 5: Communicate**

- **Internal**: Slack updates every 15 min ("Still investigating" or "Fixed, monitoring")
- **External**: If >30 min outage, email customers ("We're aware, working on it, ETA 1 hour")

**Step 6: Resolve**

- Deploy fix or confirm rollback successful
- Verify via smoke tests (create workflow, run assessment)
- Monitor for 30 min (ensure issue doesn't recur)

**Step 7: Post-Mortem** (within 24 hours)

- Write incident report (see template below)
- Share with team (if team exists, otherwise solo founder documents)
- Create action items (prevent recurrence)
- Review in weekly meeting

---

### Post-Mortem Template

**File**: `docs/incidents/YYYY-MM-DD-incident-title.md`

```markdown
# Incident Post-Mortem: [Title]

**Date**: 2024-03-15
**Duration**: 14:32 - 15:15 UTC (43 minutes)
**Severity**: P1 (High)
**Impact**: 50% of assessments failed, 5 users affected

---

## Summary

Between 14:32 and 15:15 UTC, the Claude API began returning 429 rate limit errors, causing 50% of assessments to fail. Users received "Assessment failed" errors with no results. Issue resolved by implementing retry logic with exponential backoff.

---

## Timeline (UTC)

- **14:32**: Alert fired: "Assessment failure rate >10%"
- **14:35**: Founder acknowledged alert, began investigation
- **14:40**: Identified root cause: Claude API rate limit (50 requests/min exceeded)
- **14:45**: Temporary mitigation: Restarted Celery workers to clear queue
- **14:50**: Deployed fix: Added exponential backoff retry logic
- **15:00**: Verified fix: Assessment success rate recovered to 98%
- **15:15**: Monitoring confirmed stable, incident closed

---

## Root Cause

Celery workers were making too many concurrent Claude API calls (10 workers × 5 calls each = 50 calls/min, exactly at rate limit). During peak usage (5 users starting assessments simultaneously), rate limit exceeded.

**Why Didn't We Catch This Earlier?**:

- No monitoring of API call rate (only monitored total calls per day)
- Staging tests used 1 worker (didn't reproduce production concurrency)

---

## Impact

- **Users Affected**: 5 users (all TÜV SÜD pilot users)
- **Assessments Failed**: 12 out of 24 (50% failure rate)
- **Duration**: 43 minutes downtime for assessment processing
- **Revenue Impact**: None (pilot phase, no SLA)
- **Reputation Impact**: Low (users notified proactively, fix deployed quickly)

---

## What Went Well

- ✅ Alert fired within 3 minutes of first failure
- ✅ Root cause identified in <10 minutes
- ✅ Fix deployed in 30 minutes (quick turnaround)
- ✅ Users notified proactively (didn't wait for complaints)

---

## What Went Wrong

- ❌ No rate limit monitoring (should have alerted before hitting limit)
- ❌ No retry logic for API calls (first failure = assessment failed permanently)
- ❌ Staging tests didn't catch concurrency issue (1 worker vs. 10 in prod)

---

## Action Items

| Action                                                 | Owner   | Deadline   | Status         |
| ------------------------------------------------------ | ------- | ---------- | -------------- |
| Add rate limit monitoring (alert if >40 calls/min)     | Founder | 2024-03-16 | ✅ Done        |
| Implement exponential backoff for all AI calls         | Founder | 2024-03-15 | ✅ Done        |
| Add concurrency tests to staging (simulate 10 workers) | Founder | 2024-03-20 | 🔄 In Progress |
| Document Claude API rate limits in runbook             | Founder | 2024-03-17 | ✅ Done        |

---

## Lessons Learned

1. **Monitor rate limits proactively**: Don't wait to hit limit, alert at 80%
2. **Retry all external API calls**: Transient failures should be retried, not fail permanently
3. **Staging should mirror production**: Same worker count, same concurrency patterns

---

**Incident Owner**: Founder
**Reviewed By**: (N/A - solo founder)
**Next Review**: 2024-04-15 (1 month follow-up to verify fixes working)
```

---

## Runbooks

### Runbook 1: API Down (Health Check Failing)

**Symptoms**:

- Alert: "API health check failed for 5 minutes"
- Users can't access qteria.com
- Frontend shows "Service unavailable"

**Diagnosis**:

```bash
# Check API health
curl https://api.qteria.com/health

# If timeout or 502/503:
# - Backend is down or unresponsive
# - Railway instance crashed
```

**Common Causes**:

1. Backend crashed (out of memory, unhandled exception)
2. Railway deployment failed
3. Database connection pool exhausted (backend can't connect to DB)

**Fix**:

1. **Check Railway status**:
   - Go to Railway dashboard → qteria-api service
   - Check "Deployments" tab (recent deploy failed?)
   - Check "Metrics" tab (memory 100%? CPU 100%?)

2. **If recent deploy failed**:

   ```bash
   # Rollback to previous deployment
   # Railway dashboard → Deployments → Select previous → Redeploy
   ```

3. **If out of memory**:
   - Railway dashboard → Settings → Increase memory (512MB → 1GB)
   - Redeploy

4. **If database connection pool**:
   - See "Runbook 4: Database Connection Pool Exhausted"

5. **If still down**:
   - Check Railway status page: https://status.railway.app
   - If Railway incident, wait for resolution

**Verify Fix**:

```bash
# API returns 200 OK
curl https://api.qteria.com/health

# Frontend loads
curl https://qteria.com
```

**Prevention**:

- Monitor memory usage (alert if >80%)
- Load test before deploying (ensure backend handles expected traffic)

---

### Runbook 2: High Error Rate (API Returning 500s)

**Symptoms**:

- Alert: "API error rate >1% for 5 minutes"
- Sentry shows spike in errors
- Users see "Something went wrong" errors

**Diagnosis**:

```bash
# Check Sentry for recent errors
# https://sentry.io/organizations/qteria/issues/

# Common error patterns:
# - DatabaseError: connection pool exhausted
# - KeyError: missing environment variable
# - AttributeError: recent code change broke something
```

**Common Causes**:

1. Recent deploy introduced bug
2. Database connection issues
3. Missing environment variable (forgot to set in Railway)
4. External API down (Claude API timeout)

**Fix**:

1. **If recent deploy** (<1 hour ago):

   ```bash
   # Rollback immediately
   git revert HEAD
   git push origin main
   # Or: Railway dashboard → Redeploy previous version
   ```

2. **If database connection**:
   - See "Runbook 4: Database Connection Pool Exhausted"

3. **If missing environment variable**:
   - Railway dashboard → Variables → Add missing variable
   - Redeploy

4. **If external API down**:
   - Check Claude API status: https://status.anthropic.com
   - If down, wait for resolution
   - If prolonged, notify users: "AI service temporarily unavailable"

**Verify Fix**:

- Check Sentry (error rate drops to <0.5%)
- Test affected feature manually
- Monitor for 30 min (ensure errors don't recur)

**Prevention**:

- Always test on staging before production
- Add integration tests for critical paths
- Set up synthetic monitoring (probe endpoints every 5 min)

---

### Runbook 3: Assessments Failing (High Failure Rate)

**Symptoms**:

- Alert: "Assessment failure rate >10% for 15 minutes"
- Users report "Assessment failed" errors
- Celery logs show errors

**Diagnosis**:

```bash
# Check Celery worker logs
railway logs --service qteria-celery-prod --tail 100

# Common errors:
# - AuthenticationError: Invalid API key (Claude)
# - TimeoutError: Claude API timeout
# - PDFParsingError: Corrupted PDF
# - MemoryError: Worker out of memory
```

**Common Causes**:

1. Claude API down or rate limited
2. Invalid Claude API key (expired, quota exceeded)
3. Celery workers crashed
4. Out of memory (processing large PDFs)

**Fix**:

1. **If Claude API down**:
   - Check status: https://status.anthropic.com
   - If down, notify users: "AI temporarily unavailable, will retry automatically"
   - Wait for resolution (Anthropic typically resolves in <30 min)

2. **If invalid API key**:

   ```bash
   # Test API key
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'

   # If 401 Unauthorized: API key invalid
   # Get new key from Anthropic dashboard
   # Update Railway variable: ANTHROPIC_API_KEY
   # Restart Celery workers
   ```

3. **If Celery workers crashed**:
   - Railway dashboard → qteria-celery-prod → Redeploy

4. **If out of memory**:
   - Railway dashboard → Settings → Increase memory (512MB → 1GB)
   - Redeploy

**Verify Fix**:

- Start test assessment, check if completes successfully
- Monitor failure rate (should drop to <2%)

**Prevention**:

- Set calendar reminder to rotate API keys before expiration
- Monitor API key quota (alert if approaching limit)
- Optimize PDF parsing (stream instead of loading entire file)

---

### Runbook 4: Database Connection Pool Exhausted

**Symptoms**:

- Alert: "Database connection pool >95% for 5 minutes"
- API returns 500 errors: "OperationalError: connection pool exhausted"
- Slow responses or timeouts

**Diagnosis**:

```bash
# Check active connections
railway run --service qteria-postgres psql $DATABASE_URL -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname='qteria_prod';"

# If count near max (20 on free tier, 256 on Pro):
# - Connection leak (connections not closed)
# - Too many concurrent requests
```

**Common Causes**:

1. Connection leak (FastAPI not closing connections after requests)
2. Too many concurrent users (spiky traffic)
3. Long-running queries (holding connections open)

**Fix**:

1. **Immediate** (restart backend to close connections):
   - Railway dashboard → qteria-api-prod → Redeploy

2. **Short-term** (upgrade database tier):
   - Vercel dashboard → Postgres → Upgrade to Pro (256 connections)

3. **Long-term** (fix connection leak):

   ```python
   # app/database.py
   # Reduce pool size
   engine = create_engine(
       DATABASE_URL,
       pool_size=5,  # Max 5 connections per backend instance
       max_overflow=10,  # Allow 10 overflow connections
       pool_pre_ping=True,  # Verify connections before use
       pool_recycle=3600  # Recycle connections after 1 hour
   )
   ```

4. **If long-running queries**:

   ```bash
   # Find long-running queries
   railway run --service qteria-postgres psql $DATABASE_URL -c \
     "SELECT pid, now() - pg_stat_activity.query_start AS duration, query \
      FROM pg_stat_activity \
      WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';"

   # Kill long-running query
   railway run --service qteria-postgres psql $DATABASE_URL -c \
     "SELECT pg_terminate_backend(PID);"
   ```

**Verify Fix**:

- Check connection count (should drop to <50%)
- Test API (should respond normally)
- Monitor for 1 hour (ensure connections don't leak again)

**Prevention**:

- Use connection pooling best practices (pool_size=5, max_overflow=10)
- Add monitoring for connection pool usage (alert at 80%)
- Optimize slow queries (add indexes)

---

### Runbook 5: Slow Assessment Processing (P95 >15 Minutes)

**Symptoms**:

- Alert: "P95 assessment processing time >15 minutes for 1 hour"
- Users complain "results taking too long"
- Assessments stuck in "processing" status

**Diagnosis**:

```bash
# Check queue depth
redis-cli -u $REDIS_URL llen celery

# If queue depth high (>50):
# - Not enough workers to process assessments
# - Workers slow (AI API slow, PDF parsing slow)

# Check Celery worker logs
railway logs --service qteria-celery-prod --tail 100

# Look for:
# - AI API timeouts
# - Large PDF parsing times
# - Memory warnings
```

**Common Causes**:

1. Not enough Celery workers (queue backlog)
2. Claude API slow (>60 sec per call)
3. Large PDFs (100+ pages take 5-10 min to parse)
4. Workers low on memory (swapping to disk)

**Fix**:

1. **If queue depth high** (add more workers):
   - Railway dashboard → qteria-celery-prod → Settings → Increase replicas (1 → 3)
   - Queue should drain within 30 min

2. **If Claude API slow**:
   - Check Anthropic status: https://status.anthropic.com
   - If slow globally, wait for resolution
   - If persistent, contact Anthropic support

3. **If large PDFs**:
   - Optimize PDF parsing (stream pages instead of loading entire file)
   - Set max PDF size limit (e.g., 50MB or 100 pages)
   - Notify user: "Large documents may take 10-15 min"

4. **If low memory**:
   - Railway dashboard → Settings → Increase memory (512MB → 1GB)

**Verify Fix**:

- Start test assessment with typical PDF (50 pages)
- Should complete in <10 minutes
- Monitor P95 (should drop to <10 min)

**Prevention**:

- Optimize PDF parsing code (profile hot paths)
- Cache parsed PDFs (if same document re-assessed, skip parsing)
- Batch AI API calls (10 criteria checks → 1 API call)

---

### Runbook 6: Frontend Down (Vercel 502/503)

**Symptoms**:

- qteria.com returns 502 Bad Gateway or 503 Service Unavailable
- Vercel status shows error

**Diagnosis**:

```bash
# Check Vercel deployment status
vercel --prod inspect

# Check Vercel status page
# https://www.vercel-status.com/
```

**Common Causes**:

1. Vercel edge network issue (rare, typically resolves in <10 min)
2. Recent deploy failed (build error, runtime error)
3. Vercel outage (check status page)

**Fix**:

1. **If recent deploy failed**:
   - Vercel dashboard → Deployments → Promote previous working deployment

2. **If Vercel outage**:
   - Check status: https://www.vercel-status.com/
   - Wait for resolution (typically <30 min)
   - Notify users via email: "Service temporarily unavailable, resolving shortly"

3. **If build error**:
   - Check Vercel build logs
   - Fix error locally, push fix

**Verify Fix**:

```bash
# Frontend loads
curl https://qteria.com
```

**Prevention**:

- Run `npm run build` locally before pushing (catch build errors early)
- Set up Vercel preview deployments (test in preview before promoting to production)

---

### Runbook 7: User Can't Log In (NextAuth Error)

**Symptoms**:

- User reports "Can't log in" or "Configuration error"
- NextAuth logs show OAuth callback error

**Diagnosis**:

- Check NextAuth error logs (Vercel logs → Filter by "NextAuth")
- Common errors:
  - `OAUTH_CALLBACK_ERROR: redirect_uri mismatch`
  - `OAUTH_GET_ACCESS_TOKEN_ERROR`
  - `JWT_SESSION_ERROR: secret not set`

**Common Causes**:

1. OAuth redirect URI not configured correctly (Google OAuth Console)
2. `NEXTAUTH_SECRET` not set or incorrect
3. User's session expired (edge case, refresh usually fixes)

**Fix**:

1. **If redirect_uri mismatch**:
   - Go to Google Cloud Console → Credentials → OAuth 2.0 Client IDs
   - Ensure authorized redirect URIs include:
     - `https://qteria.com/api/auth/callback/google`
     - `https://staging.qteria.com/api/auth/callback/google` (if staging)
   - Save (takes ~5 min to propagate)

2. **If NEXTAUTH_SECRET missing**:
   - Generate new secret: `openssl rand -base64 32`
   - Vercel dashboard → Environment Variables → Add `NEXTAUTH_SECRET`
   - Redeploy

3. **If session expired**:
   - Ask user to clear browser cookies and try again
   - Or: Clear all sessions (if needed): `DELETE FROM sessions;` (if using database sessions)

**Verify Fix**:

- Test login flow: Go to qteria.com → Sign In → Should redirect to Google → Back to qteria.com logged in

**Prevention**:

- Document OAuth setup in `docs/auth-setup.md`
- Test login flow on staging before production deploy

---

### Runbook 8: High AI Costs (Unexpected Claude API Spend)

**Symptoms**:

- Alert: "Claude API cost >$50/day" (expected: $1-10/day at MVP)
- Anthropic invoice shows unexpected charges

**Diagnosis**:

```bash
# Check recent AI API calls
# Query PostgreSQL for ai_api_calls logs
SELECT date(created_at), count(*), sum(cost_usd)
FROM ai_api_calls
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY date(created_at)
ORDER BY date DESC;

# Look for:
# - Spike in API calls (retry loop? runaway job?)
# - Large prompt sizes (sending entire PDF instead of text?)
```

**Common Causes**:

1. Retry loop (failed assessment retries infinitely)
2. Large prompts (sending full PDF binary instead of extracted text)
3. High assessment volume (more users than expected)

**Fix**:

1. **If retry loop**:
   - Check Celery tasks (are assessments retrying infinitely?)
   - Fix retry logic (max 3 retries, exponential backoff)
   - Cancel stuck tasks:
     ```bash
     railway run --service qteria-celery-prod celery -A app.worker.celery_app purge
     ```

2. **If large prompts**:
   - Check prompt size in logs (should be <20K tokens for 50-page PDF)
   - If sending full PDF binary: Fix code (extract text first, don't send raw PDF)

3. **If high volume**:
   - Check assessment count (more than expected?)
   - If legitimate growth: Great! Budget for higher costs
   - If bot or spam: Add rate limiting

**Verify Fix**:

- Monitor API cost for next 24 hours (should return to $1-10/day)
- Check Anthropic dashboard (no ongoing high usage)

**Prevention**:

- Set budget alerts in Anthropic dashboard ($50/day, $500/month)
- Monitor cost per assessment (alert if >$1 per assessment)
- Optimize prompts (batch criteria, reduce token usage)

---

### Runbook 9: Staging Environment Issues

**Symptoms**:

- Deploy to staging fails
- Staging shows different behavior than production

**Diagnosis**:

- Check staging deployment logs (GitHub Actions, Vercel, Railway)
- Compare staging vs. production environment variables

**Common Causes**:

1. Missing environment variables in staging
2. Different database schema (migration not run)
3. Staging using production API keys (cross-contamination)

**Fix**:

1. **If missing env vars**:
   - Copy from production (Railway dashboard → Variables → Copy to staging)
   - Redeploy staging

2. **If database schema mismatch**:

   ```bash
   # Run migrations on staging
   railway run --service qteria-api-staging alembic upgrade head
   ```

3. **If using production keys**:
   - Generate separate staging API keys (Claude, Vercel Blob, etc.)
   - Update staging environment variables

**Verify Fix**:

- Test staging (create workflow, upload PDF, run assessment)
- Should behave identically to production (just with staging data)

**Prevention**:

- Document staging setup in deployment plan
- Automate staging deploys (GitHub Actions deploys to staging on push to `staging` branch)

---

### Runbook 10: Customer Reports Incorrect AI Results

**Symptoms**:

- Customer emails: "AI flagged this as fail, but it should pass" (false positive)
- Or: "AI said pass, but this actually fails" (false negative)

**Diagnosis**:

- Review assessment in production database:
  ```sql
  SELECT * FROM assessments WHERE id = 'assess_123';
  SELECT * FROM assessment_results WHERE assessment_id = 'assess_123';
  ```
- Check AI response:
  ```sql
  SELECT ai_response_raw FROM assessment_results WHERE id = 'result_456';
  ```
- Review document and criteria (did AI misunderstand requirement?)

**Common Causes**:

1. Ambiguous criteria (unclear wording, AI misinterprets)
2. AI model error (edge case Claude doesn't handle well)
3. Document format unusual (table, image, non-standard layout)

**Fix**:

1. **If false positive** (wrongly flagged as fail):
   - Override result manually (mark as pass with note: "Manual review")
   - Update AI prompt to clarify criteria
   - Add to training examples (if building fine-tuned model later)

2. **If false negative** (missed real issue):
   - **Critical**: Notify customer immediately (apologize, explain)
   - Mark assessment as "uncertain" (yellow flag)
   - Manual review required
   - Update AI prompt to catch this case

3. **If document format issue**:
   - Improve PDF parsing (better table detection, OCR for images)
   - Ask customer for better-formatted document (if possible)

**Verify Fix**:

- Re-run assessment with updated prompt
- Check if AI now returns correct result
- Test on similar documents (ensure fix doesn't break other cases)

**Prevention**:

- Collect user feedback ("Was this correct?" thumbs up/down)
- Track false positive/negative rates (alert if >5% or >1%)
- Build feedback loop (user corrections improve AI over time)

---

## Tool Stack & Setup

### Phase 1 (MVP): Free/Low-Cost Observability

**Goal**: Basic monitoring with minimal cost (<$50/month)

**Tools**:

1. **Logging**: Railway logs (free, 30-day retention) + Vercel logs (free, 30-day retention)
2. **Error Tracking**: Sentry Free tier (5K errors/month)
3. **Metrics**: Railway metrics (built-in) + Vercel Analytics (built-in)
4. **Alerts**: Email alerts (Railway + Vercel built-in)
5. **Uptime Monitoring**: UptimeRobot (free, 50 monitors)

**Cost**: $0-10/month (Sentry free tier sufficient)

**Setup Time**: ~2 hours

1. Sign up for Sentry → Add DSN to environment variables
2. Configure Railway email alerts (CPU >80%, Memory >80%)
3. Configure Vercel deployment notifications
4. Set up UptimeRobot (monitor `/health` endpoint every 5 min)

**Limitations**:

- No custom dashboards (rely on Railway/Vercel built-in dashboards)
- No distributed tracing (just logs with request_id)
- No advanced analytics (basic metrics only)

**Sufficient For**: MVP through first paying customer (Year 1)

---

### Phase 2 (Post-Pilot): Enhanced Observability

**Goal**: Custom dashboards, better alerting, distributed tracing

**Tools**:

1. **Logging**: Grafana Cloud (free tier: 50GB logs/month)
2. **Error Tracking**: Sentry Team ($26/month, 50K errors)
3. **Metrics + Dashboards**: Grafana Cloud (free tier: 10K series)
4. **Alerts**: PagerDuty (free tier: 1 user, 10 services)
5. **Uptime Monitoring**: Better Uptime (paid, $18/month, status page + advanced monitoring)

**Cost**: ~$50-75/month

**Setup Time**: ~1 day

1. Set up Grafana Cloud (create account, get API key)
2. Configure log shipping (Railway → Grafana Loki, Vercel → Grafana Loki)
3. Create custom dashboards (6 dashboards from above)
4. Set up PagerDuty (integrate with Grafana alerts)
5. Configure Better Uptime (replace UptimeRobot)

**Benefits**:

- Custom Grafana dashboards (System Health, User Journey, Business Metrics)
- PagerDuty on-call rotation (SMS + phone call for critical alerts)
- Better log search (Grafana Loki query language)
- Public status page (Better Uptime)

**When to Upgrade**: After TÜV SÜD pilot converts to paid customer (Month 6-12)

---

### Phase 3 (Scale): Full Observability Stack

**Goal**: APM, distributed tracing, advanced analytics

**Tools**:

1. **Full Observability**: Datadog APM ($15-30/host/month) OR New Relic OR self-hosted OpenTelemetry + Grafana stack
2. **Error Tracking**: Sentry Business ($89/month, full APM)
3. **Alerts**: PagerDuty Team ($49/user/month)
4. **Uptime Monitoring**: Pingdom or Better Uptime Pro
5. **Business Intelligence**: Metabase (self-hosted, free) or Looker

**Cost**: $200-500/month (depending on tool choices)

**Setup Time**: 1-2 weeks

1. Instrument code with OpenTelemetry (frontend + backend)
2. Deploy Grafana Tempo (distributed tracing) or use Datadog APM
3. Create advanced dashboards (trace visualization, service maps)
4. Set up on-call rotation (if team >1 engineer)

**Benefits**:

- Distributed tracing (see full request flow across all services)
- APM (automatic service maps, dependency graphs)
- Advanced alerting (anomaly detection, predictive alerts)
- Business intelligence (Metabase dashboards for non-engineers)

**When to Upgrade**: Year 2+, 10+ customers, team of 3+ engineers

---

## Implementation Roadmap

### Week 1: Foundation (Critical - Do First)

**Day 1-2: Structured Logging**

- [ ] Implement structured JSON logging (frontend + backend)
- [ ] Add request_id to all logs (trace requests across services)
- [ ] Test locally (verify logs look correct)

**Day 3: Error Tracking**

- [ ] Set up Sentry (create account, add DSN to env vars)
- [ ] Test error tracking (trigger test error, verify appears in Sentry)

**Day 4-5: Basic Metrics + Alerts**

- [ ] Configure Railway alerts (CPU >80%, Memory >80%, deployments)
- [ ] Configure Vercel alerts (deployment success/failure)
- [ ] Set up UptimeRobot (monitor `/health` endpoint every 5 min)

**Day 6-7: Document Runbooks**

- [ ] Write 3 critical runbooks (API Down, High Error Rate, Assessments Failing)
- [ ] Test runbooks (simulate incidents, verify runbooks accurate)

---

### Week 2: Enhancement (Important - Do Second)

**Day 8-10: Custom Metrics**

- [ ] Add Prometheus metrics (assessments started/completed/failed, AI cost, queue depth)
- [ ] Expose `/metrics` endpoint (FastAPI)
- [ ] Test metrics (verify Prometheus format correct)

**Day 11-12: Dashboards**

- [ ] Create System Health dashboard (Railway + Vercel built-in metrics)
- [ ] Create User Journey dashboard (assessment metrics)
- [ ] Set up daily email summary (manual for now, automate later)

**Day 13-14: SLOs**

- [ ] Define SLOs (99.9% availability, P95 <10 min, 98% success rate)
- [ ] Set up tracking (spreadsheet or simple dashboard)
- [ ] Document error budgets

---

### Week 3+: Advanced (Nice to Have - Do When Revenue Validates)

**Month 2-3: Grafana Cloud**

- [ ] Set up Grafana Cloud (free tier)
- [ ] Ship logs to Grafana Loki
- [ ] Ship metrics to Grafana Cloud
- [ ] Create 6 custom dashboards (System Health, User Journey, Business, Cost, Errors, Infrastructure)

**Month 4-6: PagerDuty + Better Uptime**

- [ ] Set up PagerDuty (replace email alerts for critical alerts)
- [ ] Set up Better Uptime (status page + advanced monitoring)
- [ ] Test on-call rotation (simulate P0 incident)

**Month 12+: Distributed Tracing**

- [ ] Instrument code with OpenTelemetry (if needed for debugging complex issues)
- [ ] Deploy Grafana Tempo or use Datadog APM
- [ ] Create trace visualizations

---

## Cost Summary

### Observability Costs by Phase

| Phase                    | Tools                                                        | Monthly Cost   | When       |
| ------------------------ | ------------------------------------------------------------ | -------------- | ---------- |
| **Phase 1 (MVP)**        | Railway logs + Vercel logs + Sentry free + UptimeRobot       | $0-10/month    | Month 1-6  |
| **Phase 2 (Post-Pilot)** | Grafana Cloud free + Sentry Team + PagerDuty + Better Uptime | $50-75/month   | Month 6-24 |
| **Phase 3 (Scale)**      | Datadog APM or OpenTelemetry + full stack                    | $200-500/month | Year 2+    |

**ROI Calculation**:

- **Without observability**: 1 incident/month × 4 hours debugging = 48 hours/year wasted
- **With observability**: 1 incident/month × 30 min debugging (runbooks) = 6 hours/year
- **Savings**: 42 hours/year × $100/hour (founder time) = $4,200/year
- **Cost**: $600/year (Phase 2)
- **Net ROI**: $3,600/year or 600% ROI

**Recommendation**: Start Phase 1 (free), upgrade to Phase 2 after first paying customer ($30K ARR justifies $600/year observability cost)

---

## Observability Checklist

### Pre-Launch Checklist

**Before deploying to production, ensure**:

- [ ] Structured logging implemented (JSON format, all services)
- [ ] Sentry configured (error tracking enabled)
- [ ] Health check endpoint exists (`/health` returns 200 OK)
- [ ] Uptime monitoring configured (UptimeRobot or similar)
- [ ] Critical alerts configured (email at minimum)
- [ ] 3 runbooks documented (API Down, High Errors, Assessments Failing)
- [ ] SLOs defined (even if not automated tracking yet)
- [ ] Post-mortem template created (`docs/incident-template.md`)

---

### Monthly Observability Review

**First Monday of every month, review**:

- [ ] SLO compliance (did we meet 99.9% availability, P95 <10 min, 98% success rate?)
- [ ] Error budget (how much left? Should we pause deploys and focus on reliability?)
- [ ] Alert fatigue (too many alerts firing? Tune thresholds)
- [ ] Incident count (how many P0/P1/P2 incidents? Trending up or down?)
- [ ] Top 10 errors (from Sentry - which errors recurring? Fix or suppress?)
- [ ] Runbook gaps (did any incident lack a runbook? Write one)
- [ ] Cost (observability tools cost vs. budget)

---

### Quarterly Observability Improvements

**Every 3 months, invest in**:

- [ ] Add 1 new dashboard (based on questions you couldn't answer last quarter)
- [ ] Improve 1 runbook (based on recent incidents)
- [ ] Optimize 1 noisy alert (reduce false positives)
- [ ] Review SLOs (still appropriate? Need to tighten or loosen?)
- [ ] Tool evaluation (should we upgrade to next phase?)

---

## Conclusion

Observability is not a one-time project - it's a continuous practice. Start simple (structured logs + Sentry + basic alerts), iterate based on incidents, and upgrade tools as revenue validates spend.

**Key Principles** (Reminder):

1. **Alert on symptoms** - Users care about errors/latency, not CPU
2. **Observe journeys** - Monitor Step 3 (AI validation), not just API uptime
3. **SLOs > SLAs** - Internal targets stricter than customer contracts
4. **Dashboards answer questions** - "Is system healthy?" not "Here's all the data"
5. **Runbooks save time** - Document fixes once, reuse forever
6. **Blameless post-mortems** - Learn from incidents, don't punish
7. **Cost-aware** - Start lean, scale observability with revenue

**Next Steps**:

1. Implement Week 1 tasks (structured logging, Sentry, basic alerts)
2. Deploy to production with observability enabled
3. Respond to first incident → Write runbook
4. Review monthly → Improve incrementally

**Observability enables reliability. Reliability enables growth. Growth validates Qteria's mission: validating documents 400x faster through evidence-based AI.**

Ready to ship!

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Owner**: Solo Founder
**Review Cadence**: Monthly (after incident retrospectives or quarterly strategic review)
