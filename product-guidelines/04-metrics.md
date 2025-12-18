# Success Metrics: Qteria

> **Derived from**: product-guidelines/03-mission.md (North Star = mission outcome quantified)

---

## North Star Metric

**Metric**: Active Assessments Per Month

**Definition**: Total number of document validation assessments completed by paying customers each month where AI generated pass/fail results with evidence

**Why This**:

- Directly measures mission fulfillment (validating documents faster through AI)
- Captures actual value delivery (each assessment = 1-2 days saved, $150-300 value to customer)
- Leading indicator of retention (customers running assessments monthly are getting value)
- Scales with revenue (more customers → more assessments → more value delivered)
- Aligns with user success (Project Handlers measure success by assessments completed, not logins)

**Current**: 0 (pre-launch)

**Targets**:

- **Q2 2026** (TÜV SÜD pilot): 100 assessments/month
- **Q4 2026** (TÜV SÜD production): 500 assessments/month
- **Q4 2027** (5 customers): 2,000 assessments/month (400 per customer average)
- **2030 vision**: 10,000+ assessments/month (20-50 customers)

---

## Input Metrics (Drive North Star)

### 1. Active Customers

**Definition**: Number of notified bodies with at least one assessment run in the past 30 days

**Why It Matters**: More customers → more assessments. Primary growth lever.

**Current**: 0

**Target**:

- Q2 2026: 1 (TÜV SÜD)
- Q4 2026: 1 (TÜV SÜD production)
- Q4 2027: 5 customers
- 2030: 20-50 customers

**Lever**: Sales & customer success (land TÜV SÜD, use as reference to sell BSI, DEKRA, TÜV Rheinland)

---

### 2. Assessments Per Customer Per Month

**Definition**: Average number of assessments completed per active customer each month

**Why It Matters**: Measures depth of usage (sticky vs. sporadic). Healthy customers run 300-500/month (15-20/day).

**Current**: 0

**Target**:

- Q2 2026: 100/month (TÜV SÜD pilot, limited rollout)
- Q4 2026: 400/month (TÜV SÜD production, broader team adoption)
- Q4 2027: 400/month average across 5 customers
- 2030: 500/month (daily usage habit)

**Lever**:

