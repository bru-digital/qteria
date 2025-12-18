---
description: POST-CASCADE - Create comprehensive financial model with unit economics, revenue projections, and scenario planning
---

# POST-CASCADE: Create Financial Model

This is a **post-core extension** that creates a comprehensive financial model grounded in your user journey, market analysis, and business strategy. Run this AFTER you've completed Session 4 (tactical foundation) to model unit economics, revenue projections, cost structure, and profitability pathways.

## When to Run This

**Run AFTER Session 4+** when you have:

- ✅ User journey defined (`product-guidelines/00-user-journey.md`)
- ✅ Product strategy validated (`product-guidelines/01-product-strategy.md`)
- ✅ Metrics established (`product-guidelines/04-metrics.md`)
- ✅ Monetization model defined (`product-guidelines/04-monetization.md`)

**Ideally after additional strategy work** when you also have:

- ✅ Growth strategy created (`product-guidelines/growth-strategy.md`)
- ✅ Tech stack chosen (`product-guidelines/02-tech-stack.md`)
- So cost structure and customer acquisition costs are grounded in reality

**Skip this** if:

- You're building a pure passion project (no monetization intent)
- You're pre-revenue and need to focus purely on product validation
- You have a finance team that handles financial modeling

## Your Role

You are a financial strategist creating a data-driven financial model. Your job is to:

1. **Analyze** unit economics (CAC, LTV, payback period, margins)
2. **Project** revenue growth based on acquisition channels and conversion rates
3. **Model** cost structure (fixed and variable costs)
4. **Plan** profitability pathways and funding requirements
5. **Create** scenario analyses (conservative, realistic, aggressive)
6. **Identify** key assumptions and sensitivities
7. **Define** financial milestones and success metrics

## Critical Philosophy

**Financial models must be grounded in journey economics and validated with market data.**

- Unit economics → Derived from journey value delivery and acquisition channels
- Revenue projections → Based on realistic conversion rates and growth loops
- Cost structure → Informed by tech stack choices and team requirements
- Scenarios → Test assumptions about market response and execution
- Assumptions → Explicitly documented with validation criteria

## Cascade Inputs

This command READS previous outputs to ground financial projections in reality:

1. **Read the user journey**:

   ```bash
   Read product-guidelines/00-user-journey.md
   ```

   - What economic value does journey deliver? (ROI basis for pricing)
   - What's the journey complexity? (affects conversion rates)
   - What's the time-to-value? (affects activation and retention)

2. **Read the product strategy**:

   ```bash
   Read product-guidelines/01-product-strategy.md
   ```

   - What's the TAM/SAM/SOM? (market size constraints)
   - Who are the competitors? (pricing benchmarks)
   - What's the market positioning? (premium vs value pricing)

3. **Read the tech stack** (if available):

   ```bash
   Read product-guidelines/02-tech-stack.md
   ```

   - What are the infrastructure costs? (AWS, hosting, SaaS tools)
   - What's the team size/composition? (salary costs)
   - What are the per-user variable costs? (API calls, storage, compute)

4. **Read the metrics**:

   ```bash
   Read product-guidelines/04-metrics.md
   ```

   - What's the North Star metric? (ties to revenue)
   - What are conversion rates? (signup→activation→paid)
   - What's the expected retention? (affects LTV)

5. **Read the monetization model**:

   ```bash
   Read product-guidelines/04-monetization.md
   ```

   - What's the pricing structure? (Free/Paid tiers, enterprise)
   - What's the value metric? (per-user, per-usage, per-outcome)
   - What's the expected ARPU? (Average Revenue Per User)

6. **Read the growth strategy** (if available):

   ```bash
   Read product-guidelines/growth-strategy.md
   ```

   - What are the acquisition channels? (affects CAC)
   - What's the growth model? (viral, content, sales)
   - What are the growth loop assumptions? (viral coefficient, cycle time)

Your financial model connects journey economics → unit economics → projections → profitability.

