# Monetization Strategy: Qteria

> **Derived from**: product-guidelines/00-user-journey.md (Charge where value is delivered)

---

## Pricing Model

**Annual Subscription (Enterprise B2B)**

**Rationale**:

- **Journey fit**: TIC notified bodies plan annual budgets, prefer predictable costs over usage-based surprise bills
- **Value delivery**: Value is continuous (replace $100K/year India team with $30K/year AI platform), not per-transaction
- **Sales cycle**: Enterprise B2B with 3-6 month sales cycles → annual contracts natural fit
- **Simplicity**: Users can run unlimited assessments without usage anxiety (aligns with "run more, get more value" behavior)
- **Cash flow**: Upfront annual payment supports runway for solo founder bootstrapping

**NOT Usage-Based** (per assessment):

- ❌ Creates usage anxiety (Project Handlers might hesitate to re-run assessments, reducing value)
- ❌ Doesn't match budget planning (finance teams want fixed annual cost, not variable)
- ❌ Misaligned incentive (we want MORE assessments, charging per assessment discourages use)

**Alternative Considered**: Usage-based might work for marketplace (consultants selling workflows), but core platform is subscription.

---

## Pricing Tiers

### Pilot / Trial (Custom Engagement)

- **Price**: Free for 30-day pilot, then $30K/year
- **Includes**:
  - Unlimited workflows, users, assessments
  - White-glove onboarding (founder-led)
  - Dedicated relationship manager (founder)
  - Co-development input (pilot feedback shapes roadmap)
- **Support**: Direct founder access (email, calls, video)

**Purpose**: Land TÜV SÜD and other first 5 customers. Validate product-market fit. Generous trial removes adoption friction.

**Target Customer**: Large TIC notified bodies (TÜV SÜD, BSI, TÜV Rheinland, DEKRA, SGS)

---

### Professional ($30K/year)

- **Price**: $30,000/year per notified body (billed annually)
- **Includes**:

  - Unlimited workflows
  - Unlimited document buckets & criteria
  - Unlimited assessments
  - Unlimited Project Handlers & Process Managers
  - Evidence-based AI validation (<10 min processing)
  - PDF export of validation reports
  - Standard security (encryption at rest/transit, audit logs)
  - Email support (24-hour response SLA)
  - Quarterly business review with relationship manager

- **Does NOT Include** (Enterprise only):
  - SSO/SAML
  - Custom SLA (99.99% uptime)
  - Dedicated infrastructure
  - On-premise deployment
  - Custom AI model training

**Purpose**: Core offering for mid-to-large TIC notified bodies. Replaces $100K/year India outsourcing with 70% cost savings.

**Target Customer**: Notified bodies running 300-500 assessments/month (15-20/day)

---

### Enterprise (Custom Pricing, Starting $50K/year)

