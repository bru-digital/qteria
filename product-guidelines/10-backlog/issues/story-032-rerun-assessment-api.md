# [STORY-032] Re-Run Assessment API

**Epic**: EPIC-07 - Re-assessment & Iteration
**Priority**: P1 (Important for Production)
**Estimated Effort**: 2 days
**Journey Step**: Step 4 - Re-Run Validation

---

## User Story

**As a** Project Handler
**I want to** re-run assessment with updated documents
**So that** I can verify my fixes passed all criteria

---

## Acceptance Criteria

- [ ] POST /v1/assessments/:id/rerun endpoint working
- [ ] Creates new assessment linked to original (parent_assessment_id)
- [ ] Triggers background job with updated documents
- [ ] Results show diff from previous run
- [ ] Version history visible (assessment v1 → v2)

---

## Technical Details

**API Endpoint**:

```python
POST /v1/assessments/{assessment_id}/rerun
```

**Implementation**:

```python
@router.post("/assessments/{assessment_id}/rerun")
async def rerun_assessment(
    assessment_id: str,
    user: User = Depends(get_current_user)
):
    # Get original assessment
    original = await db.get_assessment(assessment_id)
    if original.organization_id != user.organization_id:
        raise HTTPException(403)

    # Create new assessment linked to original
    new_assessment = await db.create_assessment(
        workflow_id=original.workflow_id,
        organization_id=original.organization_id,
        user_id=user.id,
        parent_assessment_id=assessment_id,  # Link to original
        status="pending"
    )

    # Copy updated documents
    await db.copy_assessment_documents(
        from_assessment_id=assessment_id,
        to_assessment_id=new_assessment.id
    )

    # Trigger background job
    process_assessment.delay(new_assessment.id)

    return {"assessment_id": new_assessment.id}
```

---

## RICE Score

**RICE**: (80 × 2 × 0.85) ÷ 2 = **68**

---

## Definition of Done

- [ ] POST endpoint working
- [ ] Creates linked assessment
- [ ] Triggers Celery job
- [ ] Version history visible
- [ ] Tests pass
- [ ] Code reviewed and merged