- Onboarding quality (teach Process Managers to create workflows fast)
- Workflow template library (pre-built for common certification types)
- Speed (< 10 min results → users run more assessments)
- Accuracy (< 5% false positives → users trust results, don't double-check manually)

---

### 3. Assessment Completion Rate

**Definition**: % of assessments started that reach "Results Delivered" stage (not abandoned mid-process)

**Why It Matters**: Measures product reliability and UX quality. Low completion = users hitting errors or giving up.

**Current**: 0

**Target**: 95%+ (5% allowed for user error, accidental starts, test runs)

**Lever**:

- Reduce errors (PDF parsing failures, AI timeouts)
- Clear progress indicators (users know assessment is running, not stuck)
- Fast processing (<10 min, ideally <5 min → users wait instead of abandoning)

---

### 4. New Workflows Created Per Month

**Definition**: Number of new validation workflows created by Process Managers each month (across all customers)

**Why It Matters**: Workflows enable assessments. More workflows = more coverage = more usage. Healthy growth signal.

**Current**: 0

**Target**:

- Q2 2026: 5-10 workflows (TÜV SÜD pilot, experimenting with different certification types)
- Q4 2026: 10-15 workflows (TÜV SÜD refining, adding new product categories)
- Q4 2027: 50 workflows total (10 per customer average)
- 2030: 200+ workflows (reusable library, marketplace foundation)

**Lever**:

- Workflow creation UX (<30 min to create, simple interface)
- Templates (pre-built for Medical Device Class II, ISO 13485, etc.)
- Process Manager training (white-glove onboarding)

---

### 5. Assessment Success Rate (AI Accuracy)

**Definition**: % of assessments where AI results are confirmed accurate by user feedback (no false positive/negative flags)

**Why It Matters**: Trust metric. Low accuracy → users abandon tool. Strategic Goal 2 requires <5% false positive, <1% false negative.

**Current**: 0

**Target**:

- Q2 2026: 90%+ (pilot, learning phase)
- Q4 2026: 95%+ (<5% false positive, <1% false negative)
- Q4 2027: 97%+
- 2030: 98%+ (continuous improvement via feedback loop)

**Lever**:

- AI model quality (Claude Sonnet → fine-tuned if needed)
- Prompt engineering (clear criteria definitions)
- Feedback loop (users flag incorrect results, model improves)
- Confidence scoring (yellow "uncertain" for edge cases)

---

**Formula**:

```
Active Assessments Per Month =
  Active Customers
  × Assessments Per Customer Per Month
  × Completion Rate
```

**Example (Q4 2027)**:

```
2,000 = 5 customers × 400 assessments/customer × 100% completion rate
```

---

## Health Metrics (Guardrails)

### Engagement Health

- **Weekly Active Users (Project Handlers)**: Target 5+ by Q2 2026 (TÜV SÜD pilot), 25+ by Q4 2027 (5 customers × 5 users each)
- **Sessions Per User Per Week**: Target 3-5 sessions (daily usage during work week)
- **Time to First Assessment**: <1 hour from signup (activation metric)

### Retention Health

- **Day 7 Retention**: 80%+ (users who create workflow return within 7 days to run assessment)
- **Day 30 Retention**: 70%+ (monthly active usage)
- **Customer Retention (Annual)**: 100% target (enterprise B2B, high switching cost, relationship-driven)

### Product Health

- **Error Rate**: <2% (assessments fail due to technical error, not user error)
- **P95 Assessment Processing Time**: <10 minutes (95% of assessments complete in <10 min)
- **Uptime**: 99.9% (critical for enterprise trust)
- **NPS**: 50+ (world-class B2B SaaS)

### Revenue Health

- **MRR**: $0 → $2.5K (Q2 2026) → $12.5K (Q4 2027)
- **ARR**: $0 → $30K (Q2 2026) → $150K (Q4 2027)
- **Net Revenue Retention**: 100%+ (no churn, potential expansion to more users/workflows)
- **CAC Payback Period**: <12 months (enterprise sales cycle long, but LTV high)

---

## Counter-Metrics (Will Not Sacrifice)

We will NOT improve Active Assessments by degrading:

### 1. Assessment Accuracy (False Positive/Negative Rate)

**Definition**: % of assessments with AI errors (false positives: wrongly flagged as fail; false negatives: missed issues)

**Threshold**: Must stay below 5% false positive, below 1% false negative

**Why Protected**: Mission promises evidence-based validation. Users trust AI because it's accurate. Sacrificing accuracy for speed destroys trust permanently. Better to run 100 accurate assessments than 1,000 inaccurate ones.

**Trade-off Example**: Don't ship faster AI model if it increases false negatives from 0.5% → 2%. Certification Person catching missed issues = lost customer.

---

### 2. Data Privacy & Security

**Definition**: Zero customer data breaches, zero unauthorized AI training on customer documents

**Threshold**: Zero incidents (non-negotiable)

**Why Protected**: Notified bodies handle confidential certification documents. One data breach = reputation destroyed, SOC2 cert revoked, all customers churn. Strategic Goal 4 (data security) is existential.

**Trade-off Example**: Don't use cheaper AI provider if they won't sign zero-retention agreement. Pay 2x more for Claude enterprise vs. risk data leakage.

---

### 3. User Experience Simplicity

**Definition**: Time to create first workflow (<30 min), time to first assessment (<1 hour)

**Threshold**: Must stay below these targets (not regress)

**Why Protected**: Differentiation is "exceptional UX" and "simplicity over features." Adding features that slow workflow creation violates product principle and mission test.

**Trade-off Example**: Don't add "advanced criteria builder with 50 options" if it increases workflow creation time from 20 min → 60 min. Say no to feature creep.

---

### 4. Customer Relationship Quality (White-Glove Support)

**Definition**: Response time to customer questions (<24 hours), relationship manager availability

**Threshold**: Maintain dedicated relationship manager per customer (not ticket queue)

**Why Protected**: Differentiation is white-glove support. Scaling to ticket system to handle more volume destroys competitive advantage.

**Trade-off Example**: Don't hire 20 customers in one quarter if it means degrading support quality. Cap at 5-10 new customers/year to maintain relationship quality.

---

## Metric Tracking & Reporting

**Daily Dashboard** (for founder):

- Active Assessments (today)
- Assessment Success Rate (last 7 days)
- Error Rate (last 24 hours)
- Uptime (last 24 hours)

**Weekly Review** (Monday morning):

- Active Assessments (last 7 days trend)
- Active Users (WAU)
- New Workflows Created
- Customer Health Scores (usage drop-offs, support tickets)

**Monthly Review** (First Friday):

- North Star: Active Assessments Per Month (vs. target)
- Input Metrics: Active Customers, Assessments/Customer, Completion Rate, New Workflows, AI Accuracy
- Health Metrics: Retention, NPS, Error Rate, Uptime
- Revenue Metrics: MRR, ARR, Net Revenue Retention
- Counter-Metrics: Accuracy, Privacy Incidents, UX Simplicity, Support Quality

**Quarterly Strategic Review**:

- Progress toward strategic goals (Goal 1-5)
- North Star trend analysis (growth rate, plateau signals)
- Input metric deep-dives (which levers working, which stuck)
- Counter-metric validation (sacrificed anything we shouldn't have?)

---

**Connection to Journey**:

- **Active Assessments** measures **Step 3** (AI validation completed) - core journey value
- **Assessment Completion Rate** measures **Step 2 → Step 3** funnel (upload docs → results delivered)
- **New Workflows Created** measures **Step 1** (Process Manager setup) - enabler of assessments
- **Assessment Success Rate** measures **Step 3 quality** (evidence-based results users trust)
- **Day 7/30 Retention** measures **Step 4 → Step 3 loop** (re-run assessments, habit formation)

**Connection to Monetization**:

- North Star growth drives revenue because more Active Assessments = more value delivered = higher retention + expansion
- Active Customers × $30K/year = ARR (direct correlation)
- Assessments Per Customer measures product stickiness (high usage = renewal likelihood)
- Health metrics (NPS, retention) predict churn risk and expansion opportunity

**Connection to Mission**:

- "Validate documents 400x faster" → measured by Active Assessments (mission in action)
- "Evidence-based results" → measured by Assessment Success Rate (accuracy of AI)
- "TIC notified bodies" → measured by Active Customers (who we serve)
