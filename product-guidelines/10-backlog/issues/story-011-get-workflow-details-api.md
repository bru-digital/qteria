# [STORY-011] Get Workflow Details API

**Type**: Story
**Epic**: EPIC-03 (Workflow Management)
**Journey Step**: Step 1 - View Workflow Details
**Priority**: P0 (MVP Critical)
**RICE Score**: 200 (R:100 × I:2 × C:100% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When users need to see complete workflow details (including all buckets and criteria), they need a single API endpoint that returns the full workflow structure, so they can understand validation requirements before starting an assessment.

**Value Delivered**: Complete workflow details with nested buckets and criteria, enabling users to view and understand validation rules.

**Success Metric**: API response time <300ms (P95), includes all nested data in single request.

---

## Acceptance Criteria

- [ ] `GET /v1/workflows/:id` endpoint implemented
- [ ] Returns workflow with all metadata (name, description, created_at, created_by)
- [ ] Includes nested buckets array (sorted by order_index)
- [ ] Includes nested criteria array
- [ ] Returns 404 Not Found if workflow doesn't exist or belongs to different org
- [ ] Multi-tenancy enforced (only returns workflow if user's org matches)
- [ ] Response includes bucket and criteria counts
- [ ] Single database query with eager loading (no N+1 queries)

---

## Technical Approach

**Tech Stack Components Used**:

- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL (workflows, buckets, criteria tables with JOINs)

**API Endpoint** (`app/api/v1/workflows.py`):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Workflow
from app.schemas.workflow import WorkflowDetailResponse

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get workflow details with nested buckets and criteria.

    Journey Step 1: Users view complete workflow structure before assessment.
    """
    org_id = current_user["organization_id"]

    # Eager load buckets and criteria (single query)
    query = (
        select(Workflow)
        .options(
            selectinload(Workflow.buckets),
            selectinload(Workflow.criteria)
        )
        .where(Workflow.id == workflow_id)
        .where(Workflow.organization_id == org_id)
    )

    result = await db.execute(query)
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "organization_id": workflow.organization_id,
        "created_by": workflow.created_by,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "buckets": sorted(
            [
                {
                    "id": b.id,
                    "name": b.name,
                    "required": b.required,
                    "order_index": b.order_index
                }
                for b in workflow.buckets
            ],
            key=lambda x: x["order_index"]
        ),
        "criteria": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "applies_to_bucket_ids": c.applies_to_bucket_ids
            }
            for c in workflow.criteria
        ],
        "stats": {
            "bucket_count": len(workflow.buckets),
            "criteria_count": len(workflow.criteria)
        }
    }
```

**Pydantic Schema** (`app/schemas/workflow.py`):

```python
from pydantic import BaseModel
from typing import List, Optional

class BucketDetail(BaseModel):
    id: str
    name: str
    required: bool
    order_index: int

class CriteriaDetail(BaseModel):
    id: str
    name: str
    description: Optional[str]
    applies_to_bucket_ids: List[str]

class WorkflowStats(BaseModel):
    bucket_count: int
    criteria_count: int

class WorkflowDetailResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    organization_id: str
    created_by: str
    created_at: str
    updated_at: str
    buckets: List[BucketDetail]
    criteria: List[CriteriaDetail]
    stats: WorkflowStats
```

**Example Request**:

```
GET /v1/workflows/wf_abc123
Authorization: Bearer <jwt_token>
```

**Example Response**:

```json
{
  "id": "wf_abc123",
  "name": "Machinery Directive 2006/42/EC",
  "description": "Validation workflow for machinery certification",
  "organization_id": "org_tuv_sud",
  "created_by": "user_pm_123",
  "created_at": "2025-11-17T10:30:00Z",
  "updated_at": "2025-11-17T10:30:00Z",
  "buckets": [
    {
      "id": "bucket_xyz",
      "name": "Technical Documentation",
      "required": true,
      "order_index": 0
    },
    {
      "id": "bucket_abc",
      "name": "EC Declaration of Conformity",
      "required": true,
      "order_index": 1
    }
  ],
  "criteria": [
    {
      "id": "criteria_123",
      "name": "All documents must be signed",
      "description": "Check for valid signatures on every document",
      "applies_to_bucket_ids": ["all"]
    },
    {
      "id": "criteria_456",
      "name": "Risk assessment present",
      "description": "Technical documentation must include risk assessment",
      "applies_to_bucket_ids": ["bucket_xyz"]
    }
  ],
  "stats": {
    "bucket_count": 2,
    "criteria_count": 2
  }
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-009 (Create Workflow) - need workflows to retrieve
- **Blocks**:
  - STORY-012 (Update Workflow) - edit UI needs details endpoint
  - STORY-016 (Start Assessment) - assessments need workflow details

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:

- API endpoint: 0.5 days (query with eager loading)
- Schema: 0.25 days (response model)
- Testing: 0.25 days (404 cases, multi-tenancy)

---

## Definition of Done

- [ ] GET /v1/workflows/:id endpoint implemented
- [ ] Returns workflow with nested buckets and criteria
- [ ] Buckets sorted by order_index
- [ ] 404 returned if workflow not found
- [ ] 404 returned if workflow belongs to different org (multi-tenancy)
- [ ] Single query with eager loading (no N+1)
- [ ] Integration tests pass (100% coverage)
- [ ] API documented in Swagger UI
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:

- [ ] Valid workflow_id → 200 OK with full details
- [ ] Invalid workflow_id → 404 Not Found
- [ ] Workflow from different org → 404 Not Found (multi-tenancy)
- [ ] Workflow with 0 buckets → returns empty array
- [ ] Workflow with 5 buckets → buckets sorted by order_index
- [ ] Workflow with 10 criteria → all criteria returned

**Performance Tests**:

- [ ] Query uses eager loading (check SQL logs for 1 query, not N+1)
- [ ] Response time <300ms for workflow with 10 buckets + 20 criteria

---

## Risks & Mitigations

**Risk**: N+1 query problem (workflow query + N bucket queries + M criteria queries)

- **Mitigation**: Use SQLAlchemy selectinload for eager loading, verify with SQL logging

**Risk**: Large workflows (50+ buckets) cause slow response

- **Mitigation**: Monitor response time, add pagination for buckets/criteria if needed (post-MVP)

---

## Notes

- Return 404 (not 403) for other org's workflows to avoid leaking existence
- After completing this story, proceed to STORY-012 (Update Workflow)
