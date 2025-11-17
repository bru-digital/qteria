# [STORY-033] Partial Re-Assessment (Smart Caching)

**Epic**: EPIC-07 - Re-assessment & Iteration
**Priority**: P2 (Nice-to-Have, Defer to Year 2)
**Estimated Effort**: 1 day
**Journey Step**: Step 4 - Optimize Re-Run

---

## User Story

**As a** Project Handler
**I want** re-assessments to be faster by only checking updated documents
**So that** I can iterate quickly without waiting 10 minutes each time

---

## Acceptance Criteria

- [ ] Only re-validate criteria for replaced bucket
- [ ] Skip criteria for unchanged documents
- [ ] Cache previous results for unchanged criteria
- [ ] Re-assessment time <5 minutes (vs. 10 min initial)
- [ ] AI cost reduced by 50%

---

## Technical Details

**Smart Caching Logic**:
```python
# Only validate criteria that apply to replaced bucket
replaced_bucket_ids = get_replaced_buckets(original_id, new_id)

for criteria in workflow.criteria:
    if criteria.bucket_id in replaced_bucket_ids:
        # Re-validate with AI
        result = await validate_criteria(criteria, documents)
    else:
        # Reuse cached result
        result = get_cached_result(original_id, criteria.id)

    save_result(new_assessment_id, criteria.id, result)
```

---

## RICE Score

**RICE**: (60 × 1 × 0.70) ÷ 1 = **42**

---

## Definition of Done

- [ ] Partial validation logic working
- [ ] Caches unchanged criteria results
- [ ] Re-assessment time <5 min
- [ ] AI cost reduced 50%
- [ ] Tests pass
- [ ] Code reviewed and merged

---

## Notes

This is a P2 optimization - defer to Year 2 unless MVP shows re-assessment is too slow.
