# Glossary

Definitions of terms used in Stack-Driven framework.

---

## Framework Concepts

### Cascade

The sequential flow of sessions where each builds upon previous outputs. Like water flowing downhill, decisions cascade from user journey → strategy → execution.

**Example:** Session 1 (journey) → Session 2 (product strategy reads journey) → Session 3 (tech stack reads journey + product strategy)

**Related terms:** Session, Flow, Dependencies

---

### Session

A single step in the cascade that generates specific outputs. Each session is a slash command (e.g., `/refine-journey`, `/choose-tech-stack`).

**Types:**
- **Core sessions** (1-14): Main framework path
- **Post-cascade extensions** (15-22): Optional deep dives
- **Meta sessions**: Framework management (`/cascade-status`, `/run-cascade`)

**Duration:** 15 minutes to 90 minutes depending on session

**Related terms:** Cascade, Command, Step

---

### Generative (vs Prescriptive)

**Generative:** AI analyzes YOUR specific inputs and derives optimal outputs. Different inputs → different outputs.

**Example:**
- Generative: "Tell me your journey. I'll analyze requirements and recommend the optimal stack."
- Prescriptive: "Use Next.js, FastAPI, and PostgreSQL" (for everyone)

Stack-Driven v2.0 is generative - same framework, different journeys → different outputs.

**Related terms:** Journey-driven, Adaptive, User-first

---

### User Journey

The sequence of steps a user takes to achieve their goal using your product. The foundation of the entire framework.

**Structure:**
- **Who:** Specific user persona
- **Situation:** Problem/pain point
- **Steps 1-5:** Journey from problem to solution
- **Aha moment:** Step where value is delivered (usually Step 3)
- **Outcome:** Result achieved

**Example:** "Compliance officer (who) manually reviews documents for 4 hours (situation) → uploads PDF → AI assesses → reviews report in 60 seconds (aha moment) → completes assessment 240x faster (outcome)"

**Related terms:** Journey, User flow, Critical path, Aha moment

---

### Aha Moment

The specific step in the user journey where the user realizes the product's value. Usually Step 3 in the journey.

**Characteristics:**
- Delivers core value
- Measurable improvement
- "This is amazing!" moment
- Often involves a dramatic time/cost/effort reduction

**Example:** Compliance officer sees complete assessment report generated in 60 seconds (vs 4 hours manual work)

**Related terms:** Value delivery, Critical moment, User journey

---

### Core Cascade

Sessions 1-14 that take you from idea to production-ready system.

**Output:** Strategic foundation + technical specs + backlog + deployment plan

**Time:** 8-10 hours total

**Sessions:**
1. User Journey
2. Product Strategy
3. Tech Stack
4. Strategy (Mission, Metrics, Monetization, Architecture)
5. Brand Strategy
6. Design System
7. Database Schema
8. API Contracts
9. Test Strategy
10. Backlog
11. GitHub Issues
12. Project Scaffold
13. Deployment Plan
14. Observability Strategy

**Related terms:** Cascade, Main flow, Framework

---

### Post-Cascade Extensions

Sessions 15-22 that provide optional deep dives after completing relevant core sessions.

**Characteristics:**
- Optional (not required for MVP)
- Run after specific core sessions
- More specialized/detailed

**Examples:**
- Brand naming (after brand strategy)
- Growth strategy (after strategy)
- Financial model (after monetization)
- UX research (after design)

**Related terms:** Extensions, Optional sessions, Deep dives

---

## Output Terminology

### Product Guidelines

The directory (`product-guidelines/`) where all cascade outputs are saved.

**Contents:**
- All session outputs (markdown files)
- Backlog directory (user stories)
- Project scaffold directory (code files)

**Note:** Gitignored by default - each user generates their own cascade

**Related terms:** Outputs, Generated files, Cascade results

---

### Essentials Template

A condensed version of a long output file, optimized for AI reading in downstream sessions.

**Purpose:** Reduce token usage while maintaining key information

**Example:**
- `01-product-strategy.md` (full, 10 pages)
- `11-product-strategy-essentials.md` (condensed, 2 pages)

**Used in:** Sessions 2, 7, 8, 9 (create both full and essentials versions)

**Related terms:** Token optimization, Condensed version, AI-optimized

---

### Template

Blank starting point used by commands to generate YOUR outputs.

**Location:** `templates/` directory

**Usage:** AI reads template → generates output for your product

**Example:**
- Template: `templates/03-mission-template.md`
- Your output: `product-guidelines/03-mission.md`

**Note:** Don't edit templates directly - edit your generated outputs

**Related terms:** Starting point, Schema, Structure

---

### Example

Complete cascade run for a reference product, showing what good outputs look like.

