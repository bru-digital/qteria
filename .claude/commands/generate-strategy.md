---
description: Session 4 - Generate tactical foundation (mission, metrics, monetization, architecture)
---

# Session 4: Generate Strategy

This is **Session 4** of the cascade. You'll synthesize the user journey, product strategy, and tech stack into a complete tactical foundation.

## Your Role

You are a product strategist deriving tactical decisions from previous cascade outputs. Your job is to:

1. **Read** journey (`product-guidelines/00-user-journey.md`), product strategy (`product-guidelines/01-product-strategy.md`), and tech stack (`product-guidelines/02-tech-stack.md`)
2. **Derive mission** from the journey's aha moment (usually Step 3)
3. **Define North Star metric** that measures mission fulfillment
4. **Design monetization** aligned with value delivery
5. **Establish architecture principles** based on journey + tech stack

## Critical Philosophy

**Every strategic decision must trace back to the user journey.**

- Mission → Promises the journey outcome (Step 3 value)
- North Star → Measures journey completion
- Monetization → Charges where journey delivers value
- Architecture → Optimizes journey critical path

## Process

### Step 1: Read Previous Outputs

```
Read: product-guidelines/00-user-journey.md
Read: product-guidelines/11-product-strategy-essentials.md
Read: product-guidelines/02-tech-stack.md
```

**Context Optimization**: We read the essentials version of product strategy (~65% smaller). It contains vision, positioning, strategic goals, and product principles—sufficient for generating mission, metrics, monetization, and architecture without detailed market analysis.

**Extract from Journey**:

- Step 3 (aha moment) - where primary value is delivered
- Economic value (time/money saved, ROI)
- Primary user persona
- Success metrics already defined

**Extract from Product Strategy**:

- Product vision (3-5 year aspirational future)
- Strategic goals
- Product principles

**Extract from Tech Stack**:

- Core technologies chosen
- Journey-tech mappings
- Technical constraints/capabilities

### Step 2: Derive Mission Statement

**Formula**: "We help [user persona] [achieve outcome] by [unique approach]"

**How to Derive**:

1. User persona: From journey (primary user)
2. Achieve outcome: From journey Step 3 (aha moment value)
3. Unique approach: From tech stack + journey (how you deliver value differently)

**Example**:

- Journey Step 3: "Compliance officer gets assessment results in 2 minutes instead of 2 hours"
- Tech Stack: Claude API + FastAPI for AI-powered analysis
- Mission: "We help compliance officers approve documents 10x faster by transforming framework requirements into automated AI assessments"

**Validation**:

- Does it reference the journey aha moment? ✅
- Is it specific (not generic)? ✅
- Does it promise measurable outcome? ✅

### Step 3: Define North Star Metric

**Formula**: North Star = [Core Action] in journey

**How to Derive**:

1. What action represents Step 3 value delivery?
2. That's your North Star

**Example**:

- Journey Step 3: AI assessment completed
- North Star: "Weekly Active Assessments" (measures mission fulfillment)

**Input Metrics** (what drives North Star):

- Break down North Star into components
- Example: `Active Assessments = Active Users × Assessments per User × Completion Rate`
- Define 3-5 input metrics

**Health Metrics**:

- Retention (D7, D30)
- NPS
- Error rates
- API performance

**Counter-Metrics**:

- What won't you sacrifice to improve North Star?
- Example: Won't improve assessment speed by reducing accuracy

### Step 4: Design Monetization

**Principle**: Charge where value is delivered (journey Step 3)

**How to Derive**:

1. Identify value delivery moment: Journey Step 3
2. What unit of value? (per assessment, per user, per feature unlocked?)
3. Calculate value ratio: What user gets ÷ What user pays (target: 10:1+)

**Model Selection**:

- **Freemium**: If low marginal cost, viral potential
- **Pay-as-you-go**: If variable usage, clear value per unit
- **Subscription**: If predictable usage, enterprise customers
- **Hybrid**: Combine for flexibility

**Pricing Tiers**:

- Free: Generous enough to validate, limited enough to convert
- Paid: Aligned with value metric, clear upgrade path
- Enterprise: Custom for specific needs (SSO, SLA, etc.)

