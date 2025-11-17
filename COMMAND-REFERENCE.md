# Command Reference

Complete reference for all Stack-Driven slash commands.

---

## Overview

Stack-Driven includes **26 slash commands** organized into five categories:

1. **Core Cascade Commands** (14) - The main framework sessions
2. **Post-Cascade Extensions** (8) - Optional deep-dive sessions
3. **Meta Commands** (2) - Framework management
4. **Development Commands** (2) - Code review and quality assurance

---

## Quick Command Index

### Core Cascade (Sessions 1-14)

| Command | Session | Time | Output File(s) |
|---------|---------|------|----------------|
| `/refine-journey` | 1 | 30-45 min | `00-user-journey.md` |
| `/create-product-strategy` | 2 | 45-60 min | `01-product-strategy.md`, `11-product-strategy-essentials.md` |
| `/choose-tech-stack` | 3 | 15-20 min | `02-tech-stack.md` |
| `/generate-strategy` | 4 | 45-60 min | `03-mission.md`, `04-metrics.md`, `04-monetization.md`, `04-architecture.md` |
| `/create-brand-strategy` | 5 | 30-45 min | `05-brand-strategy.md` |
| `/create-design` | 6 | 30-40 min | `06-design-system.md` |
| `/design-database-schema` | 7 | 45-60 min | `07-database-schema.md`, `07-database-schema-essentials.md` |
| `/generate-api-contracts` | 8 | 45-60 min | `08-api-contracts.md`, `08-api-contracts-essentials.md` |
| `/create-test-strategy` | 9 | 30-45 min | `09-test-strategy.md`, `09-test-strategy-essentials.md` |
| `/generate-backlog` | 10 | 60-90 min | `10-backlog/*.md` (30-50 issues) |
| `/create-gh-issues` | 11 | 10-15 min | GitHub issues |
| `/scaffold-project` | 12 | 30-45 min | `12-project-scaffold.md`, `12-project-scaffold/*` |
| `/plan-deployment` | 13 | 30-45 min | `13-deployment-plan.md` |
| `/design-observability` | 14 | 30-45 min | `14-observability-strategy.md` |

**Total core cascade time:** 8-10 hours

### Post-Cascade Extensions (Optional)

| Command | When to Run | Time | Output File(s) |
|---------|-------------|------|----------------|
| `/discover-naming` | After Session 5 | 30-45 min | `15-brand-naming.md` |
| `/define-messaging` | After naming | 30-45 min | `16-brand-messaging.md` |
| `/design-brand-identity` | After messaging | 60-90 min | `17-brand-identity.md` |
| `/create-content-guidelines` | After messaging | 30-45 min | `18-content-guidelines.md` |
| `/design-user-experience` | After Session 4 | 60-90 min | `19-user-experience.md` |
| `/setup-analytics` | After Session 4 | 30-45 min | `20-analytics-plan.md` |
| `/design-growth-strategy` | After Session 4 | 60-90 min | `21-growth-strategy.md` |
| `/create-financial-model` | After Session 4 | 60-90 min | `22-financial-model.md` |

### Meta Commands

| Command | When to Run | Purpose |
|---------|-------------|---------|
| `/cascade-status` | Anytime | Check cascade progress and what to do next |
| `/run-cascade` | Session 1 start | Automatically execute all sessions sequentially |

### Development Commands

| Command | When to Run | Purpose |
|---------|-------------|---------|
| `/validate-outputs` | During/after cascade | Validate cascade outputs for quality and completeness |
| `/review-code` | During development | Guide comprehensive code review |

---

## Core Cascade Commands

### Session 1: `/refine-journey`

**Purpose:** Define your user journey through progressive interrogation

**When to run:** First step - start here

**Time required:** 30-45 minutes

**What it creates:**
- Complete user journey mapping (Steps 1-5)
- User persona definition
- Pain point identification
- Value proposition
- Journey "aha moment"

**Outputs:**
- `product-guidelines/00-user-journey.md`

**What you'll be asked:**
- Who are your users? (Be specific)
- What problem are they struggling with?
- What's their current journey?
- Where's the "aha moment" (value delivery)?
- What's the value ratio? (time saved, cost reduced, etc.)