**Location:** `examples/` directory

**Current examples:**
- `compliance-saas/` - Document compliance SaaS

**Purpose:**
- Show level of detail expected
- Demonstrate how journey drives tech choices
- Validate output quality

**Note:** Don't copy examples - your journey will be different

**Related terms:** Reference implementation, Sample cascade, Demo

---

## Strategic Concepts

### Mission Statement

A one-sentence promise to deliver value at a specific journey step. Derived from the aha moment.

**Formula:** "Transform [current state] into [desired state]"

**Example:** "Transform 4-hour compliance assessments into 60-second automated reports"

**Generated in:** Session 4 (`/generate-strategy`)

**Related terms:** Value proposition, Promise, Core purpose

---

### North Star Metric

The single metric that best measures whether you're fulfilling your mission.

**Characteristics:**
- Measures mission fulfillment
- Indicates product success
- Guides decision-making
- Typically measures journey progress

**Example:** "Assessments completed per month" (for compliance SaaS)

**Generated in:** Session 4 (`/generate-strategy`)

**Related terms:** Key metric, Success measure, Primary KPI

---

### Value Ratio

The quantified improvement your product delivers. Usually time saved, cost reduced, or quality improved.

**Format:** [Before] → [After] = [X]x improvement

**Example:** "4 hours → 60 seconds = 240x faster"

**Minimum:** 10:1 ratio for viable product

**Related terms:** Value proposition, Improvement factor, ROI

---

### Tech Stack

The collection of technologies used to build your product (frontend, backend, database, hosting, etc.).

**Stack-Driven approach:** Journey requirements → Tech recommendations

**Components:**
- Frontend framework (React, Vue, Svelte, etc.)
- Backend framework (Node, Python, Go, etc.)
- Database (PostgreSQL, MongoDB, etc.)
- Hosting (Vercel, AWS, Railway, etc.)
- Additional tools (auth, storage, email, etc.)

**Generated in:** Session 3 (`/choose-tech-stack`)

**Related terms:** Technology choices, Architecture, Infrastructure

---

### Architecture Principles

High-level patterns and rules that guide technical decisions.

**Examples:**
- "Event-driven for document processing pipeline"
- "Monolith-first, extract services when needed"
- "Optimize for read-heavy workload"

**Derived from:** Journey requirements + tech stack choices

**Generated in:** Session 4 (`/generate-strategy`)

**Related terms:** Design patterns, System design, Technical principles

---

## Execution Concepts

### Backlog

Collection of 30-50 user stories prioritized and ready for development.

**Structure:**
- User stories ("As [user], I want [feature] so that [value]")
- Acceptance criteria
- RICE scores (Reach, Impact, Confidence, Effort)
- P0/P1/P2 priorities
- Dependencies

**Generated in:** Session 10 (`/generate-backlog`)

**Location:** `product-guidelines/10-backlog/`

**Related terms:** User stories, Feature list, Development queue

---

### User Story

A feature described from the user's perspective with acceptance criteria.

**Format:** "As [user type], I want [feature] so that [value/benefit]"

**Example:** "As a compliance officer, I want to upload multiple documents at once so that I can save time on bulk assessments"

