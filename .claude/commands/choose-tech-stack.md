---
description: Session 3 - Choose optimal tech stack based on your user journey and product strategy
---

# Session 3: Choose Tech Stack

This is **Session 3** of the cascade. You'll analyze the user's journey and product strategy, then recommend a tech stack optimized for THEIR specific requirements - not generic "best practices."

## Your Role

You are a thoughtful tech architect. Your job is to:

1. **Read and analyze** the user journey (`product-guidelines/00-user-journey.md`) and product strategy (`product-guidelines/01-product-strategy.md`)
2. **Extract technical requirements** from journey steps and strategic goals
3. **Apply decision logic** (not prescriptions!)
4. **Recommend optimal tech stack** with clear journey-based reasoning
5. **Explain trade-offs** (what you didn't choose and why)

## Critical Philosophy

**Let the journey dictate the stack.**

- A real-time multiplayer game needs different tech than a document processing SaaS
- Mobile-first needs different tech than web-first
- AI-heavy workflows need different tech than CRUD apps
- SEO-critical needs different tech than internal tools

**DO NOT prescribe Next.js/FastAPI unless the journey requires it.**

## Process

### Step 1: Read User Journey and Product Strategy

Use the Read tool to read:

- `product-guidelines/00-user-journey.md`
- `product-guidelines/01-product-strategy.md`

**Extract from Journey**:

- Core user flow (Steps 1-5)
- Technical implications of each step
- User context (mobile? web? both?)

**Extract from Product Strategy**:

- Scale expectations (from market sizing)
- Competitive positioning (technical differentiators)
- Strategic goals (technical capabilities needed)
- Roadmap themes (future technical requirements)

### Step 2: Analyze Technical Requirements

For each journey step, identify technical requirements:

**Questions to Ask (internally)**:

**Real-Time Needs?**

- Does Step 3 require <1 second updates?
- Are multiple users collaborating simultaneously?
- → If yes: Consider WebSocket-friendly backends (Node.js, Go), real-time databases

**Data Complexity?**

- Is data highly relational (users → teams → projects → tasks)?
- Or document-heavy with flexible schemas?
- Or key-value patterns?
- → PostgreSQL for relational, PostgreSQL JSONB for flexible, Redis for key-value

**Scale Expectations?**

- MVP (100s of users)?
- Growth (10,000s)?
- Scale (100,000s+)?
- → Choose tech that scales without rewrites, but don't over-engineer for scale you don't have

**SEO Requirements?**

- Are shareable links important (compliance reports, portfolios)?
- Do pages need to be indexed by search engines?
- → If yes: Server-side rendering (Next.js, SvelteKit, etc.)
- → If no: SPA is fine (Vite + React, etc.)

**Mobile vs Web?**

- Is this mobile-first?
- Desktop-only internal tool?
- Both?
- → Mobile-first: Consider React Native, Flutter
- → Web-first: React/Next.js, Vue, Svelte
- → Both: Next.js for web + React Native for mobile (share some code)

**Processing Complexity?**

- Heavy AI/ML integration?
- Document/image processing?
- Simple CRUD?
- Complex calculations?
- → AI/ML: Python ecosystem (better libraries)
- → Document processing: Python (PyPDF2, python-docx)
- → Simple CRUD: Any modern framework works
- → Real-time: Node.js, Go

**Integration Needs?**

- Lots of third-party APIs?
- Webhook-heavy?
- → Consider ecosystem size (npm > PyPI > others in absolute numbers)

### Step 3: Apply Decision Framework

For each layer (frontend, backend, database, etc.), apply this logic:

**Frontend Decision Tree:**

```
Does journey require SEO/shareable links?
  Yes → Server-side rendering framework
    Is team familiar with React?
      Yes → Next.js
      No → SvelteKit or consider team expertise
  No → SPA framework
    Is it complex UI with lots of state?
      Yes → React/Vue/Svelte + Zustand/Pinia
      No → Vanilla JS or Alpine.js (keep it simple)

Is it mobile-first?
  Yes → React Native or Flutter
  No → Web framework as above
```

**Backend Decision Tree:**

```
Does journey require heavy AI/ML integration?
  Yes → Python (FastAPI, Flask)
  No → Check other requirements

Does journey require real-time <1s updates?
  Yes → Node.js (Express, Fastify) or Go
  No → Python or Node.js (both work)

Does team have strong preferences/expertise?
  Use that (boring is good)
```

**Database Decision Tree:**

```
Is data highly relational?
  Yes → PostgreSQL

Is schema unpredictable/evolving rapidly?
  Yes → PostgreSQL with JSONB (best of both worlds)
  Extreme case → MongoDB (but reconsider if PostgreSQL JSONB works)

Is it key-value or cache-heavy?
  Yes → Redis

Need graph queries?
  Yes → PostgreSQL with extensions or Neo4j
```

**AI Provider Decision Tree:**

```
Does journey require:
  Deep reasoning? → Claude (Sonnet or Opus)
  Function calling/structured output? → GPT-4
  Speed + cost optimization? → Claude Haiku or GPT-3.5
  Vision (image understanding)? → GPT-4V or Claude with vision
```

### Step 4: Make Recommendations

For each technology choice, provide:

1. **The choice**: "Frontend: Next.js"
2. **Journey requirement it serves**: "Step 4 requires shareable compliance reports (SEO matters)"
3. **Why this vs alternatives**: "Next.js provides SSR for SEO, React ecosystem for rich UI. SvelteKit would work too, but team knows React."
4. **Trade-offs**: "More complex than SPA, but journey requires it."

### Step 5: Explain What You DIDN'T Choose

This is critical for learning:

```
## What We DIDN'T Choose (And Why)

### Kubernetes / Microservices
**Why Not**: Over-engineering. Journey shows MVP scale (100s of users). Monolith scales to millions of requests. Add complexity only when needed.

### GraphQL
**Why Not**: REST is simpler. Journey doesn't show complex relational queries from frontend. KISS.
```

## Generating the Output

### Create: `product-guidelines/02-tech-stack.md`

Use `/templates/02-tech-stack-template.md` as structure.

**Required Sections**:

1. **Core Stack** (Summary)

   - Frontend: [Choice]
   - Backend: [Choice]
   - Database: [Choice]
   - Cache: [Choice if needed]
   - Storage: [Choice if needed]
   - AI: [Provider + model if AI-heavy]
   - Auth: [Provider - Clerk, Auth0, Supabase, etc.]
   - Hosting: [Where it runs]

2. **Why This Stack (Journey-Driven Decisions)**

   - For EACH choice, explain:
     - Journey requirement it serves (reference specific steps)
     - Why this technology satisfies that requirement
     - Alternatives considered and why not chosen

3. **Stack Mapping to Journey**

   - Table showing: Journey Step → Technical Requirement → Technology Solution
   - Makes journey→tech connection crystal clear

4. **Cost Estimate (MVP Phase)**

   - Be realistic about free tiers
   - Show total monthly cost for MVP scale
   - Include: hosting, database, AI APIs, auth, monitoring, etc.

5. **What We DIDN'T Choose**
   - List 3-5 technologies commonly used but not right for this journey
   - Explain why (based on journey, not opinion)

## Validation Checklist

Before writing the file, verify:

- [ ] Every tech choice references a specific journey requirement
- [ ] Alternatives are considered (not just defaulting to "popular" tech)
- [ ] Stack is cohesive (technologies work well together)
- [ ] MVP cost is realistic (<$200/month for most MVPs)
- [ ] No over-engineering (Kubernetes for 10 users, etc.)
- [ ] Clear explanation of trade-offs

## Example Decision Logic

**Scenario: Real-Time Multiplayer Drawing Game**

**Journey Analysis**:

- Step 2: 10 players drawing simultaneously
- Step 3: Changes visible in <100ms to all players
- Context: Mobile-first, creative tool

**Stack Recommendation**:

```
Frontend: React Native (mobile-first requirement)
Backend: Node.js + Socket.io (real-time <100ms requirement)
Database: Redis (fast state), PostgreSQL (game history persistence)
Hosting: Railway (simple deploys, WebSocket support)

NOT Next.js (not web-first, doesn't need SEO)
NOT FastAPI (Python slower for real-time WebSockets)
NOT DynamoDB (want relational game history)
```

**Reasoning**: Journey requires mobile + real-time → React Native + Node.js + Socket.io.

## After Generation

Once you've created the file:

1. **Show a summary**:

   ```
   ✅ Tech stack chosen!

   Your stack optimized for [key journey requirement]:
   - Frontend: [Choice] (for [journey reason])
   - Backend: [Choice] (for [journey reason])
   - Database: [Choice] (for [journey reason])
   - AI: [Choice if applicable] (for [journey reason])

   Estimated MVP cost: $[X]/month
   ```

2. **Highlight key decisions**:

   - "Chose [tech] over [alternative] because your journey requires [requirement]"

3. **Next steps**:

   ```
   ✅ Session 3 complete!

   You have a tech stack optimized for YOUR journey (not generic best practices).

   Next, we'll derive your tactical foundation: mission, metrics, monetization, and architecture principles - all from your journey and tech choices.

   When ready, run: /generate-strategy

   Or check your progress: /cascade-status
   ```

## Important Guidelines

1. **Be adaptive**: Different journeys yield different stacks. Don't prescribe.
2. **Show your work**: Always explain WHY a choice was made
3. **Consider boring**: Boring, proven tech is often the right choice
4. **Avoid resume-driven development**: No tech for tech's sake
5. **Think total cost**: Include all services, be realistic about free tiers
6. **Consider team**: If user mentions team expertise, factor it in

## Reference Files

- Template: `/templates/02-tech-stack-template.md`
- Example (don't copy!): `/examples/compliance-saas/stack/04-tech-stack.md`
- Current stack opinions (to avoid prescribing): `/stack/tech-stack.md`

---

**Now, read the user journey and product strategy, then recommend an optimal tech stack!**

Read `product-guidelines/00-user-journey.md` and `product-guidelines/01-product-strategy.md`, analyze requirements, and generate `product-guidelines/02-tech-stack.md`.
