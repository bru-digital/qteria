# [STORY-013] Delete Workflow API

**Type**: Story
**Epic**: EPIC-03 (Workflow Management)
**Journey Step**: Step 1 - Remove Workflow
**Priority**: P1 (Important, Not MVP Blocker)
**RICE Score**: 40 (R:50 × I:1 × C:80% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When Process Managers create incorrect or duplicate workflows, they need to delete them, so the workflow list stays clean and doesn't confuse Project Handlers.

**Value Delivered**: Safe workflow deletion with soft delete (archive) to preserve data integrity, preventing accidental deletion of workflows with assessments.

**Success Metric**: Workflow deletion success rate 100% (no data corruption), prevents deletion if assessments exist.

---

## Acceptance Criteria

- [ ] `DELETE /v1/workflows/:id` endpoint implemented
- [ ] Soft delete (mark as archived, don't physically delete)
- [ ] Returns 409 Conflict if workflow has assessments (can't delete)
- [ ] Returns 204 No Content on successful deletion
- [ ] RBAC enforced (only process_manager and admin)
- [ ] Multi-tenancy enforced (can only delete own org's workflows)
- [ ] 404 if workflow not found or belongs to different org
- [ ] Deleted workflow hidden from list endpoint (GET /v1/workflows)
- [ ] Deleted workflow still accessible via direct GET (for audit trail)

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL (workflows table with archived flag)

**Database Schema Addition**:
```sql
ALTER TABLE workflows ADD COLUMN archived BOOLEAN DEFAULT FALSE;
ALTER TABLE workflows ADD COLUMN archived_at TIMESTAMP;
```

**API Endpoint** (`app/api/v1/workflows.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.dependencies.auth import require_role, get_current_user
from app.database import get_db
from app.models import Workflow, Assessment, UserRole

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete workflow (archive).

    Prevents deletion if workflow has assessments (data integrity).
    """
    org_id = current_user["organization_id"]

    # Get workflow
    workflow = await Workflow.get_by_id(db, org_id, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    # Check if workflow has assessments
    assessment_count = await db.scalar(
        select(func.count(Assessment.id))
        .where(Assessment.workflow_id == workflow_id)
    )

    if assessment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete workflow with {assessment_count} assessments. Archive instead."
        )

    # Soft delete
    workflow.archived = True
    workflow.archived_at = datetime.utcnow()
    await db.commit()

    return None  # 204 No Content
```

**Update List Endpoint** (exclude archived):
```python
@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    include_archived: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List workflows (exclude archived by default)"""
    query = select(Workflow).where(
        Workflow.organization_id == current_user["organization_id"]
    )

    if not include_archived:
        query = query.where(Workflow.archived == False)

    # ... rest of pagination logic
```

---

## Dependencies

- **Blocked By**:
  - STORY-009 (Create Workflow) - need workflows to delete
  - STORY-016 (Start Assessment) - need to check assessment count
- **Blocks**: Nothing (P1 feature, not MVP blocker)

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:
- API endpoint: 0.5 days (delete logic, assessment check)
- Schema migration: 0.25 days (add archived column)
- Testing: 0.25 days (conflict scenarios)

---

## Definition of Done

- [ ] DELETE /v1/workflows/:id endpoint implemented
- [ ] Soft delete (archived flag set to true)
- [ ] 409 Conflict if assessments exist
- [ ] 204 No Content on success
- [ ] RBAC enforced (403 for project_handler)
- [ ] Multi-tenancy enforced (404 for other org's workflow)
- [ ] Archived workflows excluded from list endpoint
- [ ] Archived workflows still accessible via GET /:id (audit trail)
- [ ] Integration tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:
- [ ] Delete workflow with no assessments → 204 No Content
- [ ] Delete workflow with assessments → 409 Conflict
- [ ] Deleted workflow not in list endpoint
- [ ] Deleted workflow still accessible via GET /:id
- [ ] include_archived=true → shows archived workflows
- [ ] Project handler tries to delete → 403 Forbidden
- [ ] User from org A tries to delete org B workflow → 404 Not Found

---

## Risks & Mitigations

**Risk**: Hard delete breaks referential integrity (assessments reference deleted workflow)
- **Mitigation**: Use soft delete (archive), preserve data for audit trail

**Risk**: Archived workflows clutter database
- **Mitigation**: For MVP, accept archived workflows; post-MVP add hard delete after retention period

---

## Notes

- P1 priority - not critical for MVP, but nice-to-have
- After completing this story, proceed to STORY-014 (Workflow Builder UI)