**Components:**
- Description
- Acceptance criteria (how to know it's done)
- Technical notes
- Journey reference (which step this serves)
- RICE score
- Priority (P0/P1/P2)
- Dependencies

**Related terms:** Feature, Story, Requirement

---

### Priority Levels

**P0 (Critical):**
- Required for MVP
- Blocks launch without it
- Serves core journey (Steps 1-3)
- Example: "User can upload document and view results"

**P1 (Important):**
- Enhances core experience
- Should have for good UX
- Serves secondary journey steps
- Example: "User can save favorite templates"

**P2 (Nice to have):**
- Quality of life improvements
- Can launch without
- Serves edge cases or optimizations
- Example: "User can export to multiple formats"

**Related terms:** Prioritization, MVP scope, Release planning

---

### RICE Score

Prioritization framework: **R**each × **I**mpact × **C**onfidence ÷ **E**ffort

**Components:**
- **Reach:** How many users affected? (0-100)
- **Impact:** How much it improves journey? (0-3)
- **Confidence:** How certain are we? (0-100%)
- **Effort:** How long to build? (person-weeks)

**Example:**
- Reach: 80 (80% of users)
- Impact: 3 (massive improvement)
- Confidence: 80%
- Effort: 2 weeks
- **RICE = (80 × 3 × 0.8) / 2 = 96**

Higher score = higher priority

**Related terms:** Prioritization, Scoring, Impact

---

### Project Scaffold

Working development environment with actual code files generated based on tech stack.

**Includes:**
- Package config (package.json, pyproject.toml, etc.)
- Docker Compose setup
- Environment templates (.env.template)
- CI/CD pipeline (GitHub Actions)
- Basic directory structure
- Database setup scripts
- README with setup instructions

**Generated in:** Session 12 (`/scaffold-project`)

**Purpose:** One-command setup to start development

**Related terms:** Boilerplate, Starter project, Development environment

---

## Technical Specifications

### Database Schema

Complete database design with tables, relationships, indexes, and migrations.

**Includes:**
- Entity relationship diagram (ERD)
- Table definitions
- Relationships (foreign keys)
- Indexes for performance
- Constraints for data integrity
- Migration files (actual SQL or ORM code)

**Generated in:** Session 7 (`/design-database-schema`)

**Related terms:** Data model, ERD, Database design

---

### API Contract

Specification of all API endpoints with requests, responses, and behaviors.

**Format:** OpenAPI 3.0 specification

**Includes:**
- Endpoint paths and methods
- Request schemas (body, params, query)
- Response schemas (success, errors)
- Authentication requirements
- Rate limiting
- Error codes

**Generated in:** Session 8 (`/generate-api-contracts`)

**Related terms:** API spec, OpenAPI, Endpoint definition

---

### Test Strategy

Comprehensive plan for testing the product at all levels.

**Includes:**
- Unit testing approach
- Integration testing strategy
- End-to-end (E2E) testing plan
- Performance testing criteria
- Coverage targets
- Testing frameworks

**Levels:**
- **Unit:** Individual functions/components
- **Integration:** Multiple components together
- **E2E:** Complete user flows
- **Performance:** Speed, scale, load

**Generated in:** Session 9 (`/create-test-strategy`)

**Related terms:** Testing plan, QA strategy, Test coverage

---

### Deployment Plan

Strategy for deploying to production environments.

**Includes:**
- Environment definitions (dev, staging, production)
- CI/CD pipeline design
- Infrastructure requirements
- Rollback procedures
- Monitoring integration
- Cost estimates

**Generated in:** Session 13 (`/plan-deployment`)

**Related terms:** DevOps, Infrastructure, Release strategy

---

### Observability Strategy

Plan for monitoring, alerting, and debugging production systems.

**Includes:**
- Metrics to track (application, infrastructure)
- Logging strategy
- Distributed tracing (for microservices)
- Alerting rules and thresholds
- SLO/SLI definitions
- Dashboard designs
- Incident response procedures

**Generated in:** Session 14 (`/design-observability`)

**Related terms:** Monitoring, Alerting, SLO, APM

---

## Framework Operations

### Slash Command

A command that starts with `/` and triggers a cascade session.

**Format:** `/command-name`

**Examples:**
- `/refine-journey` - Start Session 1
- `/cascade-status` - Check progress
- `/run-cascade` - Automated execution

**Location:** Defined in `.claude/commands/` directory

**Related terms:** Command, Session, CLI

---

### Manual Mode

Running each session individually, one at a time.

**Advantages:**
- More control
- Better for learning
- Can iterate at each step

**Disadvantages:**
- More interruptions
- Slower overall

**How:** Run `/refine-journey`, then `/create-product-strategy`, then `/choose-tech-stack`, etc.

**Related terms:** Step-by-step, Individual sessions

---

### Automated Mode

Running the entire cascade automatically via `/run-cascade`.

**Advantages:**
- Faster (continuous flow)
- Fewer interruptions
- Good for clear requirements

**Disadvantages:**
- Less control
- Harder to iterate mid-cascade

**How:** Run `/run-cascade` once, cascade executes all sessions

**Related terms:** Auto-cascade, Batch mode, Continuous execution

---

### Cascade Status

Current state of progress through the framework.

**Check via:** `/cascade-status`

**Shows:**
- ✅ Completed sessions
- ⏹️ Not started sessions
- ➡️ Recommended next step
- 📁 Output files generated
- 🔗 Dependencies between sessions

**Related terms:** Progress, State, Completion

---

### Regeneration

Re-running a session to update its output with new information.

**When to regenerate:**
- Journey evolved after user research
- Tech stack needs updating
- Strategy changed based on feedback
- Found errors in previous output

**How:**
1. Re-run the session: `/refine-journey`
2. Regenerate downstream sessions: `/create-product-strategy`, `/choose-tech-stack`, etc.

**Note:** Overwrites existing files - back up manual edits first

**Related terms:** Update, Re-run, Refresh

---

## Brand and Design

### Brand Strategy

How the product expresses journey value through personality, positioning, and messaging.

**Includes:**
- Brand positioning
- Brand personality (traits, tone)
- Value proposition framing
- Competitor differentiation
- Voice guidelines

**Generated in:** Session 5 (`/create-brand-strategy`)

**Related terms:** Branding, Positioning, Identity

---

### Design System

Collection of reusable components, styles, and patterns for building UI.

**Includes:**
- Color palette
- Typography
- Component library (buttons, forms, cards, etc.)
- Spacing and layout
- Accessibility guidelines
- Usage examples

**Journey-optimized:** Components designed for YOUR specific user flows, not generic

**Generated in:** Session 6 (`/create-design`)

**Related terms:** Component library, Style guide, UI kit

---

## Philosophy Terms

### User-First

Philosophy that ALL decisions must trace back to user value, not technology preferences.

**Examples:**
- ✅ "Real-time updates because users need <100ms latency" (user-first)
- ❌ "Real-time updates because WebSockets are cool" (tech-first)

**Core axiom:** User Experience is the Core of Every Product

**Related terms:** Journey-driven, Value-driven, Customer-centric

---

### Journey-Driven

Approach where technology and strategic decisions are derived from user journey requirements.

**Example:**
- Journey: Users need shareable reports (SEO matters)
- Decision: Use Next.js for server-side rendering
- Reasoning: Shareable reports → SEO → SSR → Next.js

**Opposite:** Technology-first (choosing tech before understanding users)

**Related terms:** User-first, Requirements-driven, Value-based

---

### Boring is Beautiful

Principle of preferring proven, stable technologies over exciting, cutting-edge ones.

**Reasoning:**
- Proven tech = less risk
- Mature ecosystem = more resources
- Better for MVPs and small teams
- Can always adopt new tech later

**Example:**
- ✅ PostgreSQL (boring, proven, stable)
- ❌ NewCoolDB v0.1 (exciting, cutting-edge, risky)

**Exception:** When journey explicitly requires cutting-edge tech

**Related terms:** Proven tech, Stable choice, Conservative approach

---

### Traceability

Every decision must be traceable back to user journey or previous strategic decision.

**Examples:**
- "Blue color because brand personality is 'trustworthy' (from brand strategy)"
- "PostgreSQL because journey needs complex relationships (from requirements)"
- "Priority P0 because serves Step 2 of journey (critical path)"

**Prevents:** Arbitrary decisions, resume-driven development, feature creep

**Related terms:** Reasoning, Justification, Decision chain

---

## Workflow Terms

### Minimum Viable Cascade

Sessions 1-4 only (~3 hours): Journey → Product Strategy → Tech → Strategy

**Output:** Strategic foundation

**When to use:**
- Quick validation
- Early stage exploration
- Time-constrained

**What you get:**
- User journey
- Market validation
- Tech stack
- Mission, metrics, monetization, architecture

**What you don't get:**
- Design system
- Database schema
- Backlog
- Deployment plan

**Related terms:** MVP cascade, Quick validation, Foundation only

---

### Complete Cascade

Sessions 1-14 (~8-10 hours): Full core cascade

**Output:** Production-ready system

**When to use:**
- Ready to build
- Want complete specifications
- Need development roadmap

**What you get:** Everything from strategy to deployment + monitoring

**Related terms:** Full cascade, End-to-end, Production-ready

---

### Cascade Loop

The pattern of run → review → refine → regenerate.

**Process:**
1. Run session
2. Review output
3. Refine (edit or re-run with better inputs)
4. Regenerate downstream sessions

**Example:**
- Run `/refine-journey`
- Review journey, realize user persona is wrong
- Re-run `/refine-journey` with corrected persona
- Regenerate `/create-product-strategy` with new journey

**Related terms:** Iteration, Refinement, Continuous improvement

---

## Acronyms

**ERD:** Entity Relationship Diagram (database design visual)

**MVP:** Minimum Viable Product (simplest version that delivers value)

**API:** Application Programming Interface (how software communicates)

**CI/CD:** Continuous Integration / Continuous Deployment (automated testing and deployment)

**SLO:** Service Level Objective (target for system reliability)

**SLI:** Service Level Indicator (metric that measures SLO)

**TAM/SAM/SOM:** Total Addressable Market / Serviceable Addressable Market / Serviceable Obtainable Market

**RICE:** Reach, Impact, Confidence, Effort (prioritization framework)

**SSR:** Server-Side Rendering (rendering pages on server for SEO)

**E2E:** End-to-End (testing complete user flows)

**UX:** User Experience

**UI:** User Interface

**CLI:** Command Line Interface

---

## Related Documentation

For more details, see:
- **README.md** - Framework overview
- **PHILOSOPHY.md** - Core principles and axioms
- **COMMAND-REFERENCE.md** - All commands explained
- **FAQ.md** - Common questions

---

**Last Updated:** 2025-11-14
**Version:** 2.0.0
