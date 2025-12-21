# Analytics Implementation Plan

> **Generated**: [Date] > **Product**: [Product Name] > **Status**: [Draft/In Progress/Implemented]

## Overview

This document defines the comprehensive analytics implementation plan including event tracking, funnels, dashboards, and tooling.

**Based on**: Session 3 Metrics (product-guidelines/03-metrics.md)

- Session 3: **WHAT** to measure (North Star, success metrics) - the strategy
- This doc: **HOW** to measure (events, properties, dashboards, tools) - the implementation

---

## Analytics Strategy

### Goals

**What we want to learn**:

1. [Goal 1 - e.g., "Where users drop off in onboarding"]
2. [Goal 2 - e.g., "Which features drive retention"]
3. [Goal 3 - e.g., "How pricing affects conversion"]

### Metrics Hierarchy

_(From Session 3)_

**North Star Metric**: [Metric name]

- Current: [Baseline]
- Target: [Goal]

**Input Metrics** (drive North Star):

- [Metric 1]: [Current → Target]
- [Metric 2]: [Current → Target]
- [Metric 3]: [Current → Target]

**Health Metrics** (sustainable growth):

- [Metric 1]: [Current → Target]
- [Metric 2]: [Current → Target]

---

## Event Taxonomy

### Naming Convention

**Structure**: [Choose one]

- `object_action` (e.g., `user_signed_up`)
- `action_object` (e.g., `signed_up_user`)
- `Proper Case Object Action` (e.g., `User Signed Up`)

**Chosen convention**: [Your convention]

### Categories

**User lifecycle**:

- Authentication (signup, login, logout)
- Onboarding (profile, setup, tutorial)
- Engagement (core actions)
- Retention (return visits, reactivation)
- Monetization (upgrade, payment)
- Referral (invite, share)

**Feature usage**:

- [Feature category 1]
- [Feature category 2]
- [Feature category 3]

**System events**:

- Errors
- Performance
- Infrastructure

---

## Event Tracking Plan

### User Lifecycle Events

| Event Name              | When Fired                  | Properties                            | Priority |
| ----------------------- | --------------------------- | ------------------------------------- | -------- |
| `user_signed_up`        | User completes registration | `source`, `plan_type`, `company_size` | P0       |
| `user_logged_in`        | User authenticates          | `method` (email/oauth/sso)            | P0       |
| `onboarding_started`    | First login after signup    | `timestamp`                           | P0       |
| `onboarding_completed`  | User finishes setup         | `duration_seconds`, `steps_completed` | P0       |
| `user_invited_teammate` | User sends invite           | `role`, `invite_method`               | P1       |

---

### Core Feature Events

| Event Name          | When Fired          | Properties                     | Priority |
| ------------------- | ------------------- | ------------------------------ | -------- |
| `[feature]_created` | User creates [item] | `[property 1]`, `[property 2]` | P0       |
| `[feature]_viewed`  | User views [item]   | `[property 1]`                 | P1       |
| `[feature]_edited`  | User edits [item]   | `[property 1]`, `changes_made` | P1       |
| `[feature]_deleted` | User deletes [item] | `[property 1]`                 | P1       |
| `[feature]_shared`  | User shares [item]  | `share_method`                 | P1       |

---

### Monetization Events

| Event Name               | When Fired          | Properties                       | Priority |
| ------------------------ | ------------------- | -------------------------------- | -------- |
| `pricing_page_viewed`    | User views pricing  | `source`, `plan_viewing`         | P0       |
| `upgrade_initiated`      | User clicks upgrade | `from_plan`, `to_plan`           | P0       |
| `payment_info_entered`   | User enters payment | `plan_selected`                  | P0       |
| `subscription_created`   | Payment successful  | `plan`, `price`, `billing_cycle` | P0       |
| `subscription_cancelled` | User cancels        | `reason`, `tenure_days`          | P0       |

---

