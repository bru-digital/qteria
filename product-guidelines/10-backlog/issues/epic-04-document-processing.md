# [EPIC-04] Document Processing

**Type**: Epic
**Journey Step**: Step 2 - Project Handler Uploads Documents
**Priority**: P0 (MVP Critical)

---

## Epic Overview

Enable Project Handlers to upload PDFs and documents into workflow buckets, validate file types/sizes, store securely in Vercel Blob, and prepare for AI validation. This is **Journey Step 2** - collecting documents before assessment.

**User Value**: Project Handlers drag-drop documents into buckets, see upload progress, and start assessments with confidence that documents are securely stored.

---

## Success Criteria

- [ ] Project Handler can upload PDFs (up to 50MB each)
- [ ] Drag-drop interface for easy upload
- [ ] Progress indicator shows upload status
- [ ] File validation (PDF/DOCX only, size limits)
- [ ] Documents stored encrypted in Vercel Blob
- [ ] Can upload multiple documents per bucket
- [ ] Can replace/delete uploaded documents
- [ ] Upload success rate >95%

---

## Stories in This Epic

### STORY-015: Document Upload API [P0, 2 days]
Implement `POST /v1/documents` endpoint that accepts multipart/form-data, validates file type/size, uploads to Vercel Blob, and returns document ID + storage key.

**RICE**: R:100 × I:3 × C:90% ÷ E:2 = **135**

### STORY-016: Start Assessment API [P0, 2 days]
Implement `POST /v1/assessments` endpoint that accepts workflow_id + document_ids (mapped to bucket_ids), creates assessment record, and triggers background job.

**RICE**: R:100 × I:3 × C:100% ÷ E:2 = **150**

### STORY-017: Document Upload UI with Drag-Drop [P0, 2 days]
Create React component for document upload with drag-drop zone, file type validation (client-side), progress indicator, and error handling.

**RICE**: R:100 × I:2 × C:90% ÷ E:2 = **90**

### STORY-018: Document Download API [P0, 1 day]
Implement `GET /v1/documents/:id` endpoint that streams document from Vercel Blob with optional `?page=X` parameter for PDF page linking.

**RICE**: R:80 × I:2 × C:100% ÷ E:1 = **160**

### STORY-019: Delete Document API [P1, 1 day]
Implement `DELETE /v1/documents/:id` endpoint that removes document from Vercel Blob and database. Prevents deletion if document is part of completed assessment.

**RICE**: R:50 × I:1 × C:80% ÷ E:1 = **40**

---

## Total Estimated Effort

**8 person-days** (1.5 weeks for solo founder)

**Breakdown**:
- Backend: 4 days (upload/download/delete APIs, Vercel Blob integration)
- Frontend: 2 days (drag-drop UI, progress indicators)
- Testing: 2 days (unit + integration + E2E)

---

## Dependencies

**Blocks**:
- EPIC-05: AI Validation Engine (needs documents to process)
- STORY-020: PDF parsing (needs uploaded documents)

**Blocked By**:
- STORY-001: Database schema (assessment_documents table)
- STORY-009: Create workflow (assessments reference workflows)

---

## Technical Approach

**Tech Stack**:
- Backend: FastAPI + Vercel Blob SDK
- Storage: Vercel Blob (encrypted, 1GB free tier)
- Frontend: Next.js + react-dropzone (drag-drop)
- File Validation: Python (backend), JavaScript (frontend)

**Upload Flow**:
1. User drags PDF into bucket drop zone (frontend)
2. Frontend validates file type (PDF/DOCX), size (<50MB)
3. Frontend uploads to FastAPI via `POST /v1/documents` (multipart)
4. Backend validates again (don't trust client)
5. Backend uploads to Vercel Blob (encrypted at rest)
6. Backend stores metadata in PostgreSQL (document_id, file_name, storage_key, bucket_id)
7. Backend returns document_id to frontend
8. Frontend shows success message

**Start Assessment Flow**:
1. User clicks "Start Assessment" after uploading docs
2. Frontend calls `POST /v1/assessments` with:
   ```json
   {
     "workflow_id": "workflow_123",
     "documents": [
       {"bucket_id": "bucket_1", "document_id": "doc_1"},
       {"bucket_id": "bucket_2", "document_id": "doc_2"}
     ]
   }
   ```
3. Backend validates all required buckets have documents
4. Backend creates assessment record (status: "pending")
5. Backend enqueues Celery background job for AI validation
6. Backend returns assessment_id + estimated_time (5-10 min)

**Reference**: `product-guidelines/02-tech-stack.md` (Vercel Blob), `product-guidelines/08-api-contracts.md` (documents endpoints)

---

## Success Metrics

**User Experience**:
- Upload success rate: >95%
- Upload time (10MB PDF): <10 seconds (P95)
- Documents uploaded per assessment: 3-5 average

**Technical**:
- File validation prevents invalid uploads: 100%
- Encryption at rest: 100% (Vercel Blob default)
- Storage costs: <$5/month (MVP pilot)

---

## Definition of Done

- [ ] Document upload API working (multipart/form-data)
- [ ] Drag-drop UI working (react-dropzone)
- [ ] File validation on client and server
- [ ] Progress indicator shows upload status
- [ ] Document download works (streams from Vercel Blob)
- [ ] Start assessment validates required buckets
- [ ] Multi-tenancy enforced (users only see their org's documents)
- [ ] E2E test: Upload documents → Start assessment
- [ ] Code coverage >80% backend, >50% frontend
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: Large file uploads timeout (50MB PDFs)
- **Mitigation**: Chunked upload (if needed), increase timeout to 60 seconds

**Risk**: Vercel Blob storage limits exceeded (1GB free tier)
- **Mitigation**: Monitor usage, upgrade to paid tier ($0.15/GB) or migrate to S3

**Risk**: Malicious file upload (virus, script injection)
- **Mitigation**: Validate file type/size, scan files (ClamAV optional), store in isolated blob

---

## Testing Requirements

**Unit Tests** (85% coverage target):
- [ ] File validation logic (PDF/DOCX only, size <50MB)
- [ ] Vercel Blob upload function
- [ ] Assessment validation (required buckets check)

**Integration Tests** (80% coverage target):
- [ ] POST /v1/documents uploads to Vercel Blob
- [ ] GET /v1/documents/:id streams file
- [ ] POST /v1/assessments creates assessment record
- [ ] POST /v1/assessments returns 400 if missing required bucket
- [ ] DELETE /v1/documents/:id removes from Blob + DB
- [ ] Multi-tenancy enforced (user cannot download other org's docs)

**E2E Tests** (critical flow):
- [ ] Drag-drop PDF → Upload progress → Success message
- [ ] Upload documents → Start assessment → Status "pending"

**Performance Tests**:
- [ ] Upload 10MB PDF: <10 seconds
- [ ] Upload 20 documents concurrently: No failures

---

## Next Epic

After completing this epic, proceed to **EPIC-05: AI Validation Engine** - the critical path that delivers core value (evidence-based validation in <10 minutes).
