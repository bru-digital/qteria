# Brand Strategy: Qteria

> **Generated**: November 2025
> **Status**: Final

## Overview

This document defines the brand strategy that guides all brand decisions, visual identity, messaging, and customer experience for Qteria - an AI-powered document validation platform for the TIC (Testing, Inspection, Certification) industry.

## How This Traces to User Journey

**Journey problem** (from `product-guidelines/00-user-journey.md`):

- Project Handlers at TIC notified bodies wait 1-2 days for outsourced India teams to perform basic document validation ($100K/year)
- Quality anxiety when errors slip through to Certification Person
- Hard to experiment with validation criteria

**Journey value moment** (from `product-guidelines/00-user-journey.md`):

- **Step 3 (Aha Moment)**: "Criteria 2: Test summary missing - FAIL → [Link: test-report.pdf, page 8, section 3.2]"
- Evidence-based AI validation in <10 minutes with exact document locations
- Project Handler gets proof, not just AI opinion

**Mission promise** (from `product-guidelines/03-mission.md`):

- "We help Project Handlers at TIC notified bodies validate certification documents 400x faster by transforming manual compliance checks into AI-powered assessments with evidence-based results."

**Connection**:

- **Brand purpose** = WHY we solve document validation with quality management rigor (not AI hype)
- **Brand values** = HOW we deliver fast, transparent, simple validation (quality + transparency + expertise)
- **Brand personality** = How we show up during journey moments (direct, competent, supportive professional)

---

## Brand Purpose

**Why we exist beyond profit**

We combine AI with quality management expertise to transform document validation. Built by professionals who understand certification workflows, Qteria uses AI as a precise quality gate that validates fast and shows evidence for every decision. We believe AI should amplify expert judgment, not replace it. Validation must be transparent - every result traceable to its source.

**Core Belief**:
AI has extraordinary potential when applied with discipline and domain expertise. The TIC industry doesn't need more complexity - it needs tools built by people who understand quality management, who use AI where it excels, and who refuse to compromise transparency for convenience.

---

## Core Values

**The principles that guide every decision**

### 1. Quality Over Speed (But We Deliver Both)

**What it means**:
Traditional thinking says you choose quality OR speed. We refuse that trade-off. AI enables both - validation in 10 minutes with accuracy that matches or exceeds days of manual review. We achieve speed through smart architecture and AI orchestration, not by cutting corners on accuracy.

**How it shows up**:

- Target <5% false positive rate, <1% false negative rate
- Won't ship faster AI models if they reduce validation accuracy
- Extensive testing before launch (pilot with TÜV SÜD validates quality)
- Step 3 processing time: <10 minutes with 95%+ accuracy
- Error handling: graceful degradation, never silent failures

**Trade-offs we make**:

- We delay feature releases to ensure quality meets standards
- We invest more engineering time in PDF parsing precision (slower development, better results)
- We reject "move fast and break things" culture (reliability matters more than velocity in compliance)

**Journey Connection**: Step 3 (AI validation) delivers BOTH speed (<10 min vs 1-2 days) AND quality (evidence-based results users can verify)

---

### 2. Transparency (Evidence-Based Validation)

**What it means**:
Every AI decision must show its evidence. No black-box "the AI said so" - always a link to the exact page and section where the issue exists. Users should be able to verify the AI is correct, not blindly trust it. Confidence in our tool comes from users seeing the proof, not from marketing claims.

**How it shows up**:

- Results display format: "FAIL → [Link: test-report.pdf, page 8, section 3.2]"
- Users click the link and see exactly where the issue is
- Clear confidence levels (green = high confidence pass, yellow = uncertain, red = fail)
- No hidden AI "magic" - users understand what was checked and why
- Audit trails show every assessment, every criteria, every AI response

**Trade-offs we make**:

- Harder engineering (must parse PDFs precisely, detect sections, create accurate links)
- Can't use simpler AI approaches that don't provide evidence
- More complex UI to display evidence clearly (not just "pass/fail" buttons)

**Journey Connection**: Step 3 aha moment is "IT ACTUALLY WORKS" because AI shows proof (page 8, section 3.2), not just opinion

---

### 3. Simplicity (No Enterprise Bloat)

