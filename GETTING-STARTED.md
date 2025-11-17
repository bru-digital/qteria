# Getting Started with Stack-Driven v2.0

Welcome to Stack-Driven! This guide will walk you through the **14-session cascade** that transforms your product idea into a production-ready system with complete technical specifications.

---

## Overview

Stack-Driven uses a **cascading approach** where each session builds upon previous outputs:

1. **Sessions 1-4** → Strategic foundation (journey, product strategy, tech stack, mission/metrics/monetization/architecture)
2. **Sessions 7-9** → Technical specifications (database schema, API contracts, testing strategy)
3. **Sessions 10-11** → Backlog and GitHub issues (30-50 prioritized stories informed by technical specs)
4. **Sessions 12-14** → Development environment (project scaffold, deployment plan, observability strategy)

**Total time**: 8-10 hours to go from idea to production-ready system with complete technical specifications.

---

## Before You Start

### What You Need

1. **An idea** (doesn't have to be fully formed)
2. **Understanding of your users** (or willingness to think through it)
3. **8-10 hours** across multiple sessions (can be spread over days)

### What You'll Get

After completing the cascade:
- ✅ Validated user journey
- ✅ Tech stack optimized for YOUR requirements
- ✅ Mission statement, North Star metric, pricing strategy, architecture principles
- ✅ Complete database schema with ERD and migrations
- ✅ OpenAPI specifications and API contracts
- ✅ Comprehensive testing strategy (unit, integration, E2E)
- ✅ 30-50 prioritized user stories (P0/P1/P2) informed by technical specs
- ✅ Working development environment with actual code files
- ✅ Deployment strategy and CI/CD pipeline
- ✅ Observability strategy with monitoring and alerting
- ✅ Ready-to-build production-ready system

---

## Quick Start

The fastest way to get started:

```bash
# 1. Check your cascade status
/cascade-status

# 2a. Option A: Run cascade automatically (recommended for rapid progress)
/run-cascade

# 2b. Option B: Run sessions manually (recommended for learning)
/refine-journey

# 3. Follow the cascade (each session tells you what's next)
```

That's it! The cascade will guide you step-by-step. Use `/run-cascade` for automated execution, or run each command manually for a more hands-on learning experience.

---

## Detailed Walkthrough

### Check Your Status (Anytime)

```bash
/cascade-status
```

This shows:
- What you've completed
- What comes next
- Inputs and outputs for each session

**Run this first!** It will tell you exactly where to start.

---

### Session 1: Refine User Journey (30-45 minutes)

**Command**: `/refine-journey`

**What Happens**:
I'll ask you questions about your users, their problems, and their journey.

**What You'll Create**: `product-guidelines/00-user-journey.md`

**Tips**:
- Be specific about your user ("compliance officers" not "businesses")
- Quantify value (2 hours → 5 minutes)
- Focus on the problem, not your solution
- Identify the "aha moment" (usually Step 3)

**Next**: Run `/choose-tech-stack`

---

### Session 2: Choose Tech Stack (15-20 minutes)

**Command**: `/choose-tech-stack`

**What Happens**:
I read your journey, analyze requirements, and recommend optimal tech.

**What You'll Create**: `product-guidelines/02-tech-stack.md`

**Important**: Different journeys → different stacks!

**Next**: Run `/generate-strategy`

---

### Session 3: Generate Strategy (45-60 minutes)

**Command**: `/generate-strategy`

**What Happens**:
I derive mission, metrics, monetization, and architecture from your journey.

**What You'll Create**:
- `product-guidelines/02-mission.md`
- `product-guidelines/03-metrics.md`
- `product-guidelines/04-monetization.md`
- `product-guidelines/05-architecture.md`

**Next**: Run `/create-design`

---

### Session 4: Create Design System (30-40 minutes)

**Command**: `/create-design`

**What Happens**:
I create a design system optimized for YOUR user flows.

**What You'll Create**: `product-guidelines/06-design-system.md`

**Next**: Run `/generate-backlog`

---

### Session 5: Generate Backlog (60-90 minutes)

**Command**: `/generate-backlog`

**What Happens**:
I generate 30-50 prioritized user stories traced to journey value.

**What You'll Create**: `product-guidelines/07-backlog/` (with all issue files)

**Next**: Run `/create-gh-issues` (optional)

---

### Session 6: Create GitHub Issues (10-15 minutes)

**Command**: `/create-gh-issues`

**What Happens**:
I push all backlog issues to GitHub.

**What You'll Get**: GitHub issues ready for development

---

## After the Cascade

### Start Building!

1. Tackle P0 stories first (critical for MVP)
2. Track metrics defined in `product-guidelines/03-metrics.md`
3. Reference journey anytime to stay aligned

### Iterate

- Run `/refine-journey` again if understanding evolves
- Regenerate outputs as needed

---

## Tips for Success

### Session 1 (Journey)
- Be specific: "Solo SaaS founders" not "businesses"
- Quantify value: 4 hours → 10 minutes = 24x faster
- Find the aha moment (usually Step 3)

### Session 2 (Tech Stack)
- Trust the analysis
- Mention constraints ("We know Python")
- Override if needed

### Session 3 (Strategy)
- Validate value ratio (pricing should give 10x+ ROI)
- Check North Star measures mission

### Session 5 (Backlog)
- Check every story references journey
- Validate priorities (P0 = critical)

---

## Examples

See `/examples/compliance-saas/` for a complete cascade.

**Remember**: Don't copy it - your journey will be different!

---

## Quick Reference

```bash
/cascade-status           # Check progress
/refine-journey           # Session 1
/choose-tech-stack        # Session 2
/generate-strategy        # Session 3
/create-design            # Session 4
/generate-backlog         # Session 5
/create-gh-issues         # Session 6
```

---

**Ready?** → Run `/cascade-status` to check your progress, or `/run-cascade` to execute automatically

---

**Version**: 2.0.0
**Last Updated**: 2025-11-10
