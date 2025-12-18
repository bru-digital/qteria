# [STORY-012] Update Workflow API

**Type**: Story
**Epic**: EPIC-03 (Workflow Management)
**Journey Step**: Step 1 - Edit Workflow
**Priority**: P0 (MVP Critical)
**RICE Score**: 64 (R:80 × I:2 × C:80% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When Process Managers need to refine validation workflows (add criteria, rename buckets, fix mistakes), they need to update existing workflows, so they can continuously improve validation rules based on feedback.

**Value Delivered**: API endpoint that updates workflow metadata and nested buckets/criteria, enabling iterative improvement of validation workflows.

**Success Metric**: Workflow update success rate >95%, supports add/edit/delete of nested resources.

---

## Acceptance Criteria

- [ ] `PUT /v1/workflows/:id` endpoint implemented
- [ ] Updates workflow name and description
- [ ] Supports adding new buckets (with new order_index)
- [ ] Supports editing existing buckets (name, required, order_index)
- [ ] Supports deleting buckets (removes bucket and updates criteria)
- [ ] Supports adding new criteria
- [ ] Supports editing existing criteria
- [ ] Supports deleting criteria
- [ ] All changes in single database transaction (rollback on error)
- [ ] Returns updated workflow with new IDs
- [ ] RBAC enforced (only process_manager and admin)
- [ ] Multi-tenancy enforced (can only update own org's workflows)
- [ ] 404 if workflow not found or belongs to different org
- [ ] 409 if trying to delete bucket with documents (post-MVP constraint)

---

## Technical Approach

**Tech Stack Components Used**:

- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL (workflows, buckets, criteria tables)

**API Endpoint** (`app/api/v1/workflows.py`):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import require_role, get_current_user
from app.database import get_db
from app.models import Workflow, Bucket, Criteria, UserRole
from app.schemas.workflow import WorkflowUpdate, WorkflowDetailResponse

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

@router.put("/{workflow_id}", response_model=WorkflowDetailResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    current_user: dict = Depends(require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update workflow with nested buckets and criteria.

    Journey Step 1: Process Manager refines validation workflow.
    """
    org_id = current_user["organization_id"]

    # Get existing workflow
    workflow = await Workflow.get_by_id(db, org_id, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    try:
        async with db.begin():
            # 1. Update workflow metadata
            workflow.name = workflow_data.name
            workflow.description = workflow_data.description
            workflow.updated_at = datetime.utcnow()

            # 2. Update buckets (delete, update, create)
            existing_bucket_ids = {b.id for b in workflow.buckets}
            incoming_bucket_ids = {
                b.id for b in workflow_data.buckets if b.id
            }

            # Delete removed buckets
            for bucket_id in existing_bucket_ids - incoming_bucket_ids:
                bucket = await db.get(Bucket, bucket_id)
                await db.delete(bucket)

            # Update/create buckets
            for bucket_data in workflow_data.buckets:
                if bucket_data.id:
                    # Update existing
                    bucket = await db.get(Bucket, bucket_data.id)
                    bucket.name = bucket_data.name
                    bucket.required = bucket_data.required
                    bucket.order_index = bucket_data.order_index
                else:
                    # Create new
                    bucket = Bucket(
                        workflow_id=workflow.id,
                        name=bucket_data.name,
                        required=bucket_data.required,
                        order_index=bucket_data.order_index
                    )
                    db.add(bucket)

            # 3. Update criteria (similar logic)
            existing_criteria_ids = {c.id for c in workflow.criteria}
            incoming_criteria_ids = {
                c.id for c in workflow_data.criteria if c.id
            }

            # Delete removed criteria
            for criteria_id in existing_criteria_ids - incoming_criteria_ids:
                criteria = await db.get(Criteria, criteria_id)
                await db.delete(criteria)

            # Update/create criteria
            for criteria_data in workflow_data.criteria:
                if criteria_data.id:
                    # Update existing
                    criteria = await db.get(Criteria, criteria_data.id)
                    criteria.name = criteria_data.name
                    criteria.description = criteria_data.description
                    criteria.applies_to_bucket_ids = criteria_data.applies_to_bucket_ids
                else:
                    # Create new
                    criteria = Criteria(
                        workflow_id=workflow.id,
                        name=criteria_data.name,
                        description=criteria_data.description,
                        applies_to_bucket_ids=criteria_data.applies_to_bucket_ids
                    )
                    db.add(criteria)

            await db.flush()
            await db.commit()
            await db.refresh(workflow)

            return workflow

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )
```

**Pydantic Schema** (`app/schemas/workflow.py`):

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class BucketUpdate(BaseModel):
    id: Optional[str] = None  # None for new buckets
    name: str = Field(..., min_length=1, max_length=255)
    required: bool = True
    order_index: int = Field(..., ge=0)

class CriteriaUpdate(BaseModel):
    id: Optional[str] = None  # None for new criteria
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    applies_to_bucket_ids: List[str] = []

class WorkflowUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    buckets: List[BucketUpdate] = Field(..., min_items=1)
    criteria: List[CriteriaUpdate] = Field(..., min_items=1)
```

**Example Request** (rename workflow, add bucket, delete criteria):

```json
PUT /v1/workflows/wf_abc123
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Machinery Directive 2006/42/EC (Updated)",
  "description": "Updated validation workflow",
  "buckets": [
    {
      "id": "bucket_xyz",
      "name": "Technical Documentation (Renamed)",
      "required": true,
      "order_index": 0
    },
    {
      "id": "bucket_abc",
      "name": "EC Declaration of Conformity",
      "required": true,
      "order_index": 1
    },
    {
      "name": "Test Reports",
      "required": false,
      "order_index": 2
    }
  ],
  "criteria": [
    {
      "id": "criteria_123",
      "name": "All documents must be signed",
      "description": "Updated description",
      "applies_to_bucket_ids": ["all"]
    }
  ]
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-009 (Create Workflow) - need workflows to update
  - STORY-011 (Get Workflow Details) - edit UI needs current data
- **Blocks**:
  - STORY-014 (Workflow Builder UI) - UI needs update endpoint

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:

- API endpoint: 1 day (complex update logic for nested resources)
- Schema: 0.5 days (update models with optional IDs)
- Testing: 0.5 days (add/edit/delete scenarios)

---

## Definition of Done

- [ ] PUT /v1/workflows/:id endpoint implemented
- [ ] Updates workflow metadata (name, description)
- [ ] Adds new buckets (id=null)
- [ ] Updates existing buckets (id provided)
- [ ] Deletes removed buckets (not in request)
- [ ] Same logic for criteria (add/update/delete)
- [ ] Transaction rollback on error
- [ ] RBAC enforced (403 for project_handler)
- [ ] Multi-tenancy enforced (404 for other org's workflow)
- [ ] Integration tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:

- [ ] Update workflow name → name changed
- [ ] Add new bucket → bucket created with new ID
- [ ] Update existing bucket → bucket modified
- [ ] Delete bucket → bucket removed
- [ ] Add new criteria → criteria created
- [ ] Update existing criteria → criteria modified
- [ ] Delete criteria → criteria removed
- [ ] Transaction rollback if bucket insert fails
- [ ] Project handler tries to update → 403 Forbidden
- [ ] User from org A tries to update org B workflow → 404 Not Found

---

## Risks & Mitigations

**Risk**: Deleting bucket breaks existing assessments (references invalid bucket_id)

- **Mitigation**: For MVP, allow deletion (assessments preserve bucket snapshot); post-MVP add validation

**Risk**: Complex update logic has bugs (orphaned buckets/criteria)

- **Mitigation**: Use database transaction, test thoroughly, validate foreign keys

---

## Notes

- After completing this story, proceed to STORY-013 (Delete Workflow)
