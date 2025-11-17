# Stack-Driven Quick Reference

One-page cheat sheet for Stack-Driven framework.

---

## Core Concept

**User Experience is the Core of Every Product.** Everything flows from the journey.

Journey → Product Strategy → Tech → Strategy → Design → Technical Specs → Backlog → Scaffold → Deploy → Monitor

---

## Quick Start

```bash
/cascade-status          # Check where you are
/refine-journey          # Start Session 1
# Follow the cascade...
```

---

## Core Cascade (Sessions 1-14)

| # | Command | Time | Output |
|---|---------|------|--------|
| 1 | `/refine-journey` | 30-45m | `00-user-journey.md` |
| 2 | `/create-product-strategy` | 45-60m | `01-product-strategy.md`, `11-*-essentials.md` |
| 3 | `/choose-tech-stack` | 15-20m | `02-tech-stack.md` |
| 4 | `/generate-strategy` | 45-60m | `03-mission.md`, `04-metrics.md`, `04-monetization.md`, `04-architecture.md` |
| 5 | `/create-brand-strategy` | 30-45m | `05-brand-strategy.md` |
| 6 | `/create-design` | 30-40m | `06-design-system.md` |
| 7 | `/design-database-schema` | 45-60m | `07-database-schema.md`, `07-*-essentials.md` |
| 8 | `/generate-api-contracts` | 45-60m | `08-api-contracts.md`, `08-*-essentials.md` |
| 9 | `/create-test-strategy` | 30-45m | `09-test-strategy.md`, `09-*-essentials.md` |
| 10 | `/generate-backlog` | 60-90m | `10-backlog/*.md` (30-50 stories) |
| 11 | `/create-gh-issues` | 10-15m | GitHub issues |
| 12 | `/scaffold-project` | 30-45m | `12-project-scaffold/` (actual code) |
| 13 | `/plan-deployment` | 30-45m | `13-deployment-plan.md` |
| 14 | `/design-observability` | 30-45m | `14-observability-strategy.md` |

**Total:** 8-10 hours | **Result:** Production-ready system

---

## Post-Cascade Extensions (Optional)

| # | Command | When | Time |
|---|---------|------|------|
| 15 | `/discover-naming` | After Session 5 | 30-45m |
| 16 | `/define-messaging` | After naming | 30-45m |
| 17 | `/design-brand-identity` | After messaging | 60-90m |
| 18 | `/create-content-guidelines` | After messaging | 30-45m |
| 19 | `/design-user-experience` | After Session 4 | 60-90m |
| 20 | `/setup-analytics` | After Session 4 | 30-45m |
| 21 | `/design-growth-strategy` | After Session 4 | 60-90m |
| 22 | `/create-financial-model` | After Session 4 | 60-90m |

---

## Meta Commands

```bash
/cascade-status    # Check progress, see what's next
/run-cascade       # Auto-execute all sessions
/review-code       # Code review during development
```

---

## Execution Modes

**Manual (Step-by-step):**
```bash
/refine-journey
# Review output, then:
/create-product-strategy
# Review output, then:
/choose-tech-stack
# ... continue
```

**Automated (Continuous):**
```bash
/run-cascade    # Executes all sessions automatically
```

---

## File Structure

```
project/
├── .claude/
│   └── commands/          # Slash commands (framework)
├── templates/             # Template files (framework)
├── examples/              # Reference implementations
│   └── compliance-saas/   # Example cascade
├── product-guidelines/    # YOUR outputs (gitignored)
│   ├── 00-user-journey.md
│   ├── 01-product-strategy.md
│   ├── 02-tech-stack.md
│   ├── 03-mission.md
│   ├── 04-*.md
│   ├── 05-brand-strategy.md
│   ├── 06-design-system.md
│   ├── 07-database-schema.md
│   ├── 08-api-contracts.md
│   ├── 09-test-strategy.md
│   ├── 10-backlog/        # User stories
│   ├── 12-project-scaffold/  # Actual code files
│   ├── 13-deployment-plan.md
│   └── 14-observability-strategy.md
├── README.md
├── GETTING-STARTED.md
└── ... (other docs)
```

---

## Key Principles

1. **User-First:** Journey before technology
2. **Generative:** Different journeys → different outputs
3. **Cascading:** Each session builds on previous
4. **Traceable:** Every decision traces to journey
5. **Boring is Beautiful:** Proven tech > exotic tech

---

## Priority Levels

- **P0:** Critical for MVP (blocks launch)
- **P1:** Important for good UX (should have)
- **P2:** Nice to have (can wait)

---

## Common Workflows

### Minimum Viable Cascade (3 hours)
```bash
/refine-journey          # 45m
/create-product-strategy # 45m
/choose-tech-stack       # 20m
/generate-strategy       # 60m
# Result: Strategic foundation
```

### Complete Core (8-10 hours)
```bash
# Run all 14 core sessions
# Result: Production-ready system
```

### Update Journey + Regenerate
```bash
/refine-journey          # Update with new insights
/create-product-strategy # Regenerate with new journey
/choose-tech-stack       # Regenerate with new journey
/generate-strategy       # Regenerate with new journey
# ... continue as needed
```