## Process

### Step 1: Read All Inputs

Use the Read tool to read all cascade inputs listed above.

**Extract key financial drivers**:

- Journey ROI (value delivered vs. price)
- Market size (TAM/SAM/SOM)
- Pricing tiers and ARPU estimates
- Conversion funnel metrics
- Retention/churn assumptions
- Growth channels and CAC estimates
- Tech infrastructure costs

### Step 2: Read Template Structure

```bash
Read templates/financial-model-template.md
```

### Step 3: Calculate Unit Economics

**Unit economics are the foundation** - they determine if the business can scale profitably.

#### 3.1: Calculate Customer Acquisition Cost (CAC)

**From growth strategy** (or estimate if not available):

```
For EACH acquisition channel:
  Channel CAC = (Marketing spend + Sales spend) / New customers acquired

Blended CAC = Weighted average across all channels
```

**Decision tree for CAC estimation** (if growth strategy doesn't exist):

```
IF B2B SaaS with complex sales (>$10k ACV)
  → CAC typically 1-3x of first-year ACV
  → Includes: SDR salary, AE salary, marketing spend
  → Example: $5k-$15k per customer

ELSE IF B2B SaaS with self-serve (<$10k ACV)
  → CAC typically 20-40% of first-year revenue
  → Includes: Content marketing, paid ads, product-led growth
  → Example: $500-$2k per customer

ELSE IF B2C with paid acquisition
  → CAC typically $10-$100 depending on LTV
  → Includes: Social ads, SEM, influencer marketing
  → Example: $20-$80 per customer

ELSE IF product-led or viral growth
  → CAC typically $5-$50
  → Includes: Infrastructure costs, referral incentives
  → Example: $10-$30 per customer
```

**Validation criteria**:

- [ ] CAC is based on realistic channel costs (market benchmarks)
- [ ] Includes all costs (marketing, sales, tools, not just ad spend)
- [ ] Blended CAC accounts for channel mix
- [ ] Documented assumptions for each channel

#### 3.2: Calculate Lifetime Value (LTV)

**From monetization and metrics**:

```
LTV = (ARPU × Gross Margin) / Churn Rate

Where:
- ARPU = Average Revenue Per User (monthly or annual)
- Gross Margin = (Revenue - COGS) / Revenue
- Churn Rate = % of customers who cancel per month/year
```

**Component breakdown**:

1. **ARPU (Average Revenue Per User)**:

   ```
   From monetization tiers:
   - % of users on Free tier → $0
   - % of users on Starter tier → $X/month
   - % of users on Pro tier → $Y/month
   - % of users on Enterprise tier → $Z/month

   Blended ARPU = Weighted average
   ```

2. **Gross Margin**:

   ```
   Revenue:             100%
   - Hosting costs:     -5-15%  (from tech stack)
   - API costs:         -2-10%  (third-party services)
   - Payment fees:      -3%     (Stripe, PayPal)
   - Support costs:     -5-10%  (customer support team)
   ────────────────────────────
   Gross Margin:        70-85%  (typical for SaaS)
   ```

3. **Churn Rate**:

   ```
   From metrics (or industry benchmarks):

   B2B SaaS:
   - Annual churn:    5-7%  (low)   → Lifetime: 14-20 years
   - Annual churn:    10-15% (med)  → Lifetime: 6-10 years
   - Annual churn:    20-30% (high) → Lifetime: 3-5 years

   B2C SaaS:
   - Monthly churn:   3-5%  (low)   → Lifetime: 20-33 months
   - Monthly churn:   5-10% (med)   → Lifetime: 10-20 months
   - Monthly churn:   10-20% (high) → Lifetime: 5-10 months
   ```

**Example calculation** (B2B SaaS):

```
ARPU:              $100/month
Gross Margin:      80%
Monthly Churn:     2% (24% annual)
Customer Lifetime: 1 / 0.02 = 50 months

LTV = ($100 × 0.80) × 50 months = $4,000
```

**Validation criteria**:

- [ ] ARPU reflects realistic tier distribution (not 100% enterprise)
- [ ] Gross margin accounts for ALL variable costs
- [ ] Churn rate is documented with source (metrics, assumptions, benchmarks)
- [ ] LTV calculation is clearly shown step-by-step

#### 3.3: Validate LTV:CAC Ratio

**Industry benchmarks**:

```
LTV:CAC Ratio     Interpretation
─────────────────────────────────────────────
< 1:1             Unsustainable (losing money per customer)
1:1 - 3:1         Concerning (barely profitable)
3:1               Minimum viable (break-even after growth)
3:1 - 5:1         Healthy (sustainable growth)
5:1+              Excellent (very profitable, underspending on growth)
10:1+             May be underspending on acquisition
```

**If LTV:CAC < 3:1**, identify the lever to pull:

- Increase LTV: Reduce churn, increase ARPU (upsells, usage), improve margins
- Decrease CAC: Optimize channels, improve conversion rates, build growth loops
- Adjust business model: Change pricing, target different segment, pivot

**Payback period** (months to recover CAC):

```
Payback Period = CAC / (ARPU × Gross Margin)

Benchmarks:
- < 12 months: Excellent (VC-backable)
- 12-18 months: Good (cashflow manageable)
- 18-24 months: Concerning (requires significant capital)
- > 24 months: Problematic (very capital intensive)
```

**Validation criteria**:

- [ ] LTV:CAC ratio is ≥ 3:1 (or path to 3:1 documented)
- [ ] Payback period is ≤ 18 months (or funding plan exists)
- [ ] If ratios don't pass, improvement plan is documented

### Step 4: Model Revenue Projections

**Revenue projections flow from acquisition, conversion, and retention.**

#### 4.1: Build Customer Acquisition Model

**For EACH acquisition channel** (from growth strategy):

```
Month 1: [X] signups × [Y%] conversion to paid = [Z] new customers
Month 2: [X+growth%] signups × [Y%] conversion = [Z] new customers
...
Month 12: [X signups] × [Y%] = [Z] new customers

Total new customers Year 1: [Sum]
```

**Growth curve assumptions**:

```
IF SEO/Content-driven
  → Slow start (3-6 months), then compounds
  → Growth: 5-10% MoM once traction hits

ELSE IF Paid acquisition
  → Linear growth tied to ad spend
  → Growth: Budget × ROI consistency

ELSE IF Viral/Product-led
  → Exponential if viral coefficient > 1
  → Growth: (Users × Viral Coefficient) ^ Time

ELSE IF Sales-driven
  → Linear tied to sales team size
  → Growth: Reps × Quota / Deal Size
```

**Example** (Content + Paid hybrid):

```
Month 1:   100 signups (50 paid ads, 50 content)
Month 3:   250 signups (100 paid ads, 150 content - SEO ramping)
Month 6:   600 signups (150 paid ads, 450 content - SEO working)
Month 12: 1,500 signups (200 paid ads, 1,300 content - SEO mature)

Conversion to paid: 10%
New customers Month 12: 150
Cumulative customers: 800 (with churn factored in)
```

#### 4.2: Model Revenue Streams

**Monthly Recurring Revenue (MRR)**:

```
MRR = Total Active Customers × Blended ARPU

Month X MRR = Previous MRR + New MRR - Churned MRR + Expansion MRR

Where:
- New MRR: New customers × ARPU
- Churned MRR: Lost customers × their ARPU
- Expansion MRR: Upsells/cross-sells (typically 10-20% of MRR)
```

**Annual projections** (Years 1-3):

```
Year 1: Build foundation
- Focus: Product-market fit, initial customers
- Target: $X MRR → $Y MRR (end of year)
- ARR (Annual Recurring Revenue): MRR × 12

Year 2: Scale growth
- Focus: Channel optimization, team expansion
- Target: $Y MRR → $Z MRR
- Growth: X% YoY

Year 3: Accelerate
- Focus: Market leadership, profitability
- Target: $Z MRR → $W MRR
- Growth: Y% YoY
```

**Validation criteria**:

- [ ] Growth rates are grounded in channel capacity (not fantasy)
- [ ] Churn is factored into projections (not just new customers)
- [ ] Expansion revenue is included (upsells, cross-sells)
- [ ] Revenue targets align with market size (not exceeding SAM)

### Step 5: Model Cost Structure

**Costs fall into two categories**: Fixed (independent of customers) and Variable (scales with customers).

#### 5.1: Variable Costs (Cost of Goods Sold - COGS)

**Per-customer or per-usage costs**:

```
Infrastructure (from tech stack):
- Hosting/compute:    $X per customer per month
- Database storage:   $Y per customer per month
- API costs:          $Z per customer per month
- CDN/bandwidth:      $W per customer per month

Customer Success:
- Support costs:      $A per customer per month (staff allocation)
- Onboarding:         $B per new customer (one-time)

Payment Processing:
- Transaction fees:   3% of revenue

Total Variable Cost per Customer: $[Sum]
Gross Margin: (ARPU - Variable Cost) / ARPU = X%
```

**Example** (B2B SaaS):

```
ARPU:                 $100/month
Hosting:              -$8
Third-party APIs:     -$5
Support (allocated):  -$7
Payment fees:         -$3 (3% of $100)
────────────────────────────────
Total Variable Cost:  $23
Gross Margin:         77%
```

#### 5.2: Fixed Costs (Operating Expenses)

**Monthly operating expenses** (independent of customer count):

```
Personnel:
- Engineering:        [X] people × $[Y] = $[Z]/month
- Product/Design:     [X] people × $[Y] = $[Z]/month
- Sales/Marketing:    [X] people × $[Y] = $[Z]/month
- Operations:         [X] people × $[Y] = $[Z]/month
────────────────────────────────
Total Personnel:      $[Sum]/month

Software/Tools:
- Development tools:  $X/month
- Marketing tools:    $Y/month
- Productivity:       $Z/month
────────────────────────────────
Total SaaS tools:     $[Sum]/month

Marketing Budget:
- Paid advertising:   $X/month
- Content creation:   $Y/month
- Events/community:   $Z/month
────────────────────────────────
Total Marketing:      $[Sum]/month

Office/Admin:
- Office space:       $X/month (or $0 if remote)
- Legal/accounting:   $Y/month
- Insurance:          $Z/month
────────────────────────────────
Total Admin:          $[Sum]/month

───────────────────────────────────────────
TOTAL FIXED COSTS:    $[Sum]/month
```

**Scaling assumptions**:

```
Stage 1 (Months 0-12): MVP team
- 2-3 engineers
- 1 founder/PM
- Contract design/marketing
- Fixed costs: $30-50k/month

Stage 2 (Months 12-24): Growth team
- 5-7 engineers
- 2-3 growth/sales
- 1 designer
- Fixed costs: $80-120k/month

Stage 3 (Months 24-36): Scale team
- 10-15 engineers
- 5-8 sales/marketing
- 2-3 product/design
- Fixed costs: $150-250k/month
```

**Validation criteria**:

- [ ] Variable costs are tied to tech stack choices
- [ ] Fixed costs reflect realistic salaries for market/location
- [ ] Team growth tied to revenue milestones (not premature hiring)
- [ ] Marketing budget aligned with CAC targets

### Step 6: Calculate Profitability Pathways

**Profitability** = Revenue - Variable Costs - Fixed Costs

#### 6.1: Break-Even Analysis

**Break-even point** (when revenue covers all costs):

```
Break-even Customers = Fixed Costs / (ARPU × Gross Margin - Variable Cost per Customer)

Or simplified:
Break-even Customers = Fixed Costs / Contribution Margin per Customer
```

**Example**:

```
Fixed Costs:          $50,000/month
ARPU:                 $100/month
Variable Cost:        $23/month
Contribution Margin:  $77/month

Break-even = $50,000 / $77 = 649 customers

At 10% conversion and 2% churn:
Need 6,490+ signups/month to break even
```

**Timeline to break-even**:

```
IF current growth trajectory
  → Month X: Reach break-even customers
  → Month Y: Reach cashflow positive (including past burn)
```

#### 6.2: Funding Requirements

**Calculate total capital needed**:

```
For EACH month until profitability:
  Burn Rate = Fixed Costs + Variable Costs - Revenue

Total Capital Needed = Sum of all negative months + Runway buffer (6 months)
```

**Funding strategy decision tree**:

```
IF break-even within 12 months AND low burn (<$30k/month)
  → Bootstrap friendly
  → Consider: Revenue-based financing, small angel round

ELSE IF break-even within 24 months AND high confidence
  → Seed fundable ($500k-$2M)
  → Target: 18-24 month runway

ELSE IF break-even > 24 months OR significant market opportunity
  → Series A path ($3M-$10M)
  → Need strong growth metrics (3x YoY)

ELSE IF very long payback (>36 months)
  → Reconsider business model
  → OR target strategic investors in vertical
```

**Validation criteria**:

- [ ] Break-even timeline is realistic (based on growth projections)
- [ ] Funding requirements include 6-month buffer
- [ ] Funding strategy matches business model (bootstrap vs VC)

### Step 7: Create Scenario Analysis

**Model three scenarios** to test sensitivity to assumptions:

#### Scenario 1: Conservative (70% confidence)

**Pessimistic but realistic assumptions**:

- Conversion rates: -30% vs. base case
- Churn rates: +30% vs. base case
- CAC: +30% vs. base case
- Time to channel maturity: +50% vs. base case

**Example**:

```
Base case: 10% signup → paid, 2% monthly churn, $500 CAC
Conservative: 7% conversion, 2.6% churn, $650 CAC

Result:
- Year 1 ARR: $240k (vs. $350k base)
- Break-even: Month 20 (vs. Month 15 base)
- Funding needed: $800k (vs. $600k base)
```

**Key question**: Can we survive this scenario?

#### Scenario 2: Realistic (50% confidence)

**Base case assumptions** (from previous steps):

- Journey-informed conversion rates
- Market-benchmarked churn
- Channel-specific CAC
- Realistic growth curves

**This is your primary plan.**

#### Scenario 3: Aggressive (30% confidence)

**Optimistic but achievable assumptions**:

- Conversion rates: +30% vs. base case
- Churn rates: -30% vs. base case
- CAC: -20% vs. base case
- Viral coefficient > 1 (if product-led)

**Example**:

```
Base case: 10% signup → paid, 2% monthly churn, $500 CAC
Aggressive: 13% conversion, 1.4% churn, $400 CAC

Result:
- Year 1 ARR: $520k (vs. $350k base)
- Break-even: Month 10 (vs. Month 15 base)
- Funding needed: $400k (vs. $600k base)
```

**Key question**: What would need to be true for this scenario?

#### Scenario Comparison Table

```markdown
| Metric             | Conservative | Realistic | Aggressive |
| ------------------ | ------------ | --------- | ---------- |
| Year 1 ARR         | $X           | $Y        | $Z         |
| Year 3 ARR         | $X           | $Y        | $Z         |
| LTV:CAC            | X:1          | Y:1       | Z:1        |
| Break-even Month   | X            | Y         | Z          |
| Funding Needed     | $X           | $Y        | $Z         |
| Customers (Year 1) | X            | Y         | Z          |
```

**Validation criteria**:

- [ ] Conservative scenario is survivable (not catastrophic)
- [ ] Realistic scenario is attractive (worth pursuing)
- [ ] Aggressive scenario is plausible (not fantasy)
- [ ] Key assumptions are explicitly stated for each

### Step 8: Identify Key Assumptions & Risks

**Every financial model is built on assumptions.** Document them explicitly.

#### Critical Assumptions

**For EACH key assumption**, document:

1. **What we assumed**: [Specific number/rate]
2. **Why we believe it**: [Data source, benchmark, reasoning]
3. **Confidence level**: [High/Medium/Low]
4. **How to validate**: [What data would prove/disprove?]
5. **If wrong, impact**: [Sensitivity analysis]

**Example**:

```
Assumption: 10% signup → paid conversion rate

Why we believe it:
- Similar B2B SaaS tools average 8-12% (ChartMogul benchmark)
- Our journey time-to-value is faster than average
- Freemium tier demonstrates value before paywall

Confidence: Medium (no actual data yet)

How to validate:
- Launch free tier, measure actual conversion after 30/60/90 days
- A/B test pricing page
- Interview 10 non-converting users

If wrong (e.g., only 5% convert):
- Year 1 ARR drops by 50% ($350k → $175k)
- Break-even delays by 8 months (Month 15 → Month 23)
- Need additional funding: +$300k
```

#### Key Risks & Mitigations

**Identify top 5 financial risks**:

1. **[Risk Name]**: [Description]
   - **Likelihood**: [High/Medium/Low]
   - **Impact**: [High/Medium/Low]
   - **Mitigation**: [What can we do to reduce risk?]
   - **Contingency**: [What if it happens anyway?]

**Example**:

```
1. Market Education Risk: Customers don't understand problem/solution

   Likelihood: Medium (new category)
   Impact: High (affects conversion, extends CAC payback)

   Mitigation:
   - Invest in education content (blog, webinars, guides)
   - Offer free assessments to demonstrate value
   - Build comparison calculator (ROI tool)

   Contingency:
   - If Q2 conversion < 5%, pivot messaging to pain-first
   - Consider "done-for-you" service to prove value
   - Extend runway to 24 months instead of 18
```

### Step 9: Define Financial Milestones

**Set clear financial goals** tied to business stages:

```
Milestone 1: First Dollar (Month X)
- Goal: First paying customer
- Metric: $1 MRR
- Validation: Journey delivers value, someone will pay

Milestone 2: $10k MRR (Month X)
- Goal: Repeatability proven
- Metric: $10,000 MRR
- Validation: Can acquire 100+ customers, business model works

Milestone 3: Break-Even (Month X)
- Goal: Cashflow positive
- Metric: Revenue > Costs
- Validation: Sustainable without external funding

Milestone 4: $100k MRR (Month X)
- Goal: Scale readiness
- Metric: $100,000 MRR ($1.2M ARR)
- Validation: Channel-market fit, ready for growth investment

Milestone 5: $1M ARR (Month X)
- Goal: Market validation
- Metric: $1,000,000 ARR
- Validation: Significant market opportunity, Series A readiness
```

**For EACH milestone**, define:

- [ ] Target date
- [ ] Required metrics (customers, ARPU, LTV:CAC)
- [ ] Team size at this stage
- [ ] Funding requirement (if any)
- [ ] What unlocks next stage

## Output Format

The output should be saved to `product-guidelines/22-financial-model.md`:

Use the template at `templates/22-financial-model-template.md` as structure.

**The output includes**:

### Section 1: Executive Summary

- Business model overview
- Key metrics (LTV, CAC, LTV:CAC, payback)
- Revenue targets (Year 1, 2, 3)
- Funding requirements
- Key assumptions and risks

### Section 2: Unit Economics

- Customer Acquisition Cost (CAC) breakdown
- Lifetime Value (LTV) calculation
- LTV:CAC ratio analysis
- Payback period
- Gross margin analysis

### Section 3: Revenue Projections

- Customer acquisition model
- MRR/ARR projections (3 years)
- Revenue by tier/segment
- Expansion revenue assumptions

### Section 4: Cost Structure

- Variable costs (COGS)
- Fixed costs (OpEx)
- Team growth plan
- Marketing budget allocation

### Section 5: Profitability & Funding

- Break-even analysis
- Burn rate and runway
- Funding requirements
- Funding strategy

### Section 6: Scenario Analysis

- Conservative scenario
- Realistic scenario (base case)
- Aggressive scenario
- Comparison table

### Section 7: Assumptions & Risks

- Critical assumptions (with validation plan)
- Key risks and mitigations
- Sensitivity analysis

### Section 8: Financial Milestones

- Milestone definitions (First $, $10k MRR, Break-even, $100k MRR, $1M ARR)
- Target dates
- Success criteria

## Quality Checklist

Before completing this session, verify:

**Journey Alignment**:

- [ ] LTV calculation is based on journey value delivery (not arbitrary pricing)
- [ ] CAC estimates reflect how journey persona discovers solutions
- [ ] Revenue projections consider journey complexity (affects conversion)
- [ ] Unit economics reflect journey defensibility (affects retention)

**Data Grounding**:

- [ ] All assumptions cite sources (benchmarks, competitors, metrics)
- [ ] Projections are tied to specific growth channels (not fantasy)
- [ ] Costs reflect actual tech stack and team requirements
- [ ] Scenarios test sensitivity to key assumptions

**Business Viability**:

- [ ] LTV:CAC ratio is ≥ 3:1 (or clear path documented)
- [ ] Payback period is ≤ 18 months (or funding plan exists)
- [ ] Break-even timeline is realistic (based on growth projections)
- [ ] Conservative scenario is survivable

**Completeness**:

- [ ] All three scenarios modeled (conservative, realistic, aggressive)
- [ ] Top 5 assumptions explicitly documented
- [ ] Top 5 risks identified with mitigations
- [ ] Financial milestones tied to business stages
- [ ] "What We DIDN'T Choose" section complete

## What We DIDN'T Choose (And Why)

### Alternative Financial Model: Advertising-Based Revenue

**What it is**: Free product monetized through display ads, sponsored content, or data licensing instead of direct user payments.

**Why not (for this journey)**:

- Journey delivers B2B value (compliance, productivity) where ad-based models fail
- Users expect professional tools to be ad-free
- Revenue per user is typically 10-100x lower than SaaS ($1-$10 ARPU vs $50-$500 ARPU)
- Requires massive scale (millions of MAUs) to reach meaningful revenue
- Misaligned incentives (maximize engagement vs. solve problem efficiently)

**When to reconsider**:

- IF pivot to B2C consumer market (millions of potential users)
- IF journey naturally involves content consumption (not task completion)
- IF users are unwilling to pay directly (very low willingness to pay)
- IF reach >1M MAUs and direct monetization is challenging

**Example**: If building compliance SaaS became a compliance news/content platform with millions of readers, ads could work. But for task-based SaaS, subscription model is superior.

---

### Alternative Approach: Usage-Based Pricing (Pure Consumption)

**What it is**: Charge purely based on usage (per API call, per document processed, per report generated) with no base subscription fee.

**Why not (for this journey)**:

- Journey has predictable, recurring usage patterns (better fit for subscription)
- Pure usage pricing creates revenue unpredictability (harder to forecast)
- Users prefer predictable costs (budgeting for subscription vs. variable usage)
- Discourages product adoption (fear of runaway costs)
- Higher churn risk (easier to stop using than cancel subscription)

**When to reconsider**:

- IF usage is highly variable (some months 0, some months 1000x)
- IF serving developers/technical users (comfortable with usage-based)
- IF journey is transactional (one-time use vs. recurring workflow)
- IF following "freemium → usage" model (like Stripe, Twilio, AWS)

**Example**: If compliance assessments were rare events (once per year per customer), usage-based makes sense. But for recurring workflows (weekly/monthly assessments), subscription provides better revenue stability.

---

### Alternative Approach: Services/Consulting Revenue

**What it is**: Generate revenue primarily through professional services, consulting, or "done-for-you" implementations rather than software subscriptions.

**Why not (for this journey)**:

- Services revenue doesn't scale (linear with headcount, not software margins)
- Gross margins are lower (40-60% vs. 75-85% for SaaS)
- Team complexity (consultants + engineers + sales vs. focused product team)
- Valuation multiples are lower (1-3x revenue vs. 5-15x for SaaS)
- Distracts from product development (services pull team away from software)

**When to reconsider**:

- IF early-stage and need revenue immediately (services fund product development)
- IF market is immature (customers need hand-holding before self-serve works)
- IF deal sizes are very large (>$100k ACV) and customization is expected
- IF "land with services, expand with software" strategy (IBM, Accenture model)

**Example**: Offering "done-for-you" compliance assessments as a service could bootstrap initial revenue, but should transition to software-only model for scalability and margins.

---

### Alternative Approach: Transaction/Marketplace Fees

**What it is**: Take a percentage of transactions facilitated through the platform (like Stripe's 2.9%, Airbnb's 15%, Uber's 25%).

**Why not (for this journey)**:

- Journey doesn't involve financial transactions or matchmaking between parties
- Requires high transaction volume to generate meaningful revenue
- Adds friction (users pay more to use the platform)
- Network effects are required (chicken-egg problem at launch)
- Competitive pressure on take rate (users seek lower-fee alternatives)

**When to reconsider**:

- IF journey involves facilitating payments or transactions
- IF building a marketplace (connecting buyers and sellers)
- IF transaction value is high enough that % fee is meaningful
- IF platform creates enough value to justify take rate

**Example**: If compliance SaaS evolved into a marketplace connecting companies with compliance auditors, transaction fees could work. But for pure SaaS workflow tools, subscription model is cleaner.

## Next Steps

After completing this session:

1. **Validate assumptions**: Run customer interviews to test pricing, conversion rates, retention
2. **Update regularly**: Revisit financial model quarterly as you learn from real data
3. **Share with stakeholders**: Use this model for investor pitches, board meetings, team planning
4. **Track actuals vs. projections**: Monitor key metrics (CAC, LTV, MRR) and adjust model
5. **Run `/cascade-status`** to see your complete progress

## AI Agent Guidelines

**Special instructions for executing this command**:

1. **Don't make up numbers**: If monetization strategy doesn't include specific pricing, ASK the user for pricing assumptions before projecting revenue.

2. **Be realistic, not optimistic**: Financial models tend toward optimism. Push back on assumptions that seem aggressive. Use conservative benchmarks.

3. **Show your math**: For every calculation (LTV, CAC, break-even), show the formula and step-by-step arithmetic so users can verify and adjust.

4. **Cite sources**: When using industry benchmarks (churn rates, conversion rates, CAC), cite the source (e.g., "SaaS Capital survey", "OpenView benchmarks", "ChartMogul data").

5. **Connect to journey**: Every financial assumption should trace back to journey characteristics. Don't create generic financial models - make them journey-specific.

6. **Flag missing inputs**: If critical inputs are missing (pricing, tech stack costs, growth strategy), note what's missing and use "placeholder assumptions that need validation."

7. **Scenario math**: Ensure scenarios are internally consistent. If conservative assumes lower conversion, it should also assume higher CAC and longer sales cycles.

8. **Sensitivity table**: For key assumptions, create a sensitivity table showing impact of +/- 20% changes.

**Common pitfalls to avoid**:

- ❌ Using "hockey stick" growth curves without justification
- ❌ Ignoring churn in revenue projections (only counting new customers)
- ❌ Underestimating costs (especially marketing and personnel)
- ❌ Assuming 0% churn or 100% gross margin
- ❌ Not including 6-month cash buffer in funding requirements
- ❌ Forgetting to account for payment processing fees (3% of revenue)
- ❌ Modeling 50%+ YoY growth without explaining how (channel capacity, team size, etc.)