- **Price**: Custom (typically $50K-100K/year)
- **Includes** (everything in Professional, plus):
  - SSO/SAML integration (Okta, Azure AD, etc.)
  - Custom SLA (99.99% uptime, <15 min support response)
  - Dedicated AI model training (fine-tuned on customer's validation patterns)
  - API access for integration with existing project management tools
  - On-premise deployment option (if data privacy requires)
  - Custom legal/compliance (BAA, custom DPA, etc.)
  - Weekly check-ins with relationship manager
  - Priority feature development

**Purpose**: Very large notified bodies or multi-site organizations with specific compliance requirements

**Target Customer**: Top-tier notified bodies (BSI, TÜV SÜD if they need custom features), large MedTech consulting firms

---

## Value Metric Justification

**We charge per notified body (annual subscription)** because:

1. ✅ **Aligns with value delivery**: Value is continuous replacement of $100K/year India team. Saving $70K/year justifies $30K/year cost (3:1 ROI on direct savings alone).

2. ✅ **Users can predict costs**: Finance teams plan annual budgets. "$30K/year" is clear and predictable. "Unknown cost depending on volume" creates procurement friction.

3. ✅ **Fair for variable usage**: Some notified bodies run 200 assessments/month, others 600. Unlimited usage means both get value without penalty for high use.

4. ✅ **Natural expansion**: As notified body grows (more product types, more clients), they run more assessments → get more value → justify renewal and potential upsell to Enterprise tier.

5. ✅ **Encourages habit formation**: No usage anxiety. Project Handlers can re-run assessments freely (Step 4 in journey), experiment with workflows, train new team members.

**Value Ratio Calculation**:

**User pays**: $30,000/year

**User saves**:

- Direct cost: $100K/year (India team) → $30K/year (Qteria) = **$70K/year saved**
- Time value: 1-2 days → 10 minutes per assessment = ~400x faster
  - 500 assessments/month × 1.5 days saved each = 750 days/month = 25 days/day (equivalent to 25 person-days freed up)
  - 25 person-days × $500/day (Certification Person hourly cost) × 12 months = **$150K/year in time value** (conservative)
- Quality improvement: Fewer clarification rounds = faster certification pipeline = revenue acceleration (hard to quantify, but meaningful)

**Total value**: $70K direct + $150K time = **$220K/year**

**ROI**: $220K value ÷ $30K cost = **7.3:1** (meets 10:1 target when including quality improvements)

**Per-assessment cost** (for internal calculation):

- $30K/year ÷ 500 assessments/month ÷ 12 months = **$5 per assessment** to customer
- Value per assessment: $150-300 (time saved)
- **Per-assessment ROI**: 30-60x

---

## Unit Economics

### Target Metrics

**Year 1 (2026 - TÜV SÜD pilot)**:

- **ARPU** (Average Revenue Per User): $30,000/year (only 1 customer)
- **Gross Margin**: 95%+ (revenue $30K, costs ~$1.5K AI + infrastructure)
- **LTV** (Lifetime Value): $150K (assume 5-year retention, 95% margin)
  - Calculation: $30K/year × 5 years × 95% margin = $142.5K ≈ $150K
- **Target CAC** (Customer Acquisition Cost): <$10K (to achieve 15:1 LTV:CAC)
  - Year 1 CAC: $0 (founder relationship with TÜV SÜD)
  - Year 2+ CAC: ~$5-10K (sales time, travel to conferences, demo costs)

**Year 3 (2027 - 5 customers)**:

- **ARPU**: $30,000/year (consistent per customer)
- **Total ARR**: $150,000 (5 customers × $30K)
- **Gross Margin**: 97%+ (revenue $150K, costs ~$5K infrastructure + AI)
- **LTV**: $150K per customer
- **Actual CAC**: ~$5K per customer (reference selling from TÜV SÜD, low-cost acquisition)
- **LTV:CAC Ratio**: 30:1 (exceptional)

**Year 5 (2029 - 20 customers, path to sustainability)**:

- **ARPU**: $35,000/year (10% price increase after product maturity)
- **Total ARR**: $700,000 (20 customers × $35K)
- **Gross Margin**: 95%+ (revenue $700K, costs ~$35K infrastructure + AI)
- **LTV**: $175K per customer (5 years × $35K × 95%)
- **Target CAC**: <$15K (3-6 month sales cycles, travel, demos, trials)
- **LTV:CAC Ratio**: 11:1 (healthy SaaS)

### Revenue Targets

**30-day Goal** (Q2 2026 - TÜV SÜD pilot contract signed):

- **MRR**: $2,500 ($30K annual ÷ 12 months)
- **Milestone**: First paying customer, product-market fit validated

**90-day Goal** (Q3 2026 - TÜV SÜD production, expanding usage):

- **MRR**: $2,500 (same customer, proving retention)
- **Milestone**: 500 assessments/month, NPS 50+, preparing for customer #2

**12-month Goal** (Q2 2027 - expand to 3-4 customers):

- **ARR**: $90K-120K (3-4 customers × $30K)
- **MRR**: $7.5K-10K
- **Milestone**: TÜV SÜD renewed (100% retention), reference case study drives 2-3 new customers

**24-month Goal** (Q2 2028 - expand to 10 customers):

- **ARR**: $300K (10 customers × $30K)
- **MRR**: $25K
- **Milestone**: Proven playbook (onboard, activate, retain), ready to scale

---

## Pricing Experiments & Optionality

### Future Pricing Levers (Post-MVP)

**1. Usage-Based Add-On** (Marketplace):

- When consultants publish workflows on marketplace (2027+), charge per workflow license
- Example: Consultant creates "Medical Device Class III" workflow, licenses it for $500/year to other notified bodies
- Qteria takes 20-30% platform fee
- Expands TAM beyond direct sales (consultants create workflows, Qteria distributes)

**2. Tiered Seat Pricing** (If Customer Demand):

- Some notified bodies might want "Starter" tier for small teams
- Example: $15K/year for 5 users, $30K/year for unlimited users
- Only introduce if customers explicitly request lower-cost entry point (not needed for Year 1-2)

**3. Multi-Year Discounts** (Enterprise Retention):

- Offer 10-15% discount for 3-year contracts (e.g., $85K for 3 years vs. $90K)
- Locks in customers, improves cash flow
- Only offer after Year 2 when retention proven

**4. Premium Support SLA** (Add-On):

- Charge +$10K/year for dedicated Slack channel, <1 hour support response, 99.99% uptime SLA
- Only offer to Enterprise tier customers who explicitly need it

---

## Pricing Psychology & Positioning

### Why $30K (Not $20K or $50K)?

**$30K is the "Goldilocks" price**:

✅ **Saves customer 70%** ($100K → $30K) = compelling ROI
✅ **High enough to signal quality** (not "too cheap to be good")
✅ **Low enough to avoid C-suite approval** (many notified bodies have <$50K procurement thresholds for department heads)
✅ **Annual software budget-friendly** ($2.5K/month feels manageable vs. $5-10K/month SaaS tools)

**Anchoring to India Team Cost**:

- Sales pitch: "You're paying $100K/year for 1-2 day turnaround. What if you got 10-minute turnaround for $30K?"
- **Perceived value**: 70% cost savings + 400x speed = "no-brainer"

**NOT $20K**:

- Leaves $20K value on table (customer saves $80K instead of $70K, we capture less)
- Signals "budget tool" instead of "premium solution"

**NOT $50K**:

- Harder to justify (only $50K savings vs. $70K at $30K price)
- Triggers higher approval thresholds (CEO/CFO sign-off vs. VP-level at $30K)

---

## Sales Cycle & Payment Terms

**Sales Cycle** (Enterprise B2B):

1. **Initial Contact** (Week 0): Warm intro (TÜV SÜD reference) or conference connection
2. **Discovery Call** (Week 1-2): Understand their India team cost, pain points, validation workflows
3. **Demo** (Week 3-4): Show workflow creation → document upload → AI validation → results (15-min end-to-end demo)
4. **Pilot Proposal** (Week 5-6): 30-day free pilot with co-development agreement
5. **Pilot Execution** (Week 7-18): 3 months of hands-on usage, weekly check-ins, iterate on feedback
6. **Contract Negotiation** (Week 19-22): Legal review, security audit, pricing discussion
7. **Contract Signed** (Week 24): First $30K payment

**Total**: ~6 months from first contact to closed deal

**Payment Terms**:

- **Year 1-2**: Annual prepayment (full $30K upfront) - improves cash flow for bootstrapping
- **Year 3+**: Option for quarterly payments ($7.5K × 4) if customers prefer - reduces friction, but less cash upfront

**Pilot-to-Paid Conversion**:

- Target: 80%+ (high-touch pilot with founder involvement, co-development alignment = strong commitment)
- If pilot fails, understand why (AI accuracy? UX issues? Data privacy concerns?) and fix before next customer

---

## Expansion & Upsell Strategy

**Year 1-2: Land & Prove Value**

- Focus: Sign first 5 customers at $30K/year, prove 100% retention, build reference case studies
- No upsell yet (keep it simple, validate core product)

**Year 3+: Expand Within Accounts**

- **Upsell to Enterprise tier** ($50K+): When customers request SSO, custom SLA, API access
- **Cross-sell to sister organizations**: TÜV SÜD Germany → TÜV SÜD USA, UK, etc. (same workflows, different geographies)
- **Marketplace workflows**: Customers create workflows, license to other notified bodies, Qteria takes platform fee

**Target Net Revenue Retention**: 120%+ by Year 5

- 100% retention (no churn)
- +20% expansion (upsells to Enterprise, cross-sells to sister orgs, marketplace revenue)

---

**Connection to Other Strategy**:

**From Journey**: We charge at **Step 3** (AI Validates & Returns Evidence-Based Results) where value is delivered - users pay annual subscription to access platform that runs unlimited assessments in <10 minutes instead of waiting 1-2 days for India team

**From Mission**: Charge for delivering mission outcome - "validate documents 400x faster" = $30K/year subscription that replaces $100K/year India team (70% savings + 400x speed = clear ROI)

**To Metrics**:

- **Revenue metrics tie to North Star**: More Active Assessments Per Month = more value delivered = higher retention + expansion likelihood
- **ARR growth formula**: Active Customers × $30K/year = ARR (direct correlation)
- **Expansion metric**: Net Revenue Retention (100% base + upsells) measured quarterly

**To Product Principles**:

- **Simplicity Over Features**: Unlimited usage (no metering complexity) keeps product simple
- **White-Glove Support**: Relationship manager included in price (not separate support tier)
- **Data Privacy Non-Negotiable**: Enterprise tier offers custom DPA, BAA (charge for compliance needs)

**Pricing Validation Questions**:

- ✅ Does $30K align with value delivered? YES - 7:1 ROI ($220K value)
- ✅ Can customers afford it? YES - replacing $100K/year spend
- ✅ Can we deliver profitably? YES - 95%+ gross margin
- ✅ Does it support growth? YES - $30K × 20 customers = $600K ARR in Year 5 supports family + wealth building goal
