---
description: Session 10 - Generate complete backlog from journey through to technical specs
---

# Session 10: Generate Backlog

This is **Session 10** of the cascade. You'll create a production-ready backlog where every issue traces to user value and is informed by technical specifications (database schema, API contracts, testing strategy).

## Your Role

You're a technical product manager creating a systematic backlog from all cascade outputs.

## Process

### Step 1: Read ALL Previous Outputs

```
Read: product-guidelines/00-user-journey.md
Read: product-guidelines/11-product-strategy-essentials.md
Read: product-guidelines/02-tech-stack.md
Read: product-guidelines/03-mission.md
Read: product-guidelines/04-metrics.md
Read: product-guidelines/04-monetization.md
Read: product-guidelines/04-architecture.md
Read: product-guidelines/07-database-schema-essentials.md
Read: product-guidelines/08-api-contracts-essentials.md
Read: product-guidelines/09-test-strategy-essentials.md
```

**Context Optimization**: We read essentials files for significant context reduction:

- `11-product-strategy-essentials.md` (not `01-product-strategy.md`) - 65% reduction: Contains vision, positioning, goals, principles, and roadmap themes—without market analysis and competitive landscape.
- `07-database-schema-essentials.md` (not `07-database-schema.md`) - 56% reduction: Contains table list, ERD, relationships, and data access patterns—without column details, indexes, migrations, and scaling considerations.
- `08-api-contracts-essentials.md` (not `08-api-contracts.md`) - 80% reduction: Contains endpoint list organized by journey step with brief descriptions—without OpenAPI schemas, request/response definitions, error schemas, and authentication flow details.
- `09-test-strategy-essentials.md` (not `09-test-strategy.md`) - 66% reduction: Contains coverage targets, test types, testing tools, and quality gates—without testing philosophy, detailed examples, test data management, performance testing, security testing, and TDD/BDD workflows.

Note: Brand strategy (formerly 07) and design system (formerly 08) are now POST-CASCADE extensions if needed, not required for backlog generation.

### Step 2: Generate Epic Structure

**Create 1 epic per journey step** (typically 3-5 epics):

- Epic 01: Onboarding (Journey Steps 1-2)
- Epic 02: Core Value Delivery (Journey Step 3 - THE KEY EPIC)
- Epic 03: Results & Actions (Journey Steps 4-5)
- Epic 04: Foundation (Auth, database, infrastructure)
- Epic 05: Design System Implementation
- Epic 06: Metrics & Analytics

### Step 3: Generate User Stories (30-50 total)

For EACH journey step, create stories that:

1. **Enable that step's user value**
2. **Use specified tech stack**
3. **Implement designed components**
4. **Track defined metrics**

**Story Format** (use `/templates/issue-template.md`):

```markdown
# [STORY-001] OAuth-based signup with Google

Type: Story
Journey Step: Step 1 (Onboarding)
Priority: P0

## User Value

When a compliance officer wants to try the product, they want frictionless signup, so they can reach value quickly.

Value: Reduces signup friction, improves activation rate (key metric).

## Acceptance Criteria

- [ ] User clicks "Sign up with Google"
- [ ] OAuth flow completes, creates user in PostgreSQL
- [ ] User lands in empty dashboard (ready for Step 2)

## Technical Approach

Tech Stack: Clerk for auth, PostgreSQL for user storage, Next.js frontend

## Dependencies

Blocked By: EPIC-04 (Database schema setup)

## Estimation

Effort: 2 days (1 day Clerk integration, 1 day user creation flow)
```

### Step 4: Apply RICE Prioritization

For each story, calculate RICE:

**R (Reach)**: How many users affected per time period?
**I (Impact)**: Journey improvement (0.25 = minimal, 0.5 = low, 1 = medium, 2 = high, 3 = massive)
**C (Confidence)**: Evidence level (50% = low, 80% = medium, 100% = high)
**E (Effort)**: Person-days

**RICE Score** = (R × I × C) ÷ E

**Priority Assignment**:

- P0: RICE > [threshold], critical for MVP
- P1: Important, post-MVP
- P2: Nice-to-have, defer

### Step 5: Map Dependencies

For each story, note:

- **Blocks**: What stories can't start until this is done?
- **Blocked By**: What must be done first?

Example:

- STORY-001 (OAuth) blocks STORY-010 (User dashboard)
- STORY-001 blocked by EPIC-04 (Database setup)

## Generating the Output

### Create Directory Structure:

```
product-guidelines/10-backlog/
├── BACKLOG.md (summary)
└── issues/
    ├── epic-01-onboarding.md
    ├── epic-02-core-value.md
    ├── story-001-oauth-signup.md
    ├── story-002-document-upload.md
    └── ... (30-50 stories total)
```

### BACKLOG.md Contents:

- Epic summary (6-8 epics)
- Priority distribution (X P0 stories, Y P1, Z P2)
- Estimated timeline (total effort in weeks)
- Journey mapping (which stories serve which journey steps)

### Issue File Contents:

Use `/templates/issue-template.md` for EVERY story.

**Critical**: Each story must have:

- Journey step reference
- Clear user value
- Acceptance criteria (testable)
- Tech stack components used
- RICE score and priority
- Dependencies

## Validation Checklist

- [ ] Every issue references a journey step?
- [ ] All P0 issues have clear acceptance criteria?
- [ ] Dependencies are mapped?
- [ ] Estimates are reasonable (nothing >5 days)?
- [ ] Total backlog enables complete journey (Step 1→5)?
- [ ] Tech stack is used (stories reference chosen tech)?
- [ ] Design components are built (stories implement design system)?
- [ ] Metrics are tracked (analytics instrumented)?

## After Generation

```
✅ Session 7 complete! Production backlog generated.

Your Backlog:
📦 [X] epics covering full user journey
📋 [Y] user stories (prioritized with RICE)
   - [A] P0 stories (critical for MVP)
   - [B] P1 stories (important, post-MVP)
   - [C] P2 stories (nice-to-have)

Estimated MVP timeline: [Z] weeks

File created: product-guidelines/10-backlog/BACKLOG.md + [Y] issue files

Next, we can push these issues to GitHub.

When ready, run: /create-gh-issues
Or check progress: /cascade-status
```

## Important Guidelines

1. **Every issue traces to journey**: No "nice to have" features disconnected from user value
2. **Use specified tech stack**: Stories should reference chosen technologies
3. **Implement design system**: Stories should reference designed components
4. **Track metrics**: Include analytics instrumentation stories
5. **Reasonable estimates**: No story >5 days (break down if larger)
6. **Clear acceptance criteria**: Every story testable

## Reference

- Template: `/templates/issue-template.md`
- Example: `/examples/compliance-saas/backlog/` (if created)

---

**Now, synthesize all cascade outputs into a complete, prioritized backlog!**