### Error and Performance Events

| Event Name       | When Fired              | Properties                               | Priority |
| ---------------- | ----------------------- | ---------------------------------------- | -------- |
| `error_occurred` | Any error shown to user | `error_type`, `error_message`, `context` | P0       |
| `api_error`      | API call fails          | `endpoint`, `status_code`, `error`       | P1       |
| `page_load_slow` | Page load > 3s          | `page`, `load_time_ms`                   | P2       |

---

_[Include 30-50 total events across all categories]_

---

## User Properties

### Demographic Properties

| Property       | Type     | Source | Example Values               |
| -------------- | -------- | ------ | ---------------------------- |
| `user_id`      | string   | System | `usr_abc123`                 |
| `email`        | string   | Signup | `user@example.com`           |
| `name`         | string   | Signup | `John Doe`                   |
| `signup_date`  | datetime | System | `2025-01-15T14:30:00Z`       |
| `company_name` | string   | Signup | `Acme Corp`                  |
| `company_size` | string   | Signup | `11-50`, `51-200`, `201-500` |
| `role`         | string   | Signup | `admin`, `member`, `viewer`  |

### Behavioral Properties

| Property            | Type     | Source     | Example Values                          |
| ------------------- | -------- | ---------- | --------------------------------------- |
| `first_action_date` | datetime | Calculated | `2025-01-15T15:00:00Z`                  |
| `last_active_date`  | datetime | Calculated | `2025-01-20T10:30:00Z`                  |
| `days_since_signup` | integer  | Calculated | `5`                                     |
| `total_[actions]`   | integer  | Calculated | `42`                                    |
| `lifecycle_stage`   | string   | Calculated | `trial`, `active`, `at_risk`, `churned` |

### Firmographic Properties

_(For B2B products)_

| Property           | Type    | Source     | Example Values             |
| ------------------ | ------- | ---------- | -------------------------- |
| `industry`         | string  | Enrichment | `Technology`, `Healthcare` |
| `revenue_range`    | string  | Enrichment | `$1M-$10M`                 |
| `employee_count`   | integer | Enrichment | `150`                      |
| `location_country` | string  | IP/Signup  | `US`, `UK`, `CA`           |

### Custom Properties

| Property              | Type   | Source   | Example Values |
| --------------------- | ------ | -------- | -------------- |
| `[custom_property_1]` | [type] | [source] | [values]       |
| `[custom_property_2]` | [type] | [source] | [values]       |

---

## Conversion Funnels

### Funnel 1: Signup to Activation

**Definition**: User signs up → completes onboarding → performs core action

**Steps**:

1. **Visitor** → Lands on homepage
2. **Signup started** → Clicks "Sign up"
3. **Account created** → Completes registration (`user_signed_up`)
4. **Onboarding started** → First login (`onboarding_started`)
5. **Onboarding completed** → Finishes setup (`onboarding_completed`)
6. **Activated** → Performs [core action] (`[core_action]_created`)

**Success criteria**: [X%] conversion from step 1 to step 6

**Current**: [Baseline %]
**Target**: [Goal %]

---

### Funnel 2: Free to Paid

**Definition**: User on free plan → views pricing → subscribes

**Steps**:

1. **Free user** → Active on free plan
2. **Pricing viewed** → Views pricing page (`pricing_page_viewed`)
3. **Upgrade initiated** → Clicks upgrade CTA (`upgrade_initiated`)
4. **Payment entered** → Enters payment info (`payment_info_entered`)
5. **Subscription created** → Completes payment (`subscription_created`)

**Success criteria**: [X%] conversion from step 1 to step 5

**Current**: [Baseline %]
**Target**: [Goal %]

---

### Funnel 3: [Feature Adoption]

**Definition**: [Describe funnel]

**Steps**:
[List steps with events]

**Success criteria**: [Target conversion]

---

_[Define 5-10 critical funnels]_

---