**Example:** For a compliance SaaS, you'd define:
- User: Compliance officers at mid-size financial institutions
- Problem: Manual document review takes 4 hours per assessment
- Aha moment: AI assessment completed in 60 seconds
- Value ratio: 4 hours → 60 seconds = 240x faster

**Next step:** Run `/create-product-strategy`

**Tips:**
- Be specific about users ("compliance officers" not "businesses")
- Quantify value (4 hours → 5 minutes = 48x faster)
- Focus on problem, not solution
- Identify the "aha moment" (usually Step 3)

---

### Session 2: `/create-product-strategy`

**Purpose:** Validate journey with market analysis and competitive positioning

**When to run:** After Session 1 (journey defined)

**Time required:** 45-60 minutes

**What it creates:**
- Market sizing (TAM/SAM/SOM)
- Competitive analysis
- Strategic positioning
- Vision and goals
- Product roadmap

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - User persona, pain points

**Outputs:**
- `product-guidelines/01-product-strategy.md` (comprehensive)
- `product-guidelines/11-product-strategy-essentials.md` (for AI reading)

**What it does:**
- Analyzes your target market size
- Identifies key competitors
- Defines competitive advantages
- Creates strategic positioning
- Maps product vision to journey

**Next step:** Run `/choose-tech-stack`

**Tips:**
- Be realistic about market size
- Identify 3-5 key competitors
- Focus on differentiation from journey value
- Align vision with aha moment

---

### Session 3: `/choose-tech-stack`

**Purpose:** Recommend optimal tech stack based on journey requirements

**When to run:** After Session 2 (product strategy defined)

**Time required:** 15-20 minutes

**What it creates:**
- Technology recommendations (frontend, backend, database, hosting)
- Decision rationale for each choice
- Alternative technologies considered
- Team capability considerations

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Journey requirements
- `product-guidelines/01-product-strategy.md` - Scale expectations

**Outputs:**
- `product-guidelines/02-tech-stack.md`

**How it works:**
- Analyzes journey requirements (real-time? mobile? SEO? AI?)
- Evaluates technology options
- Recommends best fit with reasoning
- Explains trade-offs

**Example decisions:**
- Journey needs SEO → Recommends Next.js (SSR)
- Journey needs document processing + AI → Recommends Python/FastAPI
- Journey needs <100ms real-time → Recommends WebSockets

**Next step:** Run `/generate-strategy`

**Tips:**
- You can specify constraints ("team knows Python")
- Override recommendations if needed
- Trust the analysis - it's journey-driven
- "Boring is beautiful" - proven tech preferred

---

### Session 4: `/generate-strategy`

**Purpose:** Derive mission, metrics, monetization, and architecture from journey

**When to run:** After Session 3 (tech stack chosen)

**Time required:** 45-60 minutes

**What it creates:**
- Mission statement (derived from aha moment)
- North Star metric (measures mission fulfillment)
- Pricing strategy (aligned with value delivery)
- Architecture principles (journey-optimized)

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Journey and value
- `product-guidelines/02-tech-stack.md` - Technology choices

**Outputs:**
- `product-guidelines/03-mission.md`
- `product-guidelines/04-metrics.md`
- `product-guidelines/04-monetization.md`
- `product-guidelines/04-architecture.md`

**What it derives:**
- **Mission:** Promise to deliver value at specific journey step
- **Metrics:** Measures of journey progress and success
- **Monetization:** How to charge where value is delivered
- **Architecture:** Patterns to enable journey optimization

**Example (compliance SaaS):**
- Mission: "Transform 4-hour compliance assessments into 60-second automated reports"
- North Star: Assessments completed per month
- Pricing: $99/assessment (value: saves $400 in labor)
- Architecture: Event-driven for document processing pipeline

**Next step:** Run `/create-brand-strategy`

**Tips:**
- Mission should reference the aha moment
- North Star should measure mission fulfillment
- Pricing should give 10x+ ROI
- Architecture should serve critical journey steps

---

### Session 5: `/create-brand-strategy`

