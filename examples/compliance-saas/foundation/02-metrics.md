# Success Metrics: Compliance Assessment Platform

> **Context**: This is a completed example. North Star derived from mission outcome.

---

## North Star Metric

**Metric**: Weekly Active Assessments

**Definition**: Number of compliance assessments completed per week by active teams (completed = user reviewed results, not just started)

**Why This**: Directly measures mission outcome (compliance officers assessing documents faster). Each assessment represents 2-4 hours of time saved.

**Current**: 450 assessments/week
**Target**: 2,500 assessments/week by Q2 end

---

## Input Metrics (Drive North Star)

### 1. Active Teams
**Definition**: Teams with at least one assessment this week
**Why It Matters**: More active teams = more assessments
**Current**: 45 teams
**Target**: 200 teams
**Lever**: Improve activation (signup → first assessment), reduce churn

### 2. Assessments per Team
**Definition**: Average assessments completed per active team per week
**Why It Matters**: Higher usage per team = better habit formation
**Current**: 10 assessments/week
**Target**: 15 assessments/week
**Lever**: Batch processing, saved frameworks, integrations

### 3. Assessment Completion Rate
**Definition**: % of started assessments that user reviews results for
**Why It Matters**: Incomplete assessments indicate friction or lack of value
**Current**: 82%
**Target**: 90%
**Lever**: Faster processing, better result presentation, progress indicators

**Formula**: `Weekly Active Assessments = Active Teams × Assessments per Team × Completion Rate`

---

## Health Metrics (Guardrails)

### Acquisition Health
- **Signup Quality**: 55% activate within 24h (target: >60%)
- **Channel Mix**: 40% organic, 35% referral, 25% paid (balanced)

### Engagement Health
- **Weekly Active Users**: 180 (target: >400)
- **Sessions per User**: 4.2 per week (target: >5)
- **Time to First Assessment**: 8 minutes median (target: <5 min)

### Retention Health
- **D7 Retention**: 68% (target: >70%)
- **D30 Retention**: 52% (target: >60%)
- **Monthly Churn**: 6% (target: <5%)

### Revenue Health
- **MRR**: $18,400 (target: $75,000 by Q2 end)
- **ARPU**: $205/month (growing)
- **LTV:CAC**: 2.8:1 (target: >3:1)

### Product Health
- **Assessment Success Rate**: 96% (target: >95%)
- **P95 Processing Time**: 78 seconds (target: <60 sec)
- **Error Rate**: 1.2% (target: <1%)
- **NPS**: 58 (target: >60)

---

## Counter-Metrics (Will Not Sacrifice)

We will NOT improve Weekly Active Assessments by degrading:

### 1. Assessment Accuracy
**Definition**: % of flagged issues users mark as "relevant/helpful"
**Threshold**: Must stay above 70%
**Why Protected**: Inaccurate assessments destroy trust, force manual review

### 2. User Satisfaction (NPS)
**Definition**: Net Promoter Score
**Threshold**: Must stay above 50
**Why Protected**: Growth through referrals requires satisfied users

### 3. Error Rate
**Definition**: % of assessments that fail or produce errors
**Threshold**: Must stay below 2%
**Why Protected**: Reliability is critical for compliance use case

---

## MVP Success Criteria (Achieved ✓)

- [✓] 50 activated users
- [✓] 60% activation rate (signup → first assessment)
- [✓] 45% D7 retention
- [✓] NPS > 45

## Current Stage Goals (Growth - Next 90 Days)

- [ ] 2,500 weekly active assessments
- [ ] 200 active teams
- [ ] 60% D30 retention
- [ ] $75K MRR
- [ ] NPS > 60

---

## Metric Tracking

### Weekly Review Questions
1. Is North Star trending toward 2,500/week? (Need 15% week-over-week growth)
2. Which input metric needs attention? (Currently: Active Teams - need acquisition)
3. Are health metrics within ranges? (Watch: D30 retention slipping)
4. Any counter-metric concerns? (NPS stable, accuracy good)
5. What did we learn this week? (Users want batch processing - high leverage feature)

---

**Connection to Journey**:
- Time to First Assessment → Journey Step 1-2 optimization
- Completion Rate → Journey Step 3-4 quality
- Retention → Overall journey value delivery

**Connection to Monetization**:
- We charge $0.10 per assessment
- 2,500 assessments/week = 10,000/month = $1,000/month per team
- Target 200 teams = $200K MRR potential
