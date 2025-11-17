---
description: Session 14 - Create monitoring, alerting, and observability strategy
---

# Design Observability (Session 14 - Core)

You are helping the user create a comprehensive observability strategy including metrics, logs, traces, dashboards, alerts, SLOs, and incident response. This is a core session that ensures you can monitor and maintain production systems.

## When to Use This

**Run AFTER Session 13** (`/plan-deployment`):
- You've planned deployment and now need monitoring strategy
- You want observability from day one
- You need to define SLOs and error budgets

**This is now a CORE session** because:
- You can't improve what you can't measure
- Observability is essential for reliable production systems
- Monitoring ensures continuous delivery of journey value

## Your Task

Create a comprehensive observability strategy using the prompt in `/prompts/operations/monitoring.md`.

### Steps to Execute

1. **Read the observability prompt**:
   ```bash
   Read /prompts/operations/monitoring.md
   ```

2. **Read the template structure**:
   ```bash
   Read templates/14-observability-strategy-template.md
   ```

3. **Check for architecture from Session 4** (recommended):
   ```bash
   Read product-guidelines/04-architecture.md
   ```
   - Understand system components to monitor

4. **Check for metrics from Session 4** (recommended):
   ```bash
   Read product-guidelines/04-metrics.md
   ```
   - Business metrics inform technical monitoring

5. **Check for deployment plan** (recommended):
   ```bash
   Read product-guidelines/13-deployment-plan.md
   ```
   - Monitoring integrates with deployment

6. **Interview the user** following the observability prompt:
   - **Current state**: What monitoring do you have? What's missing?
   - **Golden signals**: Latency, traffic, errors, saturation - what to track?
   - **Logging strategy**: What to log? Structured logs? Retention?
   - **Tracing**: Distributed tracing? Which requests?
   - **Metrics**: RED (rate, errors, duration) or USE (utilization, saturation, errors)?
   - **Dashboards**: What views? Service health, user journey, business metrics?
   - **Alerts**: What's critical? What wakes you up at 2am?
   - **SLOs**: What reliability do users expect? Error budget?
   - **Incident response**: Runbooks, on-call rotation, post-mortems?
   - **Tools**: Datadog? Grafana? CloudWatch? Prometheus? OpenTelemetry?

7. **Develop observability strategy**:
   - Observability principles (what and why)
   - Golden signals for each service
   - Logging strategy (structured logs, retention, search)
   - Distributed tracing plan
   - Metrics architecture (RED or USE)
   - Dashboard specifications (5-8 dashboards)
   - Alert definitions (critical, warning, info)
   - SLOs and error budgets
   - On-call runbooks (10+ scenarios)
   - Incident response process
   - Post-mortem template
   - Tool recommendations
   - Cost estimates

8. **Write the output**:
   ```bash
   Write product-guidelines/14-observability-strategy.md
   ```

## Output Location

`product-guidelines/14-observability-strategy.md`

This will be used by:
- Engineers implementing monitoring
- SRE/DevOps teams managing production
- On-call engineers responding to incidents
- Product managers tracking reliability
- Executives reporting on SLOs

## Template Structure

The output follows this structure:
- Observability Philosophy (principles and goals)
- Golden Signals (latency, traffic, errors, saturation)
- Logging Strategy (what, format, retention)
- Distributed Tracing (when, what, sampling)
- Metrics Architecture (RED/USE, custom metrics)
- Dashboard Specifications (service, business, user)
- Alert Definitions (critical, warning, runbook links)
- SLOs and Error Budgets
- On-call Runbooks (troubleshooting guides)
- Incident Response Process
- Post-mortem Template
- Tool Stack and Setup
- Cost Estimates
- Observability Checklist

## Key Principles

1. **Three pillars**: Metrics (what), logs (why), traces (where)
2. **Alert on symptoms** - Not causes (alert on errors, not CPU)
3. **SLOs, not SLAs** - Define reliability expectations with error budgets
4. **Dashboards for questions** - Each dashboard answers specific questions
5. **Runbooks save time** - Document fixes when you discover them
6. **Post-mortems without blame** - Learn from incidents
7. **Cost awareness** - Observability can get expensive fast

## Example Prompt Flow

```
You: Let's design your observability strategy. First, let me check your architecture and metrics...

[Read product-guidelines/04-architecture.md and product-guidelines/04-metrics.md]

You: Got it - you have [services] and care about [business metrics]. What monitoring do you have today? What's missing?

User: [Describes current state]

You: I see. Let's start with the golden signals. For your [main service], what matters most?
- **Latency**: What response time do users expect?
- **Traffic**: How many requests/sec?
- **Errors**: What error rate is acceptable?
- **Saturation**: What's your capacity limit?

User: [Describes golden signals]

You: Perfect. Now logging - what do you need to log for debugging? User actions? API calls? Errors? Database queries?

User: [Describes logging needs]

You: Great. Do you need distributed tracing? If a request touches 5 services, do you need to trace the full path?

User: [Yes/No and requirements]

You: Excellent. Now dashboards - what questions do you need answered at a glance?
- Is the system healthy?
- Are users successful?
- Where are errors happening?
- What needs my attention?

User: [Describes dashboard needs]

You: Perfect. Now the critical question - what alerts wake you up at 2am? What's actually an emergency vs just "good to know"?

User: [Describes critical alerts]

You: Great. Let's define SLOs. What reliability do users expect? 99.9% uptime = 43 min downtime/month. Is that acceptable? Or do you need 99.99%?

User: [Defines SLO targets]

You: Perfect. With a 99.9% SLO, you have a 0.1% error budget. That's your room to experiment and take risks. When you burn through it, you focus on reliability, not features.

Now for incident response - when something breaks at 2am:
1. Who gets paged?
2. What's the first thing they check?
3. Where are the runbooks?
4. How do you communicate to users/team?

User: [Describes incident process]

[Continue through post-mortems, tools, costs...]

You: Excellent! I've created your observability strategy in product-guidelines/14-observability-strategy.md:
- Observability philosophy (three pillars, alert on symptoms)
- Golden signals for 4 services (latency, traffic, errors, saturation)
- Structured logging (JSON format, 30-day retention, key fields)
- Distributed tracing (10% sampling, critical paths)
- Metrics: RED method (rate, errors, duration) for all APIs
- 6 dashboards (system health, user journey, business metrics, errors, performance, infrastructure)
- 12 alerts (8 critical, 4 warning) with runbook links
- SLOs: 99.9% availability, p95 latency < 500ms, error rate < 0.5%
- Error budget: 43 min downtime/month, 0.5% error rate
- 10 runbooks (DB down, high latency, API errors, etc.)
- Incident response: PagerDuty → Runbook → Fix → Communicate → Post-mortem
- Post-mortem template (no blame, action items, preventions)
- Tool stack: OpenTelemetry → Grafana + Loki + Tempo (self-hosted)
- Cost estimate: $[X]/month at current scale
- Observability implementation checklist

Ready to implement? Start with golden signals and critical alerts.
```

## After This Session

**Implementation priority**:
1. **Phase 1**: Golden signals + critical alerts (Week 1)
2. **Phase 2**: Dashboards + SLOs (Week 2)
3. **Phase 3**: Distributed tracing + runbooks (Week 3+)

**Use this document**:
- When implementing monitoring code
- When setting up dashboards and alerts
- When responding to incidents (runbooks)
- When reporting on reliability (SLOs)

---

**Remember**: This is a CORE session. You can't improve what you can't measure. Good observability = good reliability and continuous delivery of journey value.
