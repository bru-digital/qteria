---
description: POST-CASCADE - Create data-driven growth strategy with acquisition channels, growth loops, and experiments
---

# POST-CASCADE: Design Growth Strategy

This is a **post-core extension** that creates a comprehensive, data-driven growth strategy. Run this AFTER you've completed Session 4 (tactical foundation with metrics and monetization) to design how you'll acquire, activate, retain, and expand your user base.

## When to Run This

**Run AFTER Session 4+** when you have:
- ✅ User journey defined (`product-guidelines/00-user-journey.md`)
- ✅ Product strategy validated (`product-guidelines/01-product-strategy.md`)
- ✅ Metrics established (`product-guidelines/04-metrics.md`)
- ✅ Monetization model defined (`product-guidelines/04-monetization.md`)

**Ideally after Session 7+** when you also have:
- ✅ Backlog generated (`product-guidelines/09-backlog/`)
- So growth experiments can be prioritized in development

**Skip this** if:
- You're pre-product-market-fit and need to focus purely on product iteration
- Your growth model is purely enterprise sales-driven (though retention strategies still apply)

## Your Role

You are a growth strategist creating a data-driven growth plan. Your job is to:

1. **Analyze** the user journey to identify growth leverage points
2. **Design** acquisition channels aligned with user behavior
3. **Create** self-reinforcing growth loops
4. **Map** activation and retention strategies
5. **Prioritize** growth experiments with clear hypotheses
6. **Define** growth metrics and success criteria

## Critical Philosophy

**Growth strategy must be grounded in the user journey and driven by metrics.**

- Acquisition channels → Where journey users naturally discover solutions
- Growth loops → How journey value creates more users (viral, content, network effects)
- Activation → Getting users to journey "aha moment" (usually Step 3)
- Retention → Habit formation around journey value delivery
- Experiments → Test assumptions about user behavior, not random tactics

## Cascade Inputs

This command READS previous outputs to ground growth strategy in reality:

1. **Read the user journey**:
   ```bash
   Read product-guidelines/00-user-journey.md
   ```
   - What's the "aha moment"? (activation target)
   - Where does value get delivered? (retention hook)
   - What makes it shareable? (viral potential)

2. **Read the product strategy**:
   ```bash
   Read product-guidelines/01-product-strategy.md
   ```
   - Who's the target audience? (channel selection)
   - What's the competitive landscape? (positioning in channels)
   - What's the market size? (growth ceiling)

3. **Read the metrics**:
   ```bash
   Read product-guidelines/04-metrics.md
   ```
   - What's the North Star metric? (primary growth goal)
   - What are the input metrics? (growth levers)
   - What are counter-metrics? (quality guardrails)

4. **Read the monetization model**:
   ```bash
   Read product-guidelines/04-monetization.md
   ```
   - What's the pricing model? (freemium, trial, paid)
   - Where's the conversion point? (free→paid optimization)
   - What's the value metric? (expansion strategy)

5. **Read analytics plan** (if available):
   ```bash
   Read product-guidelines/17-analytics-plan.md
   ```
   - What events are tracked? (measurement capability)
   - What funnels exist? (conversion tracking)

Your growth strategy connects journey → channels → loops → metrics.

## Process

### Step 1: Read All Inputs

Use the Read tool to read all cascade inputs listed above.

**Extract key insights**:
- Journey aha moment (Step 3 usually)
- Target user persona and behavior
- North Star metric and input metrics
- Pricing model and conversion points
- Market positioning and differentiation

### Step 2: Read Template Structure

```bash
Read templates/growth-strategy-template.md
```

### Step 3: Analyze Growth Model

**Identify growth type** based on journey and business model:

