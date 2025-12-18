# [EPIC-03] Workflow Management

**Type**: Epic
**Journey Step**: Step 1 - Process Manager Creates Workflow
**Priority**: P0 (MVP Critical)

---

## Epic Overview

Enable Process Managers to create, edit, and manage validation workflows. A workflow defines document buckets (categories like "Technical Documentation", "Test Reports") and criteria (validation rules like "All documents must be signed"). This is **Journey Step 1** - the foundation that enables all assessments.

**User Value**: Process Managers set up workflows in <30 minutes, enabling Project Handlers to run assessments with clear validation criteria.

---

## Success Criteria

- [ ] Process Manager can create new workflow with name and description
- [ ] Can add/edit/delete document buckets (mark as required/optional)
- [ ] Can add/edit/delete criteria (define validation rules per bucket)
- [ ] Can list all workflows for organization
- [ ] Can view workflow details (buckets + criteria)
- [ ] Can share workflow with team (other users in org)
- [ ] Workflow creation takes <30 minutes (UX goal)

---

## Stories in This Epic

### STORY-009: Create Workflow API Endpoint [P0, 2 days]

Implement `POST /v1/workflows` endpoint that creates workflow with nested buckets and criteria in single transaction. Returns created workflow with IDs.

**RICE**: R:100 × I:3 × C:100% ÷ E:2 = **150**

### STORY-010: List Workflows API [P0, 1 day]

Implement `GET /v1/workflows` endpoint with pagination, filtering by organization, and sorting by created_at. Returns list of workflows (without nested data).

**RICE**: R:100 × I:2 × C:100% ÷ E:1 = **200**

### STORY-011: Get Workflow Details API [P0, 1 day]

Implement `GET /v1/workflows/:id` endpoint that returns workflow with nested buckets and criteria. Includes workflow metadata (creator, created_at).

**RICE**: R:100 × I:2 × C:100% ÷ E:1 = **200**

### STORY-012: Update Workflow API [P0, 2 days]

Implement `PUT /v1/workflows/:id` endpoint that updates workflow name/description and nested buckets/criteria. Handles add/edit/delete of nested resources.

**RICE**: R:80 × I:2 × C:80% ÷ E:2 = **64**

### STORY-013: Delete Workflow API [P1, 1 day]

Implement `DELETE /v1/workflows/:id` endpoint with soft delete (mark as archived). Prevents deletion if workflow has assessments (409 conflict).

**RICE**: R:50 × I:1 × C:80% ÷ E:1 = **40**

### STORY-014: Workflow Builder UI [P0, 3 days]

Create React form for workflow creation with dynamic bucket/criteria fields. Users can add/remove buckets, add/remove criteria, mark buckets as required, and assign criteria to specific buckets.

**RICE**: R:100 × I:3 × C:90% ÷ E:3 = **90**

---

## Total Estimated Effort

**10 person-days** (2 weeks for solo founder)

**Breakdown**:

- Backend: 5 days (API endpoints, validation, transactions)
- Frontend: 3 days (workflow builder UI)
- Testing: 2 days (unit + integration + E2E)

---

## Dependencies

**Blocks**:

- STORY-016: Start Assessment (needs workflow to reference)
- EPIC-04: Document Processing (assessments use workflow structure)
- EPIC-05: AI Validation (criteria from workflow)

**Blocked By**:

- STORY-001: Database schema (workflows, buckets, criteria tables)
- STORY-005: Authentication (Process Manager role required)

---

## Technical Approach

**Tech Stack**:

- Backend: FastAPI + SQLAlchemy (CRUD operations)
- Database: PostgreSQL (workflows, buckets, criteria tables with foreign keys)
- Frontend: Next.js + React Hook Form (workflow builder)
- Validation: Pydantic (backend), Zod (frontend)

**API Design**:

```json
POST /v1/workflows
{
  "name": "Medical Device - Class II",
  "description": "Validation workflow for medical device certification",
  "buckets": [
    {
      "name": "Technical Documentation",
      "required": true,
      "order_index": 0
    },
    {
      "name": "Test Reports",
      "required": true,
      "order_index": 1
    }
  ],
  "criteria": [
    {
      "name": "All documents must be signed",
      "description": "Check for valid signatures on every document",
      "applies_to_bucket_ids": ["all"]
    },
    {
      "name": "Test report must include pass/fail summary",
      "description": "Verify test report has clear pass/fail section",
      "applies_to_bucket_ids": ["bucket_2"]
    }
  ]
}
```

**Database Transaction**:

1. INSERT workflow
2. INSERT N buckets (linked to workflow_id)
3. INSERT M criteria (linked to workflow_id)
4. COMMIT transaction (all-or-nothing)

**Reference**: `product-guidelines/00-user-journey.md` (Step 1), `product-guidelines/08-api-contracts.md` (workflows endpoints)

---

## Success Metrics

**User Experience**:

- Time to create first workflow: <30 minutes (target from strategy)
- Workflow creation success rate: >95% (no errors)

**Engagement**:

- New workflows created per month: 5-10 (TÜV SÜD pilot target)
- Average criteria per workflow: 3-5 (complexity indicator)

**Technical**:

- API response time (P95): <200ms for list, <300ms for create
- Workflow deletion prevented if assessments exist: 100% (data integrity)

---

## Definition of Done

- [ ] All API endpoints implemented and tested
- [ ] Workflow builder UI working (add/edit/delete buckets + criteria)
- [ ] Validation errors shown clearly (required fields, max lengths)
- [ ] Multi-tenancy enforced (users only see their org's workflows)
- [ ] RBAC enforced (only process_manager can create/edit)
- [ ] Database transactions work (rollback on error)
- [ ] E2E test: Create workflow → List workflows → View details
- [ ] Code coverage >80% for backend, >50% for frontend
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: Workflow builder UI too complex (>30 min to create)

- **Mitigation**: Usability testing with TÜV SÜD, simplify UI, provide examples

**Risk**: Nested create/update logic has bugs (orphaned buckets/criteria)

- **Mitigation**: Use database transactions, test cascade deletes thoroughly

**Risk**: Users create workflows with invalid criteria (AI can't validate)

- **Mitigation**: Provide clear guidance, example criteria, validate format

---

## Testing Requirements

**Unit Tests** (85% coverage target):

- [ ] Workflow validation logic (name required, max length)
- [ ] Bucket validation (required flag, order_index)
- [ ] Criteria validation (applies_to_bucket_ids exists)

**Integration Tests** (80% coverage target):

- [ ] POST /v1/workflows creates workflow + buckets + criteria
- [ ] GET /v1/workflows returns paginated list
- [ ] GET /v1/workflows/:id returns workflow with nested data
- [ ] PUT /v1/workflows/:id updates workflow
- [ ] DELETE /v1/workflows/:id soft deletes if no assessments
- [ ] DELETE /v1/workflows/:id returns 409 if assessments exist
- [ ] Multi-tenancy enforced (org A cannot see org B workflows)
- [ ] RBAC enforced (project_handler cannot create workflow)

**E2E Tests** (critical flow):

- [ ] Complete workflow creation flow (Journey Step 1)
- [ ] Process Manager creates workflow → Project Handler sees it

---

## Next Epic

After completing this epic, proceed to **EPIC-04: Document Processing** to enable Project Handlers to upload documents into workflow buckets.
