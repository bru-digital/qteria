# Stack-Driven Examples

This directory contains **reference implementations** showing the Stack-Driven cascade in action with real, completed examples.

## What Are These Examples?

These are **not templates** - they are fully completed cascades showing how different user journeys lead to different technical decisions. Each example shows the entire flow from user journey through to backlog generation.

## Purpose

1. **Learning**: See how the cascade works end-to-end
2. **Reference**: When stuck, see how similar products made decisions
3. **Validation**: Understand that your product will be different (and that's good!)

## Available Examples

### Compliance SaaS (`/compliance-saas/`)

**User Journey**: Compliance officers need to quickly assess documents against regulatory frameworks without reading 50+ page documents.

**Tech Stack Derived**:
- Frontend: Next.js (SEO important, server-side rendering for compliance reports)
- Backend: FastAPI (Python ecosystem for document processing, AI integration)
- Database: PostgreSQL (complex document metadata, relational integrity)
- AI: Claude Sonnet (deep reasoning for compliance analysis)
- Hosting: Vercel + Railway

**Why This Stack**: The journey requires document processing, AI-powered analysis, and shareable compliance reports - which drove these specific technology choices.

**Journey → Stack Mapping**:
- Step 2 (Upload Document) → S3 + presigned URLs
- Step 3 (AI Assessment) → Claude API + FastAPI async processing
- Step 4 (Review Results) → Next.js SSR for shareable reports
- Step 5 (Export/Share) → PDF generation, PostgreSQL for audit trails

---

### Future Examples

We plan to add contrasting examples to show how different journeys yield different stacks:

**Real-Time Collaboration Tool** (planned):
- Journey: 10 players drawing together in real-time on mobile
- Expected Stack: React Native, Node.js + Socket.io, Redis, PostgreSQL
- Why Different: Real-time interaction + mobile-first = different tech choices

**Batch Data Processing Platform** (planned):
- Journey: Upload CSV, process millions of rows, download results
- Expected Stack: SvelteKit, Python + Celery, PostgreSQL + TimescaleDB
- Why Different: Heavy compute, batch processing = different architecture

---

## How to Use These Examples

### ✅ Do:
- Study how journey requirements drove technology choices
- Reference structure and organization patterns
- See how each cascade session builds on previous outputs
- Understand trade-off reasoning

### ❌ Don't:
- Copy-paste without understanding your own journey
- Assume your product needs the same stack
- Skip the cascade and just use this as a template
- Expect your backlog to look identical

## The Key Insight

**Different journeys require different solutions.**

The Compliance SaaS example uses Next.js because SEO and shareable reports matter for compliance officers. A real-time multiplayer game would NOT use Next.js - it would need React Native and WebSockets.

**Your journey will drive your stack. Let it.**

---

## Example Structure

Each example follows this structure:

```
example-name/
├── foundation/
│   ├── 00-user-journey.md       # Session 1 output
│   ├── 01-mission.md             # Session 3 output
│   ├── 02-metrics.md             # Session 3 output
│   └── 03-monetization.md        # Session 3 output
├── stack/
│   ├── 04-tech-stack.md          # Session 2 output
│   └── 05-architecture.md        # Session 3 output
├── design/
│   └── 06-design-system.md       # Session 4 output
└── backlog/
    ├── BACKLOG.md                # Session 5 output
    └── issues/
        ├── epic-01-onboarding.md
        ├── story-001-oauth.md
        └── ...
```

Numbers indicate execution order in the cascade.

---

## Contributing Examples

Have a completed Stack-Driven cascade that shows a different journey? We'd love to add it!

Requirements:
- Complete cascade (all sessions 1-5)
- Different user journey from existing examples
- Different tech stack with clear journey-based reasoning
- Well-documented decision rationale

---

**Remember**: These examples exist to show the *process*, not to prescribe solutions. Your product's cascade will be unique because your users' journey is unique.

**Next Step**: Return to the main README and run `/cascade-status` to start your own cascade.
