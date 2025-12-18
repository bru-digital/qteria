# [STORY-037] Query Optimization & Indexing

**Epic**: EPIC-09 - Performance Optimization
**Priority**: P1 (Post-MVP Polish)
**Estimated Effort**: 2 days
**Journey Step**: Cross-Cutting - Performance

---

## User Story

**As a** developer
**I want to** optimize database queries with indexes
**So that** API responses are fast (<200ms P95)

---

## Acceptance Criteria

- [ ] Analyze slow queries with EXPLAIN ANALYZE
- [ ] Add indexes on common filters (organization_id, status, created_at)
- [ ] Optimize JOIN queries (workflows + buckets + criteria)
- [ ] API response time P95: <200ms (from <500ms)
- [ ] Database query time P95: <50ms (from <100ms)
- [ ] No write performance regression

---

## Technical Details

**Indexes to Add**:

```sql
-- Assessments by org and status
CREATE INDEX idx_assessments_org_status
ON assessments(organization_id, status);

-- Active workflows by org
CREATE INDEX idx_workflows_org_active
ON workflows(organization_id, is_active)
WHERE is_active = TRUE;

-- Assessment results
CREATE INDEX idx_assessment_results_assessment
ON assessment_results(assessment_id, pass);

-- Documents by org and bucket
CREATE INDEX idx_documents_org_bucket
ON assessment_documents(organization_id, bucket_id);
```

**Query Optimization**:

```sql
-- Before: 3 separate queries (N+1 problem)
SELECT * FROM workflows WHERE id = X;
SELECT * FROM buckets WHERE workflow_id = X;
SELECT * FROM criteria WHERE workflow_id = X;

-- After: Single JOIN query
SELECT w.*, b.*, c.*
FROM workflows w
LEFT JOIN buckets b ON b.workflow_id = w.id
LEFT JOIN criteria c ON c.workflow_id = w.id
WHERE w.id = X;
```

---

## RICE Score

**RICE**: (80 × 2 × 0.90) ÷ 2 = **72**

---

## Definition of Done

- [ ] Slow queries analyzed (EXPLAIN ANALYZE)
- [ ] Indexes added to production
- [ ] JOIN queries optimized
- [ ] API response P95 <200ms
- [ ] Database query P95 <50ms
- [ ] Load tests confirm improvements
- [ ] No write performance regression
- [ ] Code reviewed and merged
