# Qteria Product Backlog

> **Generated from**: Sessions 1-9 cascade outputs
> **Target MVP**: Q1 2026 (TÜV SÜD pilot launch)
> **Total Stories**: 42 stories across 10 epics

---

## Executive Summary

This backlog transforms the Qteria user journey into a prioritized implementation plan. Every story traces back to the core mission: **helping Project Handlers at TIC notified bodies validate certification documents 400x faster through evidence-based AI assessments**.

**MVP Focus (P0 Stories)**: Complete workflow engine that enables TÜV SÜD co-development - Process Managers can create workflows in <30 min, Project Handlers can run assessments with AI validation in <10 min, and receive evidence-based pass/fail results with exact page/section links.

---

## Epic Overview

### Foundation Epics (Enable Everything)

**Epic 01: Database & Infrastructure Setup** [P0]
- **Stories**: 4 (database schema, migrations, seed data, infrastructure)
- **Estimated Effort**: 5 days
- **Purpose**: PostgreSQL schema, API infrastructure, deployment pipeline foundation
- **Journey Impact**: Enables all other epics - no stories can start without database

**Epic 02: Authentication & Authorization** [P0]
- **Stories**: 4 (login, JWT, RBAC, multi-tenancy)
- **Estimated Effort**: 6 days
- **Purpose**: Secure access control with roles (Process Manager, Project Handler, Admin)
- **Journey Impact**: Gates all authenticated features

---

### Journey-Driven Epics (User Value)

**Epic 03: Workflow Management** [P0] → **Journey Step 1**
- **Stories**: 6 (create, edit, delete, list, share workflows)
- **Estimated Effort**: 10 days
- **Purpose**: Process Managers define validation workflows (buckets + criteria)
- **Journey Impact**: Step 1 - "Create workflow in <30 min"
- **Key Metric**: Time to create first workflow (<30 min target)

**Epic 04: Document Processing** [P0] → **Journey Step 2**
- **Stories**: 5 (upload, validate, store, retrieve, delete documents)
- **Estimated Effort**: 8 days
- **Purpose**: Project Handlers drag-drop PDFs into document buckets
- **Journey Impact**: Step 2 - "Upload documents and start assessment"
- **Key Metric**: Upload success rate (>95% target)

**Epic 05: AI Validation Engine** [P0] → **Journey Step 3** ⭐ **CRITICAL**
- **Stories**: 8 (PDF parsing, AI integration, evidence extraction, background jobs, confidence scoring)
- **Estimated Effort**: 20 days
- **Purpose**: Core AI validation with evidence-based pass/fail results in <10 min
- **Journey Impact**: Step 3 - **"AHA MOMENT"** - AI finds exact issue location with proof
- **Key Metric**: Assessment completion time (<10 min), AI accuracy (>95%)

**Epic 06: Results & Evidence Display** [P0] → **Journey Step 3 (Visual)**
- **Stories**: 4 (results page, evidence links, status polling, notifications)
- **Estimated Effort**: 7 days
- **Purpose**: Beautiful display of pass/fail results with clickable evidence links to exact pages
- **Journey Impact**: Step 3 visual delivery - users see "Criteria 2: FAIL → [Link: page 8]"
- **Key Metric**: User trust score (>95% confidence in AI results)

**Epic 07: Re-assessment & Iteration** [P1] → **Journey Step 4**
- **Stories**: 3 (replace document, re-run assessment, version tracking)
- **Estimated Effort**: 5 days
- **Purpose**: Project Handlers fix issues and re-validate without re-uploading everything
- **Journey Impact**: Step 4 - "Fixed it before Certification Person saw it"
- **Key Metric**: Re-assessment rate, time to fix issues

**Epic 08: Reporting & Export** [P1] → **Journey Step 5**
- **Stories**: 3 (generate PDF report, download, share links)
- **Estimated Effort**: 4 days
- **Purpose**: Export validation reports for handoff to Certification Person
- **Journey Impact**: Step 5 - Clean handoff with confidence
- **Key Metric**: Reports generated per assessment

---

### Polish & Scale Epics (Post-MVP)

**Epic 09: Performance Optimization** [P1]
- **Stories**: 3 (caching, parallel processing, query optimization)
- **Estimated Effort**: 6 days
- **Purpose**: Reduce assessment time from <10 min to <5 min, improve responsiveness
- **Journey Impact**: Accelerates Step 3 (faster validation = more value)
- **Key Metric**: P95 assessment time (<5 min stretch goal)

**Epic 10: Testing & Quality Assurance** [P0/P1]
- **Stories**: 2 (E2E test suite, CI/CD pipeline)
- **Estimated Effort**: 5 days
- **Purpose**: Comprehensive testing ensures reliability ("it just works" principle)
- **Journey Impact**: Protects against false negatives/positives that destroy trust
- **Key Metric**: Code coverage (>70%), uptime (99.9%)

