# [STORY-016] Start Assessment API

**Type**: Story
**Epic**: EPIC-04 (Document Processing)
**Journey Step**: Step 2 - Start Validation Assessment
**Priority**: P0 (MVP Critical)
**RICE Score**: 150 (R:100 × I:3 × C:100% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When Project Handlers finish uploading documents, they need to start the validation assessment, so the AI can analyze documents against workflow criteria and return pass/fail results.

**Value Delivered**: API endpoint that creates assessment record, validates all required buckets have documents, and triggers background AI validation job, enabling the core assessment workflow.

**Success Metric**: Assessment start success rate >95%, background job queued in <1 second.

---

## Acceptance Criteria

- [ ] `POST /v1/assessments` endpoint implemented
- [ ] Accepts workflow_id and array of {bucket_id, document_id} mappings
- [ ] Validates all required buckets have at least one document
- [ ] Creates assessment record with status "pending"
- [ ] Creates assessment_documents join records
- [ ] Enqueues Celery background job for AI validation (STORY-023)
- [ ] Returns assessment_id, status, estimated_completion_time
- [ ] Multi-tenancy enforced (can only use org's workflows/documents)
- [ ] RBAC enforced (project_handler, process_manager, admin can start)
- [ ] 400 Bad Request if missing required bucket documents
- [ ] 404 Not Found if workflow or documents don't exist

---

## Technical Approach

**Tech Stack Components Used**:

- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL (assessments, assessment_documents tables)
- Job Queue: Celery + Redis (for STORY-023)

**API Endpoint** (`app/api/v1/assessments.py`):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Assessment, AssessmentDocument, Workflow, Document
from app.schemas.assessment import AssessmentCreate, AssessmentResponse
from datetime import datetime, timedelta

router = APIRouter(prefix="/v1/assessments", tags=["assessments"])

@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def start_assessment(
    data: AssessmentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start assessment with uploaded documents.

    Journey Step 2: Project Handler starts AI validation after uploading documents.
    """
    org_id = current_user["organization_id"]

    # 1. Get workflow and validate ownership
    workflow = await Workflow.get_by_id(db, org_id, data.workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    # 2. Validate all required buckets have documents
    required_buckets = [b for b in workflow.buckets if b.required]
    provided_bucket_ids = {doc.bucket_id for doc in data.documents}
    required_bucket_ids = {b.id for b in required_buckets}

    missing_buckets = required_bucket_ids - provided_bucket_ids
    if missing_buckets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing documents for required buckets: {missing_buckets}"
        )

    # 3. Validate all documents exist and belong to organization
    for doc_mapping in data.documents:
        document = await Document.get_by_id(db, org_id, doc_mapping.document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_mapping.document_id} not found"
            )

    # 4. Create assessment record
    assessment = Assessment(
        organization_id=org_id,
        workflow_id=data.workflow_id,
        status="pending",
        started_by=current_user["id"],
        started_at=datetime.utcnow()
    )
    db.add(assessment)
    await db.flush()  # Get assessment.id

    # 5. Create assessment_documents join records
    for doc_mapping in data.documents:
        assessment_doc = AssessmentDocument(
            assessment_id=assessment.id,
            document_id=doc_mapping.document_id,
            bucket_id=doc_mapping.bucket_id
        )
        db.add(assessment_doc)

    await db.commit()
    await db.refresh(assessment)

    # 6. Enqueue background job for AI validation (STORY-023)
    # For MVP: stub this out, implement in STORY-023
    # from app.tasks import run_ai_validation
    # run_ai_validation.delay(assessment.id)

    # 7. Estimate completion time (5-10 minutes)
    estimated_completion = datetime.utcnow() + timedelta(minutes=10)

    return {
        "id": assessment.id,
        "workflow_id": assessment.workflow_id,
        "status": assessment.status,
        "started_at": assessment.started_at,
        "estimated_completion_at": estimated_completion,
        "document_count": len(data.documents)
    }
```

**Pydantic Schemas** (`app/schemas/assessment.py`):

```python
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class DocumentMapping(BaseModel):
    bucket_id: str
    document_id: str

class AssessmentCreate(BaseModel):
    workflow_id: str
    documents: List[DocumentMapping] = Field(..., min_items=1)

class AssessmentResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    estimated_completion_at: datetime
    document_count: int
```

**Example Request**:

```json
POST /v1/assessments
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "workflow_id": "workflow_abc123",
  "documents": [
    {
      "bucket_id": "bucket_xyz",
      "document_id": "doc_001"
    },
    {
      "bucket_id": "bucket_abc",
      "document_id": "doc_002"
    }
  ]
}
```

**Example Response**:

```json
{
  "id": "assessment_xyz789",
  "workflow_id": "workflow_abc123",
  "status": "pending",
  "started_at": "2025-11-17T14:45:00Z",
  "estimated_completion_at": "2025-11-17T14:55:00Z",
  "document_count": 2
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-001 (Database Schema) - need assessments, assessment_documents tables
  - STORY-009 (Create Workflow) - need workflows to reference
  - STORY-015 (Upload Documents) - need documents to assess
- **Blocks**:
  - STORY-020 (PDF Parsing) - AI validation needs assessment record
  - STORY-023 (Background Jobs) - needs assessment to process

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:

- API endpoint: 0.5 days (validation logic)
- Required bucket validation: 0.5 days (complex logic)
- Assessment record creation: 0.5 days (joins)
- Testing: 0.5 days (validation scenarios)

---

## Definition of Done

- [ ] POST /v1/assessments endpoint implemented
- [ ] Validates all required buckets have documents
- [ ] Creates assessment record (status="pending")
- [ ] Creates assessment_documents join records
- [ ] Returns 201 Created with assessment details
- [ ] 400 Bad Request if missing required bucket
- [ ] 404 Not Found if workflow/documents don't exist
- [ ] Multi-tenancy enforced (workflow/documents from user's org)
- [ ] RBAC enforced (project_handler can start)
- [ ] Integration tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Integration Tests**:

- [ ] Valid assessment → 201 Created, assessment + joins created
- [ ] Missing required bucket → 400 Bad Request
- [ ] Invalid workflow_id → 404 Not Found
- [ ] Invalid document_id → 404 Not Found
- [ ] Document from different org → 404 Not Found
- [ ] Workflow from different org → 404 Not Found
- [ ] Multiple documents per bucket → allowed
- [ ] Optional bucket missing → allowed

---

## Risks & Mitigations

**Risk**: Required bucket validation logic has bugs (missing edge cases)

- **Mitigation**: Comprehensive tests covering all scenarios, validate against workflow definition

**Risk**: Race condition (document deleted between validation and assessment creation)

- **Mitigation**: Database transaction ensures atomicity, validate documents exist in transaction

---

## Notes

- Background job stub in this story, implement in STORY-023 (Background Jobs)
- After completing this story, proceed to STORY-017 (Upload UI)
