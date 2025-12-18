---
description: POST-CASCADE - Create detailed UX research, flows, wireframes, and interaction specs
---

# Design User Experience (Post-Cascade Optional)

You are helping the user create detailed UX design including research, information architecture, user flows, wireframes, and interaction specifications. This complements the design system from Session 4.

## When to Use This

**Run AFTER Session 3** (`/generate-strategy`) if:

- You've defined strategy and need detailed UX before design system
- You want to map user flows and information architecture
- You need wireframes and interaction specs before visual design

**Or run ALONGSIDE Session 4** if:

- You're doing design system and UX simultaneously
- You have a designer who works both levels

**Difference from Session 4**:

- **Session 4** (`/create-design`): Design SYSTEM (tokens, components, patterns) - the visual language
- **This command**: UX DESIGN (research, flows, wireframes, interactions) - the structure and behavior
- **Both complement**: UX defines behavior, design system defines appearance

**Skip this** if:

- You're building a simple product without complex flows
- You prefer to discover UX through prototyping
- You don't have design resources yet

## Your Task

Create comprehensive UX design documentation using the prompt in `/prompts/design/user-experience.md`.

### Steps to Execute

1. **Read the UX design prompt**:

   ```bash
   Read /prompts/design/user-experience.md
   ```

2. **Read the template structure**:

   ```bash
   Read templates/19-user-experience-template.md
   ```

3. **Check for cascade inputs** (required):

   ```bash
   Read product-guidelines/00-user-journey.md
   Read product-guidelines/05-architecture.md
   ```

   - User journey shows the high-level flow
   - Architecture shows technical constraints and patterns

4. **Check for backlog** (recommended):

   ```bash
   Read product-guidelines/07-backlog/
   ```

   - Backlog shows specific features to design for

5. **Interview the user** following the UX design prompt:
   - **UX Research**: Who are users? What research do you have? Gaps?
   - **Information Architecture**: How is content organized? Navigation structure?
   - **User Flows**: What are the critical paths? Happy paths and edge cases?
   - **Wireframes**: Key screens at low/mid fidelity
   - **Interaction Patterns**: What happens on click, hover, scroll?
   - **Responsive Strategy**: How does UX adapt to screen sizes?
   - **Accessibility**: Screen reader, keyboard nav, ARIA requirements?
   - **Prototyping Plan**: What needs interactive validation?
   - **Usability Testing**: What will you test? With whom?

6. **Develop UX design**:
   - User research summary (personas, pain points, jobs-to-be-done)
   - Information architecture (site map, navigation hierarchy)
   - User flows (5-10 critical paths with decision points)
   - Wireframes (key screens at appropriate fidelity)
   - Interaction specifications (what happens on user actions)
   - Responsive breakpoints and adaptations
   - Accessibility requirements
   - Prototyping and testing plan

7. **Write the output**:
   ```bash
   Write product-guidelines/19-user-experience.md
   ```

## Output Location

`product-guidelines/19-user-experience.md`

This will be used by:

- Designers creating visual design (Session 4 or after)
- Developers implementing features (with design system)
- Product managers validating flows
- QA teams testing user paths
- Usability testing sessions

## Template Structure

The output follows this structure:

- UX Research Summary (users, needs, pain points)
- Information Architecture (site map, navigation)
- User Flows (critical paths with decision points)
- Wireframes (key screens, annotated)
- Interaction Specifications (behavior on actions)
- Responsive Strategy (breakpoints, adaptations)
- Accessibility Requirements (WCAG compliance)
- Micro-interactions (delightful details)
- Empty States and Error Handling
- Prototyping Plan
- Usability Testing Plan

## Key Principles

1. **Start with research** - Design from user needs, not assumptions
2. **Map before designing** - Information architecture before wireframes
3. **Show, don't describe** - Wireframes and flows over paragraphs
4. **Design for edge cases** - Empty states, errors, loading, offline
5. **Think responsive** - Mobile-first or adaptive strategy from the start
6. **Accessibility is required** - Not optional, not an afterthought
7. **Plan for testing** - How will you validate these designs?

## Example Prompt Flow

```
You: Let's design your user experience. First, let me check your user journey and architecture...

[Read product-guidelines/00-user-journey.md and product-guidelines/05-architecture.md]

You: Great! Your journey shows [key insight]. Now, what user research do you have? Have you interviewed users? Run surveys? What do you KNOW vs ASSUME?

User: [Describes research]

You: Perfect. Let's start with information architecture. What are the major sections of your product? How do users navigate between them?

User: [Describes IA]

You: Good structure. Now let's map the most critical user flow: [from journey: the core action]. Walk me through every step, every decision point, every potential error.

User: [Describes flow]

You: Excellent. Let me sketch that as a flow diagram...

[Create flow]

You: Now let's wireframe the key screens in this flow. For [screen 1], what are the essential elements? Let me describe it at low fidelity...

[Continue through key screens]

You: Great. Now let's think about interactions. When someone clicks [button], what happens? Loading state? Confirmation? Animation?

User: [Describes interactions]

You: Perfect. And how does this adapt on mobile? What changes at < 768px?

User: [Describes responsive strategy]

[Continue through accessibility, testing plan...]

You: Excellent! I've documented your complete UX design in product-guidelines/19-user-experience.md:
- User research summary (3 personas, key pain points)
- Information architecture (site map, 3-level navigation)
- 7 critical user flows with decision points
- Wireframes for 12 key screens
- Interaction specs for all actions
- Responsive strategy (4 breakpoints)
- WCAG 2.1 AA accessibility requirements
- Prototyping plan (3 flows to validate)
- Usability testing plan (5 participants, 3 tasks)

Ready to create your design system with /create-design?
```

## After This Session

**Recommended next**:

- `/create-design` (Session 4) if you haven't run it yet - use this UX as input
- Or start building with your design system (if Session 4 is complete)

**Use this document**:

- When implementing features from backlog
- When validating prototypes with users
- When onboarding new designers or developers
- When making UX decisions

---

**Remember**: This is OPTIONAL. Many teams discover UX through building. Use this if you want structured UX planning before implementation.