## Cohort Definitions

### Acquisition Cohorts

**By source**:

- Organic search
- Paid ads
- Referral
- Direct
- Social media

**By campaign**:

- [Campaign 1]
- [Campaign 2]

---

### Behavioral Cohorts

**By activation**:

- Activated (completed core action within 7 days)
- Not activated

**By engagement**:

- Power users ([X] actions per week)
- Active users ([Y] actions per week)
- At-risk users (no activity in [Z] days)
- Churned users (no activity in [W] days)

**By feature usage**:

- Users of [Feature A]
- Users of [Feature B]
- Users of both [A] and [B]
- Users of neither

---

### Business Cohorts

**By plan**:

- Free
- [Paid Tier 1]
- [Paid Tier 2]
- Enterprise

**By tenure**:

- New (< 30 days)
- Growing (30-90 days)
- Established (90-180 days)
- Mature (180+ days)

**By company size**:

- Solo (1 user)
- Small team (2-10 users)
- Medium team (11-50 users)
- Large team (51+ users)

---

## Dashboard Specifications

### Dashboard 1: Executive (North Star)

**Purpose**: Track North Star and overall business health

**Metrics**:

- North Star Metric (trend: daily, weekly, monthly)
- Key input metrics (current vs target)
- Revenue (MRR, ARR growth)
- User growth (signups, active users, retention)

**Views**:

- Line chart: North Star over time (90 days)
- Gauge: Current vs target
- Table: Breakdown by cohort

**Refresh**: Daily
**Audience**: Executives, all-hands

---

### Dashboard 2: Product (Feature Usage)

**Purpose**: Understand feature adoption and usage

**Metrics**:

- Feature usage (by feature)
- Feature adoption rate (% of users)
- Feature retention (% returning)
- Cross-feature usage patterns

**Views**:

- Bar chart: Feature usage by week
- Funnel: Feature adoption flow
- Cohort: Feature retention by signup cohort

**Refresh**: Daily
**Audience**: Product team

---

### Dashboard 3: Growth (Acquisition & Conversion)

**Purpose**: Optimize acquisition channels and conversion

**Metrics**:

- Signups by source
- Conversion rates by funnel stage
- Cost per acquisition (CPA) by channel
- Lifetime value (LTV) by cohort

**Views**:

- Funnel: Signup to activation
- Funnel: Free to paid
- Table: Channel performance (signups, conversion, CPA)
- Cohort: LTV by acquisition month

**Refresh**: Daily
**Audience**: Growth, marketing team

---

### Dashboard 4: Engineering (Performance & Errors)

**Purpose**: Monitor system health and performance

**Metrics**:

- Error rate (by type)
- Page load times (p50, p95, p99)
- API response times (by endpoint)
- Uptime/availability

**Views**:

- Line chart: Error rate over time
- Histogram: Page load distribution
- Table: Slowest endpoints
- Alert list: Active issues

**Refresh**: Real-time
**Audience**: Engineering team

---

_[Define 4-6 key dashboards]_

---

## AARRR Metrics Mapping

### Acquisition

**How users find us**

| Metric             | Event/Calculation                    | Target      |
| ------------------ | ------------------------------------ | ----------- |
| Traffic            | Pageviews                            | [X]/month   |
| Signup rate        | `user_signed_up` / Visitors          | [X%]        |
| Signups by channel | `user_signed_up` (group by `source`) | [Breakdown] |

### Activation

**First valuable experience**

| Metric                | Event/Calculation                             | Target    |
| --------------------- | --------------------------------------------- | --------- |
| Activation rate       | `[core_action]` within 7 days / Signups       | [X%]      |
| Time to activation    | Median time from signup to [core_action]      | [X] hours |
| Onboarding completion | `onboarding_completed` / `onboarding_started` | [X%]      |

### Retention

**Users coming back**

