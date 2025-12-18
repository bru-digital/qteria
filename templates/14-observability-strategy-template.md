# Observability Strategy

> **Generated**: [Date]
> **Product**: [Product Name]
> **Status**: [Draft/In Progress/Implemented]

## Overview

This document defines the comprehensive observability strategy including metrics, logs, traces, dashboards, alerts, SLOs, and incident response.

**The Three Pillars**:

- **Metrics**: What is happening (numbers, trends)
- **Logs**: Why it's happening (events, context)
- **Traces**: Where it's happening (distributed systems)

---

## Observability Philosophy

### Principles

1. **Observe symptoms, not causes**: Alert on user impact, not CPU usage
2. **SLOs over SLAs**: Define reliability with error budgets
3. **Mean Time To Resolution (MTTR) > Mean Time Between Failures (MTBF)**: Fail fast, recover faster
4. **Actionable alerts**: Every alert must have a runbook
5. **Context over volume**: High signal, low noise

### Goals

**What we want to achieve**:

1. [Goal 1 - e.g., "Detect issues before customers report them"]
2. [Goal 2 - e.g., "Reduce MTTR from [X] to [Y] minutes"]
3. [Goal 3 - e.g., "99.9% uptime with < 5 min to detect incidents"]

---

## Golden Signals

**For each service, track these four signals**:

### 1. Latency

_How long does it take to service a request?_

| Service  | Metric             | Target   | Alert Threshold |
| -------- | ------------------ | -------- | --------------- |
| API      | p50 response time  | < 100ms  | > 200ms         |
| API      | p95 response time  | < 300ms  | > 500ms         |
| API      | p99 response time  | < 1000ms | > 2000ms        |
| Database | Query time p95     | < 50ms   | > 100ms         |
| Frontend | Page load time p95 | < 2000ms | > 4000ms        |

### 2. Traffic

_How much demand is being placed on your system?_

| Service  | Metric              | Baseline | Alert Threshold             |
| -------- | ------------------- | -------- | --------------------------- |
| API      | Requests per second | [X] rps  | < 10% of baseline or > 300% |
| API      | Active connections  | [Y]      | > [max capacity]            |
| Database | Queries per second  | [Z] qps  | > 80% of capacity           |

### 3. Errors

_What is the rate of failed requests?_

| Service     | Metric                  | Target | Alert Threshold |
| ----------- | ----------------------- | ------ | --------------- |
| API         | Error rate (5xx)        | < 0.1% | > 1%            |
| API         | Client error rate (4xx) | < 5%   | > 10%           |
| Database    | Connection errors       | 0      | > 5 errors/min  |
| Third-party | API call failures       | < 1%   | > 5%            |

### 4. Saturation

_How full is your service?_

| Service  | Metric          | Target    | Alert Threshold |
| -------- | --------------- | --------- | --------------- |
| CPU      | Utilization     | < 70% avg | > 85% for 5 min |
| Memory   | Utilization     | < 80%     | > 90%           |
| Disk     | Utilization     | < 80%     | > 90%           |
| Database | Connection pool | < 70%     | > 90%           |
| Queue    | Depth           | < 100     | > 1000          |

---

## Logging Strategy

### What to Log

**Application logs**:

- ✅ User actions (login, core actions)
- ✅ Errors and exceptions
- ✅ Performance bottlenecks
- ✅ Security events (auth failures, access denied)
- ✅ Business events (subscriptions, payments)

**Infrastructure logs**:

- ✅ Server start/stop
- ✅ Deployment events
- ✅ Configuration changes
- ✅ Health check results

**What NOT to log**:

- ❌ Passwords or credentials
- ❌ Credit card numbers
- ❌ Personal identification numbers
- ❌ User-generated content (PII)

---

### Log Format

**Structured logging** (JSON format):

```json
{
  "timestamp": "2025-01-15T14:30:00.123Z",
  "level": "error",
  "service": "api",
  "environment": "production",
  "request_id": "req_abc123",
  "user_id": "usr_xyz789",
  "message": "Database connection failed",
  "error": {
    "type": "DatabaseConnectionError",
    "message": "Connection timeout after 5000ms",
    "stack": "..."
  },
  "context": {
    "endpoint": "/api/users",
    "method": "GET",
    "ip": "192.168.1.1"
  }
}
```

**Standard fields** (every log):

