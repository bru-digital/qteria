# Stack-Driven: AI Product Development Powerhouse

> **Mission**: A cascading system where AI analyzes your user journey and derives optimal decisions for your product—from strategy to shipped code.

**License:** Apache License 2.0 - See the `LICENSE` file for details.

---

## What's New in v2.0?

**v2.0** transforms Stack-Driven from a prescriptive template collection into a **generative cascade**—AI analyzes YOUR specific user journey and recommends the optimal stack, strategy, and architecture for your needs (not generic templates).

Previous versions prescribed "use Next.js, FastAPI, and PostgreSQL" for everyone. v2.0 says "tell me about your users, and I'll recommend the optimal stack for YOUR journey."

---

## What is Stack-Driven?

Stack-Driven is a comprehensive framework for building products the right way:

1. **Start with user experience** (the post-modern axiom)
2. **Let strategic decisions flow from user value**
3. **Derive technology choices from journey requirements**
4. **Generate a complete product strategy in 3-5 hours**

This isn't just a prompt collection—it's a complete product development system that guides you through **14 progressive sessions**, each building on previous outputs, to go from idea to production-ready system.

---

## User Experience is the Core of Every Product.

Everything flows from the user journey:
- Your mission → Promise to deliver value at a specific journey step
- Your metrics → Measure progress through the journey
- Your monetization → Charge where value is delivered
- Your tech stack → Optimize critical journey steps
- Your architecture → Enable journey optimization

**Start with the user, and everything else follows.**

---

## The Cascade

Stack-Driven guides you through **14 progressive sessions**, each building on previous outputs:

```
Session 1: /refine-journey             → product-guidelines/00-user-journey.md
  ↓ (AI reads journey, validates with market)

Session 2: /create-product-strategy     → product-guidelines/01-product-strategy.md
  ↓ (AI reads journey + strategy, chooses tech)

Session 3: /choose-tech-stack          → product-guidelines/02-tech-stack.md
  ↓ (AI reads journey + strategy + tech, derives tactics)

Session 4: /generate-strategy          → product-guidelines/03-mission.md
                                        product-guidelines/04-metrics.md
                                        product-guidelines/04-monetization.md
                                        product-guidelines/04-architecture.md
  ↓ (AI reads all previous, creates brand strategy)

Session 5: /create-brand-strategy      → product-guidelines/05-brand-strategy.md
  ↓ (AI reads brand strategy, creates design system)

Session 6: /create-design               → product-guidelines/06-design-system.md
  ↓ (AI reads all previous, designs technical specs)

Session 7: /design-database-schema     → product-guidelines/07-database-schema.md
  ↓ (AI reads schema, designs API surface)

Session 8: /generate-api-contracts     → product-guidelines/08-api-contracts.md
  ↓ (AI reads APIs, defines testing strategy)

Session 9: /create-test-strategy       → product-guidelines/09-test-strategy.md
  ↓ (AI reads everything, generates backlog)

Session 10: /generate-backlog          → product-guidelines/10-backlog/
  ↓ (Push to GitHub)

Session 11: /create-gh-issues          → GitHub issues
  ↓ (Generate working development environment)

Session 12: /scaffold-project          → product-guidelines/12-project-scaffold.md
                                        product-guidelines/12-project-scaffold/ (actual code files)
  ↓ (Plan deployment strategy)

Session 13: /plan-deployment           → product-guidelines/13-deployment-plan.md
  ↓ (Design observability)

Session 14: /design-observability      → product-guidelines/14-observability-strategy.md
```

**In 14 sessions** (8-10 hours total), you go from idea to production-ready system with technical specifications, deployment and monitoring strategy.

---

## Quick Start

### 1. Check Your Status

```bash
/cascade-status
```

See where you are in the cascade and what to do next.

### 2. Start the Cascade

**Option A: Automated Execution** (Recommended for continuous flow)

```bash
/run-cascade
```

I'll automatically execute sessions sequentially from your current progress point, pausing at major milestones for your review. Perfect for making rapid progress through the framework.

**Option B: Manual Step-by-Step** (Recommended for learning)

```bash
/refine-journey
```

I'll ask questions about your users, their problems, and their journey. Through progressive interrogation, we'll map your complete user flow. After each session, you manually run the next command.

