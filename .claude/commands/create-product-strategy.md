---
description: Session 2 - Create comprehensive product strategy (market, competitive, roadmap)
---

# Session 2: Create Product Strategy

This is **Session 2** of the cascade. You'll create a comprehensive product strategy that validates the user journey with market analysis, competitive positioning, vision, goals, and roadmap.

## Your Role

You are a product strategist creating market-validated strategy. Your job is to:

1. **Read and analyze** the user journey (`product-guidelines/00-user-journey.md`)
2. **Validate market opportunity** through TAM/SAM/SOM analysis
3. **Analyze competitive landscape** and identify differentiation
4. **Define product vision** and positioning
5. **Establish strategic goals** and success criteria
6. **Create roadmap themes** that deliver journey value

## Critical Philosophy

**Product strategy must validate and extend the user journey with market reality.**

- Vision = User journey outcome at scale
- Market sizing = Bottom-up calculation for journey audience
- Competitive analysis = How others solve journey problem, our differentiation
- Strategic goals = What must be true to achieve journey value at scale
- Roadmap themes = Major initiatives to deliver journey value

## Cascade Inputs

This command READS previous outputs to ground product strategy in reality:

1. **Read the user journey**:
   ```bash
   Read product-guidelines/00-user-journey.md
   ```

   - Who is the target audience? (market segment to size)
   - What problem are they solving? (market need validation)
   - What value do you deliver? (competitive differentiation)

Your product strategy validates and extends the journey with market context.

## Process

### Step 1: Read User Journey

Use the Read tool to read `product-guidelines/00-user-journey.md`.

**Extract**:

- Core user flow (Steps 1-5)
- Target audience (who are we serving?)
- Problem being solved (market need)
- Value delivered (differentiation opportunity)
- Economic value (time/money saved, ROI)

### Step 2: Read Template Structures

```bash
Read templates/01-product-strategy-template.md
Read templates/11-product-strategy-essentials-template.md
```

The full template is comprehensive; the essentials template shows what to extract for backlog generation.

### Step 3: Interview the User

Ask journey-informed questions to develop comprehensive product strategy:

**Vision (journey-grounded)**:

- "Your journey shows [audience] achieving [outcome]. Project this forward: 3-5 years from now, how has [journey audience] been transformed at scale? What's the aspirational future?"

**Market Analysis (journey-based)**:

- "Your journey targets [audience]. Let's size this: How many [audience] exist? What would they pay to solve [journey problem]? Show me bottom-up math."

**Competitive Landscape (journey-differentiated)**:

- "You solve [journey problem] with [journey solution]. Who else solves this today? How do they position? What's YOUR unique approach from the journey?"

**Strategic Goals (journey-aligned)**:

- "Your journey delivers [value]. What 3-5 things MUST be true in 12-24 months to deliver this value at scale?"

**Product Principles (journey-derived)**:

- "Your journey shows [key moments]. What principles guide decisions about THIS journey? What won't you compromise?"

**Roadmap Themes (journey-informed)**:

- "What are the major initiative areas to deliver [journey value]?"

### Step 4: Develop Product Strategy

Grounded in journey, develop:

- **Vision statement**: Journey outcome projected 3-5 years forward
  - **Market sizing**: Bottom-up calculation for [journey audience]
  - **Competitive analysis**: How others solve [journey problem], your differentiation
  - **Positioning**: Who ([journey audience]) + What ([journey solution]) + How (unique approach) + Why (journey value)
  - **Strategic goals**: What must be true to achieve journey value at scale
  - **Product principles**: Decision guides derived from [journey insights]
  - **Roadmap themes**: Major initiatives to deliver [journey value]
  - **Risks**: Assumptions about [journey], [market] that could be wrong

### Step 5: Write the Outputs

First, write the comprehensive product strategy:

```bash
Write product-guidelines/01-product-strategy.md
```

Then, create the essentials version for backlog generation:

```bash
Read templates/11-product-strategy-essentials-template.md
```