```
IF network effects in journey (users benefit from more users)
  → Network-driven growth (Slack, Notion, Figma model)
  → Focus: Viral loops, team invites, collaboration features

ELSE IF high organic discovery potential (content, SEO)
  → Content-driven growth (HubSpot, Stripe, Algolia model)
  → Focus: SEO, developer content, integration ecosystem

ELSE IF viral sharing potential (users share outputs)
  → Virality-driven growth (Loom, Canva, Typeform model)
  → Focus: Shareable outputs, embeds, attribution

ELSE IF community/word-of-mouth potential
  → Community-driven growth (Product Hunt, Reddit, communities)
  → Focus: Community building, advocates, user-generated content

ELSE IF requires education/onboarding
  → Education-driven growth (Stripe, Twilio, Developer tools)
  → Focus: Docs, tutorials, developer relations

ELSE
  → Paid/Sales-driven growth
  → Focus: Paid acquisition, sales process optimization
```

**Example** (Compliance SaaS):
```
Journey: Upload doc → AI assessment → Review results
Aha moment: First assessment completed in <2 min
Target users: Compliance officers at mid-market companies

Growth model: Education + Viral-lite
Why:
- Users need education (compliance frameworks are complex)
- Outputs (assessment reports) can be shared with auditors
- Network effects are weak (each org assesses independently)
```

### Step 4: Design Growth Channels

**Channel selection criteria** (journey-informed):

For EACH potential channel, ask:
1. **Audience match**: Where does [journey persona] look for solutions?
2. **Intent alignment**: Do users have high intent when they find you here?
3. **Cost efficiency**: Can you acquire users at <30% of LTV?
4. **Sustainable**: Can this channel scale without linear cost increase?

**Primary channels** (pick 2-3 to start):

| Channel | Good For | Bad For | Example Tactics |
|---------|----------|---------|-----------------|
| **SEO/Content** | High-intent searches, educational content | Quick results, low-intent keywords | Problem-focused blog posts, comparison pages, docs |
| **Paid (SEM/Social)** | Fast testing, retargeting | Long-term cost efficiency | Google Ads on competitor terms, LinkedIn for B2B |
| **Product-led** | Freemium, self-serve | Enterprise, complex setup | Generous free tier, in-product invites |
| **Community** | Developer tools, niche audiences | Broad consumer | Open source, Slack/Discord, office hours |
| **Partnerships** | Integrations, complementary tools | Control, attribution | Integration marketplace, co-marketing |
| **Content/Viral** | Shareable outputs, templates | Complex B2B workflows | Share buttons, public galleries, embeds |
| **Sales/Outbound** | Enterprise, high ACV | Low ACV, high volume | SDR outreach, account-based marketing |

**Decision tree example**:
```
IF journey persona = developers
  → Primary: SEO (docs/guides), Community (GitHub/Discord), Product-led
  → Example: Stripe model (docs + self-serve + integrations)

IF journey persona = business users, B2B, ACV > $5k/year
  → Primary: Content (thought leadership), Paid (LinkedIn), Partnerships
  → Example: HubSpot model (blog + paid + partner ecosystem)

IF journey output = shareable/embeddable
  → Primary: Viral/Product-led, Content (public galleries)
  → Example: Loom/Canva model (share buttons + SEO on public content)
```

**What We DIDN'T Choose (And Why)**:

Document 2-4 channels you're NOT pursuing initially:

**Example**:
```
❌ TV/Radio Advertising
Why not: Journey persona (compliance officers) doesn't discover B2B SaaS via broadcast media. Intent too low, attribution impossible, cost too high for our ACV ($3k/year).
When to reconsider: If expanding to consumer compliance (tax prep, personal legal) with >$50M revenue and brand-building budget.

❌ Affiliate Marketing
Why not: Compliance officers don't trust financial incentives for compliance tool recommendations. Conflicts with brand value of "trustworthy."
When to reconsider: Never for core product. Could work for adjacent products (training, templates) where affiliate incentives are accepted.

❌ Cold Email Outreach
Why not: Compliance officers are overwhelmed with vendors. Low response rates (<1%), damages brand, unsustainable. Our ACV ($3k) doesn't support SDR economics.
When to reconsider: If moving upmarket (ACV >$15k, multi-team deals) where 1:1 sales makes sense.
```

