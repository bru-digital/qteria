# Financial Model: [Product Name]

> **Context**: Comprehensive financial model grounded in user journey and market analysis. Created: [Date]
>
> **Derived from**:
> - `product-guidelines/00-user-journey.md` (Journey economics and value delivery)
> - `product-guidelines/01-product-strategy.md` (Market size and competitive landscape)
> - `product-guidelines/04-monetization.md` (Pricing structure and ARPU)
> - `product-guidelines/04-metrics.md` (Conversion rates and retention)
> - `product-guidelines/growth-strategy.md` (Acquisition channels and CAC - if available)

---

## Executive Summary

**Business Model**: [SaaS subscription / Usage-based / Freemium / Hybrid]

**Unit Economics** (Base Case):
- **LTV**: $[X,XXX] per customer
- **CAC**: $[XXX] blended across channels
- **LTV:CAC Ratio**: [X.X]:1 ([Assessment: Excellent/Healthy/Concerning])
- **Payback Period**: [X] months
- **Gross Margin**: [XX]%

**Revenue Projections**:
- **Year 1**: $[XXX]k ARR ([X] customers)
- **Year 2**: $[X.X]M ARR ([XX]% YoY growth)
- **Year 3**: $[X.X]M ARR ([XX]% YoY growth)

**Profitability**:
- **Break-even**: Month [XX]
- **Burn Rate**: $[XX]k/month (current), declining to $[X]k/month by Month [XX]
- **Funding Required**: $[XXX]k to reach profitability + 6-month buffer

**Key Assumptions**:
1. [Critical assumption 1 - e.g., "10% free-to-paid conversion rate"]
2. [Critical assumption 2 - e.g., "2% monthly churn"]
3. [Critical assumption 3 - e.g., "$500 blended CAC from SEO + paid channels"]

**Top Risks**:
1. [Risk 1 - e.g., "Market education required may extend CAC payback"]
2. [Risk 2 - e.g., "Competitive pressure on pricing"]
3. [Risk 3 - e.g., "Channel saturation earlier than projected"]

---

## Unit Economics

### Customer Acquisition Cost (CAC)

**Channel Breakdown**:

| Channel | % of New Customers | CAC | Source/Rationale |
|---------|-------------------|-----|------------------|
| [Channel 1] | [XX]% | $[XXX] | [How calculated / Industry benchmark] |
| [Channel 2] | [XX]% | $[XXX] | [How calculated / Industry benchmark] |
| [Channel 3] | [XX]% | $[XXX] | [How calculated / Industry benchmark] |
| **Blended CAC** | **100%** | **$[XXX]** | **Weighted average** |

**CAC Components**:
```
Marketing Spend:        $[XX,XXX]/month
Sales Spend:            $[XX,XXX]/month (if applicable)
Marketing Tools:        $[X,XXX]/month
──────────────────────────────────────
Total Acquisition Cost: $[XX,XXX]/month

New Customers/Month:    [XXX]
──────────────────────────────────────
Blended CAC:            $[XXX] per customer
```

**Validation**:
- [ ] CAC includes all costs (marketing, sales, tools)
- [ ] Benchmarked against [competitor/industry] ($[XXX]-$[XXX] range)
- [ ] Channel mix reflects growth strategy priorities
- [ ] Assumes [X]% signup-to-paid conversion rate

---

### Lifetime Value (LTV)

**Calculation**:
```
ARPU (Average Revenue Per User):     $[XXX]/month
Gross Margin:                         [XX]%
Customer Lifetime:                    [XX] months (1 / churn rate)
──────────────────────────────────────────────────────
LTV = ($[XXX] × [XX]%) × [XX] months = $[X,XXX]
```

**Component Breakdown**:

#### 1. ARPU (Blended Across Tiers)

| Tier | % of Customers | Price | Contribution to ARPU |
|------|----------------|-------|----------------------|
| Free | [XX]% | $0 | $0 |
| [Starter] | [XX]% | $[XX]/mo | $[XX] |
| [Pro] | [XX]% | $[XXX]/mo | $[XX] |
| [Enterprise] | [X]% | $[XXX]/mo | $[XX] |
| **Blended ARPU** | **100%** | | **$[XXX]/month** |

**Rationale for tier distribution**: [Why this mix? Based on journey complexity, pricing psychology, competitive positioning]

#### 2. Gross Margin

