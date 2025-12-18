# [EPIC-07] Re-assessment & Iteration

**Type**: Epic
**Journey Step**: Step 4 - Fix Issues & Re-Run Assessment
**Priority**: P1 (Important for Production)

---

## Epic Overview

Enable Project Handlers to replace failing documents and re-run assessments without re-uploading everything. This is **Journey Step 4** - iterative validation until all criteria pass.

**User Value**: Project Handlers fix issues quickly and verify fixes before forwarding to Certification Person, avoiding embarrassing back-and-forth.

---

## Success Criteria

- [ ] Project Handler can replace individual documents in assessment
- [ ] Can re-run assessment with updated documents
- [ ] Re-assessment faster than initial (caches unchanged documents)
- [ ] Version tracking (history of re-runs)
- [ ] Clear diff (which criteria changed from previous run)

---

## Stories in This Epic

### STORY-031: Replace Document in Assessment [P1, 2 days]

Implement `PUT /v1/assessments/:id/documents/:bucket_id` endpoint that replaces document for specific bucket and marks assessment as "needs re-run".

**RICE**: R:80 × I:2 × C:80% ÷ E:2 = **64**

### STORY-032: Re-Run Assessment API [P1, 2 days]

Implement `POST /v1/assessments/:id/rerun` endpoint that triggers new assessment with updated documents. Creates new assessment record linked to original (version history).

**RICE**: R:80 × I:2 × C:85% ÷ E:2 = **68**

### STORY-033: Partial Re-Assessment (Smart Caching) [P2, 1 day]

Only re-validate criteria for replaced documents (not all criteria). Skip unchanged documents to save AI cost and time.

**RICE**: R:60 × I:1 × C:70% ÷ E:1 = **42**

---

## Total Estimated Effort

**5 person-days** (1 week for solo founder)

**Breakdown**:

- Backend: 3 days (replace document, re-run logic, versioning)
- Frontend: 1 day (replace document UI)
- Testing: 1 day (integration + E2E)

---

## Dependencies

**Blocks**: Nothing (optional optimization)

**Blocked By**:

- STORY-027: Results display (need to see which criteria failed)
- STORY-021: AI validation (need working engine to re-run)

---

## Technical Approach

**Tech Stack**:

- Backend: FastAPI + Celery (same as initial assessment)
- Frontend: Next.js (replace document UI)

**Replace Document Flow**:

1. User views failed assessment results
2. User clicks "Replace Document" for failing bucket
3. User uploads new document
4. Backend replaces document in assessment_documents table
5. Backend marks assessment status: "needs_rerun"
6. Frontend shows "Re-run Assessment" button

**Re-Run Assessment Flow**:

1. User clicks "Re-run Assessment"
2. Backend creates new assessment record (linked to original via parent_assessment_id)
3. Backend triggers Celery job (same as initial assessment)
4. AI validates with updated documents
5. Results page shows diff (criteria that changed)

**Partial Re-Assessment** (STORY-033 - optional):

- Only re-validate criteria that apply to replaced bucket
- Skip criteria for unchanged documents
- Example: Replace "Test Reports" bucket → only re-check criteria that apply to that bucket
- Saves AI cost (5 criteria → 2 criteria) and time (10 min → 5 min)

**Reference**: `product-guidelines/00-user-journey.md` (Step 4)

---

## Success Metrics

**User Experience**:

- Re-assessment rate: 20-30% of assessments (users iterate to fix issues)
- Time to fix issues: <1 hour from failure to pass
- Clarification rounds avoided: Measurable via customer feedback

**Technical**:

- Re-assessment time: <5 minutes (faster than initial with caching)
- Partial re-assessment savings: 50% fewer AI calls

---

## Definition of Done

- [ ] Replace document API working
- [ ] Re-run assessment creates new linked assessment
- [ ] Results page shows diff (criteria changed)
- [ ] Version history visible (assessment 1 → assessment 2)
- [ ] Partial re-assessment (optional) only checks relevant criteria
- [ ] E2E test: View failed assessment → Replace document → Re-run → Pass
- [ ] Code coverage >80% backend, >50% frontend
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: Version history complex (hard to track changes)

- **Mitigation**: Simple parent_assessment_id link, UI shows "Previous: 2/5 passed, Current: 5/5 passed"

**Risk**: Partial re-assessment logic buggy (misses criteria)

- **Mitigation**: Test thoroughly, fallback to full re-run if logic unclear

---

## Testing Requirements

**Integration Tests** (80% coverage):

- [ ] PUT /v1/assessments/:id/documents/:bucket_id replaces document
- [ ] POST /v1/assessments/:id/rerun creates new assessment
- [ ] Partial re-assessment only checks relevant criteria
- [ ] Version history preserved (parent_assessment_id link)

**E2E Tests**:

- [ ] Complete re-assessment flow (Journey Step 4)
- [ ] Results diff shows criteria changes

---

## Next Epic

After completing this epic, proceed to **EPIC-08: Reporting & Export** to enable users to export validation reports.