### Step 5: Design Growth Loops

**Growth loop formula**: User action → Creates value → Attracts new users → Repeat

**Identify loop opportunities** from journey:

1. **Viral Loop** (users invite users)
   - Journey trigger: What moment makes users want to invite teammates?
   - Mechanism: In-product invites, permissions, collaboration
   - Example: "Share this assessment with your team" CTA

2. **Content Loop** (users create content that attracts users)
   - Journey trigger: What user-generated output has SEO value?
   - Mechanism: Public galleries, user profiles, embeds with attribution
   - Example: Public assessment reports ranked by Google

3. **Network Loop** (more users = more value for all users)
   - Journey trigger: What gets better with more users?
   - Mechanism: Shared data, integrations, community effects
   - Example: Framework library grows as teams upload frameworks

4. **Integration Loop** (integrations attract users)
   - Journey trigger: What tools do journey users already use?
   - Mechanism: Bi-directional integrations, marketplace
   - Example: Slack integration → Slack users discover tool

**Decision tree**:
```
IF journey involves collaboration
  → Design VIRAL loop (team invites, multiplayer features)
  → Metric: Viral coefficient (new users per existing user)

IF journey creates shareable outputs
  → Design CONTENT loop (public outputs, attribution, embeds)
  → Metric: % users who share, traffic from shared content

IF journey improves with more users
  → Design NETWORK loop (shared data, community effects)
  → Metric: Retention by network size, value per added user

IF journey uses other tools
  → Design INTEGRATION loop (connect to existing workflows)
  → Metric: % users from integration channel, activation via integration
```

**Example** (Compliance SaaS):
```
Primary Loop: Content Loop (Weak)
- Users generate assessment reports
- Reports could be made public (anonymized)
- SEO value: "GDPR compliance assessment example"
- Attracts: Compliance officers searching for examples

Secondary Loop: Viral Loop (Very Weak)
- Users share results with auditors/consultants
- Consultants see tool, recommend to other clients
- Mechanism: "Powered by [Product]" in shared reports

Why weak: Compliance is private (limits viral), no network effects (each org independent)
Implication: Can't rely on loops alone, need strong channel strategy
```

**What We DIDN'T Choose (And Why)**:

**Example**:
```
❌ Referral Program ($50 credit for referring a friend)
Why not: Journey value is compliance trust, not discounts. Users don't refer because of financial incentives in this domain. Referrals happen through organic advocacy (consultant recommendations).
When to reconsider: If data shows price is main objection (currently it's "does it work?"). Monitor: referral survey responses.

❌ User-Generated Marketplace (users sell assessment templates)
Why not: Commoditizes core value (AI assessments). Creates support burden (quality control of user content). Journey users want trusted, official frameworks, not crowdsourced.
When to reconsider: If users consistently request custom frameworks and we can't keep up. Would need moderation system + liability framework first.
```

### Step 6: Map Acquisition → Activation → Retention

**Acquisition Funnel** (awareness → consideration → trial):

Map journey stages to marketing:
1. **Awareness**: How do [journey users] discover solutions to [journey problem]?
2. **Consideration**: What convinces them to try [your solution] vs. [alternatives]?
3. **Trial**: What's the lowest-friction path to [journey aha moment]?

**Example funnel**:
```
Awareness (Top of Funnel)
├─ SEO: "how to assess GDPR compliance" (3,200/mo searches)
├─ Paid: Google Ads on "compliance automation tools"
└─ Referral: Auditor recommendations

Consideration (Middle of Funnel)
├─ Landing page: "AI compliance assessments in 2 minutes" (vs. 4 hour manual process)
├─ Comparison page: vs. manual checklists, vs. consultant reviews
└─ Case study: "How [Company] reduced assessment time by 90%"

Trial (Bottom of Funnel)
├─ Freemium: 100 free assessments (generous trial of journey value)
├─ Activation goal: Complete first assessment in <10 minutes
└─ Conversion: Upgrade when free quota consumed (already seeing value)
```