- `timestamp`: ISO 8601 format
- `level`: debug, info, warn, error, fatal
- `service`: Which service generated this
- `environment`: dev, staging, production
- `request_id`: Trace requests across services
- `user_id`: Associate with user (if applicable)
- `message`: Human-readable description

---

### Log Levels

**When to use each level**:

| Level     | When to Use                    | Example                | Goes to Alert?    |
| --------- | ------------------------------ | ---------------------- | ----------------- |
| **DEBUG** | Detailed diagnostic info       | "Query took 45ms"      | No                |
| **INFO**  | General informational messages | "User logged in"       | No                |
| **WARN**  | Potential issues, recoverable  | "Retry attempt 2/3"    | No                |
| **ERROR** | Error occurred, user impacted  | "Payment failed"       | Yes (if frequent) |
| **FATAL** | System crash, immediate action | "Database unreachable" | Yes (always)      |

---

### Log Retention

| Environment | Retention Period          | Reason                |
| ----------- | ------------------------- | --------------------- |
| Production  | 30 days hot, 90 days cold | Compliance, debugging |
| Staging     | 7 days                    | Cost optimization     |
| Development | 3 days                    | Cost optimization     |

**Cost estimate**: $[X]/month at [Y] GB/day

---

## Distributed Tracing

### When to Use Tracing

**Use tracing for**:

