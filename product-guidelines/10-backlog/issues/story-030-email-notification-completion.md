# [STORY-030] Email Notification on Completion

**Epic**: EPIC-06 - Results & Evidence Display
**Priority**: P1 (Important for Launch)
**Estimated Effort**: 1 day
**Journey Step**: Step 3 - Get Notified

---

## User Story

**As a** Project Handler
**I want to** receive an email when my assessment completes
**So that** I don't have to keep the browser tab open and can work on other tasks

---

## Acceptance Criteria

- [ ] Email sent when assessment status changes to "completed"
- [ ] Email includes assessment summary (X/Y criteria passed)
- [ ] Email includes clickable link to results page
- [ ] Email delivered within 1 minute of completion
- [ ] Professional email template (matches brand)
- [ ] Unsubscribe link included (optional for MVP)
- [ ] Email delivery rate >98%

---

## Technical Details

**Tech Stack**:
- Email Service: Resend or SendGrid
- Trigger: Celery job completion callback
- Template: HTML email with plain text fallback

**Email Template**:
```html
Subject: Assessment Complete: Medical Device - Class II

Hi [User Name],

Your assessment for "Medical Device - Class II" is complete.

Results: 3/5 criteria passed ✅❌

View full results: https://qteria.com/assessments/assess_123/results

---
Qteria - AI-Powered Certification Validation
```

**Implementation**:
```python
# backend/app/services/email_service.py

from resend import Resend

resend = Resend(api_key=settings.RESEND_API_KEY)

async def send_assessment_complete_email(
    user_email: str,
    user_name: str,
    assessment_id: str,
    workflow_name: str,
    passed_count: int,
    total_count: int
):
    html_content = render_template(
        "assessment_complete.html",
        user_name=user_name,
        workflow_name=workflow_name,
        passed_count=passed_count,
        total_count=total_count,
        results_url=f"{settings.FRONTEND_URL}/assessments/{assessment_id}/results"
    )

    await resend.emails.send({
        "from": "Qteria <noreply@qteria.com>",
        "to": user_email,
        "subject": f"Assessment Complete: {workflow_name}",
        "html": html_content
    })

# backend/app/workers/assessment_worker.py

@celery_app.task
def process_assessment(assessment_id: str):
    # ... run assessment ...

    # Send email on completion
    assessment = db.get_assessment(assessment_id)
    user = db.get_user(assessment.user_id)

    passed_count = sum(1 for r in assessment.results if r.pass)
    total_count = len(assessment.results)

    send_assessment_complete_email(
        user_email=user.email,
        user_name=user.name,
        assessment_id=assessment_id,
        workflow_name=assessment.workflow.name,
        passed_count=passed_count,
        total_count=total_count
    )
```

**Email Services Comparison**:
| Service | Cost | Deliverability | Ease of Use |
|---------|------|----------------|-------------|
| **Resend** | $0 (first 3,000/mo) | Excellent | Very easy (modern API) |
| **SendGrid** | $20/mo (first 100 emails) | Excellent | Good |
| **AWS SES** | $0.10/1,000 | Good | Complex (AWS setup) |

**Recommendation**: Use Resend (free tier sufficient for MVP, excellent deliverability)

---

## Dependencies

**Blocks**: None (nice-to-have feature)

**Blocked By**:
- STORY-023: Background job queue (triggers email)
- STORY-005: User login (needs user email)

---

## Testing Requirements

**Integration Tests**:
- [ ] Email sent when assessment completes
- [ ] Email includes correct data (passed/total, link)
- [ ] Email not sent if user email missing
- [ ] Email delivery confirmed (Resend webhook)

**E2E Tests**:
- [ ] Complete assessment → Email received within 1 min
- [ ] Click email link → Redirects to results page

---

## RICE Score

**Reach**: 80 (most users will appreciate email)
**Impact**: 1 (low - nice-to-have, not critical)
**Confidence**: 80%
**Effort**: 1 day

**RICE Score**: (80 × 1 × 0.80) ÷ 1 = **64**

---

## Definition of Done

- [ ] Email service integrated (Resend)
- [ ] Email template created (HTML + plain text)
- [ ] Email sent on assessment completion
- [ ] Includes summary (X/Y passed) and results link
- [ ] Delivery rate >98% (monitor via Resend dashboard)
- [ ] Integration tests pass
- [ ] E2E test: Receive email after assessment
- [ ] Code reviewed and merged to main
- [ ] Deployed to staging

---

## Notes

This is a P1 feature (not MVP blocker) but highly recommended for production. Users appreciate not having to wait on the page.

**Reference**: `product-guidelines/06-design-system.md` (email templates)