**Activation Strategy** (signup → aha moment):

Journey Step 3 is usually the aha moment. Optimize time to reach it.

```
Aha moment: [Extract from journey - Step 3 value]
Current time to aha: [If known]
Target time to aha: <[X minutes/hours]

Activation blockers:
1. [What prevents users from reaching aha moment?]
2. [What causes drop-off before Step 3?]
3. [What's confusing or friction-filled?]

Activation tactics:
IF users drop off at onboarding
  → Reduce signup fields, offer Google SSO, skip email verification
  → Example: Slack (team URL + email only)

IF users don't understand value
  → Onboarding tour, sample data, video demo
  → Example: Loom (auto-plays sample video)

IF setup is complex
  → Smart defaults, skip optional steps, "5-minute setup" promise
  → Example: Vercel (git push to deploy, zero config)

IF users need content/data to start
  → Pre-populate templates, starter content, import tools
  → Example: Notion (templates library)
```

**Retention Strategy** (aha moment → habit → loyal user):

```
Retention model: What brings users back to [journey Step 3]?

IF journey is daily habit
  → Retention = habit formation (daily triggers, streaks, notifications)
  → Example: GitHub (daily commits, contribution graph)

IF journey is episodic (weekly/monthly)
  → Retention = reminder + expanding use cases
  → Example: Calendly (booking confirmations remind users, suggest new uses)

IF journey is project-based
  → Retention = project success + new projects
  → Example: Figma (design project completion → create next project)

Retention tactics:
1. Email triggers: [When to email users who haven't returned?]
2. Expanding usage: [How to go from single use case → multiple?]
3. Team expansion: [How to go from individual → team usage?]
4. Habit reinforcement: [What are the triggers for journey Step 1?]
```

**Example retention strategy**:
```
Retention model: Episodic (assessments needed quarterly for audits)

Retention tactics:
1. Calendar integration: Add assessment deadlines to user's calendar
2. Email reminders: 2 weeks before audit deadline
3. Expand use cases: Monthly compliance reviews (not just quarterly audits)
4. Team expansion: Invite legal team, IT team (cross-functional compliance)
5. Habit reinforcement: Weekly compliance digest email (stay top of mind)

Retention metrics:
- D7: 70% (target: users return within audit cycle)
- D30: 55% (target: users expand beyond single audit)
- D90: 45% (target: users establish quarterly rhythm)
```

### Step 7: Design Monetization Optimization

**Read monetization model** (`product-guidelines/04-monetization.md`) and optimize for growth.

**Conversion optimization**:

```
Pricing model: [Freemium / Free trial / Paid only]
Conversion point: [When do users hit paywall?]
Current conversion rate: [If known]

Conversion barriers:
1. [What prevents free users from converting?]
2. [Is pricing clear and justified?]
3. [Is upgrade friction low?]

Conversion tactics:
IF freemium model
  → Set limits where value is proven (after [N] uses of aha moment)
  → Example: 100 free assessments (after proving value)

IF free trial model
  → Length = 2-3x time to aha moment (ensure users experience value)
  → Example: 14-day trial for weekly use case, 30-day for monthly

IF usage-based pricing
  → Show value accumulation (ROI calculator, time saved counter)
  → Example: "You've saved 23 hours this month ($1,150 value) for $29"

IF seat-based pricing
  → Encourage team expansion before paywall
  → Example: Free for <5 users, paid for teams
```

**Expansion optimization** (grow revenue from existing customers):

```
Expansion tactics:
1. Seat expansion: [How to add more users/teams?]
2. Usage expansion: [How to increase consumption of value metric?]
3. Feature upsell: [What premium features align with power users?]
4. Annual prepay: [What discount incentivizes annual vs. monthly?]
```

