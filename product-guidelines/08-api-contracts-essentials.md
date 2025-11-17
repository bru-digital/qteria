# API Contracts Essentials (For Backlog Generation)

> **Purpose**: Condensed endpoint reference for Session 10 (backlog generation)
> **Full Details**: See `08-api-contracts.md` for complete OpenAPI 3.0 specification, request/response schemas, error codes

---

## API Configuration

**API Style**: REST (HTTP/JSON)
**Base URL**: `/v1/` (versioned in path)
**Authentication**: JWT Bearer tokens in `Authorization: Bearer <token>` header
**Multi-Tenancy**: All endpoints filter by `org_id` from JWT (row-level isolation)

**Pagination**: `?page=1&limit=20&sort=-created_at`
**Rate Limiting**: 1000 req/hour per user, 100 uploads/hour, 50 assessments/hour

**Common Response Codes**:
- `200` OK (GET success)
- `201` Created (POST success)
- `202` Accepted (async operation started - assessments)
- `204` No Content (DELETE success)
- `400` Bad Request (validation failed)
- `401` Unauthorized (invalid/missing JWT)
- `403` Forbidden (insufficient permissions)
- `404` Not Found
- `409` Conflict (resource state error)
- `422` Unprocessable Entity (business logic error, e.g. insufficient credits)
- `429` Rate Limit Exceeded

---

## Endpoints by Journey Step

### Authentication (Pre-Journey)

- `POST /v1/auth/login` - User login, receive JWT
- `POST /v1/auth/refresh` - Refresh expired access token
- `GET /v1/auth/me` - Get current user details

---

### Workflows (Journey Step 1: Process Manager Creates Workflow)

- `GET /v1/workflows` - List workflows for organization (paginated)
- `GET /v1/workflows/:id` - Get single workflow with buckets + criteria
- `POST /v1/workflows` - Create workflow (requires: process_manager role)
- `PUT /v1/workflows/:id` - Update workflow (requires: creator or process_manager)
- `DELETE /v1/workflows/:id` - Archive workflow (soft delete, requires: process_manager)

**Key Design**: Workflows contain nested buckets (document categories) and criteria (validation rules). POST creates all in single transaction.

---

### Documents (Journey Step 2: Project Handler Uploads Documents)

- `POST /v1/documents` - Upload document (multipart/form-data, max 50MB)
- `GET /v1/documents/:id` - Download document (serves PDF with optional `?page=X`)
- `DELETE /v1/documents/:id` - Delete document

**Key Design**: Documents uploaded to temporary storage before assessment. Max 20 files per request.

---

### Assessments (Journey Steps 2-5: Run AI Validation)

- `POST /v1/assessments` - Start assessment (returns 202 Accepted, triggers async job)
- `GET /v1/assessments/:id` - Get assessment status and progress (poll every 30s)
- `GET /v1/assessments/:id/results` - Get evidence-based pass/fail results (Step 3 aha moment)
- `GET /v1/assessments` - List assessments (paginated, filterable by workflow/status/user)
- `POST /v1/assessments/:id/rerun` - Re-run with updated documents (Step 4)
- `DELETE /v1/assessments/:id` - Cancel or archive assessment

**Key Design**: Async pattern for AI validation (5-10 min processing). POST returns immediately with status "pending", frontend polls GET until status "completed". Results include page/section evidence links.

---

### Reports (Journey Step 5: Export Validation Report)

- `POST /v1/assessments/:id/reports` - Generate PDF report (async, returns report_id)
- `GET /v1/reports/:report_id` - Check generation status or get download URL
- `GET /v1/reports/:report_id/download` - Download PDF report
- `POST /v1/reports/:report_id/share` - Create public shareable link (expires in 7 days)
- `GET /public/reports/:token` - Public access to shared report (no auth required)

**Key Design**: Report generation is async (10 seconds). Public sharing creates time-limited token for external access.

---

### Organizations & Users (Admin Management)

- `GET /v1/organizations/me` - Get current organization details and usage limits
- `GET /v1/users` - List users in organization (requires: admin role)
- `POST /v1/users/invite` - Invite new user (requires: admin role)

**Key Design**: Multi-tenancy enforced via `organization_id`. Usage limits tracked per organization (assessments/month based on subscription tier).

---

## Async Patterns

### Assessment Execution Flow

```
1. POST /v1/assessments → 202 Accepted {id, status: "pending"}
2. Frontend polls GET /v1/assessments/:id every 30s
3. Status transitions: pending → processing → completed
4. When completed, GET /v1/assessments/:id/results returns evidence
```