```
Revenue:                  100%
──────────────────────────────────
Variable Costs:
- Hosting/infrastructure: -[X]%   ($[XX] per customer/month)
- Third-party APIs:       -[X]%   ($[XX] per customer/month)
- Payment processing:     -3%     (Stripe/PayPal fees)
- Customer support:       -[X]%   ($[XX] per customer/month allocated)
──────────────────────────────────
Gross Margin:             [XX]%
```

**Source**: [From tech stack cost analysis / Industry benchmarks for [category] SaaS: 70-85%]

#### 3. Customer Lifetime (Churn)

| Customer Segment | Monthly Churn | Avg. Lifetime | Source |
|------------------|---------------|---------------|--------|
| Free tier | [XX]% | [X] months | [Assumption/Benchmark] |
| Paid tier | [X]% | [XX] months | [Assumption/Benchmark] |
| Enterprise | [X]% | [XX] months | [Assumption/Benchmark] |
| **Blended** | **[X]%** | **[XX] months** | **Weighted average** |

**Churn assumption rationale**: [Why this churn rate? Based on journey stickiness, competitive differentiation, switching costs]

**Benchmark**: [B2B/B2C] SaaS in [category] typically sees [X]-[X]% monthly churn ([source])

---

### LTV:CAC Ratio Analysis

```
LTV:     $[X,XXX]
CAC:     $[XXX]
Ratio:   [X.X]:1
```

**Assessment**:
- ✅ **[Excellent / Healthy / Concerning / Unsustainable]**

**Industry Benchmark Comparison**:
```
< 1:1    → Losing money on every customer (unsustainable)
1-3:1    → Barely profitable (concerning)
3:1      → Minimum viable (break-even after costs)
3-5:1    → Healthy (our target: [X.X]:1)
5-10:1   → Excellent (very profitable)
> 10:1   → May be underspending on growth

Our ratio: [X.X]:1 → [Assessment and implications]
```

**If ratio < 3:1, improvement plan**:
- [ ] Increase LTV: [Specific tactics - upsells, reduce churn, increase prices]
- [ ] Decrease CAC: [Specific tactics - optimize channels, improve conversion, build loops]
- [ ] Timeline: [When will ratio improve to 3:1+?]

---

### Payback Period

**Calculation**:
```
Payback Period = CAC / (ARPU × Gross Margin)

Payback = $[XXX] / ($[XXX] × [XX]%) = [X.X] months
```

**Assessment**:
- ✅ **[Excellent / Good / Concerning / Problematic]**

**Benchmark**:
```
< 12 months   → Excellent (VC-backable, strong cashflow)
12-18 months  → Good (manageable)
18-24 months  → Concerning (capital intensive)
> 24 months   → Problematic (requires significant funding)

Our payback: [X] months → [Assessment]
```

**Cashflow Implications**:
- To grow from [X] → [Y] customers requires $[XXX]k in working capital
- Monthly cashflow: [New customers × CAC] - [Total customers × margin] = $[±XX]k

---

## Revenue Projections

### Customer Acquisition Model

**Growth assumptions** (from growth strategy):
- **Primary channels**: [Channel 1, Channel 2, Channel 3]
- **Growth model**: [Content-driven / Paid / Viral / Sales-driven / Hybrid]
- **Ramp timeline**: [When channels reach maturity]

**Monthly projections** (Year 1):

| Month | Signups | Conversion Rate | New Customers | Churned | Net New | Total Customers |
|-------|---------|-----------------|---------------|---------|---------|-----------------|
| M1 | [XXX] | [X]% | [XX] | 0 | [XX] | [XX] |
| M2 | [XXX] | [X]% | [XX] | [X] | [XX] | [XX] |
| M3 | [XXX] | [X]% | [XX] | [X] | [XX] | [XX] |
| M6 | [XXX] | [X]% | [XX] | [XX] | [XX] | [XXX] |
| M9 | [XXX] | [X]% | [XX] | [XX] | [XX] | [XXX] |
| M12 | [XXX] | [X]% | [XX] | [XX] | [XX] | [XXX] |

**Growth rate justification**:
```
Month 1-3:   [X]% MoM growth
Why: [Early traction, initial marketing, manual outreach]

Month 4-6:   [X]% MoM growth
Why: [SEO/content starting to work, paid ads optimized, word-of-mouth]

Month 7-12:  [X]% MoM growth
Why: [Compounding content, growth loops activating, channel maturity]
```

**Conversion funnel**:
```
Website Visitors:     [X,XXX]/month
  ↓ [X]% to signup
Signups:              [XXX]/month
  ↓ [X]% to activation (aha moment)
Activated Users:      [XXX]/month
  ↓ [X]% to paid conversion
New Customers:        [XX]/month
```