---

## User Journey Template

```
Who: [Specific user persona]
Situation: [Current pain point]

Steps:
1. [Initial state/problem]
2. [Start using product]
3. [Aha moment - value delivered] ⭐
4. [Continued value]
5. [Long-term outcome]

Value Ratio: [Before] → [After] = [X]x improvement
```

**Example:**
- Who: Compliance officers at mid-size banks
- Pain: Manual review takes 4 hours
- Aha: AI assessment in 60 seconds
- Value: 4 hours → 60 sec = 240x faster

---

## Quality Checks

### Session 1 (Journey)
- [ ] Specific user persona (not "businesses")
- [ ] Quantified value (X hours → Y minutes)
- [ ] Clear aha moment (Step 3)
- [ ] 10:1+ value ratio

### Session 3 (Tech Stack)
- [ ] Choices serve journey requirements
- [ ] Alternatives considered
- [ ] Team capabilities noted
- [ ] "Boring tech" preferred

### Session 4 (Strategy)
- [ ] Mission references aha moment
- [ ] North Star measures mission
- [ ] Pricing gives 10x+ ROI
- [ ] Architecture serves critical path

### Session 10 (Backlog)
- [ ] Every story traces to journey
- [ ] P0 stories enable MVP
- [ ] Acceptance criteria clear
- [ ] Dependencies mapped

---

## Common Issues

**"Can't find output files"**
→ Check `product-guidelines/` directory

**"Missing previous session"**
→ Run `/cascade-status` to see what's missing

**"Wrong tech recommended"**
→ Specify constraints: "Team knows Python only"

**"Too many backlog stories"**
→ Focus on P0 stories, ignore P2 for now

**"Want to update journey"**
→ Re-run session, then regenerate downstream

See **TROUBLESHOOTING.md** for more.

---

## Decision Trees

### Database Choice
1. Time-series data? → TimescaleDB, InfluxDB
2. Complex relationships? → PostgreSQL, MySQL
3. Flexible schema? → MongoDB
4. Default: **PostgreSQL** (safest)

### Frontend Choice
1. SEO critical? → Next.js, SvelteKit (SSR)
2. Mobile-first? → React Native, Flutter
3. Real-time? → React/Vue + WebSockets
4. Default: **React** + Vite (proven)

### Backend Choice
1. Document processing + AI? → Python/FastAPI
2. Real-time <100ms? → Node.js
3. High performance? → Go
4. Default: **Node.js** (versatile)

---

## RICE Prioritization

**RICE = (Reach × Impact × Confidence) ÷ Effort**

- **Reach:** % of users affected (0-100)
- **Impact:** Journey improvement (0-3)
- **Confidence:** Certainty (0-100%)
- **Effort:** Time to build (person-weeks)

Higher score = higher priority

---

## Documentation Index

| Doc | Purpose |
|-----|---------|
| **README.md** | Framework overview |
| **GETTING-STARTED.md** | Quick start guide |
| **COMMAND-REFERENCE.md** | All commands detailed |
| **FAQ.md** | Common questions |
| **TROUBLESHOOTING.md** | Common issues |
| **PHILOSOPHY.md** | Core principles |
| **CONTRIBUTING.md** | Contribution guide |
| **CHANGELOG.md** | Version history |
| **GLOSSARY.md** | Terminology |
| **QUICK-REFERENCE.md** | This cheat sheet |

---

## Output Locations

```bash
# Check all outputs
ls -la product-guidelines/

# View specific file
cat product-guidelines/00-user-journey.md

# Check backlog
ls product-guidelines/10-backlog/

# Check scaffold
ls product-guidelines/12-project-scaffold/

# View cascade status
/cascade-status
```

---

## Tips for Success

**Session 1:**
- Be specific about users
- Quantify value (ratios)
- Find the aha moment

**Session 2:**
- Research market thoroughly
- Identify real competitors
- Be honest about differentiation

**Session 3:**
- Trust journey-driven analysis
- Mention team constraints
- Boring tech > exciting tech

**Session 4:**
- Mission from aha moment
- Metrics measure mission
- Pricing = 10x+ ROI

**Sessions 7-9:**
- Support all journey steps
- Don't over-engineer for MVP
- Focus on critical paths

**Session 10:**
- P0 = critical only
- Every story → journey
- Check dependencies

**Sessions 12-14:**
- Start simple, scale later
- Automate everything
- Monitor critical paths

---

## Command Shortcuts

```bash
# Status
/cascade-status

# Core cascade
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

# Or automated
/run-cascade
```

---

## Version & License

**Version:** 2.0.0 (Generative Cascade)
**License:** Apache 2.0
**Repo:** github.com/bru-digital/stack-driven

---

## Get Help

1. Check `/cascade-status`
2. Read FAQ.md
3. Check TROUBLESHOOTING.md
4. See examples/compliance-saas/
5. Open GitHub issue

---

**Remember:** User journey first, always. Everything else flows from there.

**Ready?** → Run `/cascade-status` to begin! 🚀