### 3. Follow the Flow

After each session, I'll tell you exactly what to run next:
- `/create-product-strategy` - Validates journey with market analysis and competitive positioning
- `/choose-tech-stack` - Analyzes your journey and strategy, recommends optimal tech
- `/generate-strategy` - Derives mission, metrics, monetization, architecture
- `/design-database-schema` - Designs complete database schema with ERD and migrations
- `/generate-api-contracts` - Generates OpenAPI specs and endpoint definitions
- `/create-test-strategy` - Defines comprehensive testing strategy (unit, integration, E2E)
- `/generate-backlog` - Generates 30-50 prioritized user stories informed by technical specs
- `/create-gh-issues` - Pushes backlog to GitHub
- `/scaffold-project` - Generates working development environment with actual code files
- `/plan-deployment` - Creates deployment strategy with CI/CD and environments
- `/design-observability` - Designs monitoring, alerting, and SLO strategy

### 4. Build

Your production-ready system is ready with database schema, API contracts, testing strategy, package configs, Docker Compose, CI/CD pipeline, deployment strategy, observability setup, and documentation. Copy the scaffold files and start implementing your prioritized backlog.

**Total time**: 8-10 hours to go from idea to production-ready system with complete technical specifications.

---

## Repository Structure

### `/product-guidelines/` - YOUR Generated Strategy

**This is gitignored** - each user generates their own cascade:
```
product-guidelines/
├── 00-user-journey.md (Session 1)
├── 01-product-strategy.md (Session 2)
├── 11-product-strategy-essentials.md (Session 2)
├── 02-tech-stack.md (Session 3)
├── 03-mission.md (Session 4)
├── 04-metrics.md (Session 4)
├── 04-monetization.md (Session 4)
├── 04-architecture.md (Session 4)
├── 05-brand-strategy.md (Session 5)
├── 06-design-system.md (Session 6)
├── 07-database-schema.md (Session 7)
├── 08-api-contracts.md (Session 8)
├── 09-test-strategy.md (Session 9)
├── 10-backlog/ (Session 10)
├── 12-project-scaffold/ (Session 12 - actual code files)
│   ├── 12-project-scaffold.md (decisions documentation)
│   ├── package.json (or pyproject.toml)
│   ├── docker-compose.yml
│   ├── .env.template
│   ├── .github/workflows/ci.yml
│   └── README.md (setup instructions)
├── 13-deployment-plan.md (Session 13)
└── 14-observability-strategy.md (Session 14)
```

### `/examples/` - Reference Implementations

**Don't copy these** - they show the cascade in action with DIFFERENT journeys leading to DIFFERENT stacks.

```
examples/
├── README.md (explains examples)
├── compliance-saas/ (Next.js, FastAPI, PostgreSQL)
│   ├── foundation/ (journey, mission, metrics, monetization)
│   ├── stack/ (tech decisions, architecture)
│   ├── design/ (design system)
│   └── backlog/ (generated issues)
└── [future: real-time-collaboration, etc.]
```

**Use them to**: See how journey requirements drove specific tech choices.

### `/.claude/commands/` - The Cascade Commands

The slash commands that power the cascade. These prompt AI to read previous outputs and generate next steps.

### `/templates/` - Blank Starting Points

Used by slash commands to generate your outputs. You don't edit these directly.

### `/foundation/` & `/stack/` - Framework Guides

High-level frameworks explaining concepts. NOT prescriptive. Use as reference.

---

## Key Principles

### 1. User Journey First

Everything flows from understanding users:
- Not "I want to build X technology"
- But "Users struggle with Y problem, here's their journey..."

### 2. Cascading Decisions

Each session builds on previous outputs:
- Journey → Tech Stack (requirements drive choices)
- Journey + Tech → Strategy (mission, metrics, monetization)
- Journey + Strategy → Design (components for specific flows)
- Everything → Backlog (stories that deliver journey value)

### 3. Generative, Not Prescriptive

We don't prescribe Next.js. We:
1. Analyze your journey requirements
2. Evaluate technology options
3. Recommend best fit with reasoning
4. Explain trade-offs

### 4. Traced to Value

