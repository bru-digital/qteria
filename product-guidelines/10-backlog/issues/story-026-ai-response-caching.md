# [STORY-026] AI Response Caching

**Type**: Story
**Epic**: EPIC-05 (AI Validation Engine)
**Journey Step**: Step 3 - Cache Parsed PDFs
**Priority**: P1 (Important for Performance)
**RICE Score**: 48 (R:60 × I:1 × C:80% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When the same document is uploaded multiple times, users want to skip re-parsing to save time (10-20 seconds), so assessments start faster.

**Value Delivered**: Faster assessment start time through cached PDF parsing.

**Success Metric**: Cache hit rate >50%, parsing time saved 10-20 seconds per cached document.

---

## Acceptance Criteria

- [ ] Parsed PDF text cached in PostgreSQL (STORY-020 already implements this)
- [ ] Cache key: document content hash (SHA-256)
- [ ] Cache hit skips PDF parsing
- [ ] Cache invalidation on document update
- [ ] Cache size monitoring (prevent unbounded growth)

---

## Technical Approach

Implemented in STORY-020 via `parsed_documents` table. This story just ensures caching is tested and monitored.

---

## Dependencies

- **Blocked By**: STORY-020 (PDF Parsing) - caching already implemented there
- **Blocks**: Nothing (performance optimization)

---

## Estimation

**Effort**: 1 person-day

---

## Definition of Done

- [ ] Caching verified working
- [ ] Cache hit rate measured
- [ ] Tests pass (cache hit/miss scenarios)
- [ ] Code reviewed and merged

---

## Notes

- P1 priority - minor performance optimization
- After completing, EPIC-05 is DONE!
