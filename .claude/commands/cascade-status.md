---
description: Show complete Stack-Driven framework progress (core, post-core)
---

# Complete Framework Status Check

You are helping the user navigate the Stack-Driven framework - core cascade (Sessions 1-14) and optional post-core extensions (branding, UX, analytics, growth).

## Your Task

1. **Check which output files exist** in the `/product-guidelines` directory
2. **Display a visual progress tracker** showing core cascade and post-core extensions
3. **Tell the user exactly what to do next** (which command to run and why)
4. **Show how everything connects** - what reads what

## Complete Framework Structure

### Core Cascade (Required - Sessions 1-14 - ALWAYS START HERE)

**The main Stack-Driven flow**:

```
Session 1: /refine-journey             → product-guidelines/00-user-journey.md
Session 2: /create-product-strategy     → product-guidelines/01-product-strategy.md
                                         product-guidelines/11-product-strategy-essentials.md
Session 3: /choose-tech-stack          → product-guidelines/02-tech-stack.md
Session 4: /generate-strategy          → product-guidelines/03-mission.md
                                         product-guidelines/04-metrics.md
                                         product-guidelines/04-monetization.md
                                         product-guidelines/04-architecture.md
Session 5: /create-brand-strategy      → product-guidelines/05-brand-strategy.md
Session 6: /create-design              → product-guidelines/06-design-system.md
Session 7: /design-database-schema     → product-guidelines/07-database-schema.md
Session 8: /generate-api-contracts     → product-guidelines/08-api-contracts.md
Session 9: /create-test-strategy       → product-guidelines/09-test-strategy.md
Session 10: /generate-backlog          → product-guidelines/10-backlog/
Session 11: /create-gh-issues          → GitHub issues
Session 12: /scaffold-project          → product-guidelines/12-project-scaffold.md
                                         product-guidelines/12-project-scaffold/ (actual code files)
Session 13: /plan-deployment           → product-guidelines/13-deployment-plan.md
Session 14: /design-observability      → product-guidelines/14-observability-strategy.md
```

**This is the core** - ALWAYS start here. User journey comes first, product strategy validates market opportunity, tech stack chosen, tactical foundation established (mission, metrics, monetization, architecture), brand strategy created, design system built, technical specs (database, APIs, tests) inform the backlog, then everything flows through to scaffolding, deployment and observability. Complete these 14 sessions to go from idea to production-ready system.

---

### Post-Core Extensions (Optional - Journey-Informed)

**Run AFTER core cascade to add comprehensive branding, UX, and growth planning**. All these commands READ the journey and core outputs.

**After Session 6+** (Brand & Design Complete):

```
/design-user-experience     → product-guidelines/19-user-experience.md
    (Detailed UX flows - expands journey with research, flows, wireframes)

/setup-analytics            → product-guidelines/20-analytics-plan.md
    (Analytics implementation - implements metrics from Session 4)

/design-growth-strategy     → product-guidelines/21-growth-strategy.md
    (Growth strategy - acquisition channels, growth loops, and experiments)

/create-financial-model     → product-guidelines/22-financial-model.md
    (Financial model - unit economics, revenue projections, profitability pathways)
```

**After Backlog (Session 10+)**:

```
/discover-naming            → product-guidelines/15-brand-naming.md
    (Brand naming - names the journey solution)

/define-messaging           → product-guidelines/16-brand-messaging.md
    (Messaging framework - communicates journey value in brand voice)

/design-brand-identity      → product-guidelines/17-brand-identity.md
    (Brand identity - logo, visual system, and usage guidelines)

/create-content-guidelines  → product-guidelines/18-content-guidelines.md
    (Content style guide - journey-aligned content standards)
```

**During Development**:

```
/review-code                → (No output file - code review framework)
```

## Steps to Execute

### Step 1: Check Output Directory

Use Bash to check which files exist:

```bash
ls -la /home/user/stack-driven/product-guidelines/
```

Look for:

