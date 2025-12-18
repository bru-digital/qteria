---
description: POST-CASCADE - Generate and evaluate brand name candidates
---

# Discover Brand Naming (Post-Core Extension)

You are helping the user discover the perfect brand name through systematic generation, trademark research, and evaluation. The name should express the value they deliver in their user journey.

## When to Use This

**Run AFTER `/create-brand-strategy`** when you have:

- ✅ User journey defined (`product-guidelines/00-user-journey.md`)
- ✅ Mission statement (`product-guidelines/03-mission.md`)
- ✅ Brand strategy (`product-guidelines/05-brand-strategy.md`)

Your brand name should express the value delivered in the user journey, grounded in your brand strategy.

**Skip this** if:

- You already have a validated brand name
- You're building an internal tool without branding needs
- Your project doesn't require formal naming

## Cascade Inputs

This command READS previous outputs to create journey-aligned names:

1. **Read the user journey**:

   ```bash
   Read product-guidelines/00-user-journey.md
   ```

   - What's the core problem being solved?
   - What's the transformation users experience?
   - What keywords describe the journey value?

2. **Read the mission**:

   ```bash
   Read product-guidelines/03-mission.md
   ```

   - What promise are you making?
   - What outcome do users achieve?

3. **Read the brand strategy**:
   ```bash
   Read product-guidelines/05-brand-strategy.md
   ```

   - Brand purpose (why you exist)
   - Brand personality (how you show up)
   - Brand values (what guides you)
   - Visual direction (aesthetic fit)

Your names must express [journey value] through the lens of [brand personality].

## Your Task

Generate brand name candidates that express the value from the user journey through your brand lens.

### Steps to Execute

1. **FIRST: Read cascade inputs** (see "Cascade Inputs" section above):

   ```bash
   Read product-guidelines/00-user-journey.md
   Read product-guidelines/03-mission.md
   Read product-guidelines/05-brand-strategy.md
   ```

2. **Read the template structure**:

   ```bash
   Read templates/15-brand-naming-template.md
   ```

3. **Interview the user** with journey-informed questions:

   **Naming Direction**:
   - "Your journey helps users [problem → solution]. Should your name be descriptive (explain what you do), metaphorical (suggest the benefit), or abstract (create new meaning)?"

   **Keywords from Journey**:
   - "From your journey, we have keywords like [X, Y, Z]. Which resonate? What others come to mind?"

   **Brand Personality Fit**:
   - "Your brand personality is [personality from 05]. Should the name be [formal/casual], [serious/playful] to match?"

   **Domain Requirements**:
   - "Is .com essential, or are you open to .io, .ai, etc?"

   **Trademark Concerns**:
   - "What geography and industry do we need to check trademark clearance for?"

4. **Generate 20-30 name candidates** that connect to journey:
   - Descriptive names (express what you do in the journey)
   - Metaphorical names (suggest the journey transformation)
   - Abstract names (create new meaning for journey value)
   - Compound names (combine journey keywords)
   - All names must trace back to [journey problem/value]

5. **Trademark research** for top candidates:
   - Check USPTO database (use WebSearch or guide user to check)
   - Check domain availability (guide user to check key TLDs)
   - Flag high-risk names (too similar to existing brands)

6. **Narrow to 10 finalists** with:
   - How each name expresses journey value
   - How each name fits brand personality
   - Trademark risk assessment
   - Domain availability
   - Pros and cons

7. **Write the output**:
   ```bash
   Write product-guidelines/15-brand-naming.md
   ```

## Output Location

`product-guidelines/15-brand-naming.md`

This will be read by:

- `/define-messaging` - Uses chosen name in journey-aligned messaging
- Decision-making process (narrow to final name)

## Template Structure

The output follows this structure:

- Naming Strategy (direction and criteria)
- All Candidates (20-30 names organized by category)
- Trademark Research Summary
- 10 Finalists (with detailed analysis)
- Recommendation (top 3 with reasoning)

## Key Principles

1. **Quantity first** - Generate many options before judging
2. **Diverse styles** - Explore different naming approaches
3. **Check availability** - Don't fall in love with unavailable names
4. **Say it out loud** - Names should sound good spoken
5. **Test memorability** - Can someone recall it after one mention?
6. **Consider global** - How does it work in other languages?

## Example Prompt Flow

```
You: I've read your user journey, mission, and brand strategy. Your users struggle with [journey problem] and you help them [journey transformation]. Your brand personality is [personality traits].

Let's discover a name that expresses this value. Should your name be descriptive (explains what you do), metaphorical (suggests the transformation), or abstract (creates new meaning)?

User: [Explains preference]

You: Perfect. Your journey has keywords like [X, Y, Z from journey]. Let me generate 20-30 candidates that connect these journey concepts to your [brand personality]...

[Generate journey-connected names]

You: Here are 30 candidates organized by category. Each one connects back to [journey value]. Now let me research trademark availability for the most promising ones...

[Research]

You: Based on trademark research, journey fit, and brand alignment, here are your 10 finalists...

[Show finalists with journey traceability]

You: I've saved everything to product-guidelines/15-brand-naming.md. My top 3 recommendations are:
1. [Name] - Expresses [journey value], fits [brand personality], available
2. [Name] - Metaphor for [journey transformation], .com available
3. [Name] - Clear connection to [journey problem], safe trademark

Each name traces back to your user journey. Which direction resonates?
```

## After This Session

**Recommended next**:

- `/define-messaging` - Create messaging framework using chosen name + journey
- `/create-content-guidelines` - Develop content style with journey-aligned name

**Important**: User doesn't need to finalize name immediately. This document serves as a reference for decision-making.

---

**Remember**: This is POST-CORE. The name expresses journey value, not created in isolation. All names trace back to the user journey.
