# [EPIC-09] Performance Optimization

**Type**: Epic
**Journey Step**: Cross-Cutting (Improves All Steps)
**Priority**: P1 (Post-MVP Polish)

---

## Epic Overview

Optimize assessment processing time from <10 minutes to <5 minutes, improve API response times, and enhance user experience with caching, parallel processing, and query optimization.

**User Value**: Faster validation means more assessments per day, better user experience, and stronger competitive advantage ("10x faster than India team" → "20x faster").

---

## Success Criteria

- [ ] Assessment completion time P95: <5 minutes (stretch goal)
- [ ] API response time P95: <200ms
- [ ] Database query time P95: <50ms
- [ ] Frontend page load: <2 seconds
- [ ] No performance regressions after optimization

---

## Stories in This Epic

### STORY-037: Query Optimization & Indexing [P1, 2 days]
Analyze slow queries (EXPLAIN ANALYZE), add indexes on common filters (organization_id, status, created_at), and optimize JOIN queries.

**RICE**: R:80 × I:2 × C:90% ÷ E:2 = **72**

### STORY-038: Workflow & Criteria Caching [P1, 2 days]
Cache frequently accessed workflows and criteria in Redis (Upstash). TTL: 1 hour. Invalidate on update.

**RICE**: R:70 × I:1 × C:80% ÷ E:2 = **28**

### STORY-039: Parallel AI Validation (Batch Criteria) [P1, 2 days]
Send all criteria for single document in one Claude API call (batch mode) instead of 10 separate calls. Reduces API latency from 10 × 30s → 1 × 60s.

**RICE**: R:80 × I:2 × C:70% ÷ E:2 = **56**

---

## Total Estimated Effort

**6 person-days** (1.5 weeks for solo founder)

**Breakdown**:
- Backend: 5 days (query optimization, caching, batch AI)
- Testing: 1 day (performance benchmarks, regression tests)

---

## Dependencies

**Blocks**: Nothing (optional optimization)

**Blocked By**:
- EPIC-05: AI Validation (need working engine to optimize)
- STORY-027: Results display (need baseline performance to measure improvement)

---

## Technical Approach

**Tech Stack**:
- Caching: Redis (Upstash)
- Query Optimization: PostgreSQL indexes, EXPLAIN ANALYZE
- Batch AI: Claude API (single prompt with multiple criteria)

**Query Optimization** (STORY-037):
- Add indexes:
  ```sql
  CREATE INDEX idx_assessments_org_status ON assessments(organization_id, status);
  CREATE INDEX idx_workflows_org_active ON workflows(organization_id, is_active) WHERE is_active = TRUE;
  CREATE INDEX idx_assessment_results_assessment ON assessment_results(assessment_id, pass);
  ```
- Optimize JOIN queries (workflows + buckets + criteria):
  ```sql
  -- Before: 3 queries
  SELECT * FROM workflows WHERE id = X;
  SELECT * FROM buckets WHERE workflow_id = X;
  SELECT * FROM criteria WHERE workflow_id = X;

  -- After: 1 query with JOIN
  SELECT w.*, b.*, c.*
  FROM workflows w
  LEFT JOIN buckets b ON b.workflow_id = w.id
  LEFT JOIN criteria c ON c.workflow_id = w.id
  WHERE w.id = X;
  ```

**Workflow Caching** (STORY-038):
- Cache workflows in Redis with TTL 1 hour
- Key: `workflow:{workflow_id}`
- Value: JSON (workflow + buckets + criteria)
- Invalidate on UPDATE/DELETE
- Reduces database queries from 3 → 0 for cached workflows

**Batch AI Validation** (STORY-039):
- Instead of 10 API calls (one per criteria):
  ```python
  for criteria in workflow.criteria:
      response = claude_api.call(prompt_for_criteria(criteria))
  ```
- Batch all criteria in single prompt:
  ```python
  prompt = build_batch_prompt(workflow.criteria, document_text)
  response = claude_api.call(prompt)  # Returns JSON array
  ```
- Reduces API latency: 10 × 30s = 300s → 1 × 60s = 60s (5x faster)

**Reference**: `product-guidelines/04-architecture.md` (scaling strategy)

---

## Success Metrics

**Performance Benchmarks**:
- Assessment time P95: <5 minutes (from <10 minutes)
- API response P95: <200ms (from <500ms)
- Database query P95: <50ms (from <100ms)
- Cache hit rate: >80% (workflows fetched from Redis)

**Cost Optimization**:
- Claude API cost per assessment: <$0.15 (from $0.21 with batch mode)

---

## Definition of Done

- [ ] Database indexes added and query performance improved
- [ ] Workflow caching in Redis working (TTL 1 hour)
- [ ] Batch AI validation reduces API calls 10 → 1
- [ ] Performance benchmarks met (<5 min P95, <200ms API)
- [ ] No regressions (old features still work)
- [ ] Load testing confirms improvements
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: Caching introduces stale data (workflow updated but cache shows old version)
- **Mitigation**: Invalidate cache on UPDATE/DELETE, short TTL (1 hour)

**Risk**: Batch AI validation less accurate (Claude confused by multiple criteria)
- **Mitigation**: Test accuracy with batch prompts, fallback to individual calls if needed

**Risk**: Database indexes slow down writes
- **Mitigation**: Indexes primarily on read-heavy tables (workflows, assessments), not write-heavy (audit_logs)

---

## Testing Requirements

**Performance Tests** (benchmarks):
- [ ] Assessment time: <5 minutes P95 (before: <10 minutes)
- [ ] API response: <200ms P95 (before: <500ms)
- [ ] Database query: <50ms P95 (before: <100ms)
- [ ] Cache hit rate: >80%

**Load Tests** (scalability):
- [ ] 10 concurrent assessments: No failures, <10 min each
- [ ] 100 API requests/min: <200ms P95, no errors

**Regression Tests**:
- [ ] All existing E2E tests pass (no regressions)
- [ ] AI accuracy unchanged (batch mode vs. individual)

---

## Next Epic

After completing this epic, proceed to **EPIC-10: Testing & Quality Assurance** to ensure comprehensive test coverage and CI/CD automation.