---

### Revenue Projections (3 Years)

#### Year 1: Foundation & Initial Traction

| Quarter | New Customers | Total Customers | MRR | ARR Run Rate |
|---------|---------------|-----------------|-----|--------------|
| Q1 | [XXX] | [XXX] | $[XX]k | $[XXX]k |
| Q2 | [XXX] | [XXX] | $[XX]k | $[XXX]k |
| Q3 | [XXX] | [XXX] | $[XX]k | $[XXX]k |
| Q4 | [XXX] | [XXX] | $[XX]k | $[XXX]k |
| **Year 1 Total** | **[X,XXX]** | **[X,XXX]** | **$[XX]k** | **$[XXX]k ARR** |

**Focus**: Product-market fit, channel validation, initial customer base

---

#### Year 2: Growth & Scaling

| Quarter | New Customers | Total Customers | MRR | ARR Run Rate |
|---------|---------------|-----------------|-----|--------------|
| Q1 | [XXX] | [X,XXX] | $[XXX]k | $[X.X]M |
| Q2 | [XXX] | [X,XXX] | $[XXX]k | $[X.X]M |
| Q3 | [XXX] | [X,XXX] | $[XXX]k | $[X.X]M |
| Q4 | [XXX] | [X,XXX] | $[XXX]k | $[X.X]M |
| **Year 2 Total** | **[X,XXX]** | **[XX,XXX]** | **$[XXX]k** | **$[X.X]M ARR** |

**Growth**: [XXX]% YoY

**Focus**: Channel optimization, team expansion, market penetration

---

#### Year 3: Acceleration & Market Leadership

| Quarter | New Customers | Total Customers | MRR | ARR Run Rate |
|---------|---------------|-----------------|-----|--------------|
| Q1 | [XXX] | [XX,XXX] | $[XXX]k | $[X.X]M |
| Q2 | [XXX] | [XX,XXX] | $[XXX]k | $[X.X]M |
| Q3 | [XXX] | [XX,XXX] | $[X.X]M | $[XX]M |
| Q4 | [XXX] | [XX,XXX] | $[X.X]M | $[XX]M |
| **Year 3 Total** | **[XX,XXX]** | **[XXX,XXX]** | **$[X.X]M** | **$[XX]M ARR** |

**Growth**: [XXX]% YoY

**Focus**: Profitability, category leadership, expansion opportunities

---

### Revenue Breakdown by Segment

**Year 3 ARR Composition**:

| Segment | Customers | ARPU | Annual Revenue | % of Total |
|---------|-----------|------|----------------|------------|
| Free (upsell pipeline) | [XX,XXX] | $0 | $0 | 0% |
| [Starter tier] | [XX,XXX] | $[XX] | $[X.X]M | [XX]% |
| [Pro tier] | [X,XXX] | $[XXX] | $[X.X]M | [XX]% |
| [Enterprise tier] | [XXX] | $[X,XXX] | $[X.X]M | [XX]% |
| **Total Paid** | **[XX,XXX]** | **$[XXX]** | **$[XX]M** | **100%** |

---

### Expansion Revenue

**Net Revenue Retention (NRR)**: [XXX]%

```
Cohort starting MRR:        $[XXX]k
  + Upsells (tier upgrades): +$[XX]k  ([X]% of cohort)
  + Cross-sells (add-ons):   +$[XX]k  ([X]% of cohort)
  + Usage expansion:         +$[XX]k  (usage-based components)
  - Churn:                   -$[XX]k  ([X]% monthly churn)
  - Contraction:             -$[X]k   (downgrades)
──────────────────────────────────────────────────
Cohort ending MRR:          $[XXX]k

NRR = $[XXX]k / $[XXX]k = [XXX]%
```

**Target**: [XXX]% NRR ([Interpretation: <100% = net churn, 100-110% = stable, 110%+ = expansion])

**Expansion tactics**:
1. [Tactic 1 - e.g., "Automatic tier upgrades when usage limits hit"]
2. [Tactic 2 - e.g., "Team/seat expansion as companies grow"]
3. [Tactic 3 - e.g., "Premium features (integrations, advanced analytics)"]

---

## Cost Structure

### Variable Costs (COGS)

**Per-customer costs** (scales with customer count):

| Cost Category | Per Customer/Month | Annual (at [X,XXX] customers) | % of Revenue |
|---------------|-------------------|-------------------------------|--------------|
| Hosting/Compute | $[XX] | $[XXX]k | [X]% |
| Database/Storage | $[X] | $[XX]k | [X]% |
| Third-party APIs | $[XX] | $[XXX]k | [X]% |
| Payment Processing | $[X] | $[XX]k | 3% |
| Customer Support (allocated) | $[XX] | $[XXX]k | [X]% |
| **Total COGS** | **$[XX]** | **$[XXX]k** | **[XX]%** |