### Report Generation Flow

```
1. POST /v1/assessments/:id/reports → 201 Created {report_id, status: "generating"}
2. Poll GET /v1/reports/:report_id every 5s
3. When ready, response includes download_url
4. GET /v1/reports/:report_id/download → PDF stream
```

---

## Authentication & Authorization

**JWT Token Payload**:
```json
{
  "sub": "user_123",          // User ID
  "org_id": "org_tuv_sud",    // Organization ID (multi-tenancy)
  "email": "handler@tuvsud.com",
  "role": "project_handler"   // process_manager, project_handler, admin
}
```

**Role-Based Access**:
- `process_manager` - Can create/update/delete workflows
- `project_handler` - Can upload documents, start assessments, view results
- `admin` - Can manage users, view organization settings

**Multi-Tenancy**: All queries automatically filter by `organization_id` from JWT. Users cannot access other organizations' data.

---

## Error Response Format

All errors return consistent structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "workflow_id",
      "reason": "Workflow not found"
    },
    "request_id": "req_abc123"
  }
}
```

**Common Error Codes**:
- `VALIDATION_ERROR` (400) - Invalid input
- `INVALID_TOKEN` (401) - JWT invalid/expired
- `INSUFFICIENT_PERMISSIONS` (403) - Role not authorized
- `RESOURCE_NOT_FOUND` (404) - Workflow/assessment not found
- `WORKFLOW_HAS_ASSESSMENTS` (409) - Can't delete workflow in use
- `FILE_TOO_LARGE` (413) - Upload exceeds 50MB
- `INSUFFICIENT_CREDITS` (422) - Usage limit reached
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests
- `AI_SERVICE_UNAVAILABLE` (502) - Claude API down

---

## For Backlog Story Scoping

**When creating stories, reference**:

### Frontend Stories
- Authentication: `POST /auth/login`, `GET /auth/me`
- Workflow builder: `POST /workflows` (with nested buckets + criteria)
- Document upload: `POST /documents` (multipart/form-data)
- Assessment start: `POST /assessments` → polling `GET /assessments/:id`
- Results display: `GET /assessments/:id/results` (evidence links to `GET /documents/:id?page=X`)
- Report export: `POST /assessments/:id/reports` → `GET /reports/:id/download`

### Backend Stories
- Implement endpoints per resource
- JWT middleware for auth + multi-tenancy
- Celery background job for `POST /assessments` (enqueue AI validation task)
- PDF parsing + Claude API integration in Celery worker
- Evidence extraction (page/section detection)
- Report generation (PDF using ReportLab/WeasyPrint)

### Integration Stories
- Generate TypeScript client from OpenAPI spec
- Frontend API client setup (axios interceptors for JWT)
- Error boundary for API errors (401 → redirect to login, 429 → show rate limit message)
- Polling logic for assessments (30s interval, timeout after 15 min)

---

## Endpoint Count Summary

- **Authentication**: 3 endpoints
- **Workflows**: 5 endpoints
- **Documents**: 3 endpoints
- **Assessments**: 6 endpoints
- **Reports**: 5 endpoints
- **Organizations/Users**: 3 endpoints
- **Public**: 1 endpoint

**Total**: 28 endpoints across 6 core resources

---

## Journey-to-Endpoint Mapping

| Journey Step | Primary API Call | Returns |
|--------------|------------------|---------|
| **Step 1: Create Workflow** | `POST /v1/workflows` | Created workflow with buckets + criteria |
| **Step 2: Upload Documents** | `POST /v1/documents` (multiple) | Document IDs |
| **Step 2: Start Assessment** | `POST /v1/assessments` | 202 Accepted, assessment ID |
| **Step 3: Poll Status** | `GET /v1/assessments/:id` | Status: pending/processing/completed |
| **Step 3: View Results** | `GET /v1/assessments/:id/results` | Evidence-based pass/fail per criteria |
| **Step 4: Re-run** | `POST /v1/assessments/:id/rerun` | New assessment ID (202 Accepted) |
| **Step 5: Export Report** | `POST /v1/assessments/:id/reports` | Report ID |
| **Step 5: Download Report** | `GET /v1/reports/:id/download` | PDF stream |

---

**Complete API Details**: See `08-api-contracts.md` for full OpenAPI 3.0 specification, Pydantic schemas, rate limiting details, testing examples, and implementation notes.