**What it means**:
We focus on doing one thing exceptionally well - workflow-based document validation. Every feature request gets scrutinized: "Does this serve the core job (create workflow → upload docs → validate → see results)?" If not, we say no. Simplicity is a discipline, not laziness. We remove complexity, not add it.

**How it shows up**:

- Workflow creation takes <30 minutes (measured and tracked)
- Clean, minimal interface - no 50-button dashboards
- Say "no" to feature requests that don't serve Project Handlers or Process Managers
- Documentation is clear and concise (no 200-page manuals)
- Onboarding: users succeed in first hour, not first week

**Trade-offs we make**:

- Lose customers who want "everything in one platform" (project management, team chat, reporting dashboards)
- Turn down revenue from customers whose needs violate our simplicity principle
- Resist temptation to add features just because competitors have them

**Journey Connection**: Step 1 (Process Manager creates workflow) succeeds in <30 min because interface is simple and focused, not bloated with options

---

### 4. Domain Expertise (Built by People Who Understand)

**What it means**:
Built by professionals from the TIC industry who understand certification workflows, document requirements, and quality management systems. Not Silicon Valley outsiders guessing at requirements or applying generic AI to specialized problems. We speak the language of notified bodies because we've worked in them.

**How it shows up**:

- Co-development with TÜV SÜD (first customer shapes product with insider knowledge)
- White-glove onboarding where we understand your certification types without explanation
- Features designed for real workflows (buckets for document types, criteria for validation checks)
- Support that speaks your language (we know what SOC2, ISO 13485, Medical Device Class II mean)
- Case studies reference actual certification scenarios, not generic "document processing"

**Trade-offs we make**:

- Slower to expand to other industries (we go deep in TIC first, then adjacent markets)
- Won't hire sales reps who don't understand compliance/certification (limits hiring pool)
- Invest more time learning customer workflows instead of pushing generic product

**Journey Connection**: Process Managers trust us because workflows match their mental models (document buckets, validation criteria) - built by someone who understands certification

---

### 5. Partnership Over Transactions

**What it means**:
Every customer gets a dedicated relationship manager (not a support ticket queue). We build software WITH customers, not FOR them and disappear. Success is measured by long-term retention and NPS, not just contract signatures. We care about your outcomes, not just our revenue.

**How it shows up**:

- Dedicated relationship manager per notified body (founder for first 5-10 customers)
- Quarterly business reviews (not just when renewing contracts)
- Co-development input: pilot customers shape roadmap priorities
- White-glove onboarding: we don't hand you a login and say "good luck"
- Response time: <24 hours (often same-day for critical issues)

**Trade-offs we make**:

- Doesn't scale to thousands of customers (caps at 20-50 high-value enterprise accounts)
- Higher cost structure (relationship managers vs automated support)
- Can't offer $99/month self-service tier (focus on $30K/year partnerships)

**Journey Connection**: Process Managers and Project Handlers succeed because relationship manager helps them create workflows, troubleshoot issues, refine criteria - not left alone to figure it out

---

## Brand Personality

**How we show up as a brand**

### Personality Traits

On a scale, where Qteria falls:

- **[●●●○○]** Formal ←→ Casual (Professional middle - clear and direct, not stuffy, not chatty)
- **[●●●●○]** Serious ←→ Witty (Mostly serious - compliance isn't funny, but not robotic)
- **[●●●○○]** Authoritative ←→ Friendly (Authoritative but approachable - expert voice with warmth)
- **[●●●●○]** Reserved ←→ Bold (Reserved - let results speak, no hype or "revolutionary" claims)

### Character Description

**If Qteria was a person:**

**Who they are**:
A female quality management professional in her early 30s. Office nerd who genuinely loves details and precision. Balkan beauty with dark hair. The person you want reviewing your documents because she catches everything - and explains it clearly. She's been in certification long enough to understand the workflows, but young enough to embrace AI when it's done right.

**How they talk**:
Direct and to the point. No corporate jargon, no dancing around issues. "Here's what's wrong, here's where to find it, here's how to fix it." Friendly and supportive, but doesn't waste time. Gets what she wants. Sentences are clear and concise. Uses plain English, not buzzwords. If there's a problem, she tells you immediately with evidence. If something works, she confirms it without fanfare.

**How they dress**:
Professional - shirt with a sweater on top. Put-together but practical. Not trying to impress with designer labels, just competent and focused on the work. Everything in its place, organized, clean. Dark colors, nothing flashy. You'd see her at a certification conference and think "she knows what she's doing."

**What their colleagues say about them**:

- "She catches everything" (quality focus)
- "Super helpful, explains things clearly" (transparency + partnership)
- "No-nonsense, tells it straight" (direct communication)
- "You can count on her" (reliable, trustworthy)
- "Detail-oriented but not annoying about it" (expertise without arrogance)

---

## Brand Promise

**What customers can count on**

Every interaction will be **clear, accurate, and respectful of your expertise**.

You'll never get black-box AI results without evidence. You'll never be left wondering "why did it flag this?" You'll never feel like you're talking to someone who doesn't understand certification workflows.

You can always count on:

- **Evidence** for every validation decision (exact page and section)
- **Clarity** in communication (no jargon, no hiding behind complexity)
- **Responsiveness** from your relationship manager (<24 hours)
- **Quality** over shortcuts (we won't ship broken features to hit deadlines)

---

## Visual Direction

**Aesthetic guidance for visual identity**

### Mood and Aesthetic

**Clean, organized, trustworthy** - not flashy or trendy. The visual identity should feel like a well-organized office: everything has its place, nothing unnecessary, professional but not cold. Modern but not chasing design trends. Minimal but not sterile - subtle warmth (Balkan heritage) prevents it from feeling like generic enterprise software.

**Keywords**: Precise, professional, approachable, competent, uncluttered

### Color Direction

**Primary feeling**: Cool and professional with subtle warmth

**Color associations**:

- **Blues/Grays**: Professional, trustworthy, quality management (but not generic corporate blue)
- **Subtle warm accent**: Balkan warmth - perhaps a muted terracotta, warm gray, or subtle burgundy (not bright red)
- **White space**: Clean, organized, minimal
- **Avoid**: Bright playful colors (doesn't fit serious compliance), all-gray corporate boredom, black/dark mode as primary (prefer light, clear)

**Color psychology**:

- Primary colors convey trust, competence, precision
- Accent colors add approachability without undermining authority
- High contrast for readability (evidence links must be clear)

### Typography Direction

**Primary**: Clear, readable, modern sans-serif (not trendy geometric)

- Examples: Inter, IBM Plex Sans, Source Sans Pro
- Readable at small sizes (evidence text, document references)
- Professional but not corporate stiff

**Avoid**:

- Serif fonts (too traditional/academic for modern AI tool)
- Overly rounded fonts (too playful for compliance)
- Ultra-thin weights (hard to read, doesn't convey quality)

### Visual References

**Brands/aesthetics we admire**:

- **Stripe** - Clean, professional, trustworthy without being boring. Excellent documentation clarity.
- **Linear** - Minimal, focused, quality feel. Fast interface, no clutter. Modern but not trendy.
- **Notion** - Approachable professional. Not stuffy enterprise, not playful startup. Good balance.

**Brands/aesthetics to avoid**:

- **Generic enterprise software** (Oracle, SAP) - Too boring, gray, lifeless. Doesn't reflect our quality focus.
- **Playful startup aesthetic** (Mailchimp, Slack) - Too casual for serious compliance work. Colors too bright.
- **Complicated dashboards** (Tableau, complex analytics tools) - Too much visual noise. Violates simplicity principle.

---

## Brand Differentiation

**How we're different from alternatives**

### Competitive Landscape

**Who else serves our audience?**

- **Complicated AI document tools** (generic document processors) - Feature-rich, overwhelming UX, not specialized for compliance
- **India outsourcing teams** (current baseline) - Slow (1-2 days), expensive ($100K/year), hard to iterate on validation rules
- **Internal homegrown tools** - Custom-built by notified bodies, hard to maintain, no AI, slow to improve

### Our Differentiation

**What makes us different**:

1. **Evidence-Based AI (Not Black Boxes)**:
   - Others: "AI detected an issue" (no proof)
   - Qteria: "FAIL → [Link: test-report.pdf, page 8, section 3.2]" (click and verify)
   - Why it matters: Users trust what they can verify. Transparency builds confidence in AI validation.

2. **Radical Simplicity (Not Enterprise Bloat)**:
   - Others: 50 features, overwhelming dashboards, week-long training
   - Qteria: Workflow → Buckets → Criteria → Validate. Create workflow in <30 min.
   - Why it matters: Process Managers succeed immediately without IT department support.

3. **Domain Expertise (Not Generic AI Tools)**:
   - Others: Silicon Valley teams applying generic AI to documents
   - Qteria: Built by TIC professionals who understand certification workflows
   - Why it matters: Features match actual needs (document buckets, validation criteria), not theoretical use cases.

4. **White-Glove Partnership (Not Ticket Queues)**:
   - Others: Submit ticket, wait 3 days, get generic response
   - Qteria: Dedicated relationship manager, <24 hour response, quarterly reviews
   - Why it matters: Enterprise customers need reliable support for mission-critical validation.

5. **Enterprise Data Privacy (Not Consumer AI)**:
   - Others: Documents processed through consumer AI APIs, unclear retention policies
   - Qteria: Zero-retention AI agreements, SOC2/ISO 27001 path, audit trails
   - Why it matters: Notified bodies handle confidential certification documents, can't risk data leaks.

---

## Brand Applications

**Where and how brand shows up**

### Primary Touchpoints

**Website (qteria.com)**:

- **How brand manifests**: Clean, organized layout (simplicity). Clear explanations of evidence-based validation (transparency). Case studies from TIC industry (domain expertise). No hype, just results.
- **Tone**: Professional, direct. "Here's the problem. Here's how we solve it. Here's proof it works."
- **Visuals**: Screenshots showing evidence links, workflow creation UI. Clean white space, professional color palette.

**Product UI (Application Interface)**:

- **How brand manifests**: Minimal, focused interface. Workflow builder is clear and fast. Results page prominently displays evidence links. No cluttered dashboards.
- **Tone**: Direct instructions. "Upload documents" not "Let's get started on your validation journey!" Error messages explain exactly what's wrong and how to fix it.
- **Visuals**: Clean forms, clear typography, high-contrast evidence links (users must be able to click and verify easily).

**Marketing Materials (Case Studies, Presentations)**:

- **How brand manifests**: Concrete metrics ($70K savings, 400x faster), real customer quotes (TÜV SÜD), evidence-based claims (no "revolutionary" hype).
- **Tone**: Factual, credible. "TÜV SÜD reduced assessment time from 1-2 days to <10 minutes while maintaining 95%+ accuracy."
- **Visuals**: Professional presentation templates, clear data visualization, customer logos.

**Customer Support (Email, Calls, Relationship Manager)**:

- **How brand manifests**: Direct, helpful responses. No scripted corporate-speak. Expert advice on workflow setup, criteria refinement.
- **Tone**: "Here's what I see. Try this. Let me know if you need help." Friendly but efficient.
- **Visuals**: Email signature with clean branding, professional video call backgrounds.

**Social Media / LinkedIn (Professional Presence)**:

- **How brand manifests**: Thought leadership on AI in quality management, case studies, industry insights. No memes, no hype.
- **Tone**: Professional expertise. Share learnings about AI validation, compliance trends, customer success stories.
- **Visuals**: Clean branded graphics, professional headshots, industry event photos.

### Brand Consistency

**What stays consistent** (never changes):

- Evidence-based validation (always show proof, never black-box AI)
- Simplicity in design (resist feature creep, keep UI minimal)
- Direct, clear communication (no jargon, no corporate fluff)
- Professional visual identity (clean, organized, trustworthy aesthetic)
- Partnership approach (relationship managers, not ticket queues)

**What adapts** (flexes for context):

- Formality level (more casual in onboarding calls, more formal in contracts/legal)
- Visual complexity (marketing materials can be richer, product UI stays minimal)
- Content depth (case studies detailed, UI microcopy concise)
- Channel-specific tone (LinkedIn professional, email supportive, product UI instructional)

---

## Decision Framework

**Using this brand strategy**

When making decisions, ask:

1. **Does this align with our brand purpose?**
   - Are we combining AI with quality management expertise (not just building AI hype)?
   - Are we amplifying expert judgment (not replacing it)?
   - Are we maintaining transparency (evidence traceable)?

2. **Does this reflect our core values?**
   - Quality Over Speed: Are we maintaining accuracy while improving speed?
   - Transparency: Can users verify AI decisions with evidence?
   - Simplicity: Does this remove complexity or add it?
   - Domain Expertise: Are we leveraging TIC industry knowledge?
   - Partnership: Are we building WITH customers or AT them?

3. **Does this match our personality?**
   - Professional but not stuffy? (clear, direct communication)
   - Serious but not robotic? (focused on results, not cold)
   - Authoritative but approachable? (expert voice with warmth)
   - Reserved but confident? (results speak, no hype)

4. **Does this deliver on our promise?**
   - Clear: Can users understand what happened and why?
   - Accurate: Is the AI validation result correct and proven?
   - Respectful of expertise: Are we treating users as professionals?

5. **Does this differentiate us?**
   - Evidence-based (not black-box)?
   - Simple (not bloated)?
   - Built by domain experts (not generic AI builders)?
   - White-glove partnership (not transactional)?

**If the answer to any question is "no," reconsider the decision.**

---

## Brand Examples in Practice

### ✅ Good: Aligned with Brand

**Feature Decision**: Add feedback mechanism where users can flag false positives/negatives

- ✅ Purpose: Improves AI through transparency (users help refine validation)
- ✅ Values: Transparency (users verify AI), Partnership (co-develop quality), Quality (continuous improvement)
- ✅ Personality: Direct ("Flag if incorrect"), supportive ("Help us improve")

**Marketing Copy**: "Qteria validates certification documents in <10 minutes with evidence for every decision. See exactly where issues are - page, section, reasoning. Built by TIC professionals for notified bodies."

- ✅ Purpose: Combines AI with quality management, shows transparency
- ✅ Personality: Direct, factual, no hype
- ✅ Differentiation: Evidence-based, domain expertise

**Support Response**: "I see the issue - the AI flagged page 8 because it expected a signature in section 3.2. Check the document there. If it's actually signed but AI missed it, flag it as false positive and we'll refine the model. Let me know if you need help."

- ✅ Purpose: Transparent explanation (shows evidence)
- ✅ Values: Partnership (collaborative problem-solving), Transparency (explains AI reasoning)
- ✅ Personality: Direct, helpful, competent

### ❌ Bad: Misaligned with Brand

**Feature Decision**: Add team chat inside product

- ❌ Values: Violates Simplicity (not core to validation workflow)
- ❌ Purpose: Doesn't serve AI validation mission
- **Decision**: Say no. Users have Slack/Teams already.

**Marketing Copy**: "Revolutionary AI technology disrupts certification! Game-changing automation transforms your workflow!"

- ❌ Personality: Too bold/hyped (violates "reserved")
- ❌ Differentiation: Sounds like generic AI hype (not quality management focus)
- **Fix**: "AI validation built with quality management rigor. Fast results backed by evidence."

**Support Response**: "We apologize for any inconvenience. Your ticket #12345 has been escalated to our support team. We'll get back to you within 3 business days."

- ❌ Values: Violates Partnership (sounds transactional, not relationship-driven)
- ❌ Personality: Too formal/corporate (not direct and helpful)
- **Fix**: "I see your assessment timed out. Let me check the logs and get back to you today."

---

## Next Steps

- [x] Brand strategy complete and documented
- [ ] Run `/create-design` (Session 6) - Create design system informed by this brand strategy
- [ ] Optional: Run `/discover-naming` to validate "Qteria" or explore alternatives
- [ ] Optional: Run `/define-messaging` to create messaging framework aligned with brand
- [ ] Share with TÜV SÜD stakeholders for feedback and alignment
- [ ] Use as reference during product development and customer interactions

---

## Document Control

**Status**: Final
**Last Updated**: November 2025
**Next Review**: After TÜV SÜD pilot launch (Q2 2026)
**Owner**: Founder
**Stakeholders**: TÜV SÜD (first customer), future team members, investors

---

**Brand Summary**: Qteria is the competent, direct quality management professional who uses AI the right way - transparent, simple, built by people who understand certification. We deliver speed AND quality, not speed OR quality. Every decision shows evidence. Every customer gets a relationship manager. No enterprise bloat, no AI hype, just results you can verify.
