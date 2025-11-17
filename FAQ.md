# Frequently Asked Questions

Common questions about Stack-Driven framework.

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Getting Started](#getting-started)
3. [Framework Philosophy](#framework-philosophy)
4. [Using the Cascade](#using-the-cascade)
5. [Tech Stack Decisions](#tech-stack-decisions)
6. [Customization](#customization)
7. [Templates vs Examples](#templates-vs-examples)
8. [Time and Effort](#time-and-effort)
9. [Team Usage](#team-usage)
10. [Extensions and Integrations](#extensions-and-integrations)
11. [Comparison to Alternatives](#comparison-to-alternatives)

---

## General Questions

### What is Stack-Driven?

Stack-Driven is an AI-assisted product development framework that takes you from idea to production-ready system through a systematic cascade of 14 progressive sessions.

It's **not** just templates or prompts - it's a **generative system** where each session analyzes your specific user journey and derives optimal decisions for your product.

**Key principle:** User experience is the core of every product. Everything flows from the journey.

---

### Is this just templates I could copy?

**No.** Templates are static. Stack-Driven is **generative**:

- **Templates (static):** "Here's a mission statement, fill in the blanks"
- **Stack-Driven (generative):** "Tell me your user journey. I'll analyze it and derive a mission statement that promises value at your aha moment"

**Example:**
- Template: "We help [users] do [thing]"
- Stack-Driven: Analyzes your journey (compliance officers, 4-hour → 60-second assessment) → Mission: "Transform 4-hour compliance assessments into 60-second automated reports"

Same framework, different journeys → different outputs.

---

### Who is this for?

**Ideal users:**

1. **Startup Founders** - Get CPO + CTO + Head of Design outputs in 8-10 hours
2. **Solo Developers** - Ship products that feel like they were built by a full team
3. **Product Teams** - Align on strategy before building
4. **AI Coding Agents** - Reference strategy files to make decisions aligned with product vision
5. **Engineering Teams** - Understand "why" behind architectural decisions

**Not ideal for:**
- People who want generic templates
- Teams with strong existing strategy (though can validate/refine)
- Projects with fixed tech stack constraints (though framework adapts)

---

### What's the output? What do I get?

After completing the core cascade (Sessions 1-14), you have:

**Strategic Foundation:**
- User journey map
- Market validation (TAM/SAM/SOM, competitive analysis)
- Mission statement, North Star metric, pricing strategy
- Brand strategy and design system

**Technical Specifications:**
- Tech stack optimized for YOUR requirements
- Database schema (ERD, migrations)
- API contracts (OpenAPI specs)
- Testing strategy (unit, integration, E2E)
- Architecture principles

**Execution Ready:**
- 30-50 prioritized user stories (P0/P1/P2)
- GitHub issues ready for development
- Complete project scaffold (runnable code)
- Deployment strategy and CI/CD pipeline
- Observability and monitoring plan

**Time investment:** 8-10 hours
**Result:** Production-ready system from idea to deployment

---

### Is this free? Open source?

**Yes.** Stack-Driven is:
- Open source (Apache 2.0 license)
- Free to use
- Community-maintained

**However:**
- You need access to an AI assistant (Claude, etc.)
- AI assistant usage may have costs
- Framework is free, AI usage is separate

---

## Getting Started

### Where do I start?

```bash
/cascade-status
```

This shows your current progress and tells you exactly what to run next.

If starting fresh:
```bash
/refine-journey
```

See **GETTING-STARTED.md** for detailed onboarding.

---

### Do I have to do all 14 sessions?

**Minimum viable cascade** (Sessions 1-4, ~3 hours):
- Journey → Product Strategy → Tech Stack → Strategy (mission/metrics/monetization/architecture)
- **Result:** Strategic foundation

**Recommended core** (Sessions 1-14, ~8-10 hours):
- Complete cascade to production-ready system
- **Result:** Strategy + technical specs + backlog + deployment plan

**Optional extensions** (Sessions 15-22):
- Branding (naming, messaging, identity)
- Growth strategy and financial model
- Deep UX research
- Analytics implementation

You decide based on your needs.

---

### Should I use automated (`/run-cascade`) or manual mode?

**Manual (run each command individually):**
- ✅ Better for learning
- ✅ More control at each step
- ✅ Can iterate and refine
- ❌ More interruptions
- ❌ Slower overall

**Automated (`/run-cascade`):**
- ✅ Faster (continuous flow)
- ✅ Fewer interruptions
- ✅ Good for clear requirements
- ❌ Less control
- ❌ Harder to iterate mid-cascade

**Recommendation:**
- First time? Manual (learn the framework)
- Clear requirements? Automated (rapid progress)
- Unsure about journey? Manual (iterate Session 1 first)

---

### Can I stop and resume later?

**Yes.** The cascade is stateful:

```bash
# Day 1
/refine-journey
/create-product-strategy
/choose-tech-stack

# Day 2 (resume)
/cascade-status  # See you're at Session 4
/generate-strategy
# ... continue
```

All outputs are saved to `product-guidelines/` and persist between sessions.

---

### How do I know if I'm doing it right?

**Quality checks at each session:**

1. **Does output reference your journey?** Every decision should trace to user value
2. **Does it feel specific to your product?** Generic outputs mean you weren't specific enough in inputs
3. **Can you defend the choices?** AI provides reasoning - does it make sense?
4. **Are there alternatives considered?** "What We DIDN'T Choose" sections force critical thinking

**Run** `/cascade-status` to verify file dependencies are met.

**Compare** with examples: `examples/compliance-saas/` shows what good outputs look like.

---

## Framework Philosophy

### Why start with user journey, not technology?

**The core axiom:** User Experience is the Core of Every Product.

Starting with technology is backwards:
- ❌ "I want to build a Next.js app" → Then find a problem it can solve
- ✅ "Users struggle with X problem" → What technology best solves this?

**Example:**
- **Wrong:** "I'll use Next.js because I know React"
- **Right:** "Users need shareable reports (SEO matters) → Next.js SSR makes sense"

Technology serves users, not the other way around.

---

### What if I already know what tech I want to use?

**You can!** Specify constraints in Session 3:

```bash
/choose-tech-stack

# When asked:
"Our team already uses Python/Django.
We want to continue with this stack.
Please validate if it fits our journey or recommend adjustments."
```

AI will either:
1. Validate your choice aligns with journey
2. Suggest modifications (e.g., add Next.js frontend for SSR)
3. Warn if there's a major mismatch

You always have final say. Framework provides reasoning, you decide.

---

### What does "generative, not prescriptive" mean?

**Prescriptive (templates):**
- "Use this mission statement template"
- "Here's a backlog of common features"
- "Choose from these 3 tech stacks"

**Generative (Stack-Driven):**
- "Tell me your journey. I'll analyze your aha moment and derive a mission that promises that value."
- "Based on your journey, architecture, and tech stack, I'll generate 30-50 stories specific to your product."
- "I'll analyze your journey requirements (real-time? mobile? SEO? AI?) and recommend the optimal stack with reasoning."

Same framework → Different journeys → Different outputs.

---

### Can I disagree with a recommendation?

**Absolutely.** The framework shows reasoning for every decision:

- "I chose X because your journey requires Y"
- "I considered Z but ruled it out because [trade-off]"

If you disagree:
1. Edit the output file directly
2. Re-run the session with different constraints
3. Override the recommendation

**Example:**
```bash
/choose-tech-stack
# AI recommends: PostgreSQL

# You prefer: MongoDB
# Edit product-guidelines/02-tech-stack.md to use MongoDB
# Future sessions will use your choice
```

Framework is opinionated but flexible.

---

## Using the Cascade

### What happens if I skip a session?

**Short answer:** Downstream sessions won't have required inputs.

**Example:**
- Skip Session 2 (product strategy)
- Session 3 (tech stack) can't analyze scale expectations
- Session 4 (strategy) can't derive mission without market context

**Some sessions are more critical:**
- **Must not skip:** Sessions 1-4 (foundation)
- **Highly valuable:** Sessions 5-14 (completeness)
- **Optional:** Sessions 15-22 (extensions)

If you skip, you can always go back and run it later, then re-run downstream sessions.

---

### How do I update a previous decision?

**Re-run that session, then regenerate downstream sessions:**

```bash
# Change journey after user interviews
/refine-journey

# Regenerate everything that depends on journey:
/create-product-strategy
/choose-tech-stack
/generate-strategy
# ... etc

# Or use automated:
/run-cascade
```

**Warning:** This overwrites files. Back up manual edits first:
```bash
cp -r product-guidelines product-guidelines.backup
```

---

### Can I run sessions out of order?

**Not recommended.** The cascade is designed to flow:

```
Journey → Product Strategy → Tech → Strategy → Brand → Design → Database → API → Tests → Backlog → Issues → Scaffold → Deploy → Observe
```

Each session reads outputs from previous sessions.

**However**, some post-cascade extensions are independent:
- `/discover-naming` (after brand strategy)
- `/design-growth-strategy` (after strategy)
- `/create-financial-model` (after monetization)

Check `COMMAND-REFERENCE.md` for dependencies.

---

### What's the difference between "core cascade" and "post-cascade extensions"?

**Core Cascade (Sessions 1-14):**
- Required for production-ready system
- Each builds on previous (strict dependency)
- Takes you from idea to deployment plan
- 8-10 hours total

**Post-Cascade Extensions (Sessions 15-22):**
- Optional deep dives
- Run after completing relevant core sessions
- Independent (can pick and choose)
- Examples: Brand naming, growth strategy, financial model

**Minimum to ship:** Core Sessions 1-4
**Complete system:** Core Sessions 1-14
**Full framework:** Core + selected extensions

---

### How do I know which files a session reads?

Every command documents its inputs:

```bash
# Check command file
cat .claude/commands/generate-strategy.md

# Look for "Inputs (What This Reads)" section
```

Or check `COMMAND-REFERENCE.md` for quick reference.

Or run `/cascade-status` to see full dependency tree.

---

## Tech Stack Decisions

### Will Stack-Driven recommend the best tech stack for my product?

**Yes**, with caveats:

1. **Journey-driven:** Recommendation is based on YOUR journey requirements
2. **Reasoned:** AI explains WHY each technology was chosen
3. **Adaptable:** You can specify constraints (team expertise, budget, etc.)
4. **Not absolute:** "Best" depends on context

**What it analyzes:**
- Real-time requirements? → WebSockets, Node.js
- SEO important? → SSR (Next.js, SvelteKit)
- Document processing + AI? → Python ecosystem
- Mobile-first? → React Native, Flutter
- Complex data relationships? → PostgreSQL
- Rapid iteration? → Flexible schema (MongoDB)

**Different journeys → Different stacks.**

---

### What if I don't agree with the tech choices?

**Override them.** You have three options:

1. **Provide constraints upfront:**
   ```bash
   /choose-tech-stack
   # Specify: "Team only knows JavaScript. Budget is $50/month."
   ```

2. **Edit the output:**
   ```bash
   vim product-guidelines/02-tech-stack.md
   # Change recommendations
   ```

3. **Re-run with different inputs:**
   ```bash
   /choose-tech-stack
   # Different answers → Different recommendations
   ```

Future sessions will use your choices.

---

### Does Stack-Driven support [my preferred technology]?

**Yes.** Stack-Driven is technology-agnostic:

- Supports any frontend (React, Vue, Svelte, etc.)
- Supports any backend (Node, Python, Go, etc.)
- Supports any database (PostgreSQL, MySQL, MongoDB, etc.)
- Supports any hosting (Vercel, AWS, Railway, etc.)

**How?**
- Session 3 chooses tech based on journey
- Sessions 7-12 generate code/config for chosen tech
- AI adapts templates to your specific stack

**Example:** If you choose Python/FastAPI:
- Session 12 scaffolds `pyproject.toml`, FastAPI server, etc.
- Not generic - specific to FastAPI

---

### Can I use Stack-Driven for non-web products?

**Yes**, though it's optimized for web/SaaS:

**Works well for:**
- Web applications
- Mobile apps (using web tech or native)
- SaaS products
- APIs and services
- Chrome extensions

**Can work for:**
- Desktop applications (Electron, etc.)
- CLI tools
- Libraries/frameworks

**Not designed for:**
- Hardware products
- Physical goods
- Services without software

The key is defining the user journey - if there's a digital journey, Stack-Driven can help.

---

## Customization

### Can I modify the templates?

**Yes.** Templates are in `templates/` directory:

```bash
# Edit any template
vim templates/06-design-system-template.md
```

Sessions use these templates when generating outputs.

**However:**
- Modifying templates affects future sessions
- May break cascade if you remove required sections
- Consider creating custom commands instead

---

### Can I add my own slash commands?

**Yes.** See `IMPLEMENTATION-PROMPT.md` for detailed guidance.

**Quick overview:**
1. Create `.claude/commands/my-command.md`
2. Follow existing command structure
3. Create corresponding template in `templates/`
4. Update `/cascade-status` to include your command

**Best practices:**
- Read inputs from previous sessions
- Output to `product-guidelines/`
- Include "What We DIDN'T Choose" section
- Trace decisions back to journey

---

### Can I change the output directory?

**Not recommended**, but possible:

Current: All outputs go to `product-guidelines/`

To change:
1. Update all commands to reference new directory
2. Update `.gitignore`
3. Update documentation

**Warning:** This breaks cascade integration. Better to symlink:
```bash
ln -s product-guidelines my-custom-folder
```

---

### Can I use Stack-Driven for multiple products?

**Yes.** Each product should have its own cascade:

```bash
# Project A
cd project-a/
/refine-journey
# ... generate project-a/product-guidelines/

# Project B
cd project-b/
/refine-journey
# ... generate project-b/product-guidelines/
```

Each directory has independent `product-guidelines/` outputs.

Or use branches:
```bash
git checkout -b product-a-cascade
# Run cascade

git checkout -b product-b-cascade
# Run cascade
```

---

## Templates vs Examples

### What's the difference between `templates/` and `examples/`?

**Templates (`templates/`):**
- Blank starting points
- Used by commands to generate YOUR outputs
- You don't edit these directly (edit outputs instead)

**Examples (`examples/`):**
- Complete cascade runs for reference
- Shows what good outputs look like
- Currently: `examples/compliance-saas/`

**Workflow:**
1. AI reads `templates/03-mission-template.md`
2. AI generates `product-guidelines/03-mission.md` for YOUR product
3. You compare with `examples/compliance-saas/foundation/01-mission.md` to see quality

---

### Should I copy the examples?

**No.** Examples are for **reference**, not copying:

- `examples/compliance-saas/` shows a SaaS product journey
- **Your** journey will be different
- **Your** tech stack will likely be different
- **Your** mission, metrics, backlog will be different

**Use examples to:**
- Understand what good outputs look like
- Check level of detail expected
- Validate your outputs have similar structure

**Don't:**
- Copy and paste from examples
- Assume your journey matches the example
- Skip sessions because "example did it differently"

---

### Will there be more examples?

**Planned examples:**
- Real-time multiplayer game (shows mobile + WebSockets stack)
- E-commerce marketplace (shows different architecture)
- B2C mobile app (shows different journey → different stack)

Check `examples/` directory for latest additions.

---

## Time and Effort

### How long does the full cascade take?

**Core Cascade (Sessions 1-14):** 8-10 hours total

**Breakdown:**
- Session 1 (Journey): 30-45 min
- Session 2 (Product Strategy): 45-60 min
- Session 3 (Tech Stack): 15-20 min
- Session 4 (Strategy): 45-60 min
- Session 5 (Brand): 30-45 min
- Session 6 (Design): 30-40 min
- Session 7 (Database): 45-60 min
- Session 8 (API): 45-60 min
- Session 9 (Testing): 30-45 min
- Session 10 (Backlog): 60-90 min
- Session 11 (GitHub): 10-15 min
- Session 12 (Scaffold): 30-45 min
- Session 13 (Deployment): 30-45 min
- Session 14 (Observability): 30-45 min

**Can spread over days/weeks** - sessions are independent time blocks.

---

### Can I do it faster?

**Yes**, using `/run-cascade`:

- Automated execution (fewer interruptions)
- Can complete in 6-8 hours
- Less iteration, more speed

**Trade-off:** Less control, harder to iterate.

**Fastest minimum viable:**
- Sessions 1-4 only: ~3 hours
- Gets you strategic foundation
- Can fill in Sessions 5-14 later

---

### Is this faster than doing it manually?

**Yes, significantly:**

**Without Stack-Driven:**
- User research: 2-3 weeks
- Market analysis: 1-2 weeks
- Tech stack decision: 1 week (with debates)
- Mission/strategy: 1 week
- Design system: 2-3 weeks
- Database design: 1 week
- API design: 1-2 weeks
- Backlog generation: 1-2 weeks

**Total: 10-15 weeks**

**With Stack-Driven:**
- Complete cascade: 8-10 hours
- User validation (separate): 1-2 weeks
- **Total: ~2 weeks** (most of that is user interviews, not strategy work)

**Speedup: ~5-7x faster**

---

### What takes the longest?

**Longest sessions:**
- Session 10 (Backlog): 60-90 min (generates 30-50 stories)
- Session 2 (Product Strategy): 45-60 min (market research)
- Session 4 (Strategy): 45-60 min (derives 4 strategy docs)
- Session 7 (Database): 45-60 min (complete schema)
- Session 8 (API): 45-60 min (OpenAPI spec)

**Why?**
- These generate large, detailed outputs
- Require analyzing multiple previous sessions
- Involve complex decision trees

**Worth it:** Quality outputs take time. Framework is optimized for quality over speed.

---

## Team Usage

### Can multiple people use Stack-Driven together?

**Yes.** Two approaches:

**Approach 1: Collaborative (recommended)**
```bash
# Shared repository
git clone repo
cd repo

# Person A runs sessions 1-2
/refine-journey
/create-product-strategy
git add product-guidelines/
git commit -m "Sessions 1-2"
git push

# Person B continues
git pull
/choose-tech-stack
/generate-strategy
git commit -m "Sessions 3-4"
git push
```

**Approach 2: Individual, then merge**
```bash
# Person A: Research journey
/refine-journey

# Person B: Research strategy
/create-product-strategy

# Meet and merge insights
```

**Best practice:**
- Run Session 1 together (align on journey)
- Split later sessions by expertise (designer does Session 6, engineer does Session 7)
- Review outputs together

---

### What roles should be involved?

**Ideal team:**
- **Founder/Product Manager:** Sessions 1-5 (journey, strategy, brand)
- **Designer:** Sessions 5-6 (brand, design)
- **Engineer:** Sessions 7-9, 12-14 (database, API, testing, scaffold, deployment, observability)
- **Product Manager:** Session 10 (backlog)

**Solo founder?**
- You do everything
- Framework gives you outputs as if you had a team

**Small team?**
- 2 people can split sessions
- Review each other's outputs

---

### How do we resolve disagreements about outputs?

**Framework provides reasoning:**

1. **Check the decision rationale:**
   - Every choice has "Why we chose X"
   - Every choice has "What we DIDN'T choose and why"

2. **Trace back to journey:**
   - Does this serve the user?
   - Which journey step does this optimize?

3. **Re-run with different inputs:**
   - If mission feels wrong, check if journey is accurate
   - Update journey, regenerate mission

4. **Edit directly:**
   - You always have final say
   - Framework is a tool, not a dictator

**Disagreement example:**
- Designer wants blue, engineer wants green
- Check: What does brand strategy say? (trustworthy → blue)
- Decision traces to user perception of trust

---

## Extensions and Integrations

### Can I use Stack-Driven with [my existing tool]?

**Likely yes.** Stack-Driven outputs are just markdown files:

**Integrations:**
- **Notion/Obsidian:** Copy markdown files directly
- **Jira/Linear:** Use `/create-gh-issues` or manually import backlog
- **Figma:** Reference design system (Session 6) when designing
- **VS Code:** Reference API contracts (Session 8) when coding
- **Terraform/Pulumi:** Use deployment plan (Session 13) as guide

**No lock-in:** All outputs are standard formats (markdown, JSON, code).

---

### Can Stack-Driven generate actual code?

**Yes**, in Session 12 (`/scaffold-project`):

- Generates package.json / pyproject.toml
- Generates docker-compose.yml
- Generates .env.template
- Generates CI/CD pipeline (GitHub Actions)
- Generates basic directory structure
- Generates database migrations (based on Session 7 schema)

**What it doesn't generate:**
- Complete application logic (you write this)
- UI components (you implement from design system)
- Business logic (you implement from backlog)

**Purpose:** Scaffold to start development, not complete application.

---

### Does Stack-Driven replace [other tool]?

**Stack-Driven complements, not replaces:**

| Tool | Stack-Driven Relationship |
|------|---------------------------|
| **Figma** | Stack-Driven creates design system → Implement in Figma |
| **Jira** | Stack-Driven generates backlog → Import to Jira |
| **Notion** | Stack-Driven creates strategy docs → Store in Notion |
| **GitHub Projects** | Stack-Driven creates issues → Manage in GitHub |
| **Cursor/Claude Code** | Reference Stack-Driven outputs when coding |

**Stack-Driven = Strategy layer**
**Other tools = Execution layer**

---

### Can I export outputs to other formats?

**Currently:** Outputs are markdown (`.md`)

**Easy conversions:**
```bash
# Markdown → PDF
pandoc product-guidelines/03-mission.md -o mission.pdf

# Markdown → HTML
pandoc product-guidelines/06-design-system.md -o design.html

# Markdown → Notion
# Copy and paste (Notion supports markdown)

# Markdown → Google Docs
# Copy and paste or use docs.google.com import
```

**API formats** (Session 8):
- OpenAPI spec is standard JSON/YAML
- Can import to Postman, Swagger UI, etc.

---

## Comparison to Alternatives

### How is this different from business plan templates?

**Business plan templates:**
- Static documents
- Generic sections to fill in
- Same structure for everyone
- Focuses on financials and market

**Stack-Driven:**
- Generative system
- Adapts to your journey
- Different journey → different outputs
- Focuses on user value → strategic decisions

**Example:**
- Template: "Describe your target market"
- Stack-Driven: "Walk me through your user's journey. I'll derive your target market from who experiences the pain point."

---

### How is this different from just using ChatGPT?

**ChatGPT/Claude (standalone):**
- Single prompts
- No memory between sessions
- No structured cascade
- Generic outputs
- You manage context

**Stack-Driven:**
- 14 connected sessions
- Each reads previous outputs
- Structured cascade with validation
- Journey-specific outputs
- Framework manages context

**Analogy:**
- ChatGPT = Individual consultants
- Stack-Driven = Consulting firm with systematic methodology

---

### How is this different from Product Hunt "idea validation" tools?

**Idea validation tools:**
- Survey templates
- Landing page builders
- Beta signup forms

**Stack-Driven:**
- Complete product development framework
- Goes from idea → production-ready system
- Not just validation, but execution strategy

**Stack-Driven includes validation** (Session 2: product strategy with market analysis) **but goes far beyond.**

---

### How is this different from Y Combinator's resources?

**YC resources:**
- Advice and frameworks
- Startup School lectures
- Community and funding

**Stack-Driven:**
- AI-assisted implementation
- Generates actual deliverables
- Systematic execution (not just advice)

**Complementary:**
- Use YC resources for learning and community
- Use Stack-Driven to systematize and execute
- Both emphasize user-first thinking

---

## Still Have Questions?

### Where can I find more help?

1. **Documentation:**
   - `README.md` - Overview
   - `GETTING-STARTED.md` - Quick start
   - `COMMAND-REFERENCE.md` - All commands
   - `TROUBLESHOOTING.md` - Common issues
   - `PHILOSOPHY.md` - Framework principles

2. **Check cascade status:**
   ```bash
   /cascade-status
   ```

3. **Examples:**
   ```bash
   ls examples/compliance-saas/
   ```

4. **Open an issue:**
   - GitHub repository > Issues > New Issue

---

### How can I contribute?

See `CONTRIBUTING.md` for guidelines.

**Ways to contribute:**
- Add example implementations (different journeys)
- Improve cascade prompts
- Enhance documentation
- Share case studies
- Report bugs or suggestions

---

### What's the roadmap?

**Current focus (v2.0):**
- ✅ Generative cascade (not prescriptive templates)
- ✅ Complete framework (14 core sessions)
- ✅ Post-cascade extensions (8 optional deep dives)
- ✅ Production readiness (deployment + observability)

**Future considerations:**
- More example implementations
- UI/web interface (currently CLI-based)
- Integration plugins (Notion, Jira, etc.)
- Advanced analytics and tracking
- Community showcase of completed cascades

See GitHub Issues for active discussions.

---

**Last Updated:** 2025-11-14
**Version:** 2.0.0