- **Core cascade**: `00-user-journey.md`, `01-product-strategy.md`, `11-product-strategy-essentials.md`, `02-tech-stack.md`, `03-mission.md`, `04-metrics.md`, `04-monetization.md`, `04-architecture.md`, `05-brand-strategy.md`, `06-design-system.md`, `07-database-schema.md`, `08-api-contracts.md`, `09-test-strategy.md`, `10-backlog/`, `12-project-scaffold.md`, `13-deployment-plan.md`, `14-observability-strategy.md`
- **Post-core extensions (optional)**: `15-brand-naming.md`, `16-brand-messaging.md`, `17-brand-identity.md`, `18-content-guidelines.md`, `19-user-experience.md`, `20-analytics-plan.md`, `21-growth-strategy.md`, `22-financial-model.md`

### Step 2: Display Complete Progress

Create a comprehensive visual status display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Stack-Driven Framework Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORE CASCADE (Required - Always Start Here)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 00-user-journey.md            (Session 1 ✓)
✅ 01-product-strategy.md        (Session 2 ✓)
✅ 11-product-strategy-essentials.md (Session 2 ✓)
✅ 02-tech-stack.md              (Session 3 ✓)
❌ 03-mission.md                 (Session 4 - Not started)
❌ 04-metrics.md                 (Session 4 - Not started)
❌ 04-monetization.md            (Session 4 - Not started)
❌ 04-architecture.md            (Session 4 - Not started)
❌ 05-brand-strategy.md          (Session 5 - Not started)
❌ 06-design-system.md           (Session 6 - Not started)
❌ 07-database-schema.md         (Session 7 - Not started)
❌ 08-api-contracts.md           (Session 8 - Not started)
❌ 09-test-strategy.md           (Session 9 - Not started)
❌ 10-backlog/                   (Session 10 - Not started)
❌ 12-project-scaffold.md        (Session 12 - Not started)
❌ 13-deployment-plan.md         (Session 13 - Not started)
❌ 14-observability-strategy.md  (Session 14 - Not started)

Progress: ████░░░░░░░░░░░░ 21% (3 of 14 core sessions complete)