**Purpose:** Express journey value through brand positioning and personality

**When to run:** After Session 4 (strategy complete)

**Time required:** 30-45 min

**What it creates:**
- Brand positioning
- Brand personality
- Value proposition framing
- Brand voice guidelines
- Competitor differentiation

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - User and value
- `product-guidelines/03-mission.md` - Mission and promise
- `product-guidelines/04-metrics.md` - Success measures

**Outputs:**
- `product-guidelines/05-brand-strategy.md`

**What it defines:**
- How to communicate journey value
- Brand personality aligned with users
- Messaging that resonates with pain points
- Differentiation from competitors

**Next step:** Run `/create-design`

**Tips:**
- Brand should express journey value
- Personality should match target users
- Focus on emotional connection to aha moment

---

### Session 6: `/create-design`

**Purpose:** Create design system optimized for user journey flows

**When to run:** After Session 5 (brand strategy complete)

**Time required:** 30-40 minutes

**What it creates:**
- Color palette
- Typography system
- Component library (specific to journey flows)
- Spacing and layout systems
- Accessibility guidelines

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - User flows
- `product-guidelines/05-brand-strategy.md` - Brand personality

**Outputs:**
- `product-guidelines/06-design-system.md`

**What it designs:**
- Components for YOUR specific user flows
- Not generic design system - journey-optimized
- Every component serves a journey step

**Example (compliance SaaS):**
- Document upload component (Step 1)
- Progress indicator (Step 2)
- Report viewer (Step 3)
- Colors convey trust (blue) and success (green)

**Next step:** Run `/design-database-schema`

**Tips:**
- Design serves journey, not aesthetics
- Components should map to journey steps
- Accessibility is required, not optional

---

### Session 7: `/design-database-schema`

**Purpose:** Design complete database schema with ERD and migrations

**When to run:** After Session 6 (design system complete)

**Time required:** 45-60 minutes

**What it creates:**
- Complete database schema
- Entity relationship diagram (ERD)
- Migration files (actual code)
- Indexes and constraints
- Data validation rules

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Data needs from journey
- `product-guidelines/02-tech-stack.md` - Database choice
- `product-guidelines/04-architecture.md` - Data patterns

**Outputs:**
- `product-guidelines/07-database-schema.md` (documentation)
- `product-guidelines/07-database-schema-essentials.md` (for AI reading)

**What it generates:**
- Complete schema design
- Relationships between entities
- Indexes for performance
- Constraints for data integrity
- Migration files in tech stack format (Prisma, SQL, etc.)

**Example output:**
- ERD diagram
- Table definitions
- Migration scripts ready to run

**Next step:** Run `/generate-api-contracts`

**Tips:**
- Schema should support all journey steps
- Include indexes for critical queries
- Consider future scale from journey analysis

---

### Session 8: `/generate-api-contracts`

**Purpose:** Generate comprehensive API contracts with OpenAPI specification

**When to run:** After Session 7 (database schema designed)

**Time required:** 45-60 minutes

**What it creates:**
- OpenAPI 3.0 specification
- All API endpoints
- Request/response schemas
- Authentication requirements
- Error handling

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Journey flows
- `product-guidelines/07-database-schema.md` - Data models
- `product-guidelines/02-tech-stack.md` - API framework

**Outputs:**
- `product-guidelines/08-api-contracts.md` (documentation)
- `product-guidelines/08-api-contracts-essentials.md` (for AI reading)

**What it generates:**
- Complete OpenAPI spec
- Endpoint definitions for each journey step
- Authentication strategy
- Rate limiting considerations
- Error response standards

**Example endpoints:**
- `POST /api/documents` (upload)
- `GET /api/documents/:id/status` (check progress)
- `GET /api/documents/:id/report` (retrieve results)

**Next step:** Run `/create-test-strategy`

**Tips:**
- Every journey step should have API support
- Include error cases and edge cases
- Document authentication clearly

---

### Session 9: `/create-test-strategy`

**Purpose:** Define comprehensive testing strategy (unit, integration, E2E)

**When to run:** After Session 8 (API contracts defined)

**Time required:** 30-45 minutes