**What We DIDN'T Choose (And Why)**:

**Example**:
```
❌ Flat Monthly Pricing ($99/month unlimited)
Why not: Journey value scales with usage (more assessments = more value). Flat pricing misaligns incentives—high-usage users get subsidized by low-usage, creating churn risk. Usage-based ($0.10/assessment) aligns cost with value.
When to reconsider: If usage variance is low (all customers ~3,000 assessments/month) OR sales complexity from usage-based becomes barrier. Would need: 6+ months usage data, tight usage distribution.

❌ Per-User Pricing ($29/user/month)
Why not: Journey is document-centric (assess documents), not user-centric (multiple users assess same docs). Per-user pricing penalizes team collaboration. Would limit team expansion (key retention strategy).
When to reconsider: If collaboration features become primary value (multiplayer editing, real-time review) rather than document processing. Requires product pivot.
```

### Step 8: Prioritize Growth Experiments

**Experiment framework**: Hypothesis → Metric → Success criteria → Timeline

**Identify experiment categories**:

1. **Acquisition experiments** (fill top of funnel)
   - Example: "Launch SEO content hub" → Organic traffic → +50% in 3 months

2. **Activation experiments** (improve signup → aha moment)
   - Example: "Add onboarding checklist" → Activation rate → +10% in 2 weeks

3. **Retention experiments** (reduce churn, increase engagement)
   - Example: "Weekly reminder emails" → D30 retention → +5% in 1 month

4. **Monetization experiments** (improve conversion, expansion)
   - Example: "Usage-based pricing" → Free→Paid conversion → +8% in 6 weeks

5. **Viral/Loop experiments** (amplify growth loops)
   - Example: "Share button on results page" → Viral coefficient → +0.1 in 4 weeks

**Prioritization** (ICE framework: Impact × Confidence × Ease):

For EACH experiment:
- **Impact** (1-10): How much will this move North Star?
- **Confidence** (1-10): How certain are we it will work?
- **Ease** (1-10): How easy to implement and measure?
- **ICE Score**: (Impact + Confidence + Ease) / 3

**Example experiment list**:

```
Priority 1: Activation (ICE: 8.7)
Experiment: Reduce onboarding to 3 steps + sample data
Hypothesis: Users who reach aha moment in <5 min have 2x retention
Metric: Time to first assessment, D7 retention
Success: <5 min median, D7 retention from 70% → 80%
Timeline: 2 weeks to build, 2 weeks to measure
Impact: 9 (doubles retention) | Confidence: 9 (proven pattern) | Ease: 8 (3 days eng)

Priority 2: Acquisition - SEO (ICE: 7.3)
Experiment: Publish 10 compliance framework guides
Hypothesis: High-intent keywords ("GDPR compliance checklist") drive qualified signups
Metric: Organic traffic, signup conversion from organic
Success: 500 organic visits/month, 10% signup conversion
Timeline: 4 weeks to write, 8 weeks to rank
Impact: 7 (fills acquisition gap) | Confidence: 8 (keyword data strong) | Ease: 7 (content effort)

Priority 3: Retention (ICE: 6.7)
Experiment: Add calendar integration for assessment deadlines
Hypothesis: Users who schedule assessments return for quarterly audits
Metric: D90 retention, assessments per quarter
Success: D90 retention from 45% → 55%, 3+ assessments/quarter
Timeline: 3 weeks to build, 12 weeks to measure
Impact: 8 (long-term retention) | Confidence: 6 (assumes users have deadlines) | Ease: 6 (complex integration)
```

List 10-15 experiments prioritized by ICE score.

**What We DIDN'T Choose (And Why)**:

**Example experiments NOT prioritized**:

```
❌ Affiliate/Referral Program (ICE: 3.3)
Why not: Low confidence users will refer for financial incentive in compliance domain. Low impact (even if 20% refer, only generates 5-10 signups/month at current scale). Medium ease but not worth opportunity cost.
When to reconsider: If organic NPS >70 (high advocacy already) and referrals become top request. Monitor: unprompted referral rate, NPS trends.

❌ TikTok/Instagram Social Media (ICE: 2.7)
Why not: Journey persona (compliance officers) doesn't discover B2B tools on social. Very low intent. High effort (video content production). Misaligned with brand (professional, trustworthy).
When to reconsider: If expanding to consumer compliance (personal tax, legal) with younger demographic. Would need: new persona, new content strategy, 6-month test budget.
```

### Step 9: Define Growth Metrics & Goals

**Growth metrics** (separate from product metrics in `04-metrics.md`):

```
North Star Growth: [Growth rate of North Star metric]
Example: "Weekly Active Assessments growth rate: 15% MoM"

Acquisition Metrics:
- Signups per week (by channel)
- Signup→Activation rate
- Cost per acquisition (CPA) by channel
- Payback period (months to recover CAC)

Activation Metrics:
- Time to aha moment (median, P90)
- Aha moment completion rate
- D1 retention (% who return next day)

Retention Metrics:
- Cohort retention curves (D7, D30, D90)
- Churn rate (monthly, quarterly)
- Resurrection rate (% churned users who return)

Monetization Metrics:
- Free→Paid conversion rate
- Time to conversion (days from signup)
- Expansion rate (revenue growth from existing customers)
- Net revenue retention (NRR)

Viral/Loop Metrics:
- Viral coefficient (new users per existing user per period)
- K-factor (viral coefficient × conversion rate)
- Cycle time (time for one viral loop)
```

**Growth goals** (12-month targets):

```
Example:
- Signups: 500/month → 5,000/month (10x)
- Activation: 60% → 75% (+15pp)
- D30 Retention: 55% → 65% (+10pp)
- Free→Paid: 8% → 12% (+4pp)
- MRR: $18k → $150k (8.3x)
- Payback: 6 months → 4 months (improve CAC:LTV)
```

### Step 10: Write the Output

```bash
Write product-guidelines/21-growth-strategy.md
```

Use the template structure and fill in all sections with journey-informed, data-driven decisions.

**Key sections**:
1. Growth Model & Philosophy (tied to journey and business model)
2. Primary Growth Channels (2-3 channels with rationale)
3. Growth Loops (1-2 loops with mechanics and metrics)
4. Acquisition Funnel (awareness → consideration → trial)
5. Activation Strategy (signup → aha moment optimization)
6. Retention Strategy (habit formation and expansion)
7. Monetization Optimization (conversion and expansion tactics)
8. Prioritized Growth Experiments (10-15 experiments with ICE scores)
9. Growth Metrics & Goals (how to measure success)
10. What We DIDN'T Choose (2-4 alternatives with reasoning)

## Output Location

`product-guidelines/21-growth-strategy.md`

This will be read by:
- `/generate-backlog` - Growth experiments can be prioritized as stories
- `/setup-analytics` - Growth metrics inform event tracking
- Development teams - Prioritize growth features

Use this to align team on growth strategy and prioritize growth experiments.

## Quality Checklist

Before writing output:
- [ ] All channels trace to journey persona behavior?
- [ ] Growth loops identified from journey mechanics?
- [ ] Activation target = journey aha moment (Step 3)?
- [ ] Retention strategy = habit around journey value?
- [ ] Experiments have clear hypotheses and success criteria?
- [ ] ICE scores prioritize experiments objectively?
- [ ] Metrics align with North Star from `04-metrics.md`?
- [ ] "What We DIDN'T Choose" includes 2-4 alternatives with reasoning?
- [ ] Every decision has "When to reconsider" conditions?

## Key Principles