**Gross Margin**: [XX]% (Revenue - COGS)

**Cost assumptions**:
- **Hosting**: [Platform] at $[X]/[unit], estimate [X units] per customer
- **APIs**: [List key APIs - e.g., "Anthropic Claude API $X per 1M tokens, estimate X calls/customer/month"]
- **Support**: [X] FTE support for every [XXX] customers = $[XX] per customer/month

---

### Fixed Costs (Operating Expenses)

**Monthly operating expenses** (independent of customer count):

#### Year 1 (Foundation)

| Category | Headcount | Cost/Month | Annual |
|----------|-----------|------------|--------|
| **Engineering** | [X] | $[XX]k | $[XXX]k |
| **Product/Design** | [X] | $[XX]k | $[XXX]k |
| **Marketing** | [X] | $[XX]k | $[XXX]k |
| **Sales** (if applicable) | [X] | $[XX]k | $[XXX]k |
| **Operations/Admin** | [X] | $[XX]k | $[XXX]k |
| **Software/Tools** | - | $[X]k | $[XX]k |
| **Marketing Budget** | - | $[XX]k | $[XXX]k |
| **Office/Misc** | - | $[X]k | $[XX]k |
| **Total OpEx** | **[X] people** | **$[XX]k/mo** | **$[XXX]k** |

---

#### Year 2 (Growth)

| Category | Headcount | Cost/Month | Annual |
|----------|-----------|------------|--------|
| **Engineering** | [X] | $[XXX]k | $[X.X]M |
| **Product/Design** | [X] | $[XX]k | $[XXX]k |
| **Marketing** | [X] | $[XX]k | $[XXX]k |
| **Sales** | [X] | $[XX]k | $[XXX]k |
| **Customer Success** | [X] | $[XX]k | $[XXX]k |
| **Operations/Admin** | [X] | $[XX]k | $[XXX]k |
| **Software/Tools** | - | $[XX]k | $[XXX]k |
| **Marketing Budget** | - | $[XX]k | $[XXX]k |
| **Office/Misc** | - | $[X]k | $[XX]k |
| **Total OpEx** | **[XX] people** | **$[XXX]k/mo** | **$[X.X]M** |

---

#### Year 3 (Scale)

| Category | Headcount | Cost/Month | Annual |
|----------|-----------|------------|--------|
| **Engineering** | [XX] | $[XXX]k | $[X.X]M |
| **Product/Design** | [X] | $[XXX]k | $[X.X]M |
| **Marketing** | [X] | $[XXX]k | $[X.X]M |
| **Sales** | [XX] | $[XXX]k | $[X.X]M |
| **Customer Success** | [X] | $[XXX]k | $[X.X]M |
| **Operations/Admin** | [X] | $[XXX]k | $[X.X]M |
| **Software/Tools** | - | $[XX]k | $[XXX]k |
| **Marketing Budget** | - | $[XXX]k | $[X.X]M |
| **Office/Misc** | - | $[XX]k | $[XXX]k |
| **Total OpEx** | **[XX] people** | **$[XXX]k/mo** | **$[X.X]M** |

---

### Hiring Plan Rationale

**Team growth tied to milestones**:

```
$0 → $10k MRR:     [X] people (MVP team - mostly founders/contract)
$10k → $100k MRR:  [X] people (add 1-2 engineers, 1 marketer)
$100k → $500k MRR: [XX] people (scale team - eng, sales, success)
$500k → $1M+ MRR:  [XX+] people (full team - all functions)
```

**Hiring priorities**:
1. [Month X]: [Role] - [Why needed at this stage]
2. [Month X]: [Role] - [Why needed at this stage]
3. [Month X]: [Role] - [Why needed at this stage]

---

## Profitability & Funding

### Profit & Loss Summary

| | Year 1 | Year 2 | Year 3 |
|------------------------|------------|------------|------------|
| **Revenue** | $[XXX]k | $[X.X]M | $[XX]M |
| **COGS** | -$[XX]k | -$[XXX]k | -$[X.X]M |
| **Gross Profit** | $[XXX]k | $[X.X]M | $[XX]M |
| **Gross Margin** | [XX]% | [XX]% | [XX]% |
| | | | |
| **Operating Expenses** | -$[XXX]k | -$[X.X]M | -$[X.X]M |
| | | | |
| **EBITDA** | -$[XXX]k | -$[XXX]k / +$[XX]k | +$[X.X]M |
| **EBITDA Margin** | -[XXX]% | -[XX]% / +[X]% | +[XX]% |

