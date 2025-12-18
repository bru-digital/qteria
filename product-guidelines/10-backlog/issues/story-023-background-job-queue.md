# [STORY-023] Background Job Queue (Celery + Redis)

**Type**: Story
**Epic**: EPIC-05 (AI Validation Engine)
**Journey Step**: Step 3 - Async AI Validation Processing
**Priority**: P0 (MVP Critical - Enables Async Validation)
**RICE Score**: 90 (R:100 × I:3 × C:90% ÷ E:3)

---

## User Value

**Job-to-Be-Done**: When assessments take 5-10 minutes to process, users need background job processing with status updates, so they can start assessments and check back later without waiting synchronously.

**Value Delivered**: Reliable async processing that handles long-running AI validation jobs, with retry logic and failure recovery.

**Success Metric**: Background job success rate >98%, jobs complete within estimated time.

---

## Acceptance Criteria

- [ ] Celery worker configured with Redis queue (Upstash)
- [ ] Assessment validation job enqueued from STORY-016
- [ ] Worker processes: PDF parsing → Claude validation → Evidence extraction
- [ ] Retry logic (3 attempts with exponential backoff)
- [ ] Timeout handling (15 min max per job)
- [ ] Job status tracking (pending → in_progress → completed/failed)
- [ ] Updates assessment status in database
- [ ] Error messages stored for failed assessments
- [ ] Worker monitoring/health checks

---

## Technical Approach

**Setup Celery Worker**:

```python
# app/tasks.py
from celery import Celery
from app.services.pdf_parser import PDFParser
from app.services.claude_validator import ClaudeValidator
from app.models import Assessment

celery = Celery(
    "qteria",
    broker="redis://upstash-redis-url",
    backend="redis://upstash-redis-url"
)

@celery.task(
    bind=True,
    max_retries=3,
    time_limit=900  # 15 minutes
)
def run_assessment_validation(self, assessment_id: str):
    try:
        # 1. Fetch assessment + documents
        assessment = await Assessment.get_by_id(assessment_id)
        assessment.status = "in_progress"
        await assessment.save()

        # 2. Parse PDFs (STORY-020)
        parser = PDFParser()
        parsed_docs = []
        for doc in assessment.documents:
            parsed = await parser.parse_pdf(doc.file_path, doc.id)
            parsed_docs.append(parsed)

        # 3. Validate with Claude (STORY-021, 022)
        validator = ClaudeValidator()
        results = []
        for criteria in assessment.workflow.criteria:
            result = await validator.validate_criteria(
                criteria.name,
                criteria.description,
                parsed_docs,
                doc.file_name
            )
            results.append(result)

        # 4. Store results
        assessment.results = results
        assessment.status = "completed"
        await assessment.save()

    except Exception as e:
        assessment.status = "failed"
        assessment.error_message = str(e)
        await assessment.save()
        raise self.retry(exc=e, countdown=60)  # Retry in 60s
```

---

## Dependencies

- **Blocked By**: STORY-016 (Start Assessment), STORY-020, STORY-021, STORY-022
- **Blocks**: STORY-027 (Status Polling)

---

## Estimation

**Effort**: 3 person-days

---

## Definition of Done

- [ ] Celery worker running
- [ ] Jobs enqueued and processed
- [ ] Retry logic works
- [ ] Timeout handling works
- [ ] Assessment status updated correctly
- [ ] Worker health checks implemented
- [ ] Tests pass (job processing, retries)
- [ ] Code reviewed and merged

---

## Notes

- Background jobs are **critical for UX** - users can't wait 10 min synchronously
- After completing, proceed to STORY-024 (Confidence Scoring)
