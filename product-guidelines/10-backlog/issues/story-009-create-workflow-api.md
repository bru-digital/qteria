# [STORY-009] Create Workflow API Endpoint

**Type**: Story
**Epic**: EPIC-03 (Workflow Management)
**Journey Step**: Step 1 - Process Manager Creates Workflow
**Priority**: P0 (MVP Critical)
**RICE Score**: 150 (R:100 × I:3 × C:100% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When a Process Manager needs to define validation criteria for certification documents, they need to create a workflow with document buckets and validation criteria, so Project Handlers can run assessments against those rules.

**Value Delivered**: Single API endpoint that creates complete workflow structure (workflow + buckets + criteria) in one atomic transaction, enabling Process Managers to define validation workflows programmatically.

**Success Metric**: Workflow creation success rate >95%, API response time <300ms (P95).

---

## Acceptance Criteria

- [ ] `POST /v1/workflows` endpoint implemented
- [ ] Accepts workflow with nested buckets and criteria in single request
- [ ] Creates workflow, buckets, and criteria in single database transaction
- [ ] Returns created workflow with all IDs (workflow_id, bucket_ids, criteria_ids)
- [ ] Validates required fields (workflow name, bucket names, criteria text)
- [ ] Multi-tenancy enforced (workflow assigned to user's organization)
- [ ] RBAC enforced (only process_manager and admin roles)
- [ ] Rollback transaction if any part fails (all-or-nothing)
- [ ] API response includes proper error messages for validation failures
- [ ] 201 Created status on success

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI + SQLAlchemy (async)
- Database: PostgreSQL (workflows, buckets, criteria tables)
- Validation: Pydantic models

**API Endpoint** (`app/api/v1/workflows.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import require_role, get_current_user
from app.database import get_db
from app.models import Workflow, Bucket, Criteria, UserRole
from app.schemas.workflow import WorkflowCreate, WorkflowResponse

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: dict = Depends(require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create workflow with nested buckets and criteria.

    Journey Step 1: Process Manager defines validation workflow.
    """
    try:
        async with db.begin():
            # 1. Create workflow
            workflow = Workflow(
                name=workflow_data.name,
                description=workflow_data.description,
                organization_id=current_user["organization_id"],
                created_by=current_user["id"]
            )
            db.add(workflow)
            await db.flush()  # Get workflow.id

            # 2. Create buckets
            buckets = []
            for bucket_data in workflow_data.buckets:
                bucket = Bucket(
                    workflow_id=workflow.id,
                    name=bucket_data.name,
                    required=bucket_data.required,
                    order_index=bucket_data.order_index
                )
                db.add(bucket)
                buckets.append(bucket)

            await db.flush()  # Get bucket IDs

            # 3. Create criteria
            for criteria_data in workflow_data.criteria:
                criteria = Criteria(
                    workflow_id=workflow.id,
                    name=criteria_data.name,
                    description=criteria_data.description,
                    applies_to_bucket_ids=criteria_data.applies_to_bucket_ids
                )
                db.add(criteria)

            await db.flush()
            await db.commit()

            # 4. Refresh to get all relationships
            await db.refresh(workflow)

            return workflow

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )
```

**Pydantic Schemas** (`app/schemas/workflow.py`):
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class BucketCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    required: bool = True
    order_index: int = Field(..., ge=0)

class CriteriaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    applies_to_bucket_ids: List[str] = []  # ["all"] or list of bucket IDs

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    buckets: List[BucketCreate] = Field(..., min_items=1)
    criteria: List[CriteriaCreate] = Field(..., min_items=1)

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    organization_id: str
    created_by: str
    created_at: str
    buckets: List[dict]
    criteria: List[dict]
```

**Example Request**:
```json
POST /v1/workflows
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Machinery Directive 2006/42/EC",
  "description": "Validation workflow for machinery certification",
  "buckets": [
    {
      "name": "Technical Documentation",
      "required": true,
      "order_index": 0
    },
    {
      "name": "EC Declaration of Conformity",
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
      "name": "Risk assessment present",
      "description": "Technical documentation must include risk assessment",
      "applies_to_bucket_ids": []  # Will be linked after bucket IDs known
    }
  ]
}
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
    }
  ]
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-001 (Database Schema) - need workflows, buckets, criteria tables
  - STORY-007 (RBAC) - need process_manager role enforcement
  - STORY-008 (Multi-tenancy) - need organization_id filtering
- **Blocks**:
  - STORY-010 (List Workflows) - need workflows to list
  - STORY-016 (Start Assessment) - assessments reference workflows

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:
- API endpoint: 0.5 days (route, handler)
- Pydantic schemas: 0.5 days (validation models)
- Transaction logic: 0.5 days (workflow + buckets + criteria insert)
- Testing: 0.5 days (unit + integration tests)

---

## Definition of Done

- [ ] POST /v1/workflows endpoint implemented
- [ ] Accepts workflow with nested buckets and criteria
- [ ] Creates all resources in single transaction
- [ ] Returns 201 Created with complete workflow data
- [ ] Validation errors return 400 Bad Request with clear messages
- [ ] RBAC enforced (403 for project_handler)
- [ ] Multi-tenancy enforced (workflow assigned to user's org)
- [ ] Transaction rollback tested (partial failure scenarios)
- [ ] Integration tests pass (100% coverage of happy path + errors)
- [ ] API documented in Swagger UI (/docs)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests** (100% coverage required):
- [ ] Valid workflow → 201 Created with all IDs
- [ ] Missing workflow name → 400 Bad Request
- [ ] Empty buckets array → 400 Bad Request
- [ ] Duplicate bucket names → allowed (no constraint)
- [ ] Transaction rollback on bucket insert failure
- [ ] Project handler tries to create → 403 Forbidden
- [ ] User from org A creates workflow → workflow.organization_id = org_a
- [ ] Criteria with applies_to_bucket_ids=["all"] → valid

**Edge Cases**:
- [ ] Workflow with 10 buckets, 20 criteria → succeeds
- [ ] Bucket order_index not sequential → allowed
- [ ] Criteria with empty description → allowed (optional field)

---

## Risks & Mitigations

**Risk**: Transaction fails halfway (workflow created, buckets fail) → orphaned workflow
- **Mitigation**: Use database transaction with rollback, test thoroughly

**Risk**: applies_to_bucket_ids references non-existent bucket
- **Mitigation**: For MVP, allow any string (validated later when assessments run); post-MVP add foreign key constraint

**Risk**: Concurrent workflow creation causes ID collisions
- **Mitigation**: Use UUID primary keys (guaranteed unique)

---

## Notes

- This is the **first user-facing feature** that delivers journey value (Step 1)
- Keep API simple for MVP - defer workflow templates, versioning to post-MVP
- After completing this story, proceed to STORY-010 (List Workflows) for read operations