---

## Priority Distribution

| Priority | Count | Purpose | Timeline |
|----------|-------|---------|----------|
| **P0** | 28 stories | Critical for MVP - TÜV SÜD pilot | Q1 2026 (12 weeks) |
| **P1** | 12 stories | Important for production launch | Q2 2026 (8 weeks) |
| **P2** | 2 stories | Nice-to-have, defer to Year 2 | 2027+ |

**Total**: 42 stories

---

## Journey Mapping (Stories by User Journey Step)

| Journey Step | Epic | Story Count | Estimated Effort |
|--------------|------|-------------|------------------|
| **Foundation** (Prerequisite) | Epic 01, 02 | 8 stories | 11 days |
| **Step 1**: Process Manager Creates Workflow | Epic 03 | 6 stories | 10 days |
| **Step 2**: Project Handler Uploads Documents | Epic 04 | 5 stories | 8 days |
| **Step 3**: AI Validates & Returns Results ⭐ | Epic 05, 06 | 12 stories | 27 days |
| **Step 4**: Re-Run Assessment | Epic 07 | 3 stories | 5 days |
| **Step 5**: Export Report | Epic 08 | 3 stories | 4 days |
| **Cross-Cutting** (Performance, Testing) | Epic 09, 10 | 5 stories | 11 days |

**Total Estimated Effort**: 76 person-days (~15 weeks for solo founder, ~8 weeks with 1 helper)

---

## MVP Timeline Estimate

### Phase 1: Foundation (Weeks 1-2)
**Focus**: Database, auth, infrastructure
- Epic 01: Database & Infrastructure (5 days)
- Epic 02: Authentication & Authorization (6 days)
**Deliverable**: Can log in, database ready

### Phase 2: Workflow Creation (Weeks 3-4)
**Focus**: Process Manager can create workflows
- Epic 03: Workflow Management (10 days)
**Deliverable**: Process Manager creates workflow with buckets + criteria in <30 min

### Phase 3: Document Upload (Week 5)
**Focus**: Project Handler can upload documents
- Epic 04: Document Processing (8 days)
**Deliverable**: Drag-drop PDFs, upload to secure storage

### Phase 4: AI Validation (Weeks 6-9) ⭐ **CRITICAL PATH**
**Focus**: Core AI engine - validate documents with evidence
- Epic 05: AI Validation Engine (20 days)
- Epic 06: Results Display (7 days)
**Deliverable**: Assessment completes in <10 min, shows evidence-based pass/fail

### Phase 5: Polish & Launch Prep (Weeks 10-12)
**Focus**: Re-assessment, reporting, testing
- Epic 07: Re-assessment (5 days)
- Epic 08: Reporting (4 days)
- Epic 10: Testing & E2E suite (5 days)
**Deliverable**: Complete end-to-end flow ready for TÜV SÜD pilot

**MVP Launch Target**: Week 12 (Q1 2026)

---

## RICE Prioritization Summary

**RICE Formula**: (Reach × Impact × Confidence) ÷ Effort

### Top 10 Highest RICE Scores (Must-Do First)

1. **STORY-001**: Database schema setup (RICE: 100) - Foundation
2. **STORY-005**: User login with Auth.js (RICE: 80) - Foundation
3. **STORY-009**: Create workflow API endpoint (RICE: 90) - Step 1
4. **STORY-015**: Upload documents to Vercel Blob (RICE: 85) - Step 2
5. **STORY-020**: PDF parsing with PyPDF2 (RICE: 95) - Step 3
6. **STORY-021**: Claude AI integration (RICE: 100) - Step 3 ⭐
7. **STORY-022**: Evidence extraction (page/section links) (RICE: 95) - Step 3 ⭐
8. **STORY-023**: Background job queue (Celery + Redis) (RICE: 90) - Step 3
9. **STORY-027**: Results display with evidence links (RICE: 85) - Step 3
10. **STORY-010**: List workflows for organization (RICE: 75) - Step 1

**Pattern**: Foundation → Step 1 (Workflows) → Step 2 (Documents) → Step 3 (AI Validation) is the critical path.

---

## Success Metrics Tracking

**North Star Metric**: Active Assessments Per Month
- **Target (Q2 2026)**: 100 assessments/month (TÜV SÜD pilot)
- **Tracked In**: PostgreSQL (assessments table)

**Input Metrics** (Backlog Coverage):
- ✅ **Active Customers**: Epic 02 (auth + multi-tenancy)
- ✅ **Assessments Per Customer**: Epic 03-06 (workflow → validation flow)
- ✅ **Assessment Completion Rate**: Epic 05, 06 (reliability)
- ✅ **New Workflows Created**: Epic 03 (workflow creation UX)
- ✅ **Assessment Success Rate (AI Accuracy)**: Epic 05 (confidence scoring, feedback loop)