**What it creates:**
- Unit testing strategy
- Integration testing approach
- End-to-end testing plan
- Performance testing criteria
- Test coverage goals

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Critical paths to test
- `product-guidelines/08-api-contracts.md` - APIs to test
- `product-guidelines/02-tech-stack.md` - Testing frameworks

**Outputs:**
- `product-guidelines/09-test-strategy.md` (documentation)
- `product-guidelines/09-test-strategy-essentials.md` (for AI reading)

**What it defines:**
- What to test (and what not to test)
- Testing frameworks and tools
- Coverage targets
- CI/CD integration
- Critical path testing (journey steps)

**Next step:** Run `/generate-backlog`

**Tips:**
- Focus on critical journey paths
- E2E tests should mirror user journey
- Don't over-test (80% coverage target)

---

### Session 10: `/generate-backlog`

**Purpose:** Generate 30-50 prioritized user stories informed by all previous sessions

**When to run:** After Session 9 (test strategy defined)

**Time required:** 60-90 minutes

**What it creates:**
- 30-50 user stories
- RICE prioritization (Reach, Impact, Confidence, Effort)
- P0/P1/P2 labels
- Dependencies mapped
- Every story traced to journey step

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Journey to support
- `product-guidelines/07-database-schema.md` - Data features
- `product-guidelines/08-api-contracts.md` - API features
- All previous sessions for context

**Outputs:**
- `product-guidelines/10-backlog/` directory
- Individual `.md` files for each story
- `P0-*.md`, `P1-*.md`, `P2-*.md`

**What it generates:**
- User stories: "As [user], I want [feature] so that [value]"
- Acceptance criteria
- Technical notes
- Dependencies
- RICE scores

**Example stories:**
- P0: Document upload functionality
- P0: AI assessment engine
- P1: User authentication
- P2: Email notifications

**Next step:** Run `/create-gh-issues`

**Tips:**
- P0 = critical for MVP (journey steps 1-3)
- Every story should reference a journey step
- Check dependencies to avoid blockers

---

### Session 11: `/create-gh-issues`

**Purpose:** Push all backlog issues to GitHub

**When to run:** After Session 10 (backlog generated)

**Time required:** 10-15 minutes

**What it creates:**
- GitHub issues for all backlog stories
- Proper labels (P0, P1, P2)
- Milestone assignments
- Project board organization

**Inputs (what it reads):**
- `product-guidelines/10-backlog/*.md` - All user stories

**Outputs:**
- GitHub issues in your repository

**What it does:**
- Converts backlog files to GitHub issues
- Applies labels and milestones
- Sets up project board (optional)
- Creates issue relationships

**Next step:** Run `/scaffold-project`

**Tips:**
- Ensure GitHub CLI is authenticated
- Review labels before creating
- Can re-run if issues need updates

---

### Session 12: `/scaffold-project`

**Purpose:** Generate working development environment with actual code files

**When to run:** After Session 11 (issues created)

**Time required:** 30-45 minutes

**What it creates:**
- Complete project scaffold
- Package manager configs (package.json, pyproject.toml, etc.)
- Docker Compose for local development
- Environment configuration (.env.template)
- CI/CD pipeline (GitHub Actions)
- Setup documentation

**Inputs (what it reads):**
- `product-guidelines/02-tech-stack.md` - Technologies to scaffold
- `product-guidelines/04-architecture.md` - Structure and patterns
- `product-guidelines/07-database-schema.md` - Database setup
- `product-guidelines/10-backlog/` - What features to support

**Outputs:**
- `product-guidelines/12-project-scaffold.md` (decisions documentation)
- `product-guidelines/12-project-scaffold/` directory with:
  - `package.json` or `pyproject.toml`
  - `docker-compose.yml`
  - `.env.template`
  - `.github/workflows/ci.yml`
  - `README.md` (setup instructions)
  - Basic directory structure
  - Configuration files

**What it generates:**
- Working development environment
- All dependencies configured
- Database setup scripts
- CI/CD pipeline
- One-command setup

**Next step:** Run `/plan-deployment`