---

### Break-Even Analysis

**Break-even calculation**:
```
Fixed Costs:                $[XX]k/month
Contribution Margin/Customer: $[XX]/month (ARPU × Gross Margin - variable cost)
──────────────────────────────────────────────────────
Break-even Customers:       [XXX] customers

At [X]% conversion rate:    Need [X,XXX] signups/month
```

**Break-even timeline**:
- **Target month**: Month [XX]
- **Customers at break-even**: [XXX] customers
- **MRR at break-even**: $[XX]k

**Path to break-even**:

| Milestone | Month | Customers | MRR | Status |
|-----------|-------|-----------|-----|--------|
| First $ | M[X] | [X] | $[X]k | [How we get here] |
| $10k MRR | M[X] | [XXX] | $10k | [Validation milestone] |
| $50k MRR | M[XX] | [XXX] | $50k | [Scale readiness] |
| **Break-even** | **M[XX]** | **[XXX]** | **$[XX]k** | **Cashflow positive** |
| $100k MRR | M[XX] | [X,XXX] | $100k | [Series A readiness] |

---

### Burn Rate & Runway

**Monthly burn rate** (revenue - total costs):

| Period | Revenue | Costs | Burn Rate | Cumulative Burn |
|--------|---------|-------|-----------|-----------------|
| Month 1-3 | $[X]k/mo | $[XX]k/mo | -$[XX]k/mo | -$[XXX]k |
| Month 4-6 | $[XX]k/mo | $[XX]k/mo | -$[XX]k/mo | -$[XXX]k |
| Month 7-12 | $[XX]k/mo | $[XX]k/mo | -$[X]k/mo | -$[XXX]k |
| **Total Year 1** | **$[XXX]k** | **$[X.X]M** | | **-$[XXX]k** |

**Runway calculation**:
```
Starting Capital:        $[XXX]k
Monthly Burn Rate:       $[XX]k/month (average)
──────────────────────────────────────
Runway:                  [XX] months
```

**Burn reduction timeline**:
- Month [X]: Burn peaks at $[XX]k/month (team ramp-up)
- Month [X]: Burn reduces to $[XX]k/month (revenue growing faster than costs)
- Month [X]: Break-even (burn = $0)
- Month [X]: Cashflow positive (+$[X]k/month)

---

### Funding Requirements

**Total capital needed to reach profitability**:

```
Pre-revenue runway:      $[XXX]k  (Months 0-6)
Growth phase:            $[XXX]k  (Months 7-18)
Buffer (6 months):       $[XXX]k  (Safety margin)
──────────────────────────────────────────────
Total Funding Needed:    $[XXX]k - $[X.X]M
```

**Funding strategy**:

```
IF bootstrap friendly (break-even < 12 months, burn < $30k/mo)
  → Revenue-based financing or small angel round ($100k-$250k)
  → Focus: Extend runway, accelerate channel testing

ELSE IF seed stage (break-even 12-24 months, strong traction)
  → Seed round: $[XXX]k - $[X.X]M
  → Target: 18-24 month runway to hit $[X]M ARR
  → Use: Team expansion, marketing scale, product development

ELSE IF Series A (>$1M ARR, 3x YoY growth)
  → Series A round: $[X]M - $[XX]M
  → Target: Scale to $[XX]M ARR
  → Use: Sales team, market expansion, category leadership
```

**Our recommendation**: [Strategy and rationale based on model]

**Milestones for next funding round**:
- [ ] Reach $[XXX]k ARR ([X]x from current)
- [ ] Demonstrate [XX]% YoY growth
- [ ] Achieve LTV:CAC ≥ [X]:1
- [ ] Prove [X] channels work (CAC < $[XXX])
- [ ] NRR ≥ [XXX]%

---

## Scenario Analysis

### Scenario Comparison

| Metric | Conservative (70%) | Realistic (50%) | Aggressive (30%) |
|--------|-------------------|-----------------|------------------|
| **Year 1 ARR** | $[XXX]k | $[XXX]k | $[XXX]k |
| **Year 3 ARR** | $[X.X]M | $[XX]M | $[XX]M |
| **LTV** | $[X,XXX] | $[X,XXX] | $[X,XXX] |
| **CAC** | $[XXX] | $[XXX] | $[XXX] |
| **LTV:CAC** | [X.X]:1 | [X.X]:1 | [X.X]:1 |
| **Break-even Month** | Month [XX] | Month [XX] | Month [XX] |
| **Funding Needed** | $[X.X]M | $[XXX]k | $[XXX]k |
| **Customers (Year 3)** | [XX,XXX] | [XXX,XXX] | [XXX,XXX] |

