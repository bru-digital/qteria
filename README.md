# Qteria

**AI-driven document pre-assessment for TIC industry**

Qteria helps Testing, Inspection, and Certification (TIC) organizations validate certification documents 400x faster through evidence-based AI assessments, reducing pre-assessment time from 1-2 days to under 10 minutes.

---

## About This Repository

This repository contains the complete product strategy and development scaffold for Qteria, generated using the Stack-Driven framework.

### What's Inside

- **`product-guidelines/`** - Complete cascade outputs (Sessions 1-12)
  - User journey and product strategy
  - Tech stack and architecture decisions
  - Database schema and API contracts
  - Test strategy and prioritized backlog
  - **Project scaffold** (ready-to-deploy development environment)

---

## Quick Start

### Copy Scaffold to Start Development

```bash
# Copy scaffold files to project root
cp -r product-guidelines/12-project-scaffold/* .
cp -r product-guidelines/12-project-scaffold/.github .
cp product-guidelines/12-project-scaffold/.[^.]* .

# Setup environment
cp .env.template .env
# Edit .env with your secrets

# Start local services
npm run docker:up

# Install dependencies
npm install
cd apps/api && pip install -r requirements-dev.txt && cd ../..

# Run database migrations
npm run db:migrate

# Start development servers
npm run dev       # Terminal 1: Next.js on :3000
npm run dev:api   # Terminal 2: FastAPI on :8000
```

See `product-guidelines/12-project-scaffold/README.md` for complete setup instructions.

---

## Product Overview

### The Problem

TIC notified bodies currently:
- Pay $100K/year for outsourced document pre-assessment teams
- Wait 1-2 days for basic validation results
- Experience embarrassing back-and-forth when errors slip through
- Have no visibility into validation progress

### The Solution

Qteria provides:
- **10-minute AI validation** (vs 1-2 days)
- **Evidence-based results** with exact page/section links
- **Zero false negatives** (catches what manual teams catch)
- **Minimal false positives** (doesn't flag non-issues)
- **Clean handoff** to certification personnel

### Business Model

- **Target Customer**: TIC notified bodies (TÜV SÜD, BSI, DEKRA, etc.)
- **Pricing**: $30K/year per customer (70% cost savings vs outsourcing)
- **Value Ratio**: 10:1+ (customer saves $70K direct + time value)
- **MVP Goal**: TÜV SÜD pilot, Q2 2026

---

## Tech Stack

**Frontend**: Next.js 14+ (React, TypeScript, Tailwind)
**Backend**: FastAPI (Python)
**Database**: PostgreSQL with JSONB
**Cache/Queue**: Redis (Upstash)
**Storage**: Vercel Blob (or AWS S3)
**AI**: Claude 3.5 Sonnet (Anthropic) with zero-retention
**Auth**: Auth.js (NextAuth) → Clerk when revenue allows
**Hosting**: Vercel (frontend) + Railway/Render (backend)

---

## Architecture Principles

1. **Journey-Step Optimization** - Optimize for Step 3 (AI validation in <10 min), not theoretical scale
2. **Boring Technology + Strategic Innovation** - 90% proven tech, 10% differentiation
3. **API-First Design** - Clean REST API enables future integrations
4. **Fail-Safe Architecture** - Reliability over performance (compliance industry)
5. **Observable & Debuggable** - Measure everything, solo founder needs visibility

---

## Project Status

### Cascade Complete (12/14 core sessions)

✅ **Session 1**: User Journey
✅ **Session 2**: Product Strategy
✅ **Session 3**: Tech Stack
✅ **Session 4**: Tactical Foundation (mission, metrics, monetization, architecture)
✅ **Session 5**: Brand Strategy
✅ **Session 6**: Design System
✅ **Session 7**: Database Schema
✅ **Session 8**: API Contracts
✅ **Session 9**: Test Strategy
✅ **Session 10**: Backlog (42 stories, 10 epics)
✅ **Session 11**: GitHub Issues
✅ **Session 12**: Project Scaffold

🔲 **Session 13**: Deployment Plan (optional)
🔲 **Session 14**: Observability Strategy (optional)

### Ready to Build

The scaffold is production-ready. Start with STORY-001 (Database schema setup) from the backlog.

---

## Repository Structure

```
qteria/
├── product-guidelines/           # All cascade outputs
│   ├── 00-user-journey.md       # Session 1
│   ├── 01-product-strategy.md   # Session 2
│   ├── 02-tech-stack.md         # Session 3
│   ├── 03-mission.md            # Session 4
│   ├── 04-*.md                  # Session 4 (metrics, monetization, architecture)
│   ├── 05-brand-strategy.md     # Session 5
│   ├── 06-design-system.md      # Session 6
│   ├── 07-database-schema*.md   # Session 7
│   ├── 08-api-contracts*.md     # Session 8
│   ├── 09-test-strategy*.md     # Session 9
│   ├── 10-backlog/              # Session 10 (42 stories)
│   ├── 11-*.md                  # Session 11 (essentials)
│   ├── 12-project-scaffold/     # Session 12 (complete dev environment)
│   └── 12-project-scaffold.md   # Session 12 documentation
│
└── README.md                     # This file
```

---

## Next Steps

### Option 1: Continue Cascade (Optional)

Run remaining sessions:
- Deployment plan: Define hosting, CI/CD, monitoring strategy
- Observability: Create metrics, logging, alerting implementation

### Option 2: Start Building (Recommended)

1. Copy scaffold to root (see Quick Start above)
2. Follow setup in `product-guidelines/12-project-scaffold/README.md`
3. Start implementing from backlog: `product-guidelines/10-backlog/`
4. Begin with STORY-001: Database schema setup

---

## Key Metrics

**North Star**: Active Assessments Per Month

**Input Metrics**:
- Active Customers
- Assessments Per Customer
- Assessment Completion Rate
- New Workflows Created
- Assessment Success Rate (AI Accuracy)

**Counter-Metrics** (protect quality):
- Assessment Accuracy (<5% false positive, <1% false negative)
- Data Privacy (zero incidents)
- UX Simplicity (workflow creation <30 min)
- Support Quality (white-glove relationship management)

---

## Product Principles

1. **Simplicity Over Features** - Ship minimal, focused tools. If it doesn't serve validation workflow, cut it.
2. **Data Privacy is Non-Negotiable** - Customer data never trains models, full encryption, audit trails, SOC2/ISO 27001.
3. **Evidence Over Opinion** - Every AI validation must show evidence (page, section, document link).
4. **White-Glove Support** - Dedicated relationship manager per customer. Not a ticket queue.
5. **Ship Working Software** - Reliability over speed. "It just works" reputation earned by never shipping bugs.

---

## License

Proprietary - All rights reserved

---

## Contact

For questions about this product strategy or implementation:
- **Repository**: https://github.com/bru-digital/qteria
- **Framework**: Built using Stack-Driven cascade methodology

---

**Built with evidence-based validation and senior-level simplicity in mind.**
