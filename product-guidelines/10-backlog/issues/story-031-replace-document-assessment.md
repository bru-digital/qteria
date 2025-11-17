# [STORY-031] Replace Document in Assessment

**Epic**: EPIC-07 - Re-assessment & Iteration
**Priority**: P1 (Important for Production)
**Estimated Effort**: 2 days
**Journey Step**: Step 4 - Fix Issues & Re-Run

---

## User Story

**As a** Project Handler
**I want to** replace failing documents without re-uploading everything
**So that** I can quickly fix issues and re-validate

---

## Acceptance Criteria

- [ ] "Replace Document" button visible for each bucket in failed assessment
- [ ] Upload new document replaces existing document
- [ ] Assessment status marked as "needs_rerun"
- [ ] Previous document still accessible (version history)
- [ ] Re-run button appears after replacement
- [ ] Multi-tenant isolation (can't replace other org's documents)

---

## Technical Details

**API Endpoint**:
```python
PUT /v1/assessments/{assessment_id}/documents/{bucket_id}
```

**Implementation**:
```python
@router.put("/assessments/{assessment_id}/documents/{bucket_id}")
async def replace_document(
    assessment_id: str,
    bucket_id: str,
    file: UploadFile,
    user: User = Depends(get_current_user)
):
    # Verify access
    assessment = await db.get_assessment(assessment_id)
    if assessment.organization_id != user.organization_id:
        raise HTTPException(403)

    # Upload new document to Vercel Blob
    blob_url = await upload_to_vercel_blob(file)

    # Create new document record
    new_doc = await db.create_document(
        name=file.filename,
        blob_url=blob_url,
        organization_id=user.organization_id
    )

    # Update assessment_documents table
    await db.update_assessment_document(
        assessment_id=assessment_id,
        bucket_id=bucket_id,
        new_document_id=new_doc.id,
        replaced_document_id=old_doc.id  # Keep for history
    )

    # Mark assessment as needs_rerun
    await db.update_assessment(assessment_id, status="needs_rerun")

    return {"message": "Document replaced", "document_id": new_doc.id}
```

---

## RICE Score

**RICE**: (80 × 2 × 0.80) ÷ 2 = **64**

---

## Definition of Done

- [ ] PUT endpoint working
- [ ] Replaces document in assessment
- [ ] Status marked "needs_rerun"
- [ ] Version history preserved
- [ ] Tests pass
- [ ] Code reviewed and merged
