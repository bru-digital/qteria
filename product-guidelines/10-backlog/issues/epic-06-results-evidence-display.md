# [EPIC-06] Results & Evidence Display

**Type**: Epic
**Journey Step**: Step 3 (Visual) - Display Evidence-Based Results
**Priority**: P0 (MVP Critical)

---

## Epic Overview

Display AI validation results beautifully with pass/fail status, confidence indicators, and clickable evidence links to exact pages/sections in documents. This is the **visual delivery of the aha moment** - users see proof that AI found the exact issue location.

**User Value**: Project Handlers see clear, trustworthy results with evidence they can verify, building confidence in AI validation.

---

## Success Criteria

- [ ] Results page shows all criteria with pass/fail status
- [ ] Color-coded confidence (green/yellow/red)
- [ ] Clickable evidence links open PDF at exact page
- [ ] Overall assessment status (X/Y criteria passed)
- [ ] Status polling shows progress while assessment runs
- [ ] Email/in-app notification when complete
- [ ] Results load in <2 seconds

---

## Stories in This Epic

### STORY-027: Assessment Results Display UI [P0, 2 days]
Create React component that shows assessment results: list of criteria with pass/fail badges, confidence colors, evidence links, and AI reasoning. Overall status shows "3/5 criteria passed".

**RICE**: R:100 × I:3 × C:95% ÷ E:2 = **142**

### STORY-028: Evidence Link to PDF Page [P0, 2 days]
Implement clickable evidence links that open PDF in browser at specific page (using `#page=8` anchor). Download PDF from `GET /v1/documents/:id?page=X` and display in iframe or new tab.

**RICE**: R:100 × I:3 × C:90% ÷ E:2 = **135**

### STORY-029: Assessment Status Polling [P0, 2 days]
Implement frontend polling (every 30 seconds) of `GET /v1/assessments/:id` to check status. Show progress indicator while "pending" or "processing", redirect to results when "completed".

**RICE**: R:100 × I:2 × C:100% ÷ E:2 = **100**

### STORY-030: Email Notification on Completion [P1, 1 day]
Send email to user when assessment completes. Email includes assessment summary (X/Y passed) and link to results page.

**RICE**: R:80 × I:1 × C:80% ÷ E:1 = **64**

---

## Total Estimated Effort

**7 person-days** (1.5 weeks for solo founder)

**Breakdown**:
- Frontend: 5 days (results UI, evidence links, polling)
- Backend: 1 day (email notifications)
- Testing: 1 day (unit + E2E)

---

## Dependencies

**Blocks**:
- EPIC-07: Re-assessment (needs results display to show updated results)
- EPIC-08: Reporting (export generates report from same data)

**Blocked By**:
- STORY-021: Claude AI integration (needs results to display)
- STORY-022: Evidence extraction (needs evidence data)

---

## Technical Approach

**Tech Stack**:
- Frontend: Next.js + React (results UI)
- Polling: React useEffect hook (30s interval)
- PDF Display: Browser native (PDF.js or iframe with #page= anchor)
- Notifications: SendGrid or Resend (email)

**Results Display UI**:
```tsx
<AssessmentResults>
  <OverallStatus>3/5 criteria passed</OverallStatus>
  <CriteriaList>
    <CriteriaItem pass={true} confidence="high">
      ✅ GREEN: Criteria 1: Signatures present - PASS
    </CriteriaItem>
    <CriteriaItem pass={false} confidence="high">
      ❌ RED: Criteria 2: Test summary missing - FAIL
      → [Link: test-report.pdf, page 8, section 3.2]
    </CriteriaItem>
    <CriteriaItem pass={true} confidence="medium">
      ⚠️ YELLOW: Criteria 3: Risk matrix complete - PASS (AI unsure, please verify)
    </CriteriaItem>
  </CriteriaList>
</AssessmentResults>
```

**Evidence Link Flow**:
1. User clicks evidence link
2. Frontend calls `GET /v1/documents/doc_123?page=8`
3. Backend streams PDF from Vercel Blob
4. Frontend opens PDF in new tab with `#page=8` anchor
5. Browser scrolls to page 8 automatically

**Status Polling Flow**:
1. Assessment starts (status: "pending")
2. Frontend polls `GET /v1/assessments/:id` every 30 seconds
3. Status transitions: pending → processing → completed
4. When completed, stop polling and redirect to results page

**Email Notification**:
```
Subject: Assessment Complete: Medical Device - Class II

Hi [User Name],

Your assessment for "Medical Device - Class II" is complete.

Results: 3/5 criteria passed

View full results: [Link to assessment results page]

- Qteria Team
```

**Reference**: `product-guidelines/00-user-journey.md` (Step 3), `product-guidelines/06-design-system.md` (UI components)

---

## Success Metrics

**User Experience**:
- Results page load time: <2 seconds
- Evidence link click-through rate: >50% (users verify evidence)
- User trust score: >95% (confident in AI results)

**Technical**:
- Polling efficiency: No more than 1 request per 30 seconds
- Email delivery rate: >98%
- PDF display success rate: >95%

---

## Definition of Done

- [ ] Results UI displays all criteria with pass/fail
- [ ] Confidence colors work (green/yellow/red)
- [ ] Evidence links open PDF at exact page
- [ ] Status polling updates UI (pending → processing → completed)
- [ ] Email notifications sent on completion
- [ ] Overall status shows X/Y passed
- [ ] E2E test: Start assessment → Poll status → View results → Click evidence
- [ ] Code coverage >50% frontend
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: PDF display fails in browser (compatibility)
- **Mitigation**: Test across Chrome, Firefox, Safari; fallback to download

**Risk**: Polling overloads backend (too frequent)
- **Mitigation**: 30 second interval, exponential backoff if needed

**Risk**: Evidence links broken (page doesn't exist)
- **Mitigation**: Validate evidence_page during extraction (STORY-022)

---

## Testing Requirements

**Unit Tests** (50% coverage target):
- [ ] Results display component renders data correctly
- [ ] Evidence link generation (URL with page parameter)
- [ ] Polling logic (starts, stops on completion)

**Integration Tests**:
- [ ] GET /v1/assessments/:id returns status
- [ ] GET /v1/assessments/:id/results returns criteria results
- [ ] GET /v1/documents/:id?page=X streams PDF

**E2E Tests** (critical flow):
- [ ] Complete assessment → Poll status → View results
- [ ] Click evidence link → PDF opens at page 8
- [ ] Email notification received after completion

---

## Next Epic

After completing this epic, proceed to **EPIC-07: Re-assessment & Iteration** to enable users to fix issues and re-run validation.
