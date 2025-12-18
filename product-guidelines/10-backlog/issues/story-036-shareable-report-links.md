# [STORY-036] Shareable Public Report Links

**Epic**: EPIC-08 - Reporting & Export
**Priority**: P2 (Nice-to-Have, Defer to Year 2)
**Estimated Effort**: 1 day
**Journey Step**: Step 5 - Share Report

---

## User Story

**As a** Project Handler
**I want to** create shareable public links to reports
**So that** I can share reports with Certification Person without email attachments

---

## Acceptance Criteria

- [ ] POST /v1/reports/:id/share creates public token
- [ ] Public URL: /public/reports/:token (no auth required)
- [ ] Token expires in 7 days
- [ ] Rate limiting on public endpoint
- [ ] Can revoke shared links

---

## Technical Details

**API Endpoints**:

```python
POST /v1/reports/{report_id}/share  # Create public token
GET /public/reports/{token}          # Public access (no auth)
DELETE /v1/reports/{report_id}/share # Revoke
```

**Implementation**:

```python
import secrets

@router.post("/reports/{report_id}/share")
async def create_shareable_link(
    report_id: str,
    user: User = Depends(get_current_user)
):
    # Generate token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    await db.create_public_token(
        report_id=report_id,
        token=token,
        expires_at=expires_at
    )

    public_url = f"{settings.FRONTEND_URL}/public/reports/{token}"
    return {"public_url": public_url, "expires_at": expires_at}

@router.get("/public/reports/{token}")
async def get_public_report(token: str):
    token_record = await db.get_public_token(token)

    if not token_record or token_record.expires_at < datetime.utcnow():
        raise HTTPException(404, "Link expired or invalid")

    # Stream PDF (same as download endpoint)
    report = await db.get_report(token_record.report_id)
    # ... stream PDF from blob_url ...
```

---

## RICE Score

**RICE**: (40 × 1 × 0.60) ÷ 1 = **24**

---

## Definition of Done

- [ ] POST /share endpoint working
- [ ] GET /public/reports/:token working
- [ ] Token expiration enforced
- [ ] Rate limiting implemented
- [ ] Can revoke tokens
- [ ] Tests pass
- [ ] Code reviewed and merged

---

## Notes

This is P2 - defer to Year 2 unless customers explicitly request it. Email attachments sufficient for MVP.
