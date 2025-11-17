# Monetization Strategy: Compliance Assessment Platform

> **Context**: This is a completed example. Pricing aligned with value delivery moment (Step 3: AI Assessment).

---

## Pricing Model

**Hybrid**: Freemium + Pay-As-You-Go with subscription option

**Rationale**:
- Freemium allows risk-free trial (compliance officers need to validate accuracy)
- Pay-as-you-go aligns cost with value (pay only when you get value)
- Subscription option for predictability (finance teams prefer fixed costs)

---

## Pricing Tiers

### Free
- **100 assessments/month**
- Basic compliance frameworks (SOC2, GDPR, HIPAA)
- Community support (documentation + forum)
- 30-day history retention

**Purpose**: Validation tier - prove accuracy and value before commitment

### Pay-As-You-Go
- **$0.10 per document assessed**
- All compliance frameworks (15+ frameworks)
- Email support (24-hour response)
- 12-month history retention
- API access
- No monthly minimum

**Purpose**: Flexibility for variable usage, perfect for small teams

### Business ($299/month)
- **3,500 assessments/month included** (effective rate: $0.085/assessment)
- Additional assessments: $0.08 each
- All frameworks + custom framework creation
- Priority email + chat support
- Unlimited history retention
- Advanced API access + webhooks
- Team collaboration features

**Purpose**: Best value for regular users, predictable costs

### Enterprise (Custom Pricing)
- **Volume pricing for >10,000 assessments/month**
- Dedicated compliance frameworks
- SSO + advanced security
- SLA (99.9% uptime)
- Dedicated support + CSM
- Custom integrations
- On-premise deployment option (for highly regulated industries)

**Purpose**: Large organizations with specific compliance/security needs

---

## Value Metric Justification

**We charge per assessment** because:

1. ✅ **Aligns with value delivery**: Each assessment saves 2-4 hours ($150-300 value)
2. ✅ **Users can predict costs**: "I assess 50 docs/month = $5 cost, ~$7,500 savings"
3. ✅ **Fair for variable usage**: Some months are heavy, some are light
4. ✅ **Natural expansion**: Successful users assess more documents
5. ✅ **Simple to understand**: No "credits" or abstract units

**Value Ratio**:
- User pays: $0.10 per assessment
- User saves: $150-300 in time (2-4 hours × $75/hour loaded cost)
- **ROI: 1,500x - 3,000x per assessment**

---

## Pricing Psychology Applied

### Anchor High with Annual Discount
```
Business: $299/month ($3,588/year)
Business Annual: $2,990/year (save $598, ~17%)
```

### Free Tier is Generous (But Limited)
- 100 free assessments = $10 of value if paid
- Enough to validate product (2-3 months of light usage)
- Creates natural upgrade path when users exceed limit

### Business Tier is Obviously Best Value
- PAYG: 3,500 assessments = $350
- Business: 3,500 assessments + features = $299
- Savings clear, drives tier selection

### Enterprise is "Contact Us"
- Not trying to productize every edge case
- Signals premium, custom service
- Allows negotiation for large deals

---

## Unit Economics

### Current Metrics
- **ARPU**: $205/month (mix of PAYG and Business tiers)
- **Gross Margin**: 85% (low infrastructure costs per assessment)
- **Monthly Churn**: 6%
- **Avg Customer Lifetime**: ~17 months
- **LTV**: $205 × 0.85 × 17 = $2,962

### Target CAC
- **LTV:CAC Target**: 3:1
- **Max CAC**: $987
- **Current CAC**: $1,050 (slightly high, improving with referrals)

### Revenue Targets
- **Current MRR**: $18,400
- **30-day Goal**: $25,000 MRR
- **90-day Goal**: $50,000 MRR
- **12-month Goal**: $200,000 MRR (path to $2.4M ARR)

---

## Monetization by Customer Segment

### Individual Compliance Officer
- **Tier**: Pay-As-You-Go
- **Usage**: 20-50 assessments/month
- **Revenue**: $2-5/month
- **Value**: Time savings justify upgrade to Business at higher volume