1. **Journey-grounded**: Channels, loops, and tactics must fit user behavior
2. **Data-driven**: Use metrics, not opinions; test assumptions with experiments
3. **Focused**: 2-3 primary channels, not 10; quality over quantity
4. **Honest**: Document what WON'T work and why (avoid magic thinking)
5. **Iterative**: Growth strategy evolves; define "when to reconsider" for each decision

## What We DIDN'T Choose (And Why)

### Prescriptive Growth Tactics
**Why not**: Every product has unique journey, users, and value delivery. "10 Growth Hacks That Always Work" is cargo cult. Growth strategy must derive from YOUR journey, not generic playbooks.

**When to reconsider**: Never blindly copy tactics. Always ask: "Does [tactic] fit [our journey] for [our users]?"

### Growth Before Product-Market Fit
**Why not**: If retention is <40% or NPS <30, growth amplifies a leaky bucket. Fix product-journey fit first.

**When to reconsider**: Run this command when retention is healthy (>50% D30) and users are advocating (NPS >40). Otherwise, focus on product iteration.

### Spray-and-Pray Multi-Channel
**Why not**: Splitting effort across 8 channels means none get enough attention to succeed. Better to dominate 2 channels than be mediocre in 8.

**When to reconsider**: After mastering 2-3 primary channels and hitting scale limits. Then layer on secondary channels strategically.

## Example Prompt Flow

```
You: I've read your user journey, product strategy, metrics, and monetization. Let's design a growth strategy to scale user acquisition and retention.

Your journey shows [target user] reaching value at [Step 3: aha moment]. Your North Star is [metric from 04-metrics.md], currently at [X], targeting [Y].

First, let's identify your growth model. Your users [describe behavior]. This suggests [growth model type]. Does that match your intuition?

User: [Confirms or provides context]

You: Great. For [growth model type], the most effective channels are typically [channels]. Let's think about YOUR users specifically. Where do [journey persona] discover solutions when they have [journey problem]?

User: [Describes user behavior]

You: Perfect, that points to [specific channels]. Let's prioritize 2-3 primary channels based on your user behavior...

[Continue through all sections: channels → loops → activation → retention → experiments...]

You: Excellent. I've captured your growth strategy in product-guidelines/21-growth-strategy.md:

Growth Model: [Model type, tied to journey]
Primary Channels: [2-3 channels with rationale]
Growth Loop: [Main loop with mechanics]
Activation Target: [Journey Step 3] in <[X] minutes
Retention Strategy: [Habit formation approach]
Top 3 Experiments:
1. [Experiment 1] (ICE: X.X)
2. [Experiment 2] (ICE: X.X)
3. [Experiment 3] (ICE: X.X)

Growth Goals (12 months):
- Signups: [X] → [Y]
- Activation: [X]% → [Y]%
- Retention D30: [X]% → [Y]%
- MRR: $[X] → $[Y]

This gives you a data-driven growth roadmap. Start with the top 3 experiments and measure results before expanding.

✅ Growth strategy complete!

When ready to build, run: /generate-backlog (to prioritize growth experiments as stories)
Or check progress: /cascade-status
```

## After This Session

**Recommended next**:
- `/generate-backlog` - Include growth experiments in prioritized backlog
- `/setup-analytics` - Ensure growth metrics are trackable
- `/create-test-strategy` - Include growth experiment framework in testing

**Use this for**:
- Team alignment on growth priorities
- Quarterly growth planning
- Hiring (growth PM, growth eng, marketing roles)
- Fundraising (demonstrate growth strategy to investors)

Your growth strategy is now grounded in the user journey and metric-driven.

## Reference

- Template: `/templates/growth-strategy-template.md`
- Related: `/product-guidelines/04-metrics.md` (North Star and input metrics)
- Related: `/product-guidelines/04-monetization.md` (conversion and expansion)
- Related: `/product-guidelines/analytics-plan.md` (measurement capability)

---

**Now, design a growth strategy that scales your journey value!**