---

### Conservative Scenario (70% confidence)

**"What if things go slower than expected?"**

**Assumptions** (relative to realistic):
- Conversion rates: -30% ([X]% → [X]%)
- Churn rates: +30% ([X]% → [X]%)
- CAC: +30% ($[XXX] → $[XXX])
- Growth rates: -30% (channels mature slower)
- Time to break-even: +50% (Month [XX] → Month [XX])

**Key metrics**:
- **Year 1 ARR**: $[XXX]k (vs. $[XXX]k realistic)
- **Year 3 ARR**: $[X.X]M (vs. $[XX]M realistic)
- **LTV:CAC**: [X.X]:1 (vs. [X.X]:1 realistic)
- **Break-even**: Month [XX] (vs. Month [XX] realistic)
- **Funding needed**: $[X.X]M (vs. $[XXX]k realistic)

**Can we survive this scenario?**
- [✅ / ⚠️ / ❌] [Assessment: e.g., "Yes with additional $XXXk bridge funding"]

**What would trigger this scenario?**
1. [Trigger 1 - e.g., "Market education takes longer than expected"]
2. [Trigger 2 - e.g., "Competitive pressure on pricing"]
3. [Trigger 3 - e.g., "Channel saturation sooner than projected"]

**Early warning signs** (metrics to watch):
- Month 3: If MRR < $[X]k, we're tracking conservative
- Month 6: If churn > [X]%, tightening product-market fit needed
- Month 9: If CAC > $[XXX], channel strategy needs revision

---

### Realistic Scenario (50% confidence)

**"Base case - what we expect"**

This is the main projection detailed in previous sections.

**Based on**:
- Journey-informed conversion rates
- Market-benchmarked churn and CAC
- Realistic channel growth curves
- Conservative assumptions on unknowns

**Key metrics**:
- **Year 1 ARR**: $[XXX]k
- **Year 3 ARR**: $[XX]M
- **LTV:CAC**: [X.X]:1
- **Break-even**: Month [XX]
- **Funding needed**: $[XXX]k

---

### Aggressive Scenario (30% confidence)

**"What if everything goes right?"**

**Assumptions** (relative to realistic):
- Conversion rates: +30% ([X]% → [X]%)
- Churn rates: -30% ([X]% → [X]%)
- CAC: -20% ($[XXX] → $[XXX])
- Growth rates: +40% (viral effects kick in)
- Time to break-even: -40% (Month [XX] → Month [XX])

**Key metrics**:
- **Year 1 ARR**: $[XXX]k (vs. $[XXX]k realistic)
- **Year 3 ARR**: $[XX]M (vs. $[XX]M realistic)
- **LTV:CAC**: [X.X]:1 (vs. [X.X]:1 realistic)
- **Break-even**: Month [XX] (vs. Month [XX] realistic)
- **Funding needed**: $[XXX]k (vs. $[XXX]k realistic)

**What would need to be true?**
1. [Condition 1 - e.g., "Viral coefficient > 1.2 (strong word-of-mouth)"]
2. [Condition 2 - e.g., "Journey delivers 20x value (raises willingness to pay)"]
3. [Condition 3 - e.g., "SEO compounds faster (domain authority)"]

**Upside opportunities**:
- [Opportunity 1 - e.g., "Strategic partnership accelerates distribution"]
- [Opportunity 2 - e.g., "Market tailwind (new regulation drives demand)"]
- [Opportunity 3 - e.g., "Product-led growth loop stronger than expected"]

---

## Assumptions & Risks

### Critical Assumptions

#### Assumption 1: [Name] - [Value] - Confidence: [High/Medium/Low]

**What we assumed**: [Specific assumption - e.g., "10% free-to-paid conversion rate"]

**Why we believe it**:
- [Data source / benchmark - e.g., "B2B SaaS average is 8-12% (ChartMogul)"]
- [Journey rationale - e.g., "Our time-to-value is faster than average"]
- [Competitive analysis - e.g., "Competitors report similar rates"]

**How to validate** (next 90 days):
- [Validation method 1 - e.g., "Launch freemium, measure actual 30/60/90-day conversion"]
- [Validation method 2 - e.g., "A/B test pricing page variants"]
- [Validation method 3 - e.g., "Interview 10 free users who didn't convert"]