**Tips:**
- Copy generated files to your project
- Run `docker-compose up` to verify
- Follow README for setup
- Actual runnable code, not just templates

---

### Session 13: `/plan-deployment`

**Purpose:** Create deployment strategy and CI/CD pipeline plan

**When to run:** After Session 12 (project scaffolded)

**Time required:** 30-45 minutes

**What it creates:**
- Deployment strategy (environments, CI/CD, rollout)
- Environment configuration (dev, staging, production)
- CI/CD pipeline details
- Infrastructure as code
- Rollback procedures

**Inputs (what it reads):**
- `product-guidelines/02-tech-stack.md` - Hosting platform
- `product-guidelines/04-architecture.md` - Deployment patterns
- `product-guidelines/04-metrics.md` - Success metrics

**Outputs:**
- `product-guidelines/13-deployment-plan.md`

**What it defines:**
- Deployment environments
- CI/CD workflow
- Infrastructure requirements
- Monitoring integration
- Rollback and recovery plans
- Cost estimates

**Next step:** Run `/design-observability`

**Tips:**
- Start simple (single environment for MVP)
- Automate everything
- Plan for rollback from day 1

---

### Session 14: `/design-observability`

**Purpose:** Design monitoring, alerting, and observability strategy

**When to run:** After Session 13 (deployment planned)

**Time required:** 30-45 minutes

**What it creates:**
- Monitoring strategy (metrics, logs, traces)
- Alerting rules and thresholds
- SLO/SLI definitions
- Incident response procedures
- Dashboard designs

**Inputs (what it reads):**
- `product-guidelines/00-user-journey.md` - Critical paths to monitor
- `product-guidelines/04-metrics.md` - Business metrics
- `product-guidelines/13-deployment-plan.md` - Infrastructure

**Outputs:**
- `product-guidelines/14-observability-strategy.md`

**What it defines:**
- What to monitor (and what not to)
- Alerting strategy
- SLOs for critical paths
- Logging approach
- Incident response
- Performance budgets

**Next step:** Start building! Copy scaffold files and implement P0 features.

**Tips:**
- Monitor journey critical paths first
- Don't over-alert (alert fatigue is real)
- SLOs should align with user experience
- Start with basics, expand as you scale

---

## Post-Cascade Extension Commands

These are **optional** deep-dive sessions that extend the core cascade. Run them after completing relevant core sessions.

### `/discover-naming`

**Purpose:** Generate and evaluate brand name candidates

**When to run:** After Session 5 (brand strategy complete)

**Time required:** 30-45 minutes

**What it creates:**
- 20-30 name candidates
- Evaluation criteria
- Domain availability checks
- Trademark considerations
- Final recommendations

**Inputs:**
- `product-guidelines/05-brand-strategy.md` - Brand personality
- `product-guidelines/00-user-journey.md` - Value proposition

**Outputs:**
- `product-guidelines/15-brand-naming.md`

**Use when:**
- You need a product/company name
- You want systematic naming evaluation
- You need to check domain availability

---

### `/define-messaging`

**Purpose:** Create brand messaging framework and voice guidelines

**When to run:** After naming (or after Session 5)

**Time required:** 30-45 minutes

**What it creates:**
- Messaging hierarchy
- Value propositions for different audiences
- Voice and tone guidelines
- Key messages
- Messaging do's and don'ts

**Inputs:**
- `product-guidelines/05-brand-strategy.md` - Brand foundation
- `product-guidelines/15-brand-naming.md` - Name context

**Outputs:**
- `product-guidelines/16-brand-messaging.md`

**Use when:**
- Creating marketing copy
- Need consistent messaging
- Multiple writers need guidelines

---

### `/design-brand-identity`

**Purpose:** Design comprehensive brand identity (logo, visual system, guidelines)

**When to run:** After messaging complete

**Time required:** 60-90 minutes

**What it creates:**
- Logo concepts and guidelines
- Color system
- Typography
- Visual language
- Brand guidelines document

**Inputs:**
- `product-guidelines/05-brand-strategy.md` - Personality
- `product-guidelines/16-brand-messaging.md` - Messaging

**Outputs:**
- `product-guidelines/17-brand-identity.md`

