# [STORY-027] Assessment Results Display UI

**Epic**: EPIC-06 - Results & Evidence Display
**Priority**: P0 (MVP Critical)
**Estimated Effort**: 2 days
**Journey Step**: Step 3 (Visual) - Display Evidence-Based Results

---

## User Story

**As a** Project Handler
**I want to** see a clear results page with pass/fail status for all criteria
**So that** I can quickly understand which criteria passed/failed and see evidence for each decision

---

## Acceptance Criteria

- [ ] Results page displays overall assessment status (e.g., "3/5 criteria passed")
- [ ] Each criteria shows pass/fail badge with color coding (green=pass, red=fail, yellow=uncertain)
- [ ] Confidence indicators displayed for each criteria (high/medium/low)
- [ ] AI reasoning/explanation shown for each criteria result
- [ ] Evidence links displayed (clickable) for each criteria
- [ ] Page loads in <2 seconds
- [ ] Mobile-responsive design
- [ ] Clear visual hierarchy (overall status → criteria list → evidence)

---

## Technical Details

**Tech Stack**:
- Frontend: Next.js 14 + React + TypeScript
- Styling: Tailwind CSS (from design system)
- State: React Query (for data fetching)
- API: `GET /v1/assessments/:id/results`

**Component Structure**:
```tsx
<AssessmentResults>
  <OverallStatusCard>
    <StatusBadge>3/5 Criteria Passed</StatusBadge>
    <CompletedTime>Completed 5 minutes ago</CompletedTime>
  </OverallStatusCard>

  <CriteriaList>
    <CriteriaCard
      pass={true}
      confidence="high"
      title="Criteria 1: Signatures present"
      reasoning="All required signatures found..."
      evidenceLinks={[{doc: "technical-file.pdf", page: 3}]}
    />
    <CriteriaCard
      pass={false}
      confidence="high"
      title="Criteria 2: Test summary missing"
      reasoning="Could not locate pass/fail summary table..."
      evidenceLinks={[{doc: "test-report.pdf", page: 8, section: "3.2"}]}
    />
    ...
  </CriteriaList>
</AssessmentResults>
```

**API Response Format**:
```json
{
  "assessment_id": "assess_123",
  "workflow_name": "Medical Device - Class II",
  "status": "completed",
  "completed_at": "2026-01-15T14:32:00Z",
  "overall_pass": false,
  "criteria_results": [
    {
      "criteria_id": "crit_1",
      "criteria_text": "All documents have valid signatures",
      "pass": true,
      "confidence": "high",
      "reasoning": "All required signatures found in technical-file.pdf",
      "evidence": [
        {"document_id": "doc_123", "document_name": "technical-file.pdf", "page": 3}
      ]
    },
    {
      "criteria_id": "crit_2",
      "criteria_text": "Test reports include pass/fail summary",
      "pass": false,
      "confidence": "high",
      "reasoning": "Could not locate pass/fail summary table in section 3.2",
      "evidence": [
        {"document_id": "doc_456", "document_name": "test-report.pdf", "page": 8, "section": "3.2"}
      ]
    }
  ]
}
```

**Color Coding**:
- Green (pass + high confidence): ✅ Strong pass
- Red (fail + high confidence): ❌ Strong fail
- Yellow (any + medium/low confidence): ⚠️ Please verify

---

## Dependencies

**Blocks**:
- STORY-031: Replace document (needs results display to show what failed)
- STORY-034: Generate PDF report (uses same data)

**Blocked By**:
- STORY-021: Claude AI integration (needs AI results)
- STORY-022: Evidence extraction (needs evidence data)
- STORY-023: Background job queue (needs completed assessment)

---

## Testing Requirements

**Unit Tests** (50% coverage):
- [ ] AssessmentResults component renders correctly
- [ ] CriteriaCard shows pass/fail badge based on status
- [ ] Confidence colors applied correctly (green/yellow/red)
- [ ] Evidence links formatted correctly

**Integration Tests**:
- [ ] GET /v1/assessments/:id/results returns expected data
- [ ] Results page fetches and displays data

**E2E Tests**:
- [ ] Navigate to results page after assessment completes
- [ ] All criteria displayed with correct pass/fail status
- [ ] Evidence links clickable

---

## Design Reference

**Figma**: See `product-guidelines/06-design-system.md` for:
- Color palette (green/red/yellow for confidence)
- Typography (headings, body text)
- Card component styles
- Badge components

**Visual Example**:
```
┌────────────────────────────────────────────┐
│ Assessment Results                         │
│ Medical Device - Class II                  │
│                                            │
│ ┌────────────────────────────────────────┐ │
│ │ 3/5 Criteria Passed                    │ │
│ │ Completed 5 minutes ago                │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ ✅ GREEN                                    │
│ Criteria 1: Signatures present             │
│ All required signatures found...           │
│ 📄 technical-file.pdf (page 3)            │
│                                            │
│ ❌ RED                                      │
│ Criteria 2: Test summary missing           │
│ Could not locate pass/fail table...        │
│ 📄 test-report.pdf (page 8, section 3.2)  │
│                                            │
│ ⚠️ YELLOW                                   │
│ Criteria 3: Risk matrix complete           │
│ AI unsure - please verify manually         │
│ 📄 risk-assessment.pdf (page 12)          │
└────────────────────────────────────────────┘
```

---

## RICE Score

**Reach**: 100 (every user sees results page)
**Impact**: 3 (high - core value delivery)
**Confidence**: 95%
**Effort**: 2 days

**RICE Score**: (100 × 3 × 0.95) ÷ 2 = **142**

---

## Definition of Done

- [ ] Results page implemented in Next.js
- [ ] Displays overall status (X/Y passed)
- [ ] Shows all criteria with pass/fail badges
- [ ] Confidence colors working (green/yellow/red)
- [ ] Evidence links displayed (clickable)
- [ ] AI reasoning shown for each criteria
- [ ] Mobile-responsive
- [ ] Unit tests pass (50% coverage)
- [ ] E2E test: View results page
- [ ] Code reviewed and merged to main
- [ ] Deployed to staging

---

## Notes

This is the **visual delivery of the aha moment** - users see proof that AI found exact issue locations. This story focuses purely on display (next story handles clicking evidence links).

**Reference**: `product-guidelines/00-user-journey.md` (Step 3)