POST-CORE EXTENSIONS (Optional - Journey-Informed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
After Session 6+ (Optional UX/growth):
❌ 19-user-experience.md     (Detailed UX flows)
❌ 20-analytics-plan.md      (Analytics implementation)
❌ 21-growth-strategy.md     (Growth strategy)
❌ 22-financial-model.md     (Financial model & unit economics)

After Session 10+ (Optional marketing polish):
❌ 15-brand-naming.md        (Brand naming)
❌ 16-brand-messaging.md     (Messaging framework)
❌ 17-brand-identity.md      (Brand identity)
❌ 18-content-guidelines.md  (Content style guide)

Status: 0 of 8 post-core extensions complete (optional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Determine Next Step

Based on what files exist, determine the next recommended action:

#### Decision Logic:

**If no core cascade files exist**:

- **Recommend**: Start with Session 1 (`/refine-journey`)
- **NEVER suggest branding first** - journey ALWAYS comes first

**If only 00-user-journey.md exists**:

- **Recommend**: Session 2 (`/create-product-strategy`)

**If 00 and 01 exist**:

- **Recommend**: Session 3 (`/choose-tech-stack`)

**If 00-02 exist**:

- **Recommend**: Session 4 (`/generate-strategy`)

**If 00-04 architecture exist (Session 4 complete)**:

- **Recommend**: Session 5 (`/create-brand-strategy`)

**If 00-05 brand-strategy exists (Session 5 complete)**:

- **Recommend**: Session 6 (`/create-design`)

**If 00-06 design-system exists (Session 6 complete)**:

- **Recommend**: Session 7 (`/design-database-schema`)
- **Also suggest** (optional):
  - `/design-user-experience` (product-guidelines/19-user-experience.md)
  - `/setup-analytics` (product-guidelines/20-analytics-plan.md)
  - `/design-growth-strategy` (product-guidelines/21-growth-strategy.md)
  - `/create-financial-model` (product-guidelines/22-financial-model.md)

**If 00-07 database exists (Session 7 complete)**:

- **Recommend**: Session 8 (`/generate-api-contracts`)

**If 00-08 api exists (Session 8 complete)**:

- **Recommend**: Session 9 (`/create-test-strategy`)

**If 00-09 test exists (Session 9 complete)**:

- **Recommend**: Session 10 (`/generate-backlog`)

**If 00-10 backlog exists (Session 10 complete)**:

- **Recommend**: Session 11 (`/create-gh-issues`)

**If 00-10 backlog + GitHub issues exist (Session 11 complete)**:

- **Recommend**: Session 12 (`/scaffold-project`)

**If 00-12 scaffold exists (Session 12 complete)**:

- **Recommend**: Session 13 (`/plan-deployment`)

**If 00-13 deployment plan exists (Session 13 complete)**:

- **Recommend**: Session 14 (`/design-observability`)

**If all core cascade complete (Sessions 1-14)**:

- **Congratulate** them!
- **Recommend**: Copy scaffold files and start building!
- **Also suggest** (optional):
  - `/discover-naming` (product-guidelines/15-brand-naming.md)
  - `/define-messaging` (product-guidelines/16-brand-messaging.md)
  - `/design-brand-identity` (product-guidelines/17-brand-identity.md)
  - Post-core extensions for comprehensive planning

### Step 4: Show Next Step Details

For the next recommended session, display:

```
👉 Next Step: Run /generate-strategy

📥 Reads (cascade inputs):
- product-guidelines/00-user-journey.md (your validated user journey)
- product-guidelines/01-product-strategy.md (market validation and strategic goals)
- product-guidelines/11-product-strategy-essentials.md (condensed for backlog generation)
- product-guidelines/02-tech-stack.md (your chosen tech stack)

📤 Will create:
- product-guidelines/03-mission.md (mission statement derived from journey)
- product-guidelines/04-metrics.md (North Star metric and success metrics)
- product-guidelines/04-monetization.md (pricing strategy aligned with value)
- product-guidelines/04-architecture.md (architecture principles)

⏱️ Estimated time: 15-20 minutes (AI-assisted conversation)

💡 What happens: I'll analyze your journey, product strategy, and tech stack to derive your tactical foundation - mission, metrics, monetization, and architecture principles. Every decision will trace back to your user journey.

🔗 Cascades to:
- Session 5: Brand strategy will express your journey value
- Session 6: Design system will implement brand and architecture
- Session 7: Database schema will model your data
- Session 10: Backlog will be prioritized by your metrics
- Sessions 13-14: Deployment and observability will enable reliable delivery
- Optional: /setup-analytics will implement detailed event tracking for your metrics
- Optional: /design-user-experience will create detailed UX design

Ready? Run: /generate-strategy
```

### Step 5: Show Optional Extensions

If appropriate, suggest optional post-core commands:

```
💡 Optional Post-Core Extensions (Journey-Informed)

After Session 6 (Brand & Design Complete), consider:
├─ /design-user-experience → Detailed UX flows & wireframes (product-guidelines/19-user-experience.md)
├─ /setup-analytics → Implement metrics tracking (product-guidelines/20-analytics-plan.md)
├─ /design-growth-strategy → Acquisition channels & growth loops (product-guidelines/21-growth-strategy.md)
└─ /create-financial-model → Unit economics and revenue projections (product-guidelines/22-financial-model.md)

After Session 10 (Backlog Complete), consider:
├─ /discover-naming → Extend brand with name generation (product-guidelines/15-brand-naming.md)
├─ /define-messaging → Communicate journey value (product-guidelines/16-brand-messaging.md)
├─ /design-brand-identity → Logo and visual identity system (product-guidelines/17-brand-identity.md)
└─ /create-content-guidelines → Journey-aligned content (product-guidelines/18-content-guidelines.md)

During development:
├─ /validate-outputs → Validate cascade outputs for quality (use anytime)
└─ /review-code → Code review framework (use anytime)

All post-core extensions READ the journey - nothing precedes the user journey.
```

## Example Output

Here's an example of what you should output:

```
📊 Stack-Driven Cascade Status

Your Cascade Progress:
✅ 00-user-journey.md        (Session 1 complete)
❌ 01-product-strategy.md    (Not started)
❌ 11-product-strategy-essentials.md (Not started)
❌ 02-tech-stack.md          (Not started)
❌ 03-mission.md             (Not started)
❌ 04-metrics.md             (Not started)
❌ 04-monetization.md        (Not started)
❌ 04-architecture.md        (Not started)
❌ 05-brand-strategy.md      (Not started)
❌ 06-design-system.md       (Not started)
❌ 07-database-schema.md     (Not started)
❌ 08-api-contracts.md       (Not started)
❌ 09-test-strategy.md       (Not started)
❌ 10-backlog/               (Not started)
❌ 12-project-scaffold.md    (Not started)
❌ 13-deployment-plan.md     (Not started)
❌ 14-observability-strategy.md (Not started)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Progress: █░░░░░░░░░░░░░ 7% (1 of 14 sessions complete)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 Next Step: Run /create-product-strategy

📥 Inputs needed:
- Reads: product-guidelines/00-user-journey.md (your validated user journey)

📤 Will create:
- product-guidelines/01-product-strategy.md (market validation, competitive analysis, strategic goals)
- product-guidelines/11-product-strategy-essentials.md (condensed version for backlog generation)

⏱️ Estimated time: 20-30 minutes

💡 What happens: I'll analyze your user journey and validate it with market sizing (TAM/SAM/SOM), competitive analysis, and strategic positioning. This creates a market-validated foundation before choosing technology.

Ready? Run: /create-product-strategy
```

## Important Guidelines

1. **Always check files** - Don't assume what exists, actually check the /product-guidelines directory
2. **Be encouraging** - This is a journey, celebrate progress
3. **Be specific** - Tell them EXACTLY what command to run next
4. **Show connections** - Explain how previous outputs inform the next session
5. **Keep it visual** - Use emojis, progress bars, clear sections

## Edge Cases

### If they've skipped sessions

**Message**:

```
⚠️ Warning: Some outputs are missing

The cascade works best sequentially because each session reads previous outputs:
- Session 1 → feeds → Session 2
- Sessions 1+2 → feed → Session 3
- etc.

Missing: [list files]

Recommendation: Either fill in the gaps or accept that later sessions won't have full context.
```

### If all core cascade complete

**Message**:

```
🎉 Core Cascade Complete!

You've successfully completed all 14 Stack-Driven core sessions:
✅ User Journey defined
✅ Product Strategy validated (market, competitive, goals)
✅ Tech stack chosen
✅ Tactical foundation established (mission, metrics, monetization, architecture)
✅ Brand strategy created (expresses journey value)
✅ Design system created (brings brand to life)
✅ Database schema designed
✅ API contracts generated
✅ Test strategy created
✅ Backlog generated
✅ GitHub issues created
✅ Project scaffold ready (working development environment)
✅ Deployment strategy defined (CI/CD, environments, rollout)
✅ Observability strategy created (monitoring, SLOs, incident response)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What's next?

Option 1: Start Building 🚀
→ Copy files from product-guidelines/12-project-scaffold/ to your project root
→ Follow README.md setup instructions
→ Set up CI/CD using product-guidelines/13-deployment-plan.md
→ Implement monitoring using product-guidelines/14-observability-strategy.md
→ Run docker-compose up && npm install && npm run dev
→ Start implementing P0 stories from your backlog

Option 2: Add Optional Extensions 📊
→ /discover-naming (generate brand name - 15-brand-naming.md)
→ /define-messaging (messaging framework - 16-brand-messaging.md)
→ /design-brand-identity (visual identity - 17-brand-identity.md)
→ /create-content-guidelines (content style guide - 18-content-guidelines.md)
→ /design-user-experience (detailed UX flows - 19-user-experience.md)
→ /setup-analytics (analytics implementation - 20-analytics-plan.md)
→ /design-growth-strategy (growth strategy - 21-growth-strategy.md)
→ /create-financial-model (financial model - 22-financial-model.md)

Option 3: Iterate & Refine 🔄
→ Run /refine-journey if your understanding evolves
→ Any session can be re-run to update outputs
→ Later sessions will cascade the changes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You have everything from idea to production-ready system. Now go ship! 🎯
```

### If post-cascade files exist

**Track and display** them:

```
POST-CORE EXTENSIONS COMPLETE:
✅ 20-analytics-plan.md (Analytics implementation ready)
✅ 17-brand-identity.md (Brand identity created)
✅ 21-growth-strategy.md (Growth strategy defined)
❌ 19-user-experience.md (Not started)

You're adding comprehensive planning! Consider UX flows for complete product definition.
```

## Important Guidelines

1. **Always check files** - Don't assume what exists
2. **Start with core cascade** - Unless user explicitly wants branding first
3. **Explain optional extensions** - Pre and post-cascade are valuable but optional
4. **Be encouraging** - Celebrate progress
5. **Be specific** - Tell them EXACTLY what command to run next
6. **Show connections** - Explain how outputs flow through cascade
7. **Keep it visual** - Use emojis, progress bars, clear sections
8. **Don't overwhelm** - Introduce post-cascade extensions after core is complete

## Summary of All Commands

**Core Cascade (Required - Always Start Here)**:

- `/refine-journey` - Session 1: User journey
- `/create-product-strategy` - Session 2: Market validation, competitive analysis, strategic goals
- `/choose-tech-stack` - Session 3: Tech stack
- `/generate-strategy` - Session 4: Mission, metrics, monetization, architecture
- `/create-brand-strategy` - Session 5: Brand foundation (expresses journey value)
- `/create-design` - Session 6: Design system (brings brand to life)
- `/design-database-schema` - Session 7: Database schema & migrations
- `/generate-api-contracts` - Session 8: API contracts & OpenAPI specs
- `/create-test-strategy` - Session 9: Testing strategy
- `/generate-backlog` - Session 10: User stories
- `/create-gh-issues` - Session 11: GitHub issues
- `/scaffold-project` - Session 12: Working development environment
- `/plan-deployment` - Session 13: Deployment & CI/CD
- `/design-observability` - Session 14: Monitoring & SLOs

**Post-Core Extensions (Optional - Journey-Informed)**:

After Session 6+:

- `/design-user-experience` - Detailed UX flows (product-guidelines/19-user-experience.md)
- `/setup-analytics` - Analytics implementation (product-guidelines/20-analytics-plan.md)
- `/design-growth-strategy` - Growth strategy (product-guidelines/21-growth-strategy.md)
- `/create-financial-model` - Financial model & unit economics (product-guidelines/22-financial-model.md)

After Session 10+:

- `/discover-naming` - Brand naming (product-guidelines/15-brand-naming.md)
- `/define-messaging` - Messaging framework (product-guidelines/16-brand-messaging.md)
- `/design-brand-identity` - Brand identity system (product-guidelines/17-brand-identity.md)
- `/create-content-guidelines` - Content style guide (product-guidelines/18-content-guidelines.md)

Dev-time:

- `/validate-outputs` - Validate cascade outputs for quality (anytime)
- `/review-code` - Code review framework (anytime)

**Meta**:

- `/cascade-status` - Show this status (what you're running now!)
- `/run-cascade` - Execute sessions automatically from current progress

## Reference Files

Mention if helpful:

- `/examples/compliance-saas/` - Complete cascade example
- `/templates/` - All template files
- `README.md` - Framework overview
- `GETTING-STARTED.md` - Onboarding guide

Now, check the output directory and show the user their complete framework status!