**Use when:**
- Need complete brand identity
- Creating marketing materials
- Establishing visual consistency

---

### `/create-content-guidelines`

**Purpose:** Create detailed content style guide and microcopy patterns

**When to run:** After messaging defined

**Time required:** 30-45 minutes

**What it creates:**
- Content style guide
- Microcopy patterns (buttons, errors, success messages)
- Editorial guidelines
- SEO considerations
- Content templates

**Inputs:**
- `product-guidelines/16-brand-messaging.md` - Voice and tone
- `product-guidelines/00-user-journey.md` - User context

**Outputs:**
- `product-guidelines/18-content-guidelines.md`

**Use when:**
- Writing UI copy
- Creating help documentation
- Need consistent content voice

---

### `/design-user-experience`

**Purpose:** Create detailed UX research, flows, wireframes, and interaction specs

**When to run:** After Session 4 (strategy complete)

**Time required:** 60-90 minutes

**What it creates:**
- Detailed user flows
- Wireframes for key screens
- Interaction specifications
- UX research plan
- Usability testing criteria

**Inputs:**
- `product-guidelines/00-user-journey.md` - High-level journey
- `product-guidelines/06-design-system.md` - Components

**Outputs:**
- `product-guidelines/19-user-experience.md`

**Use when:**
- Need detailed UX specifications
- Building complex interactions
- Want to validate UX before development

---

### `/setup-analytics`

**Purpose:** Create detailed analytics implementation plan

**When to run:** After Session 4 (metrics defined)

**Time required:** 30-45 minutes

**What it creates:**
- Analytics tool recommendations
- Event tracking plan
- Funnel analysis setup
- Dashboard designs
- Privacy and compliance considerations

**Inputs:**
- `product-guidelines/04-metrics.md` - What to measure
- `product-guidelines/00-user-journey.md` - Critical paths

**Outputs:**
- `product-guidelines/20-analytics-plan.md`

**Use when:**
- Implementing analytics
- Need to track metrics from Session 4
- Want data-driven decisions

---

### `/design-growth-strategy`

**Purpose:** Create data-driven growth strategy with acquisition channels and experiments

**When to run:** After Session 4 (strategy complete)

**Time required:** 60-90 minutes

**What it creates:**
- Acquisition channel analysis
- Growth loops identification
- Experiment roadmap
- Channel-specific tactics
- CAC/LTV projections

**Inputs:**
- `product-guidelines/00-user-journey.md` - Target audience
- `product-guidelines/04-monetization.md` - Unit economics
- `product-guidelines/01-product-strategy.md` - Market size

**Outputs:**
- `product-guidelines/21-growth-strategy.md`

**Use when:**
- Planning go-to-market
- Need customer acquisition strategy
- Want to optimize growth loops

---

### `/create-financial-model`

**Purpose:** Create comprehensive financial model with unit economics and projections

**When to run:** After Session 4 (monetization defined)

**Time required:** 60-90 minutes

**What it creates:**
- Unit economics (CAC, LTV, payback)
- Revenue projections (3-5 years)
- Cost structure analysis
- Scenario planning
- Fundraising considerations

**Inputs:**
- `product-guidelines/04-monetization.md` - Pricing
- `product-guidelines/21-growth-strategy.md` - Acquisition costs
- `product-guidelines/01-product-strategy.md` - Market size

**Outputs:**
- `product-guidelines/22-financial-model.md`

**Use when:**
- Fundraising preparation
- Need financial projections
- Validating business model viability

---

## Meta Commands

### `/cascade-status`

**Purpose:** Check cascade progress and determine next steps

**When to run:** Anytime

**What it does:**
- Shows which sessions are complete
- Shows what comes next
- Displays cascade flow
- Lists inputs/outputs for each session
- Identifies any missing dependencies

**No outputs** - informational only

**Use when:**
- Starting the framework (shows where to begin)
- Lost track of progress
- Need to know what to run next
- Want to see full cascade structure

**Example output:**
```
Core Cascade Progress:
✅ Session 1: /refine-journey (complete)
✅ Session 2: /create-product-strategy (complete)
⏹️ Session 3: /choose-tech-stack (not started)

Next step: Run /choose-tech-stack
```