Every decision references user value:
- Tech choice? Serves journey step X
- Feature priority? Improves metric Y
- Design decision? Reduces friction at step Z

### 5. Self-Documenting

At any point, run `/cascade-status` to see:
- What you've completed
- What comes next
- How sessions connect

---

## The Flow

```
1. USER JOURNEY (/refine-journey)
   ↓
   What problem are we solving for whom?

2. PRODUCT STRATEGY (/create-product-strategy)
   ↓
   Market validation: TAM/SAM/SOM, competitive analysis
   Strategic positioning: Vision, goals, roadmap

3. TECH STACK (/choose-tech-stack)
   ↓
   What technologies best serve the journey and strategy?

4. TACTICS (/generate-strategy)
   ↓
   Mission: What outcome do we promise?
   Metrics: How do we measure success?
   Monetization: How do we charge for value?
   Architecture: What patterns enable scale?

5. BRAND (/create-brand-strategy)
   ↓
   How do we express journey value?

6. DESIGN (/create-design)
   ↓
   What components serve specific user flows?

7. BACKLOG (/generate-backlog)
   ↓
   What do we build first?

8. GITHUB (/create-gh-issues)
   ↓
   Ship features aligned with strategy

9. SCAFFOLD (/scaffold-project)
   ↓
   Generate working development environment

10. DEPLOYMENT (/plan-deployment)
    ↓
    How do we ship reliably?

11. OBSERVABILITY (/design-observability)
    ↓
    How do we monitor and maintain?
```

---

## Use Cases

### Startup Founders
Get a complete product development framework without hiring a CPO, CTO, and Head of Design. In 3-5 hours.

### Product Teams
Align on strategy before building. Use as shared decision-making framework.

### Solo Developers
Ship products that feel like they were built by a full team.

### AI Coding Agents
Reference generated strategy files to make decisions aligned with your product vision.

### Engineering Teams
Understand the "why" behind architectural decisions. Maintain coherence as you scale.

---

## Example: How Cascade Adapts

### Scenario 1: Compliance Document SaaS

**Journey**:
- Step 1: Upload 100-page PDF
- Step 2: Select compliance frameworks
- Step 3: AI assesses in 60 seconds
- Step 4: Review shareable report (SEO matters)

**Tech Stack Derived**:
- Frontend: Next.js (SSR for shareable reports)
- Backend: FastAPI (Python for document processing + AI)
- Database: PostgreSQL (JSONB for flexible assessment results)
- AI: Claude Sonnet (deep reasoning for compliance)

**Why This Stack**: Journey requires document processing + AI reasoning + shareable reports → Python ecosystem + SSR

### Scenario 2: Real-Time Multiplayer Game

**Journey**:
- Step 1: Join room on mobile
- Step 2: 10 players draw simultaneously
- Step 3: See changes <100ms
- Step 4: Save game replay

**Tech Stack Derived**:
- Frontend: React Native (mobile-first requirement)
- Backend: Node.js + Socket.io (real-time WebSockets)
- Database: Redis (fast state) + PostgreSQL (history)
- Hosting: Railway (WebSocket support)

**Why This Stack**: Journey requires mobile + real-time <100ms → React Native + Node.js + WebSockets

**Same framework. Different journeys. Different stacks.**

---

## Philosophy

### We Believe:

**✓ User experience is the foundation** (not technology)
**✓ Journey dictates stack** (not generic "best practices")
**✓ Every decision traces to value** (no arbitrary choices)
**✓ Boring is beautiful** (proven tech > exotic tech)
**✓ Generative > Prescriptive** (analyze → recommend, don't dictate)
**✓ Simple execution** (5-6 clear sessions, not 50 fragmented tasks)
**✓ Focus is the ultimate advantage** (say no often)

### We Reject:

**✗ One-size-fits-all stacks** (Next.js isn't always the answer)
**✗ Feature-first thinking** (builds what's interesting, not valuable)
**✗ Resume-driven development** (Kubernetes because it's trendy)
**✗ Technology-first thinking** (choosing tech before understanding users)
**✗ Build-it-all syndrome** (can't say no to features)

---

## Real-World Results

**After completing the cascade, you have**:

📋 **Strategic Foundation**:
- Mission statement (derived from journey aha moment)
- North Star metric (measures mission fulfillment)
- Pricing strategy (aligned with value delivery)

🛠️ **Technical Decisions**:
- Tech stack (optimized for YOUR requirements)
- Architecture principles (journey-optimized)
- Design system (components for your specific flows)

🎯 **Execution Backlog**:
- 30-50 user stories (prioritized with RICE)
- Every story traced to journey step
- Dependencies mapped
- Ready for GitHub

💻 **Development Environment**:
- Complete project scaffold (monorepo or single-repo)
- Package manager configs (package.json / pyproject.toml)
- Docker Compose for local development
- CI/CD pipeline (GitHub Actions)
- Environment configuration templates
- Setup documentation

🚀 **Production Readiness**:
- Deployment strategy (environments, CI/CD, rollout)
- Observability strategy (metrics, logs, traces, SLOs)
- Incident response procedures
- Rollback and recovery plans

**Time investment**: 6-8 hours
**Output**: Production-ready system from idea to deployment + monitoring
**Approach**: Generative (analyzed), not templated (copy-pasted)

---

## Frequently Asked Questions

### "Is this just templates?"

No. Templates are static. The cascade is **generative**:
- I ask questions about YOUR users
- I analyze YOUR journey requirements
- I recommend optimal tech for YOUR needs
- I derive strategy from YOUR journey

Same cascade, different journeys → different outputs.

### "What if I disagree with a recommendation?"

The cascade shows reasoning for every decision:
- "I chose X because your journey requires Y"
- You can override any choice
- Run sessions again to regenerate with new constraints

### "Can I use my own tech stack?"

Yes! In Session 2 (/choose-tech-stack), you can:
- Specify team expertise ("we know Python")
- Note constraints ("must use AWS")
- I'll adapt recommendations to your context

### "Do I have to do all 11 sessions?"

Sessions 1-4 are critical (journey → strategy → stack → tactics).
Sessions 5-7 are highly valuable (brand → design → backlog).
Session 8 is convenience (push to GitHub).
Session 9 bridges strategy to code (scaffold dev environment).
Sessions 10-11 are essential for production (deployment + observability).

Minimum viable cascade: Sessions 1-4 (2-3 hours).
Complete core cascade: Sessions 1-11 (6-8 hours).

---

## Getting Started

```bash
# 1. Check your cascade status
/cascade-status

# 2. Start Session 1 (define your user journey)
/refine-journey

# 3. Follow the cascade (each session tells you what's next)
# /create-product-strategy
# /choose-tech-stack
# /generate-strategy
# /create-brand-strategy
# /create-design
# /generate-backlog
# /create-gh-issues
# /scaffold-project
# /plan-deployment
# /design-observability

# 4. Copy scaffold files, set up CI/CD, implement monitoring, and start building!
```

**Ready?** → Run `/cascade-status` to check your progress, or `/run-cascade` to execute the framework automatically.

---

## Contributing

We welcome contributions that:
- Add new example implementations (different journeys)
- Improve cascade prompts and decision frameworks
- Enhance documentation
- Share real-world case studies

**Guidelines:**
1. Maintain the user-first philosophy
2. Keep the generative (not prescriptive) approach
3. Always trace decisions to user journey
4. Provide clear reasoning for recommendations
5. Test with diverse journey types

---

## Community & Support

- **Documentation**: You're reading it! Start with `/cascade-status`
- **Issues**: Found a bug or unclear prompt? Open an issue
- **Discussions**: Share your cascade results
- **Examples**: Completed a cascade? Consider contributing as example

---

## Why This Exists

Most product teams struggle with:
- Starting with technology instead of user needs
- Losing strategic clarity as they build
- Inconsistent decision-making
- Generic advice that doesn't fit their specific context

**Stack-Driven solves this** by providing:
- Clear starting point (user journey)
- AI-guided analysis (generative cascade)
- Opinionated recommendations (with reasoning)
- Complete strategy (in 3-5 hours)
- Execution backlog (ready for development)

**Result**: Products that feel intentional, not accidental.

---

**Last Updated**: 2025-11-10
**Version**: 2.0.0
**License**: Apache 2.0

---

**Remember**: The best products start with understanding users, not choosing frameworks.

**Start your cascade** → Run `/cascade-status`