- Multi-service requests (microservices)
- Complex workflows (many steps)
- Performance debugging (where's the slowdown?)

**Don't need tracing for**:

- Monolithic apps (logs sufficient)
- Simple request/response (metrics sufficient)

---

### Trace Implementation

**Tool**: [Jaeger / Zipkin / AWS X-Ray / OpenTelemetry]

**Sampling strategy**:

- **100% of errors**: Always trace failed requests
- **10% of successful requests**: Sample successes to reduce cost
- **100% of slow requests** (> 2s): Always trace slow requests

**Example trace**:

```
Request: GET /api/orders/123
├─ API Gateway (5ms)
├─ Auth Service (15ms)
│  └─ Redis lookup (3ms)
├─ Order Service (150ms)
│  ├─ Database query (100ms) ← SLOWEST
│  ├─ Inventory Service (30ms)
│  └─ User Service (20ms)
└─ Response (5ms)

Total: 175ms
```

**What to trace**:

- HTTP requests
- Database queries
- Cache lookups
- External API calls
- Message queue operations

---

## Metrics Architecture

### Metrics Collection

**Approach**: [RED method / USE method]

#### RED Method (for services)

_Recommended for request-driven services_

- **Rate**: Requests per second
- **Errors**: Requests that fail
- **Duration**: Time to complete requests

#### USE Method (for resources)

_Recommended for infrastructure_

- **Utilization**: % of resource used
- **Saturation**: Degree of overload
- **Errors**: Count of error events

---

### Custom Metrics

**Business metrics**:

```javascript
// Example: Track signups
metrics.increment('user.signup', 1, {
  source: 'organic',
  plan: 'pro',
})

// Example: Track revenue
metrics.gauge('revenue.mrr', 50000, {
  currency: 'USD',
})
```

**Product metrics**:

```javascript
// Example: Track feature usage
metrics.increment('feature.used', 1, {
  feature: 'export',
  format: 'csv',
})
```

**Performance metrics**:

```javascript
// Example: Track function duration
const start = Date.now()
await performExpensiveOperation()
const duration = Date.now() - start
metrics.timing('operation.duration', duration, {
  operation: 'expensive_task',
})
```

---

### Metrics Aggregation

**Time windows**:

- Real-time: 1-minute buckets
- Short-term: 5-minute buckets
- Medium-term: 1-hour buckets
- Long-term: 1-day buckets

**Retention**:

- 1-min data: 24 hours
- 5-min data: 7 days
- 1-hour data: 90 days
- 1-day data: 2 years

---

## Dashboard Specifications

### Dashboard 1: System Health (Overview)

**Purpose**: Is the system healthy right now?

**Audience**: Everyone (displayed on TV/monitors)

**Metrics**:

- **Status indicator**: 🟢 Healthy / 🟡 Degraded / 🔴 Down
- **Error rate**: Current vs baseline (5-min window)
- **Latency**: p50, p95, p99 (5-min window)
- **Traffic**: Requests per second (1-min window)
- **Active incidents**: Count and severity

**Layout**:

```
┌─────────────────────────────────────────┐
│  System Status: 🟢 Healthy             │
├─────────────────────────────────────────┤
│  Error Rate: 0.05% (baseline: 0.1%)    │
│  [Line chart: last 24 hours]           │
├─────────────────────────────────────────┤
│  Latency: p95 = 280ms (target: 300ms)  │
│  [Line chart: p50, p95, p99]           │
├─────────────────────────────────────────┤
│  Traffic: 1,250 rps                     │
│  [Line chart: last 24 hours]           │
├─────────────────────────────────────────┤
│  Active Incidents: 0                    │
└─────────────────────────────────────────┘
```

**Refresh**: Every 30 seconds

---

### Dashboard 2: Service Deep Dive

**Purpose**: Debug issues in specific service

**Audience**: Engineers, on-call

**Metrics** (per service):

- Request rate (rps)
- Error rate (% and absolute count)
- Latency percentiles (p50, p95, p99)
- Top errors (by count)
- Slowest endpoints (by p95)
- Dependency health (upstream/downstream services)

**Filters**:

- Time range (last 1h, 6h, 24h, 7d)
- Environment (production, staging)
- Version (compare releases)

---

### Dashboard 3: User Journey

**Purpose**: Monitor user experience end-to-end

**Audience**: Product, customer success

**Metrics**:

- Signup funnel (conversion at each step)
- Activation rate (% completing core action)
- Error rate for user-facing actions
- User-reported errors (support tickets)

**Layout**:

```
Signup Funnel:
Landing (1000) → Signup (500) → Email Verify (450) → Activated (400)
   100%            50%              90%                 89%

Critical User Flows:
  Login flow: 99.5% success (5 errors in last hour)
  Core action: 98.2% success (18 errors in last hour)
  Payment flow: 100% success (0 errors in last hour)
```

---

### Dashboard 4: Infrastructure

**Purpose**: Monitor resource utilization

**Audience**: Platform/DevOps, on-call

**Metrics**:

- CPU utilization (per host, avg/max)
- Memory utilization (per host, avg/max)
- Disk usage (per host, % used)
- Network traffic (in/out)
- Database connections (active/max)
- Queue depth (per queue)

**Alerts**:

- CPU > 85% for 5+ minutes
- Memory > 90%
- Disk > 90%
- Database connections > 90% of pool

---

_[Define 4-6 key dashboards]_

---

## Alert Definitions

### Alert Severity Levels

| Level        | When to Use                              | Response Time            | Notification            |
| ------------ | ---------------------------------------- | ------------------------ | ----------------------- |
| **Critical** | User-facing outage, data loss            | Immediate (page on-call) | PagerDuty, Slack, Phone |
| **Warning**  | Degraded performance, approaching limits | 15 minutes               | Slack                   |
| **Info**     | FYI, no action needed                    | N/A                      | Slack (optional)        |

---

### Critical Alerts

#### Alert 1: High Error Rate

**Condition**: Error rate > 1% for 5 minutes

**Why critical**: Users experiencing failures

**Runbook**: `/runbooks/high-error-rate.md`

**Notification**: PagerDuty → on-call engineer

**Expected response**: Investigate within 5 minutes, resolve or rollback within 15 minutes

---

#### Alert 2: API Down

**Condition**: Health check fails 3 consecutive times (3 minutes)

**Why critical**: Service is unavailable

**Runbook**: `/runbooks/api-down.md`

**Notification**: PagerDuty → on-call engineer

**Expected response**: Investigate immediately, restore service within 10 minutes

---

#### Alert 3: Database Connection Failure

**Condition**: > 10 database connection errors per minute

**Why critical**: Application can't access data

**Runbook**: `/runbooks/database-connection-failure.md`

**Notification**: PagerDuty → on-call engineer

**Expected response**: Investigate immediately, restore connection within 5 minutes

---

#### Alert 4: Disk Space Critical

**Condition**: Disk usage > 95%

**Why critical**: System could crash when disk full

**Runbook**: `/runbooks/disk-space-critical.md`

**Notification**: PagerDuty → on-call engineer

**Expected response**: Free up space within 30 minutes

---

### Warning Alerts

#### Alert 5: High Latency

**Condition**: p95 latency > 500ms for 10 minutes

**Why warning**: Users experiencing slowness but not failures

**Runbook**: `/runbooks/high-latency.md`

**Notification**: Slack #alerts channel

**Expected response**: Investigate during business hours, optimize if persistent

---

#### Alert 6: Elevated Error Rate

**Condition**: Error rate > 0.5% for 15 minutes (but < 1%)

**Why warning**: Errors increasing but not yet critical

**Runbook**: `/runbooks/elevated-errors.md`

**Notification**: Slack #alerts channel

**Expected response**: Monitor, investigate if continues

---

_[Define 8-12 critical alerts, 5-10 warning alerts]_

---

## SLOs and Error Budgets

### Service Level Objectives

**What is an SLO?**

- Target reliability level (e.g., 99.9% uptime)
- Measured over a time window (e.g., 30 days)
- Creates an error budget (allowable downtime)

---

### SLO 1: API Availability

**Definition**: API returns 200/300 responses (not 500s)

**Target**: 99.9% of requests succeed

**Measurement window**: 30 days

**Error budget**: 0.1% failure rate = 43.2 minutes downtime/month

**Current performance**: [X%]

**Error budget remaining**: [Y] minutes this month

**What happens when budget exhausted**:

- Stop all feature work
- Focus on reliability improvements
- No deploys except bug fixes

---

### SLO 2: API Latency

**Definition**: API responds within acceptable time

**Target**: 95% of requests < 500ms (p95 latency)

**Measurement window**: 30 days

**Error budget**: 5% of requests can be > 500ms

**Current performance**: p95 = [X]ms

**Error budget remaining**: [Y]% slow requests allowed this month

---

### SLO 3: Critical User Flow Success Rate

**Definition**: Users can complete [core action]

**Target**: 99% of attempts succeed

**Measurement window**: 7 days

**Error budget**: 1% failure rate

**Current performance**: [X%] success

**Error budget remaining**: [Y]% failures allowed this week

---

### Error Budget Policy

**When error budget is healthy** (> 50% remaining):

- ✅ Ship new features
- ✅ Deploy to production multiple times/day
- ✅ Take calculated risks

**When error budget is low** (< 20% remaining):

- ⚠️ Slow down feature releases
- ⚠️ Increase testing
- ⚠️ Focus on stability

**When error budget is exhausted** (0% remaining):

- 🛑 Feature freeze
- 🛑 Only reliability improvements
- 🛑 Post-mortem required

---

## On-Call Runbooks

### Runbook Template

Each runbook should include:

1. **Symptoms**: What you're seeing (alerts, user reports)
2. **Diagnosis**: How to confirm the issue
3. **Fix**: Step-by-step resolution
4. **Prevention**: How to prevent recurrence
5. **Escalation**: When to escalate, who to contact

---

### Runbook 1: High Error Rate

**Symptoms**:

- Alert: "Error rate > 1% for 5 minutes"
- Users reporting errors
- Error tracking shows spike

**Diagnosis**:

1. Check error rate dashboard (which errors?)
2. Check logs for common error messages:
   ```bash
   # Search logs for errors in last 10 minutes
   kubectl logs -l app=api --since=10m | grep ERROR
   ```
3. Check recent deployments (did we just deploy?)
4. Check third-party status pages (is Stripe down?)

**Fix**:

**If caused by recent deployment**:

```bash
# Rollback to previous version
kubectl rollout undo deployment/api-deployment

# Verify error rate returns to normal
# Check dashboard after 5 minutes
```

**If caused by bad data**:

```bash
# Fix data issue
# Example: Remove invalid records
DELETE FROM users WHERE email IS NULL;

# Verify errors stop
```

**If caused by third-party outage**:

```bash
# Enable feature flag to disable feature
featureFlags.disable('stripe-payments');

# Or: Add circuit breaker to fail fast
```

**Prevention**:

- Add more comprehensive tests
- Improve staging environment to catch before prod
- Add gradual rollout (canary deployment)

**Escalation**:

- If unable to resolve in 15 minutes → escalate to senior engineer
- If data corruption → escalate to data team
- If third-party → check status page, contact their support if needed

---

### Runbook 2: API Down

**Symptoms**:

- Alert: "Health check failing"
- Users can't access application
- All requests timing out

**Diagnosis**:

1. Check if service is running:

   ```bash
   kubectl get pods -l app=api

   # Are pods in "Running" state?
   # Are there any "CrashLoopBackOff"?
   ```

2. Check service logs:

   ```bash
   kubectl logs -l app=api --tail=100

   # Look for errors on startup
   ```

3. Check recent changes:
   - Recent deployments?
   - Infrastructure changes?
   - Database migrations?

**Fix**:

**If pods are crashing**:

```bash
# Check pod status
kubectl describe pod [pod-name]

# Common issues:
# - Out of memory → increase memory limit
# - Failed health check → check health endpoint
# - Image pull error → check image tag

# Quick fix: Rollback deployment
kubectl rollout undo deployment/api-deployment
```

**If database is down**:

```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier [name]

# If down, check AWS console for details
# May need to restore from backup
```

**If infrastructure issue**:

```bash
# Check AWS/GCP status page
# Check networking (security groups, VPC)
# Escalate to platform team
```

**Prevention**:

- Implement proper health checks
- Add resource limits and requests
- Set up auto-restart policies
- Multi-AZ deployment for high availability

**Escalation**:

- If unable to restart service in 10 minutes → escalate to platform team
- If database issue → escalate to database admin
- If cloud provider outage → wait for status updates, communicate to users

---

_[Create 8-12 runbooks for common scenarios]_

---

## Incident Response Process

### Incident Severity

| Severity  | Definition                                   | Example                           | Response Time       |
| --------- | -------------------------------------------- | --------------------------------- | ------------------- |
| **SEV-1** | Complete outage, all users affected          | API down, database down           | Immediate (< 5 min) |
| **SEV-2** | Significant degradation, many users affected | High error rate, slow performance | 15 minutes          |
| **SEV-3** | Minor issue, few users affected              | Feature broken, UI bug            | 1 hour              |

---

### Incident Response Steps

#### 1. Detect (0-5 minutes)

**How incidents are detected**:

- Monitoring alerts (automated)
- User reports (support tickets)
- Team member notices (manual)

**First actions**:

- [ ] Acknowledge alert in PagerDuty
- [ ] Triage severity (SEV-1, 2, or 3)
- [ ] Create incident in incident management tool

---

#### 2. Communicate (5-10 minutes)

**Internal communication**:

- [ ] Post in #incidents Slack channel:
  ```
  🔴 INCIDENT: [Title]
  Severity: SEV-2
  Impact: [What's broken?]
  Investigating: @engineer
  Status page: [Link if public]
  ```
- [ ] Assign incident commander (for SEV-1)
- [ ] Loop in relevant teams

**External communication** (if customer-facing):

- [ ] Update status page: "Investigating"
- [ ] If SEV-1: Consider email to affected customers

---

#### 3. Diagnose (10-20 minutes)

**Diagnosis steps**:

- [ ] Check dashboards (errors, latency, traffic)
- [ ] Check logs (what errors are occurring?)
- [ ] Check recent changes (deployments, config, migrations)
- [ ] Check dependencies (third-party services, database)
- [ ] Follow runbook for this issue

**Document findings** in #incidents thread

---

#### 4. Fix (20-45 minutes)

**Resolution approaches**:

- **Rollback**: Deploy previous version (fastest)
- **Hotfix**: Fix the bug and deploy (if quick)
- **Disable feature**: Use feature flag to turn off broken feature
- **Scale up**: Add more resources if capacity issue
- **Wait**: If third-party outage, wait for their resolution

**Actions**:

- [ ] Execute fix
- [ ] Verify fix (check dashboards, test manually)
- [ ] Confirm error rate returns to normal
- [ ] Confirm latency returns to normal

---

#### 5. Monitor (45-60 minutes)

**Post-fix monitoring**:

- [ ] Watch dashboards for 15-30 minutes
- [ ] Ensure no new issues arise
- [ ] Check for customer reports (support tickets)

**Communication**:

- [ ] Update #incidents: "Resolved"
- [ ] Update status page: "Resolved"
- [ ] If customer impact: Send resolution email

---

#### 6. Post-Mortem (Within 48 hours)

**For SEV-1 and SEV-2 incidents**:

- [ ] Schedule post-mortem meeting (within 48 hours)
- [ ] Write post-mortem document (template below)
- [ ] Share with team for review
- [ ] Create action items to prevent recurrence
- [ ] Assign owners and due dates

---

### Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

**Date**: [Date]
**Severity**: [SEV-1/2/3]
**Duration**: [X] minutes
**Impact**: [How many users affected?]
**Author**: [Name]

## Summary

[2-3 sentences: What happened?]

## Timeline

**[Time]** - Incident began (first alert)
**[Time]** - Team notified
**[Time]** - Root cause identified
**[Time]** - Fix deployed
**[Time]** - Incident resolved
**[Time]** - Monitoring period ended

## Root Cause

[Detailed explanation of what caused the incident]

## Impact

- **Users affected**: [X users or %]
- **Duration**: [Y minutes]
- **Revenue impact**: $[Z] (if applicable)
- **SLO impact**: [% of error budget consumed]

## What Went Well

- [Thing 1 - e.g., "Fast detection via alerts"]
- [Thing 2 - e.g., "Clear communication in #incidents"]
- [Thing 3 - e.g., "Quick rollback procedure"]

## What Went Wrong

- [Thing 1 - e.g., "Staging didn't catch the bug"]
- [Thing 2 - e.g., "Took 10 min to identify root cause"]
- [Thing 3 - e.g., "Rollback procedure was manual"]

## Action Items

| Action                                                   | Owner     | Due Date | Priority |
| -------------------------------------------------------- | --------- | -------- | -------- |
| [Action 1 - e.g., "Add test coverage for this scenario"] | @engineer | [Date]   | High     |
| [Action 2 - e.g., "Automate rollback procedure"]         | @devops   | [Date]   | High     |
| [Action 3 - e.g., "Improve staging environment"]         | @team     | [Date]   | Medium   |

## Lessons Learned

[What did we learn? How can we improve?]

---

**No blame. No punishment. Only learning.**
```

---

## Tool Stack

### Recommended Tools

| Category           | Tool                                  | Cost                                          | Why                                               |
| ------------------ | ------------------------------------- | --------------------------------------------- | ------------------------------------------------- |
| **Metrics**        | [Prometheus + Grafana]                | Free (self-hosted) or $[X]/mo (Grafana Cloud) | Open source, powerful, widely adopted             |
| **Logs**           | [Loki / ELK / Datadog]                | $[X]/month                                    | Scalable, searchable, integrates with metrics     |
| **Traces**         | [Jaeger / OpenTelemetry]              | Free (self-hosted) or $[X]/mo (Datadog APM)   | Distributed tracing, visualize request flows      |
| **Dashboards**     | [Grafana]                             | Free or $[X]/mo                               | Flexible, beautiful, integrates everything        |
| **Alerts**         | [Prometheus Alertmanager / PagerDuty] | PagerDuty $[X]/user/mo                        | Reliable, on-call management                      |
| **APM**            | [Datadog / New Relic]                 | $[X]/host/mo                                  | Application performance monitoring                |
| **Uptime**         | [UptimeRobot / Pingdom]               | $[X]/month                                    | External monitoring (outside your infrastructure) |
| **Error tracking** | [Sentry]                              | $[X]/month                                    | Error aggregation, stack traces, releases         |

### Total estimated cost: $[X]/month

---

## Observability Checklist

Before going to production:

### Metrics

- [ ] Golden signals instrumented (latency, traffic, errors, saturation)
- [ ] Business metrics tracked
- [ ] Custom metrics for key user actions
- [ ] Dashboards created and accessible
- [ ] Metrics retention policy configured

### Logs

- [ ] Structured logging implemented
- [ ] Log levels used correctly
- [ ] No PII in logs
- [ ] Logs aggregated in central system
- [ ] Log retention policy configured

### Traces

- [ ] Distributed tracing configured (if applicable)
- [ ] Sampling strategy defined
- [ ] Traces linked to logs (request_id)

### Alerts

- [ ] Critical alerts configured
- [ ] Warning alerts configured
- [ ] Runbooks written for each alert
- [ ] On-call rotation scheduled
- [ ] Alert routing configured (PagerDuty/Slack)
- [ ] Alert fatigue prevented (only actionable alerts)

### SLOs

- [ ] SLOs defined for critical user journeys
- [ ] Error budgets calculated
- [ ] Error budget policy agreed upon
- [ ] SLO dashboards created

### Incident Response

- [ ] Incident process documented
- [ ] Runbooks created
- [ ] Post-mortem template created
- [ ] Team trained on incident response
- [ ] On-call rotation scheduled

---

## Next Steps

- [ ] Review with engineering and ops teams
- [ ] Set up tool accounts
- [ ] Implement instrumentation (Phase 1: Golden signals)
- [ ] Create dashboards
- [ ] Configure alerts
- [ ] Test alerting (trigger test alert)
- [ ] Train team on dashboards and runbooks
- [ ] Schedule on-call rotation
- [ ] Run fire drill (simulate incident)

---

## Document Control

**Status**: [Draft/In Progress/Implemented]
**Last Updated**: [Date]
**Next Review**: [Quarterly]
**Owner**: [Name/Role - SRE/Platform]
**On-Call Schedule**: [Link to PagerDuty or schedule]