---

### `/run-cascade`

**Purpose:** Automatically execute all sessions sequentially from current progress

**When to run:** Session 1 start (or after any session to auto-continue)

**Time required:** Full cascade time (8-10 hours, can pause/resume)

**What it does:**
- Executes sessions automatically in order
- Pauses at major milestones for review
- Handles dependencies between sessions
- Continues from where you left off

**Use when:**
- Want rapid progress through framework
- Prefer automated execution
- Have clear requirements (less iteration needed)

**vs Manual:**
- Manual (individual commands): Better for learning, more control
- Auto (/run-cascade): Faster, fewer interruptions

---

## Development Commands

### `/validate-outputs`

**Purpose:** Validate cascade outputs for quality and completeness

**When to run:** During or after cascade sessions

**What it does:**
- Validates all cascade outputs against Stack-Driven quality standards
- Checks journey alignment (decisions trace to user value)
- Verifies philosophy adherence (user-first, journey-driven, generative)
- Assesses completeness and consistency across sessions
- Identifies generic outputs that need more specificity
- Provides actionable recommendations for improvement

**Quality criteria checked:**
- **Journey Alignment**: References specific journey steps, quantified value
- **Philosophy Adherence**: User-first thinking, not tech-first
- **Completeness**: All template sections filled, alternatives considered
- **Consistency**: Cross-file references match (tech aligns with journey, etc.)
- **Specificity**: Concrete examples, not generic statements
- **Technical Soundness**: Proper indexes, error handling, edge cases

**Outputs:**
- Comprehensive quality report (in conversation, no file created)
- Critical issues that must be addressed
- Important suggestions for improvement
- Sessions to regenerate if needed

**Use when:**
- Unsure if outputs are specific enough (not generic)
- Want to verify quality before continuing cascade
- Preparing to share outputs with team/stakeholders
- Checking journey alignment after completing sessions
- Identifying which sessions may need refinement

**Example issues caught:**
- Generic journey descriptions ("users want better experience")
- Tech choices without journey justification
- Missing "What We DIDN'T Choose" sections
- Inconsistent references across files
- Superficial analysis where depth needed

**Tips:**
- Run after completing key milestones (Session 4, 10, 14)
- Address critical issues before continuing cascade
- Compare outputs to `examples/compliance-saas/` for quality benchmark
- Use to validate before sharing with team

---

### `/review-code`

**Purpose:** Guide comprehensive code review with quality framework

**When to run:** During development, before merging PRs

**What it does:**
- Provides code review checklist
- Checks alignment with:
  - Architecture principles
  - Design system
  - API contracts
  - Testing strategy
- Reviews for:
  - Security vulnerabilities
  - Performance issues
  - Code quality
  - Journey alignment

**Use when:**
- Reviewing pull requests
- Quality check before deployment
- Ensuring consistency with strategy

---

## Command Workflows

### Minimum Viable Cascade (3 hours)

Essential sessions only:

```bash
/refine-journey          # 45 min
/create-product-strategy # 45 min
/choose-tech-stack       # 20 min
/generate-strategy       # 60 min
```

**Result:** Strategic foundation (journey, market, tech, mission, metrics, monetization, architecture)

---

### Complete Core Cascade (8-10 hours)

All core sessions:

```bash
/refine-journey
/create-product-strategy
/choose-tech-stack
/generate-strategy
/create-brand-strategy
/create-design
/design-database-schema
/generate-api-contracts
/create-test-strategy
/generate-backlog
/create-gh-issues
/scaffold-project
/plan-deployment
/design-observability
```

**Result:** Production-ready system from idea to deployment + monitoring

---

### Full Framework + Extensions (12-15 hours)

Core + selected extensions:

```bash
# Core cascade (8-10 hours)
/refine-journey ... /design-observability

# Branding extensions (3-4 hours)
/discover-naming
/define-messaging
/design-brand-identity
/create-content-guidelines

# Growth extensions (2-3 hours)
/design-growth-strategy
/create-financial-model
/setup-analytics
```