| Metric              | Event/Calculation                         | Target |
| ------------------- | ----------------------------------------- | ------ |
| D1 retention        | Active day 1 / Signups                    | [X%]   |
| D7 retention        | Active day 7 / Signups                    | [X%]   |
| D30 retention       | Active day 30 / Signups                   | [X%]   |
| Weekly active users | Unique users with [action] in past 7 days | [X]    |

### Revenue

**Monetization**

| Metric             | Event/Calculation                | Target |
| ------------------ | -------------------------------- | ------ |
| Conversion to paid | `subscription_created` / Signups | [X%]   |
| MRR                | Sum of recurring revenue         | $[X]   |
| ARPU               | MRR / Active users               | $[X]   |
| LTV                | ARPU × Avg lifetime (months)     | $[X]   |

### Referral

**Viral growth**

| Metric            | Event/Calculation                           | Target |
| ----------------- | ------------------------------------------- | ------ |
| Invite rate       | `user_invited_teammate` / Active users      | [X%]   |
| Invite acceptance | Signups with `source=invite` / Invites sent | [X%]   |
| Viral coefficient | Invites × Acceptance rate                   | [X]    |

---

## A/B Testing Roadmap

### Experiment 1: [Hypothesis - e.g., "Shorter signup increases conversion"]

**Hypothesis**: [Clear hypothesis]