**If we're wrong** (sensitivity analysis):
```
IF conversion is 7% (30% lower):
  → Year 1 ARR: $[XXX]k → $[XXX]k (-30%)
  → Break-even: Month [XX] → Month [XX] (+5 months)
  → Funding needed: +$[XXX]k

IF conversion is 13% (30% higher):
  → Year 1 ARR: $[XXX]k → $[XXX]k (+30%)
  → Break-even: Month [XX] → Month [XX] (-3 months)
  → Funding needed: -$[XX]k
```

---

#### Assumption 2: [Name] - [Value] - Confidence: [High/Medium/Low]

[Repeat structure for 4-6 critical assumptions]

---

### Key Risks & Mitigations

#### Risk 1: [Risk Name] - Likelihood: [High/Med/Low] - Impact: [High/Med/Low]

**Description**: [What could go wrong?]

**Impact on model**:
- [Financial impact - e.g., "Increases CAC by 50%, extends payback to 18 months"]
- [Timeline impact - e.g., "Delays break-even by 6 months"]
- [Funding impact - e.g., "Requires additional $XXXk"]

**Early warning signs**:
- [Sign 1 - e.g., "Month 3: If conversion < 5%"]
- [Sign 2 - e.g., "Month 6: If CAC > $XXX"]

**Mitigation strategy**:
1. [Action 1 - e.g., "Invest in education content upfront"]
2. [Action 2 - e.g., "Build ROI calculator to demonstrate value"]
3. [Action 3 - e.g., "Offer free assessments to prove value"]

**Contingency plan** (if risk materializes):
- [Contingency 1 - e.g., "Pivot messaging to pain-first approach"]
- [Contingency 2 - e.g., "Add 'done-for-you' service tier"]
- [Contingency 3 - e.g., "Extend runway, reduce burn rate"]

---

#### Risk 2: [Risk Name] - Likelihood: [High/Med/Low] - Impact: [High/Med/Low]

[Repeat structure for 5-7 key risks]

---

### Sensitivity Analysis

**Impact of +/- 20% change in key variables**:

| Variable | -20% | Base | +20% | Most Sensitive Outcome |
|----------|------|------|------|------------------------|
| **Conversion Rate** | $[XXX]k ARR | $[XXX]k ARR | $[XXX]k ARR | [Impact] |
| **Churn Rate** | $[XXX]k ARR | $[XXX]k ARR | $[XXX]k ARR | [Impact] |
| **CAC** | $[XXX]k funding | $[XXX]k funding | $[XXX]k funding | [Impact] |
| **ARPU** | $[XXX]k ARR | $[XXX]k ARR | $[XXX]k ARR | [Impact] |
| **Growth Rate** | Month [XX] BE | Month [XX] BE | Month [XX] BE | [Impact] |

**Most sensitive variables** (biggest impact on outcomes):
1. [Variable 1] - [Why most sensitive]
2. [Variable 2] - [Why most sensitive]
3. [Variable 3] - [Why most sensitive]

**Focus areas**: Prioritize validating and optimizing the most sensitive variables.

---

## Financial Milestones

### Milestone 1: First Dollar - Target: Month [X]

**Goal**: First paying customer (validates willingness to pay)

**Success Criteria**:
- [ ] ≥1 paying customer
- [ ] $[X]+ MRR
- [ ] Customer completes journey (activation → value delivery)

**Requirements to hit**:
- Product: [What product state needed]
- Team: [What team composition needed]
- Marketing: [What marketing/sales needed]
- Funding: [How much capital deployed]

**What this validates**:
- Journey delivers value (someone will pay)
- Pricing is acceptable (at least to one persona)
- Path to revenue exists

**What comes next**: Prove repeatability (10 customers)

---

### Milestone 2: $10k MRR - Target: Month [X]

**Goal**: Repeatability proven (validates business model)

**Success Criteria**:
- [ ] $10,000 MRR
- [ ] [XXX]+ active customers
- [ ] [X]% monthly churn or lower
- [ ] At least 2 acquisition channels working

**Requirements to hit**:
- Product: [Product state needed]
- Team: [Team size/composition]
- Marketing: [Marketing/sales state]
- Funding: $[XXX]k deployed

**What this validates**:
- Multiple customers see value (not a fluke)
- Acquisition channels work
- Business model is viable

**What comes next**: Prepare to scale ($100k MRR)

---

### Milestone 3: Break-Even - Target: Month [XX]

**Goal**: Cashflow positive (sustainable without funding)