**Result:** Complete product, brand, and growth strategy

---

## Common Patterns

### Rerunning Sessions

Any session can be re-run to regenerate outputs:

```bash
# Initial run
/refine-journey

# ... later, after user interviews ...
# Refine and regenerate
/refine-journey  # Updates journey
/choose-tech-stack  # Regenerates with new journey
/generate-strategy  # Regenerates with new tech
# etc.
```

**Cascade automatically updates downstream sessions.**

---

### Skipping Sessions

Not recommended, but possible:

- **Can skip:** Post-cascade extensions (all optional)
- **Should NOT skip:** Core Sessions 1-4 (foundation)
- **Consider carefully:** Sessions 5-14 (highly valuable)

**If you skip a session, downstream sessions won't have required inputs.**

---

### Partial Cascade

Focus on specific outcomes:

**Just want tech stack recommendation?**
```bash
/refine-journey
/choose-tech-stack
```

**Just want backlog?**
```bash
/refine-journey
/create-product-strategy
/choose-tech-stack
/generate-strategy
/generate-backlog
```

**Just want development environment?**
```bash
# Complete Sessions 1-11 first
/scaffold-project
```

---

## Tips for Success

### Session 1 (Journey)
- Be specific: "Solo SaaS founders" not "businesses"
- Quantify value: 4 hours → 10 minutes = 24x faster
- Find the aha moment (usually Step 3)
- Focus on problem, not your solution

### Session 2 (Product Strategy)
- Research market size thoroughly
- Identify real competitors (not "no competitors")
- Be honest about differentiation
- Validate assumptions with data

### Session 3 (Tech Stack)
- Trust the journey-driven analysis
- Mention constraints ("We know Python")
- Override if you have strong reasons
- Boring tech > exciting tech for MVPs

### Session 4 (Strategy)
- Mission should reference aha moment
- North Star should measure mission
- Pricing should give 10x+ ROI
- Architecture should serve critical path

### Sessions 5-6 (Brand & Design)
- Brand expresses journey value
- Design serves journey, not aesthetics
- Components map to journey steps
- Personality matches target users

### Sessions 7-9 (Technical Specs)
- Schema supports all journey steps
- APIs cover every user action
- Tests focus on critical paths
- Don't over-engineer for MVP

### Session 10 (Backlog)
- Every story references journey
- P0 = critical for MVP
- Check dependencies
- Accept criteria should be specific

### Sessions 12-14 (Production Readiness)
- Start simple, scale later
- Automate everything
- Monitor critical paths first
- Plan for failure (rollback, recovery)

---

## Troubleshooting

### "I don't see my output files"

Output files are saved to `product-guidelines/` (gitignored by default).

```bash
ls product-guidelines/
```

---

### "Command says it can't find previous session file"

You may have skipped a required session. Run `/cascade-status` to see what's missing.

```bash
/cascade-status
```

---

### "I want to change a previous decision"

Re-run the session that made that decision. Downstream sessions will automatically reference the updated file.

```bash
# Change tech stack
/choose-tech-stack  # Make different choices

# Regenerate strategy with new tech
/generate-strategy
```

---

### "Session output doesn't match my needs"

Provide more specific constraints when running the command:
- Mention team capabilities ("we're Python experts")
- State limitations ("budget is $50/month")
- Reference specific requirements from journey

You can also edit the output files directly.

---

## Command Development

Want to create your own commands? See `IMPLEMENTATION-PROMPT.md` for detailed guidance on creating new slash commands that integrate with the cascade.

---

## Version History

**Current version:** 2.0.0

See `CHANGELOG.md` for version history and changes.

---

## Additional Resources

- **README.md** - Framework overview and philosophy
- **GETTING-STARTED.md** - New user onboarding
- **PHILOSOPHY.md** - Framework principles and architecture
- **TROUBLESHOOTING.md** - Common issues and solutions
- **FAQ.md** - Frequently asked questions
- **GLOSSARY.md** - Framework terminology
- **QUICK-REFERENCE.md** - One-page cheat sheet

---

**Last Updated:** 2025-11-14
**Version:** 2.0.0