**Counter-Metrics** (Protected):
- ✅ **Assessment Accuracy**: Epic 05 (AI validation, evidence extraction)
- ✅ **Data Privacy**: Epic 02 (multi-tenancy), Epic 04 (encryption)
- ✅ **UX Simplicity**: Epic 03 (workflow creation <30 min)
- ✅ **Support Quality**: Instrumented via audit logs (Epic 01)

---

## Dependencies & Blockers

### Critical Path Dependencies

**Phase 1 (Foundation) BLOCKS everything**:
- STORY-001 (Database schema) blocks ALL data stories
- STORY-005 (Authentication) blocks ALL authenticated endpoints

**Phase 2 (Workflows) BLOCKS assessments**:
- STORY-009 (Create workflow) blocks STORY-020 (Start assessment)
- Workflows must exist before assessments can reference them

**Phase 3 (Documents) BLOCKS AI validation**:
- STORY-015 (Upload documents) blocks STORY-021 (AI validation)
- Documents must be stored before AI can process them

**No Parallel Work** (Solo Founder):
- Must complete Foundation → Workflows → Documents → AI sequentially
- Can't parallelize until Phase 4 (AI + Results can be split if 2 people)

### Optional Features (Can Defer)

- **STORY-033**: Re-assessment with partial updates [P1] - nice-to-have, not MVP blocker
- **STORY-036**: Shareable report links [P2] - defer to Year 2
- **STORY-038**: Performance optimization (caching) [P1] - only if <10 min target not met
- **STORY-042**: Advanced analytics dashboard [P2] - post-launch

---

## Risk Mitigation

### High-Risk Stories (Technical Complexity)

**STORY-021**: Claude AI integration for validation [P0, 5 days]
- **Risk**: AI accuracy <95% (false positives/negatives)
- **Mitigation**: Extensive prompt engineering, test with real TÜV SÜD documents, feedback loop

**STORY-022**: Evidence extraction (page/section links) [P0, 4 days]
- **Risk**: PDF parsing unreliable (section detection fails)
- **Mitigation**: Use multiple libraries (PyPDF2 + pdfplumber), fallback to page-only if sections unclear

**STORY-023**: Background job queue (Celery + Redis) [P0, 3 days]
- **Risk**: Jobs fail silently, user waits indefinitely
- **Mitigation**: Retry logic, timeout handling, clear error messages

### Low-Risk Stories (Straightforward CRUD)

- STORY-009: Create workflow API [P0, 2 days] - standard REST endpoint
- STORY-015: Upload documents [P0, 2 days] - Vercel Blob API well-documented
- STORY-027: Results display [P0, 2 days] - React component rendering data

---

## What's NOT in This Backlog (Scope Boundaries)

**Not Building** (Aligns with "Simplicity Over Features" principle):
- ❌ **Batch processing** (50+ assessments at once) - adds complexity, violates simplicity
- ❌ **Custom reporting dashboards** - use basic PDF export, not analytics
- ❌ **In-app chat** / collaboration - focus on validation, not project management
- ❌ **Mobile app** - journey is desktop-first, no mobile signals
- ❌ **Workflow templates library** - defer to Q2 2026 after TÜV SÜD validates patterns
- ❌ **API integrations** (project management tools) - Enterprise tier feature, Year 2+
- ❌ **Multi-language documents** - English-only for MVP

**Why Not**: Every "no" protects the mission - fast, evidence-based validation. Feature creep would delay TÜV SÜD pilot and violate product principles.

---

## Next Steps

1. **Review with stakeholders**: Validate epic structure and story breakdown
2. **Refine RICE scores**: Adjust based on TÜV SÜD co-development priorities
3. **Create GitHub issues**: Run `/create-gh-issues` to push backlog to GitHub
4. **Start Phase 1**: Begin with STORY-001 (Database schema setup)

---

## File Structure

```
product-guidelines/10-backlog/
├── BACKLOG.md (this file - summary)
└── issues/
    ├── epic-01-database-infrastructure.md
    ├── epic-02-authentication-authorization.md
    ├── epic-03-workflow-management.md
    ├── epic-04-document-processing.md
    ├── epic-05-ai-validation-engine.md
    ├── epic-06-results-evidence-display.md
    ├── epic-07-reassessment-iteration.md
    ├── epic-08-reporting-export.md
    ├── epic-09-performance-optimization.md
    ├── epic-10-testing-quality-assurance.md
    ├── story-001-database-schema-setup.md
    ├── story-002-database-migrations.md
    ├── ... (42 total story files)
```

---

**Backlog Status**: ✅ Complete - Ready for implementation

**Last Updated**: 2025-11-17
**Next Review**: After TÜV SÜD pilot kickoff (Q2 2026)