### Small Compliance Team (2-5 people)
- **Tier**: Business
- **Usage**: 200-500 assessments/month
- **Revenue**: ~$299/month (included in plan)
- **Value**: Predictable costs, team features

### Enterprise Compliance Department (10+ people)
- **Tier**: Enterprise
- **Usage**: 1,000-10,000+ assessments/month
- **Revenue**: $2,000-15,000/month (custom pricing)
- **Value**: Security, SLA, dedicated support, custom frameworks

---

## Expansion Strategy

### Natural Expansion Path
1. **Start**: Free tier → validate product
2. **Grow**: Exceed 100/month → upgrade to PAYG
3. **Scale**: Consistent 200+ assessments → upgrade to Business for savings
4. **Enterprise**: Team growth + security requirements → Enterprise

### Expansion Revenue Drivers
- **Usage Growth**: Users assess more documents over time (20 → 50 → 100/month)
- **Team Growth**: Individual → team → department
- **Feature Upgrades**: API access, custom frameworks, integrations
- **Net Revenue Retention Target**: 110% (users expand usage faster than churn)

---

## Pricing Experiments Completed

### Experiment 1: Price Point
- Tested: $0.05 vs $0.10 vs $0.15 per assessment
- Result: $0.10 optimal (conversion barely changed, revenue up 40%)
- Learning: Value is so high that price sensitivity is low up to $0.15

### Experiment 2: Free Tier Limit
- Tested: 50 vs 100 vs 200 free assessments
- Result: 100 is sweet spot (75% hit limit and convert, 50 had high bounce)
- Learning: Too stingy = distrust, too generous = no conversion urgency

### Experiment 3: Business Tier Pricing
- Tested: $199 vs $299 vs $399
- Result: $299 maximum revenue per visitor
- Learning: Business buyers care more about value than price

---

## Revenue Instrumentation

### Tracking Implementation (see ../stack/04-tech-stack.md for tech)

**Metering**:
- Event: `assessment_completed`
- Attributes: `user_id`, `team_id`, `framework`, `timestamp`, `document_size`
- Storage: PostgreSQL `usage_events` table

**Billing**:
- Provider: Stripe
- Sync: Real-time usage → Stripe metered billing
- Invoicing: Automatic monthly for PAYG, upfront for Business

**Limits**:
- Free tier: Redis counter `assessments:{user_id}:{month}`
- Gate: Check before allowing assessment submission
- UX: Show "80% of free limit used" warnings

**Upgrades**:
- Trigger: In-app prompt at 80%, 90%, 100% of free limit
- Flow: Self-serve Stripe Checkout
- Fallback: Sales assist for Enterprise

**Transparency**:
- Dashboard: Real-time usage counter in header
- Billing page: Current month usage + projected cost
- Alerts: Email at 80% of plan limit

---

## Connection to Other Strategy

**From Journey**: We charge at Step 3 (AI Assessment) - where value is delivered

**From Mission**: Charge for speed of assessment - our core promise

**To Metrics**: Revenue metrics (MRR, ARPU) tie to North Star (more assessments = more revenue)

**To Tech Stack**: Stripe integration, PostgreSQL usage tracking, Redis rate limiting

---

## Common Questions

**Q: Why not charge per user?**
A: Usage varies wildly per person (some assess 5 docs/month, others 100). Per-assessment is fairer.

**Q: Why PAYG option when Business has better unit economics?**
A: Removes barrier to entry. Many users start PAYG, grow into Business. Acquisition > optimization at this stage.

**Q: What if users game the free tier?**
A: 100/month is generous but not exploitable. Would need 10 fake accounts to avoid paying $10/month - not worth it.

**Q: How do you handle failed assessments?**
A: Don't charge. Only completed assessments count. Builds trust.

---

**Next in Cascade**: Monetization requirements inform tech stack decisions (Stripe integration, usage tracking, rate limiting architecture).