**Success Criteria**:
- [ ] Revenue ≥ Total Costs
- [ ] $[XX]k+ MRR
- [ ] [XXX]+ customers
- [ ] LTV:CAC ≥ 3:1
- [ ] Churn ≤ [X]%

**Requirements to hit**:
- Product: [Product maturity]
- Team: [X] people
- Marketing: [Marketing state]
- Funding: $[XXX]k total deployed

**What this validates**:
- Business is sustainable
- Unit economics work at scale
- Can grow without external capital (choose to vs. need to)

**What comes next**: Accelerate growth ($100k MRR)

---

### Milestone 4: $100k MRR - Target: Month [XX]

**Goal**: Scale readiness (Series A fundable)

**Success Criteria**:
- [ ] $100,000 MRR ($1.2M ARR)
- [ ] [X,XXX]+ customers
- [ ] [XX]%+ YoY growth
- [ ] 3+ channels contributing customers
- [ ] NRR ≥ [XXX]%

**Requirements to hit**:
- Product: [Product state]
- Team: [XX] people
- Marketing: [Marketing state]
- Funding: $[XXX]k total deployed

**What this validates**:
- Proven channel-market fit
- Scalable customer acquisition
- Ready for growth capital

**What comes next**: Market leadership ($1M ARR)

---

### Milestone 5: $1M ARR - Target: Month [XX]

**Goal**: Market validation (category leadership)

**Success Criteria**:
- [ ] $1,000,000 ARR
- [ ] [XX,XXX]+ customers
- [ ] Market leader or #2 in category
- [ ] [XX]%+ EBITDA margin (or path to profitability)
- [ ] Brand recognition in target market

**Requirements to hit**:
- Product: [Product state]
- Team: [XX]+ people
- Marketing: [Marketing state]
- Funding: $[X]M+ total deployed

**What this validates**:
- Significant market opportunity
- Sustainable competitive advantage
- Long-term business viability

**What comes next**: Continue scaling, profitability, potential exit paths

---

## Model Validation & Updates

**This model should be updated**:
- ✅ Monthly: Update actuals vs. projections
- ✅ Quarterly: Revise assumptions based on learnings
- ✅ Annually: Rebuild model with actual data

**Tracking against model**:

| Metric | Projected (Month X) | Actual (Month X) | Variance | Action |
|--------|---------------------|------------------|----------|--------|
| MRR | $[XX]k | $[XX]k | +/- [X]% | [What to do] |
| Customers | [XXX] | [XXX] | +/- [X]% | [What to do] |
| CAC | $[XXX] | $[XXX] | +/- [X]% | [What to do] |
| Churn | [X]% | [X]% | +/- [X]% | [What to do] |
| Burn Rate | $[XX]k | $[XX]k | +/- [X]% | [What to do] |

**Variance thresholds**:
- ± 10%: Normal variance, continue monitoring
- ± 20%: Investigate cause, may need model adjustment
- ± 30%+: Significant variance, revise assumptions

**Model evolution**:
- **Months 0-6**: Heavy assumptions, low confidence, update frequently
- **Months 6-12**: Some actuals, medium confidence, monthly updates
- **Months 12-24**: Strong actuals, high confidence, quarterly updates
- **Months 24+**: Mature model, forecast vs. actual analysis, annual rebuild

---

## Appendix: Calculations & Formulas

### Core Formulas

```
LTV = (ARPU × Gross Margin) / Churn Rate

CAC = (Marketing Spend + Sales Spend) / New Customers

LTV:CAC Ratio = LTV / CAC

Payback Period = CAC / (ARPU × Gross Margin)

Gross Margin % = (Revenue - COGS) / Revenue

Break-even Customers = Fixed Costs / (ARPU × Gross Margin)

MRR = Total Active Customers × Blended ARPU

ARR = MRR × 12

NRR = (Starting MRR + Expansion - Churn - Contraction) / Starting MRR

Burn Rate = Revenue - (COGS + OpEx)

Runway (months) = Cash Balance / Monthly Burn Rate
```

---

## Next Steps

1. **Validate critical assumptions**: [List top 3 assumptions to test next]
2. **Track actuals vs. projections**: Set up dashboard to monitor key metrics
3. **Update quarterly**: Revise model based on learnings
4. **Share with stakeholders**: Use for investor pitches, board meetings, team alignment
5. **Run `/cascade-status`** to see your complete framework progress

---

**Model Version**: 1.0
**Created**: [Date]
**Last Updated**: [Date]
**Next Review**: [Date + 90 days]