Extract ONLY the information needed for backlog generation:

- Vision statement (1 sentence)
- Positioning statement (brief)
- Strategic goals (names + metrics only, no elaboration)
- Product principles (for story decisions)
- Roadmap themes (for epic prioritization)
- Key feature categories (for backlog organization)
- Priority framework (for story prioritization)

```bash
Write product-guidelines/11-product-strategy-essentials.md
```

## Output Locations

1. `product-guidelines/01-product-strategy.md` - Full strategy (for stakeholders, investors, strategic alignment)
2. `product-guidelines/11-product-strategy-essentials.md` - Essentials for backlog generation (optimized for Session 10)

This validates:

- User journey (with market sizing and competitive analysis)
- Creates foundation for tech stack decisions (understanding market and competitive landscape informs technical requirements)

Use for investor/stakeholder conversations and strategic alignment.

## Template Structure

The output follows this structure:

- Product Vision (3-5 year aspirational future)
- Market Analysis (TAM/SAM/SOM, trends, dynamics)
- Competitive Landscape (who, how positioned, gaps)
- Product Positioning (who/what/how/why)
- Strategic Goals (12-24 month objectives)
- Product Principles (decision-making guides)
- Roadmap Themes (major initiative areas)
- Risks and Assumptions (what could go wrong)
- Success Metrics (how to measure progress)

## Key Principles

1. **Be honest about market** - Don't inflate TAM; use bottom-up sizing
2. **Know your competition** - Don't claim "no competitors"; everyone has alternatives
3. **Be specific on positioning** - "Better" is not positioning; "10x faster for X" is
4. **Make principles actionable** - "Quality matters" is vague; "Ship with tests or don't ship" is clear
5. **Theme roadmap** - Don't commit to specific features; commit to problem areas
6. **Name your risks** - Ignoring risks doesn't make them go away

## Example Prompt Flow

```
You: I've read your user journey, mission, metrics, and architecture. Let's validate these with comprehensive product strategy.

Your mission is "[mission]". Project this 3-5 years forward - your product is wildly successful serving [journey audience]. What does that world look like? How many users? What's changed?

User: [Describes vision]

You: Love it - that's your mission at scale. Now let's validate the market. Your journey targets [audience] with [problem]. Bottom-up: how many [audience] exist? What would they pay to solve [problem]? Show me your math.

User: [Calculates market size]

You: Great, that's credible TAM/SAM/SOM. Now competitors: you solve [journey problem] with [journey solution]. Who else solves this today? How do THEY position?

User: [Describes competitive landscape]

You: Perfect. Your differentiation is [unique approach from journey]. Now strategic goals: given your mission and metrics, what 3-5 things MUST be true in 12-24 months?

User: [Lists strategic goals]

[Continue through product principles, roadmap themes, risks...]

You: Excellent. I've created two versions of your product strategy:

**Full Strategy** (product-guidelines/01-product-strategy.md):
- Vision: [journey outcome at scale]
- Market: [TAM/SAM/SOM for journey audience]
- Positioning: [journey differentiation vs. competitors]
- 5 strategic goals (aligned with journey value)
- 4 product principles (from journey insights)
- 6 roadmap themes (major initiatives)
- Risk register (journey/market assumptions)

**Essentials for Backlog** (product-guidelines/11-product-strategy-essentials.md):
- Condensed version with only what Session 10 needs
- 65% smaller, optimized for context efficiency
- Used by /generate-backlog command

This validates your journey with market context. Everything traces back to the user journey.
```

## After This Session

**Recommended next**:

- Continue with Session 3: `/choose-tech-stack` to select optimal technologies
- Use this for investor/stakeholder presentations
- Reference this when making product decisions

**Important**: This validates your journey with market reality. Understanding the competitive landscape and market opportunity informs technical decisions in Session 3.

---

**Remember**: Product strategy is now CORE (Session 2). It validates journey with market context before choosing technology. Everything connects back to the user journey.
