# [STORY-010] List Workflows API

**Type**: Story
**Epic**: EPIC-03 (Workflow Management)
**Journey Step**: Step 1 - Process Manager Views Workflows
**Priority**: P0 (MVP Critical)
**RICE Score**: 200 (R:100 × I:2 × C:100% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When users need to see available validation workflows, they need a paginated list of workflows for their organization, so they can select which workflow to use for assessments or edit existing workflows.

**Value Delivered**: Fast, paginated API that lists all workflows for organization, enabling users to discover and select workflows.

**Success Metric**: API response time <200ms (P95), supports 100+ workflows per organization.

---

## Acceptance Criteria

- [ ] `GET /v1/workflows` endpoint implemented
- [ ] Returns paginated list of workflows (default 20 per page)
- [ ] Includes workflow metadata (id, name, description, created_at, created_by)
- [ ] Does NOT include nested buckets/criteria (use GET /:id for details)
- [ ] Supports pagination (page, per_page query params)
- [ ] Supports sorting (sort_by=created_at, order=desc)
- [ ] Multi-tenancy enforced (only returns user's org workflows)
- [ ] Returns empty array if no workflows exist
- [ ] Includes pagination metadata (total_count, page, per_page, total_pages)

---

## Technical Approach

**Tech Stack Components Used**:

- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL (workflows table)

**API Endpoint** (`app/api/v1/workflows.py`):

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Workflow
from app.schemas.workflow import WorkflowListResponse

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|name)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List workflows for organization with pagination.

    Journey Step 1: Process Manager views available workflows.
    """
    org_id = current_user["organization_id"]

    # Count total workflows
    count_query = select(func.count(Workflow.id)).where(
        Workflow.organization_id == org_id
    )
    total_count = await db.scalar(count_query)

    # Get paginated workflows
    offset = (page - 1) * per_page
    query = select(Workflow).where(
        Workflow.organization_id == org_id
    )

    # Apply sorting
    if order == "desc":
        query = query.order_by(getattr(Workflow, sort_by).desc())
    else:
        query = query.order_by(getattr(Workflow, sort_by).asc())

    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    workflows = result.scalars().all()

    return {
        "workflows": [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "created_at": w.created_at,
                "created_by": w.created_by
            }
            for w in workflows
        ],
        "pagination": {
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page
        }
    }
```

**Pydantic Schema** (`app/schemas/workflow.py`):

```python
from pydantic import BaseModel
from typing import List

class WorkflowListItem(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: str
    created_by: str

class PaginationMeta(BaseModel):
    total_count: int
    page: int
    per_page: int
    total_pages: int

class WorkflowListResponse(BaseModel):
    workflows: List[WorkflowListItem]
    pagination: PaginationMeta
```

**Example Request**:

```
GET /v1/workflows?page=1&per_page=20&sort_by=created_at&order=desc
Authorization: Bearer <jwt_token>
```

**Example Response**:

```json
{
  "workflows": [
    {
      "id": "wf_abc123",
      "name": "Machinery Directive 2006/42/EC",
      "description": "Validation workflow for machinery certification",
      "created_at": "2025-11-17T10:30:00Z",
      "created_by": "user_pm_123"
    },
    {
      "id": "wf_xyz789",
      "name": "Medical Device Regulation",
      "description": null,
      "created_at": "2025-11-16T14:20:00Z",
      "created_by": "user_pm_456"
    }
  ],
  "pagination": {
    "total_count": 42,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-009 (Create Workflow) - need workflows to list
- **Blocks**:
  - STORY-014 (Workflow Builder UI) - UI needs list endpoint

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:

- API endpoint: 0.5 days (query, pagination logic)
- Schema: 0.25 days (response model)
- Testing: 0.25 days (pagination, sorting tests)

---

## Definition of Done

- [ ] GET /v1/workflows endpoint implemented
- [ ] Returns paginated workflows
- [ ] Pagination works (page, per_page params)
- [ ] Sorting works (sort_by, order params)
- [ ] Multi-tenancy enforced (only org's workflows)
- [ ] Empty array returned if no workflows
- [ ] Pagination metadata accurate (total_count, total_pages)
- [ ] Integration tests pass (100% coverage)
- [ ] API documented in Swagger UI
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:

- [ ] No workflows → returns empty array with total_count=0
- [ ] 1 workflow → returns array with 1 item
- [ ] 25 workflows, page=1, per_page=20 → returns first 20
- [ ] 25 workflows, page=2, per_page=20 → returns last 5
- [ ] sort_by=name, order=asc → workflows sorted alphabetically
- [ ] sort_by=created_at, order=desc → newest first
- [ ] User from org A → only sees org A workflows (not org B)
- [ ] Invalid page=0 → 400 Bad Request
- [ ] Invalid per_page=1000 → 400 Bad Request (max 100)

---

## Risks & Mitigations

**Risk**: Query slow with 1000+ workflows

- **Mitigation**: Index on organization_id + created_at, limit per_page to 100

**Risk**: Pagination metadata incorrect (total_pages calculation)

- **Mitigation**: Test edge cases (0 workflows, 1 workflow, exact multiple of per_page)

---

## Notes

- Keep response lean - no nested buckets/criteria (use GET /:id for details)
- After completing this story, proceed to STORY-011 (Get Workflow Details)