**Metric**: [Primary metric - what you're optimizing]

**Variants**:

- **Control (A)**: [Current experience]
- **Variant (B)**: [Changed experience]

**Sample size needed**: [Calculate based on traffic and effect size]

**Duration**: [1-2 weeks minimum]

**Success criteria**: [X% improvement with 95% confidence]

**Priority**: [High/Medium/Low]

---

### Experiment 2: [Hypothesis]

[Repeat structure]

---

_[Plan 8-12 experiments for next 6 months]_

---

## Tool Recommendations

### Analytics Stack

**Primary analytics**: [Amplitude / Mixpanel / Heap / PostHog]

- **Why**: [Reasoning]
- **Cost**: $[X]/month at [volume]
- **Pros**: [Benefit 1, 2, 3]
- **Cons**: [Limitation 1, 2]

**Event collection**: [Segment / RudderStack / Custom]

- **Why**: [Reasoning]
- **Cost**: $[X]/month
- **Pros**: [Benefits]
- **Cons**: [Limitations]

**Product analytics**: [Already covered / Add tool]

**Session replay**: [FullStory / LogRocket / Hotjar]

- **Why**: [Reasoning]
- **Cost**: $[X]/month
- **Use case**: [When to use]

**A/B testing**: [Optimizely / LaunchDarkly / GrowthBook / Custom]

- **Why**: [Reasoning]
- **Cost**: $[X]/month

**Warehouse** (optional): [Snowflake / BigQuery / Redshift]

- **Why**: [If needed for advanced analysis]
- **Cost**: $[X]/month

### Tool Setup Guide

#### 1. Segment (Event Collection Layer)

**Installation**:

```javascript
// Example implementation
<script>
  !function(){var analytics=window.analytics=window.analytics||[];
  // ... Segment snippet
}();
</script>
```

**Configuration**:

- Source: [Web / Mobile / Server]
- Destinations: [Amplitude, ...]

---

#### 2. Amplitude (Product Analytics)

**Setup**:

1. Create project in Amplitude
2. Get API key
3. Configure Segment destination
4. Set up tracking plan

**Key configurations**:

- User identification: [How you identify users]
- Event properties: [Standard properties]
- User properties: [Standard properties]

---

_[Include setup for each tool]_

---

## Privacy and Compliance

### Data Collection Principles

**What we collect**:

- ✅ [Type 1 - e.g., "Product usage events"]
- ✅ [Type 2 - e.g., "Anonymous behavior data"]
- ✅ [Type 3]

**What we don't collect**:

- ❌ [Type 1 - e.g., "Keystroke logging"]
- ❌ [Type 2 - e.g., "Personal messages/content"]
- ❌ [Type 3]

### GDPR Compliance

- [ ] Cookie consent mechanism
- [ ] Right to access (data export)
- [ ] Right to be forgotten (data deletion)
- [ ] Data processing agreement with vendors
- [ ] Privacy policy updated
- [ ] Data retention policy (e.g., 24 months)

### CCPA Compliance

- [ ] "Do Not Sell My Data" option
- [ ] Privacy policy disclosures
- [ ] Data deletion on request

### Data Security

- [ ] PII encrypted at rest and in transit
- [ ] Access controls (role-based)
- [ ] Audit logging
- [ ] Regular security reviews

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Track North Star and critical path

**Events to implement**:

- [ ] User lifecycle (signup, login, activation)
- [ ] Core action events (the [X] actions that matter most)
- [ ] Conversion events (pricing viewed, subscription created)

**Deliverables**:

- [ ] Segment installed and configured
- [ ] Primary analytics tool (Amplitude) connected
- [ ] North Star dashboard created
- [ ] Activation funnel tracking

**Validate**: Can we measure North Star? Can we see activation funnel?

---

### Phase 2: Feature Usage (Weeks 3-4)

**Goal**: Understand feature adoption and retention

**Events to implement**:

- [ ] All core feature events (created, viewed, edited, deleted)
- [ ] Feature usage by cohort
- [ ] User properties (behavioral)

**Deliverables**:

- [ ] Product dashboard created
- [ ] Feature adoption tracking
- [ ] Cohort definitions set up

**Validate**: Can we see which features users love? Can we identify power users?

---

### Phase 3: Growth & Optimization (Weeks 5-8)

**Goal**: Optimize acquisition and conversion

**Events to implement**:

- [ ] Detailed funnel events (every drop-off point)
- [ ] Attribution tracking (source, campaign)
- [ ] A/B test event tracking

**Deliverables**:

- [ ] Growth dashboard created
- [ ] All conversion funnels tracked
- [ ] A/B testing infrastructure
- [ ] Session replay tool installed

**Validate**: Can we optimize each funnel stage? Can we run experiments?

---

### Phase 4: Advanced Analytics (Week 9+)

**Goal**: Deep insights and predictions

**Events to implement**:

- [ ] Performance and error tracking
- [ ] Advanced user properties
- [ ] Predictive cohorts

**Deliverables**:

- [ ] Engineering dashboard
- [ ] Churn prediction model
- [ ] LTV calculations
- [ ] Data warehouse (if needed)

**Validate**: Can we predict churn? Can we calculate true LTV?

---

## Validation Checklist

Before launch, verify:

### Event Tracking

- [ ] All P0 events fire correctly
- [ ] Event properties are accurate
- [ ] User properties update correctly
- [ ] Events appear in analytics tool within [X] minutes

### Dashboards

- [ ] North Star dashboard shows real data
- [ ] Funnels calculate correctly
- [ ] Cohorts segment properly
- [ ] All dashboards accessible to right teams

### Privacy

- [ ] Cookie consent works
- [ ] Privacy policy updated
- [ ] Data deletion process tested
- [ ] PII handling verified

### Team Readiness

- [ ] Team trained on dashboards
- [ ] Documentation complete
- [ ] Event tracking guide shared with eng
- [ ] Analytics point person designated

---

## Next Steps

- [ ] Review with data/product team
- [ ] Get engineering to size implementation
- [ ] Set up analytics tools accounts
- [ ] Begin Phase 1 implementation
- [ ] Schedule weekly analytics review meeting
- [ ] Plan first experiment from A/B testing roadmap

---

## Document Control

**Status**: [Draft/In Progress/Implemented]
**Last Updated**: [Date]
**Next Review**: [Quarterly]
**Owner**: [Name/Role - Product/Data]
**Contributors**: [Engineering, Growth, Product]
