# [STORY-022] Evidence Extraction (Page/Section Links)

**Type**: Story
**Epic**: EPIC-05 (AI Validation Engine)
**Journey Step**: Step 3 - Link Evidence to Exact Locations
**Priority**: P0 (MVP Critical - Proof of AI Findings)
**RICE Score**: 64 (R:100 × I:3 × C:85% ÷ E:4)

---

## User Value

**Job-to-Be-Done**: When AI finds issues, users need clickable links to exact document locations (page + section), so they can instantly verify findings without searching through 50+ pages.

**Value Delivered**: Evidence-based validation with exact page/section references, proving AI accuracy and building user trust.

**Success Metric**: Evidence links work 100%, users can verify AI findings in <30 seconds.

---

## Acceptance Criteria

- [ ] Extracts evidence_page and evidence_section from Claude response
- [ ] Validates page number exists in PDF (1-N)
- [ ] Validates section name matches detected sections (from STORY-020)
- [ ] Stores evidence in assessment_results table
- [ ] Generates clickable links: `/documents/{id}?page=8`
- [ ] Handles missing evidence (null values gracefully)
- [ ] Evidence validation error rate <1%

---

## Technical Approach

Parse Claude JSON, validate against parsed PDF structure, store in database:

```python
async def extract_and_validate_evidence(
    claude_response: Dict,
    parsed_document: List[Dict]
) -> Dict:
    evidence_page = claude_response.get("evidence_page")
    evidence_section = claude_response.get("evidence_section")

    # Validate page exists
    if evidence_page:
        max_page = max(p["page"] for p in parsed_document)
        if evidence_page < 1 or evidence_page > max_page:
            evidence_page = null  # Invalid page

    # Validate section exists
    if evidence_section:
        sections = [p["section"] for p in parsed_document]
        if evidence_section not in sections:
            evidence_section = null  # Fuzzy match later

    return {
        "evidence_page": evidence_page,
        "evidence_section": evidence_section,
        "evidence_link": f"/documents/{doc_id}?page={evidence_page}"
    }
```

---

## Dependencies

- **Blocked By**: STORY-020 (PDF Parsing), STORY-021 (Claude AI)
- **Blocks**: STORY-028 (Evidence Links UI)

---

## Estimation

**Effort**: 4 person-days

---

## Definition of Done

- [ ] Evidence extraction working
- [ ] Page/section validation working
- [ ] Evidence links generated
- [ ] Stored in assessment_results table
- [ ] Tests pass (100% validation accuracy)
- [ ] Code reviewed and merged

---

## Notes

- Evidence links are **key to user trust** - they prove AI found real issues
- After completing, proceed to STORY-023 (Background Jobs)