**Example**:

- Value delivered: Each assessment saves 2-4 hours ($150-300 value)
- Pricing: $0.10 per assessment
- Value ratio: 1,500x - 3,000x
- Model: Freemium (100 free) + PAYG ($0.10 each) + Business ($299/month includes 3,500)

### Step 5: Establish Architecture Principles

**How to Derive** (from journey + tech stack):

**Critical Path Optimization**:

- Journey Step 3 is critical → Optimize this path
- Example: "Assessment processing <60 seconds" → Async architecture, progress indicators

**Tech Stack Patterns**:

- Based on chosen tech, establish patterns
- Example: "PostgreSQL JSONB for flexible assessment results, Redis for framework caching"

**Principles** (typically 3-5):

1. Journey-step optimization (optimize critical path, not theoretical scale)
2. Boring technology + strategic innovation (proven tech 90%, innovate 10%)
3. API-first design (enables integrations)
4. Fail-safe (compliance = reliability critical)
5. Observable (measure everything)

## Generating the Outputs

Create 4 files:

### 1. `product-guidelines/03-mission.md`

Use `/templates/03-mission-template.md`.

**Key Sections**:

- Mission statement (one sentence)
- Who we serve, value delivered, how we're different
- Mission tests (feature, partnership, hiring decisions)
- Connection to journey (which step), to metrics (North Star), to monetization

### 2. `product-guidelines/04-metrics.md`

Use `/templates/04-metrics-template.md`.

**Key Sections**:

- North Star metric (definition, why, targets)
- Input metrics (3-5 that drive North Star, with formula)
- Health metrics (engagement, retention, revenue, product health)
- Counter-metrics (what won't sacrifice)
- Connection to journey steps, to monetization

### 3. `product-guidelines/04-monetization.md`

Use `/templates/04-monetization-template.md`.

**Key Sections**:

- Pricing model (with rationale from journey)
- Pricing tiers (Free, Paid, Enterprise with clear purpose)
- Value metric justification (why this unit, value ratio calculation)
- Unit economics (ARPU, LTV, CAC targets)
- Revenue targets (30/90/365 days)
- Connection to journey (where charged), mission (what charged for)

### 4. `product-guidelines/04-architecture.md`

Use `/templates/04-architecture-template.md`.

**Key Sections**:

- Architecture overview (diagram if helpful)
- Core principles (3-5, journey-derived)
- Data flow for critical journey step
- Database schema (key tables)
- Scaling strategy (current capacity, bottlenecks)
- Connection to journey (optimizes Step X)

## Validation Checklist

Before writing files:

- [ ] Mission references journey aha moment?
- [ ] North Star measures mission outcome?
- [ ] Monetization charges where value delivered?
- [ ] Pricing has clear value ratio (10:1+)?
- [ ] Architecture optimizes journey critical path?
- [ ] All decisions trace to journey?

## After Generation

Show summary:

```
✅ Session 4 complete! Tactical foundation established.

Your Strategy:
📋 Mission: [One-sentence mission]
📊 North Star: [Metric name]
💰 Pricing: [Model summary]
🏗️  Architecture: [Key principle]

Files created:
- product-guidelines/03-mission.md
- product-guidelines/04-metrics.md
- product-guidelines/04-monetization.md
- product-guidelines/04-architecture.md

Next, we'll create a brand strategy that expresses your journey value.

When ready, run: /create-brand-strategy
Or check progress: /cascade-status
```

## Important Guidelines

1. **Trace everything to journey**: Don't invent new personas/problems
2. **Be specific**: Use actual numbers from journey (time saved, cost, etc.)
3. **Show connections**: Explicitly link mission→metrics→monetization
4. **Validate value ratio**: User should get 10x+ what they pay
5. **Keep architecture simple**: Optimize for journey, not theoretical scale

## Reference Files

- Templates: `/templates/03-mission-template.md`, `/templates/04-metrics-template.md`, `/templates/04-monetization-template.md`, `/templates/04-architecture-template.md`
- Examples: `/examples/compliance-saas/foundation/` and `/examples/compliance-saas/stack/`

---

**Now, read the journey, product strategy, and tech stack, then generate all 4 tactical foundation files!**
