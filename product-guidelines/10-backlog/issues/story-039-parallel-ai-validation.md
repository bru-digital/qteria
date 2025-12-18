# [STORY-039] Parallel AI Validation (Batch Criteria)

**Epic**: EPIC-09 - Performance Optimization
**Priority**: P1 (Post-MVP Polish)
**Estimated Effort**: 2 days
**Journey Step**: Cross-Cutting - Performance

---

## User Story

**As a** developer
**I want to** batch all criteria into single Claude API call
**So that** assessments complete faster (10 min → 5 min)

---

## Acceptance Criteria

- [ ] Send all criteria in one Claude API call (instead of 10 separate calls)
- [ ] Claude returns JSON array with results for all criteria
- [ ] Reduces API latency: 10 × 30s → 1 × 60s (5x faster)
- [ ] AI accuracy unchanged (batch vs. individual)
- [ ] Assessment completion time P95: <5 minutes
- [ ] AI cost per assessment reduced ~30%

---

## Technical Details

**Before (Individual Calls)**:

```python
for criteria in workflow.criteria:
    prompt = build_prompt(criteria, document_text)
    response = await claude_api.call(prompt)  # 30 seconds each
    # Total: 10 criteria × 30s = 300 seconds (5 minutes)
```

**After (Batch Call)**:

```python
# Build batch prompt with all criteria
batch_prompt = f"""
Validate the following criteria against the document:

Document text: {document_text}

Criteria to validate:
1. {criteria_1_text}
2. {criteria_2_text}
...
10. {criteria_10_text}

Return JSON array:
[
  {{"criteria_id": "crit_1", "pass": true, "confidence": "high", ...}},
  {{"criteria_id": "crit_2", "pass": false, "confidence": "high", ...}},
  ...
]
"""

response = await claude_api.call(batch_prompt)  # 60 seconds
results = json.loads(response)  # Array of 10 results

# Total: 1 × 60s = 60 seconds (1 minute)
# Speedup: 300s → 60s = 5x faster
```

**Batch Prompt Template**:

```python
def build_batch_prompt(criteria_list, document_text):
    criteria_json = [
        {
            "criteria_id": c.id,
            "criteria_text": c.text,
            "bucket_name": c.bucket.name
        }
        for c in criteria_list
    ]

    return f"""
You are validating certification documents against compliance criteria.

Document text:
{document_text}

Validate ALL of the following criteria:
{json.dumps(criteria_json, indent=2)}

Return JSON array with results for each criteria:
[
  {{
    "criteria_id": "crit_1",
    "pass": true,
    "confidence": "high",
    "reasoning": "Found required signatures on page 3",
    "evidence_page": 3,
    "evidence_section": "Signatures"
  }},
  ...
]
"""
```

---

## RICE Score

**RICE**: (80 × 2 × 0.70) ÷ 2 = **56**

---

## Definition of Done

- [ ] Batch prompt implementation working
- [ ] Claude returns JSON array for all criteria
- [ ] AI accuracy unchanged (test with real data)
- [ ] Assessment time P95 <5 minutes
- [ ] API latency reduced 5x
- [ ] AI cost per assessment reduced ~30%
- [ ] Tests pass (unit + integration)
- [ ] Code reviewed and merged

---

## Risks & Mitigations

**Risk**: Batch mode less accurate (Claude confused by multiple criteria)

- **Mitigation**: Test extensively with TÜV SÜD data; fallback to individual calls if accuracy drops

**Risk**: Claude API timeout (batch prompt too large)

- **Mitigation**: Limit batch size to 10 criteria; split if needed

---

## Notes

This optimization critical for competitive advantage: "400x faster than India team" depends on <5 min assessment time.
