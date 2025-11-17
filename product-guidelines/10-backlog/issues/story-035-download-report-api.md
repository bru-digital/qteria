# [STORY-035] Download Report API

**Epic**: EPIC-08 - Reporting & Export
**Priority**: P1 (Important for Launch)
**Estimated Effort**: 1 day
**Journey Step**: Step 5 - Download Report

---

## User Story

**As a** Project Handler
**I want to** download generated PDF reports
**So that** I can attach them to emails or save them locally

---

## Acceptance Criteria

- [ ] GET /v1/reports/:id/download streams PDF
- [ ] Content-Disposition header triggers download
- [ ] Filename includes workflow name and date
- [ ] Multi-tenant access control
- [ ] Download speed acceptable (<5 seconds for 1MB)

---

## Technical Details

**API Endpoint**:
```python
GET /v1/reports/{report_id}/download
```

**Implementation**:
```python
@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    user: User = Depends(get_current_user)
):
    report = await db.get_report(report_id)
    assessment = await db.get_assessment(report.assessment_id)

    # Verify access
    if assessment.organization_id != user.organization_id:
        raise HTTPException(403)

    # Stream PDF from Vercel Blob
    async with httpx.AsyncClient() as client:
        response = await client.get(report.blob_url)

    # Generate filename
    filename = f"qteria-report-{assessment.workflow.name}-{report.generated_at.date()}.pdf"
    filename = filename.replace(" ", "-").lower()

    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return Response(content=response.content, headers=headers)
```

---

## RICE Score

**RICE**: (80 × 1 × 1.00) ÷ 1 = **80**

---

## Definition of Done

- [ ] GET endpoint working
- [ ] Streams PDF from Vercel Blob
- [ ] Triggers browser download
- [ ] Filename includes workflow name
- [ ] Access control enforced
- [ ] Tests pass
- [ ] Code reviewed and merged
