# API Contracts: Qteria

> **Derived from**: Journey Steps 1-5, FastAPI tech stack, database schema, architecture principles
> **Purpose**: Complete REST API specification for frontend integration and future third-party integrations

---

## API Overview

**API Style**: REST (RESTful HTTP/JSON)
**Base URL**:

- Production: `https://api.qteria.com/v1`
- Staging: `https://api-staging.qteria.com/v1`
- Local: `http://localhost:8000/v1`

**Framework**: FastAPI (Python) with auto-generated OpenAPI docs
**Authentication**: JWT Bearer tokens (Auth.js → Clerk migration)
**Content Type**: `application/json` (except file uploads: `multipart/form-data`)
**Versioning Strategy**: URL path (`/v1/`, `/v2/`) - simple, explicit, debuggable

**Endpoint Count**: 28 total endpoints across 6 core resources
**Auto-Generated Docs**: `/docs` (Swagger UI), `/redoc` (ReDoc)

---

## Authentication

### Auth Method

**JWT Bearer Tokens** in `Authorization` header:

```http
Authorization: Bearer <jwt_token>
```

**Token Structure** (Auth.js/Clerk):

```json
{
  "sub": "user_123", // User ID
  "org_id": "org_456", // Organization ID (multi-tenancy)
  "email": "handler@tuvsud.com",
  "role": "project_handler", // process_manager, project_handler, admin
  "exp": 1672531200 // Expiration timestamp
}
```

**Token Lifetime**:

- Access token: 1 hour
- Refresh token: 7 days (handled by Auth.js/Clerk)

**Unauthenticated Endpoints**:

- `POST /auth/login` - Login endpoint
- `POST /auth/register` - Registration (disabled in production, invite-only)
- `GET /public/reports/:token` - Public shareable assessment reports

**Multi-Tenancy Enforcement**:
All authenticated endpoints automatically filter by `org_id` from JWT. Users can only access resources within their organization.

---

## Core Resources

### Resource Hierarchy

```
Organizations (notified bodies)
 └─> Users (Process Managers, Project Handlers)
     └─> Workflows (validation templates)
         ├─> Buckets (document categories)
         ├─> Criteria (validation rules)
         └─> Assessments (validation runs)
             ├─> Assessment Documents (uploaded files)
             └─> Assessment Results (per-criteria outcomes with evidence)
```

---

## API Endpoints by Journey Step

### Authentication (Journey: Login)

#### `POST /v1/auth/login`

**Purpose**: Authenticate user and receive JWT token
**Journey Step**: Pre-Step 1 (before workflow creation)
**Request**:

```json
{
  "email": "handler@tuvsud.com",
  "password": "secure_password"
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "handler@tuvsud.com",
    "name": "Anna Schmidt",
    "role": "project_handler",
    "organization_id": "org_tuv_sud",
    "organization_name": "TÜV SÜD"
  }
}
```

**Errors**:

- 401: Invalid credentials
- 429: Rate limit exceeded (10 attempts/hour per IP)

---

#### `POST /v1/auth/refresh`

**Purpose**: Refresh expired access token
**Request**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

---

#### `GET /v1/auth/me`

**Purpose**: Get current authenticated user details
**Auth**: Required
**Response** (200 OK):

```json
{
  "id": "user_123",
  "email": "handler@tuvsud.com",
  "name": "Anna Schmidt",
  "role": "project_handler",
  "organization_id": "org_tuv_sud",
  "organization_name": "TÜV SÜD",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Workflows (Journey Step 1: Create Validation Workflow)

#### `GET /v1/workflows`

**Purpose**: List all workflows for current user's organization
**Auth**: Required
**Query Params**:

- `page` (int, default: 1) - Page number for pagination
- `limit` (int, default: 20, max: 100) - Items per page
- `is_active` (bool, optional) - Filter by active/archived
- `sort` (string, default: "-created_at") - Sort field (prefix `-` for DESC)

**Response** (200 OK):

```json
{
  "data": [
    {
      "id": "workflow_abc123",
      "name": "Medical Device - Class II",
      "description": "Validation workflow for Class II medical devices",
      "is_active": true,
      "created_by": "user_123",
      "created_by_name": "Anna Schmidt",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "buckets_count": 3,
      "criteria_count": 5,
      "assessments_count": 42
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 12,
    "total_pages": 1
  }
}
```

---

#### `GET /v1/workflows/:id`

**Purpose**: Get single workflow with buckets and criteria
**Auth**: Required
**Response** (200 OK):

```json
{
  "id": "workflow_abc123",
  "name": "Medical Device - Class II",
  "description": "Validation workflow for Class II medical devices",
  "is_active": true,
  "created_by": "user_123",
  "created_by_name": "Anna Schmidt",
  "organization_id": "org_tuv_sud",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "buckets": [
    {
      "id": "bucket_1",
      "name": "Technical Documentation",
      "description": "Product specifications, design files",
      "required": true,
      "accepted_file_types": ["pdf", "docx"],
      "order_index": 0
    },
    {
      "id": "bucket_2",
      "name": "Test Reports",
      "description": "Safety and performance test results",
      "required": true,
      "accepted_file_types": ["pdf"],
      "order_index": 1
    },
    {
      "id": "bucket_3",
      "name": "Risk Assessment",
      "description": "ISO 14971 risk management file",
      "required": false,
      "accepted_file_types": ["pdf", "xlsx"],
      "order_index": 2
    }
  ],
  "criteria": [
    {
      "id": "criteria_1",
      "name": "All documents must be signed",
      "description": "Each document should have authorized signature",
      "applies_to_bucket_ids": ["bucket_1", "bucket_2", "bucket_3"],
      "order_index": 0
    },
    {
      "id": "criteria_2",
      "name": "Test report must include pass/fail summary",
      "description": "Section 5.1 should contain clear pass/fail for each test",
      "applies_to_bucket_ids": ["bucket_2"],
      "order_index": 1
    },
    {
      "id": "criteria_3",
      "name": "Risk matrix must be complete",
      "description": "All identified hazards must have severity and probability ratings",
      "applies_to_bucket_ids": ["bucket_3"],
      "order_index": 2
    }
  ]
}
```

**Errors**:

- 404: Workflow not found or not in user's organization

---

#### `POST /v1/workflows`

**Purpose**: Create new workflow (Process Manager only)
**Auth**: Required (role: process_manager or admin)
**Request**:

```json
{
  "name": "Medical Device - Class II",
  "description": "Validation workflow for Class II medical devices",
  "buckets": [
    {
      "name": "Technical Documentation",
      "description": "Product specifications, design files",
      "required": true,
      "accepted_file_types": ["pdf", "docx"]
    },
    {
      "name": "Test Reports",
      "description": "Safety and performance test results",
      "required": true,
      "accepted_file_types": ["pdf"]
    }
  ],
  "criteria": [
    {
      "name": "All documents must be signed",
      "description": "Each document should have authorized signature",
      "applies_to_bucket_ids": [0, 1]
    },
    {
      "name": "Test report must include pass/fail summary",
      "description": "Section 5.1 should contain clear pass/fail for each test",
      "applies_to_bucket_ids": [1]
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "id": "workflow_abc123",
  "name": "Medical Device - Class II",
  "description": "Validation workflow for Class II medical devices",
  "is_active": true,
  "created_by": "user_123",
  "created_at": "2024-01-15T10:30:00Z",
  "buckets": [...],
  "criteria": [...]
}
```

**Errors**:

- 400: Validation error (missing required fields, invalid bucket reference)
- 403: User role not authorized (must be process_manager or admin)

---

#### `PUT /v1/workflows/:id`

**Purpose**: Update workflow (name, description, buckets, criteria)
**Auth**: Required (role: process_manager or admin, or created_by user)
**Request**: Same as POST (full replacement)
**Response** (200 OK): Updated workflow object
**Errors**:

- 403: Not authorized to update (not creator, not process_manager)
- 409: Workflow has active assessments (can't modify criteria that are in use)

---

#### `DELETE /v1/workflows/:id`

**Purpose**: Archive workflow (soft delete, sets is_active=false)
**Auth**: Required (role: process_manager or admin)
**Response** (204 No Content)
**Errors**:

- 403: Not authorized
- 409: Workflow has pending/processing assessments

---

### Documents (Journey Step 2: Upload Documents)

#### `POST /v1/documents`

**Purpose**: Upload document to temporary storage (before assessment)
**Auth**: Required
**Content-Type**: `multipart/form-data`
**Request**:

```
file: <binary PDF/DOCX/XLSX file>
bucket_id: "bucket_1" (optional, for validation)
```

**Response** (201 Created):

```json
{
  "id": "doc_xyz789",
  "file_name": "technical-spec.pdf",
  "file_size_bytes": 2048576,
  "file_type": "application/pdf",
  "storage_key": "uploads/org_tuv_sud/doc_xyz789.pdf",
  "uploaded_at": "2024-01-15T11:00:00Z",
  "uploaded_by": "user_123"
}
```

**Limits**:

- Max file size: 50MB
- Accepted types: PDF, DOCX, XLSX
- Max 20 files per request

**Errors**:

- 400: Invalid file type or size
- 413: Payload too large (>50MB)
- 429: Rate limit (max 100 uploads/hour per user)

---

#### `GET /v1/documents/:id`

**Purpose**: Download document (serves PDF with proper headers)
**Auth**: Required (must belong to user's organization)
**Query Params**:

- `page` (int, optional) - Open PDF at specific page (#page=X anchor)

**Response** (200 OK):

- Content-Type: `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `inline; filename="technical-spec.pdf"`
- Binary file stream

**Errors**:

- 404: Document not found or not in user's organization

---

#### `DELETE /v1/documents/:id`

**Purpose**: Delete uploaded document (before or after assessment)
**Auth**: Required
**Response** (204 No Content)
**Errors**:

- 404: Document not found
- 409: Document is part of completed assessment (can't delete historical evidence)

---

### Assessments (Journey Steps 2-5: Run Validation)

#### `POST /v1/assessments`

**Purpose**: Start new assessment (triggers background AI validation)
**Auth**: Required
**Journey Step**: Step 2 (Project Handler uploads docs and starts assessment)
**Request**:

```json
{
  "workflow_id": "workflow_abc123",
  "documents": [
    {
      "bucket_id": "bucket_1",
      "document_ids": ["doc_xyz789", "doc_xyz790"]
    },
    {
      "bucket_id": "bucket_2",
      "document_ids": ["doc_xyz791"]
    }
  ],
  "notify_on_completion": true
}
```

**Response** (202 Accepted):

```json
{
  "id": "assessment_def456",
  "workflow_id": "workflow_abc123",
  "workflow_name": "Medical Device - Class II",
  "status": "pending",
  "created_by": "user_123",
  "created_at": "2024-01-15T11:05:00Z",
  "estimated_duration_seconds": 600,
  "documents_count": 3,
  "criteria_count": 5
}
```

**Behavior**:

- Returns immediately (202 Accepted)
- Enqueues Celery background job
- Frontend polls `GET /v1/assessments/:id` for status updates
- Email notification sent when status becomes "completed"

**Errors**:

- 400: Missing required documents (bucket marked required but no docs)
- 404: Workflow not found
- 422: Insufficient credits (usage-based pricing enforcement)

---

#### `GET /v1/assessments/:id`

**Purpose**: Get assessment status and progress
**Auth**: Required
**Journey Step**: Step 3 (Frontend polls during AI processing)
**Response** (200 OK):

**While Processing**:

```json
{
  "id": "assessment_def456",
  "workflow_id": "workflow_abc123",
  "workflow_name": "Medical Device - Class II",
  "status": "processing",
  "progress_percent": 60,
  "progress_message": "Validating criteria 3 of 5...",
  "created_by": "user_123",
  "created_at": "2024-01-15T11:05:00Z",
  "started_processing_at": "2024-01-15T11:05:30Z",
  "estimated_completion_at": "2024-01-15T11:15:30Z"
}
```

**When Completed**:

```json
{
  "id": "assessment_def456",
  "workflow_id": "workflow_abc123",
  "workflow_name": "Medical Device - Class II",
  "status": "completed",
  "created_by": "user_123",
  "created_at": "2024-01-15T11:05:00Z",
  "started_processing_at": "2024-01-15T11:05:30Z",
  "completed_at": "2024-01-15T11:12:45Z",
  "duration_ms": 435000,
  "overall_pass": false,
  "criteria_passed": 4,
  "criteria_failed": 1,
  "ai_cost_cents": 21
}
```

**Errors**:

- 404: Assessment not found

---

#### `GET /v1/assessments/:id/results`

**Purpose**: Get evidence-based pass/fail results per criteria
**Auth**: Required
**Journey Step**: Step 3 (Aha moment - evidence-based results display)
**Response** (200 OK):

```json
{
  "assessment_id": "assessment_def456",
  "workflow_name": "Medical Device - Class II",
  "status": "completed",
  "overall_pass": false,
  "completed_at": "2024-01-15T11:12:45Z",
  "results": [
    {
      "criteria_id": "criteria_1",
      "criteria_name": "All documents must be signed",
      "pass": true,
      "confidence": "high",
      "evidence": null,
      "reasoning": "All 3 documents contain authorized signatures in designated sections"
    },
    {
      "criteria_id": "criteria_2",
      "criteria_name": "Test report must include pass/fail summary",
      "pass": false,
      "confidence": "high",
      "evidence": {
        "document_id": "doc_xyz791",
        "document_name": "test-report.pdf",
        "page": 8,
        "section": "3.2 Test Results",
        "text_snippet": "...observed values recorded but no explicit pass/fail stated..."
      },
      "reasoning": "Test results are documented but missing clear pass/fail determination in section 3.2"
    },
    {
      "criteria_id": "criteria_3",
      "criteria_name": "Risk matrix must be complete",
      "pass": true,
      "confidence": "medium",
      "evidence": {
        "document_id": "doc_xyz790",
        "document_name": "risk-assessment.pdf",
        "page": 12,
        "section": "5. Risk Matrix",
        "text_snippet": "...all 14 identified hazards include severity (1-5) and probability (A-E)..."
      },
      "reasoning": "All identified hazards in section 5 have complete severity and probability ratings"
    }
  ]
}
```

**Errors**:

- 404: Assessment not found
- 409: Assessment still processing (status != "completed")

---

#### `GET /v1/assessments`

**Purpose**: List assessments for current user's organization
**Auth**: Required
**Query Params**:

- `page`, `limit` (pagination)
- `workflow_id` (filter by workflow)
- `status` (filter: pending, processing, completed, failed)
- `created_by` (filter by user)
- `sort` (default: "-created_at")

**Response** (200 OK):

```json
{
  "data": [
    {
      "id": "assessment_def456",
      "workflow_name": "Medical Device - Class II",
      "status": "completed",
      "overall_pass": false,
      "created_by_name": "Anna Schmidt",
      "created_at": "2024-01-15T11:05:00Z",
      "duration_ms": 435000
    }
  ],
  "pagination": {...}
}
```

---

#### `POST /v1/assessments/:id/rerun`

**Purpose**: Re-run assessment with updated documents
**Auth**: Required
**Journey Step**: Step 4 (Project Handler fixes issues and re-runs)
**Request**:

```json
{
  "replace_documents": [
    {
      "bucket_id": "bucket_2",
      "document_ids": ["doc_xyz792"]
    }
  ]
}
```

**Response** (202 Accepted): New assessment object with status "pending"
**Behavior**: Creates new assessment, reuses workflow + unchanged docs, replaces specified docs

---

#### `DELETE /v1/assessments/:id`

**Purpose**: Cancel pending/processing assessment or archive completed
**Auth**: Required
**Response** (204 No Content)
**Errors**:

- 409: Can't cancel already completed assessment

---

### Reports (Journey Step 5: Export Validation Report)

#### `POST /v1/assessments/:id/reports`

**Purpose**: Generate PDF summary report of assessment results
**Auth**: Required
**Request**:

```json
{
  "include_evidence_links": true,
  "include_ai_reasoning": false,
  "format": "pdf"
}
```

**Response** (201 Created):

```json
{
  "report_id": "report_ghi789",
  "assessment_id": "assessment_def456",
  "status": "generating",
  "estimated_completion_seconds": 10
}
```

**Polling**: `GET /v1/reports/:report_id`

---

#### `GET /v1/reports/:report_id`

**Purpose**: Check report generation status or download
**Auth**: Required
**Response When Ready** (200 OK):

```json
{
  "report_id": "report_ghi789",
  "assessment_id": "assessment_def456",
  "status": "ready",
  "download_url": "https://api.qteria.com/v1/reports/report_ghi789/download",
  "expires_at": "2024-01-16T11:12:45Z",
  "file_size_bytes": 524288
}
```

---

#### `GET /v1/reports/:report_id/download`

**Purpose**: Download generated PDF report
**Auth**: Required
**Response** (200 OK):

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="assessment-report-2024-01-15.pdf"`
- Binary PDF stream

---

#### `POST /v1/reports/:report_id/share`

**Purpose**: Generate public shareable link (expires in 7 days)
**Auth**: Required
**Request**:

```json
{
  "expires_in_days": 7
}
```

**Response** (201 Created):

```json
{
  "public_url": "https://qteria.com/public/reports/abcd1234efgh5678",
  "expires_at": "2024-01-22T11:12:45Z"
}
```

---

#### `GET /public/reports/:token`

**Purpose**: Public access to shared assessment report (no auth)
**Response** (200 OK): HTML page with embedded PDF viewer
**Errors**:

- 404: Token invalid or expired

---

### Organizations & Users (Admin)

#### `GET /v1/organizations/me`

**Purpose**: Get current user's organization details
**Auth**: Required
**Response** (200 OK):

```json
{
  "id": "org_tuv_sud",
  "name": "TÜV SÜD",
  "subscription_tier": "professional",
  "subscription_status": "active",
  "subscription_start_date": "2024-01-01",
  "usage_limits": {
    "assessments_per_month": 500,
    "users": 20
  },
  "usage_current_month": {
    "assessments": 42,
    "users": 5
  }
}
```

---

#### `GET /v1/users`

**Purpose**: List users in organization (admin only)
**Auth**: Required (role: admin)
**Response** (200 OK):

```json
{
  "data": [
    {
      "id": "user_123",
      "email": "handler@tuvsud.com",
      "name": "Anna Schmidt",
      "role": "project_handler",
      "created_at": "2024-01-10T09:00:00Z",
      "last_login_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {...}
}
```

---

#### `POST /v1/users/invite`

**Purpose**: Invite new user to organization (admin only)
**Auth**: Required (role: admin)
**Request**:

```json
{
  "email": "newuser@tuvsud.com",
  "name": "Max Müller",
  "role": "project_handler"
}
```

**Response** (201 Created):

```json
{
  "id": "user_789",
  "email": "newuser@tuvsud.com",
  "invite_sent_at": "2024-01-15T12:00:00Z",
  "invite_expires_at": "2024-01-22T12:00:00Z"
}
```

---

## Error Handling

### Standard Error Response Format

All errors return consistent JSON structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "workflow_id",
      "reason": "Workflow not found"
    },
    "request_id": "req_abc123xyz"
  }
}
```

### HTTP Status Codes

**Success**:

- `200 OK` - GET, PUT, PATCH requests successful
- `201 Created` - POST requests creating resources
- `202 Accepted` - Async operations started (assessments)
- `204 No Content` - DELETE requests successful

**Client Errors**:

- `400 Bad Request` - Invalid input (validation failed)
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Valid token but insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource state conflict (e.g., can't delete workflow with active assessments)
- `413 Payload Too Large` - File upload exceeds 50MB
- `422 Unprocessable Entity` - Business logic error (e.g., insufficient credits)
- `429 Too Many Requests` - Rate limit exceeded

**Server Errors**:

- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Claude API or Vercel Blob unavailable
- `503 Service Unavailable` - Maintenance mode
- `504 Gateway Timeout` - Claude API timeout

### Common Error Codes

| Code                       | HTTP Status | Description                                 |
| -------------------------- | ----------- | ------------------------------------------- |
| `VALIDATION_ERROR`         | 400         | Request body validation failed              |
| `INVALID_TOKEN`            | 401         | JWT token invalid or expired                |
| `INSUFFICIENT_PERMISSIONS` | 403         | User role not authorized                    |
| `RESOURCE_NOT_FOUND`       | 404         | Workflow, assessment, or document not found |
| `WORKFLOW_HAS_ASSESSMENTS` | 409         | Can't delete/modify workflow in use         |
| `FILE_TOO_LARGE`           | 413         | Upload exceeds 50MB limit                   |
| `INVALID_FILE_TYPE`        | 400         | File type not PDF/DOCX/XLSX                 |
| `INSUFFICIENT_CREDITS`     | 422         | Organization usage limit reached            |
| `RATE_LIMIT_EXCEEDED`      | 429         | Too many requests                           |
| `AI_SERVICE_UNAVAILABLE`   | 502         | Claude API down                             |
| `ASSESSMENT_TIMEOUT`       | 504         | AI validation took >15 minutes              |

---

## Rate Limiting

### Rate Limit Strategy

**Per-User Limits** (by JWT `sub`):

- Standard endpoints: 1000 requests/hour
- Document uploads: 100 uploads/hour
- Assessment creation: 50 assessments/hour
- Auth endpoints: 10 login attempts/hour per IP

**Per-Organization Limits** (by JWT `org_id`):

- Assessments per month: Tier-based (trial: 10, professional: 500, enterprise: unlimited)

### Rate Limit Headers

All responses include rate limit info:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1672534800
```

**When Exceeded** (429 response):

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_at": "2024-01-15T13:00:00Z"
    }
  }
}
```

---

## Pagination

### Pagination Pattern

All list endpoints support cursor-based pagination:

**Request**:

```
GET /v1/workflows?page=2&limit=20&sort=-created_at
```

**Response**:

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 156,
    "total_pages": 8
  }
}
```

**Sort Parameter**:

- Prefix `-` for descending: `-created_at` (newest first)
- No prefix for ascending: `name` (A-Z)
- Default: `-created_at`

---

## Webhooks (Future)

**Not in MVP**, but architecture supports:

```
POST /v1/webhooks (create webhook subscription)
GET /v1/webhooks (list subscriptions)
DELETE /v1/webhooks/:id (unsubscribe)
```

**Events**:

- `assessment.completed` - Assessment finished processing
- `assessment.failed` - Assessment failed (AI error, timeout)
- `workflow.created` - New workflow added
- `organization.usage_limit_reached` - 80% of monthly assessments used

---

## What We DIDN'T Choose (And Why)

### GraphQL API

**What**: Query language letting clients request exact fields needed
**Why Not**:

- Journey has simple CRUD (not complex nested queries)
- REST easier to debug (curl, Postman, browser tools)
- FastAPI OpenAPI auto-docs excellent (Swagger UI)
- No over-fetching problem (predictable queries per page)

**Reconsider If**:

- Mobile app needs bandwidth optimization
- Frontend requires highly variable data shapes (50+ optional fields)
- Third-party integrations need flexible queries

---

### gRPC API

**What**: High-performance RPC with Protocol Buffers (binary)
**Why Not**:

- Web browsers need grpc-web proxy (extra complexity)
- JSON easier to debug than binary
- No network bottleneck (assessments are async, not real-time)
- REST/JSON standard for B2B SaaS integrations

**Reconsider If**:

- Microservices with high-volume service-to-service calls
- Need bidirectional streaming (real-time collaboration)

---

### WebSocket for Real-Time Updates

**What**: Persistent bidirectional connection for live updates
**Why Not**:

- Polling every 30 seconds acceptable for 5-10 min assessments
- WebSocket adds complexity (connection management, scaling, firewall issues)
- Simpler to implement and debug (standard HTTP)

**Reconsider If**:

- Need <1 second updates (real-time collaboration)
- Multiple users watching same assessment
- Mobile app (battery efficiency with push notifications)

---

### Header-Based API Versioning

**What**: Version in `Accept: application/vnd.qteria.v2+json` header
**Why Not**:

- URL versioning (`/v1/`, `/v2/`) simpler, more explicit
- Easier to test (just change URL, not headers)
- Better error messages (404 vs 406 Not Acceptable)

**Reconsider If**: Building hypermedia API (HATEOAS)

---

### OAuth 2.0 Authorization Server

**What**: Full OAuth with authorization code flow, client credentials, scopes
**Why Not**:

- B2B SaaS uses Clerk/Auth0 (not app authorization)
- No third-party app integrations yet (no "Qteria App Store")
- Complexity not justified for MVP

**Reconsider If**:

- Building platform with third-party apps (like Slack/GitHub)
- Need programmatic API access with fine-grained scopes

---

### API Gateway (Kong, AWS API Gateway)

**What**: Centralized gateway for rate limiting, auth, logging
**Why Not**:

- FastAPI middleware handles rate limiting, auth, logging
- MVP stage (single service, not microservices)
- Operational complexity (another service to maintain)

**Reconsider If**:

- Microservices architecture (multiple backend services)
- Advanced rate limiting needs (per-endpoint quotas, burst protection)
- Detailed API analytics and monetization

---

## Testing & Development

### Auto-Generated API Docs

**FastAPI provides**:

- Swagger UI: `https://api.qteria.com/docs`
- ReDoc: `https://api.qteria.com/redoc`
- OpenAPI JSON: `https://api.qteria.com/openapi.json`

### Example API Calls

**Login and Get Token**:

```bash
curl -X POST https://api.qteria.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "handler@tuvsud.com", "password": "secure_password"}'
```

**Create Workflow**:

```bash
curl -X POST https://api.qteria.com/v1/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Medical Device - Class II",
    "buckets": [...],
    "criteria": [...]
  }'
```

**Upload Document**:

```bash
curl -X POST https://api.qteria.com/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@technical-spec.pdf" \
  -F "bucket_id=bucket_1"
```

**Start Assessment**:

```bash
curl -X POST https://api.qteria.com/v1/assessments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "workflow_abc123",
    "documents": [...]
  }'
```

**Poll Assessment Status**:

```bash
curl -X GET https://api.qteria.com/v1/assessments/assessment_def456 \
  -H "Authorization: Bearer $TOKEN"
```

**Get Results**:

```bash
curl -X GET https://api.qteria.com/v1/assessments/assessment_def456/results \
  -H "Authorization: Bearer $TOKEN"
```

### Client SDK Generation

Use OpenAPI Generator to create client libraries:

```bash
# TypeScript/Axios (Next.js frontend)
openapi-generator-cli generate \
  -i https://api.qteria.com/openapi.json \
  -g typescript-axios \
  -o ./src/api-client

# Python (testing, internal tools)
openapi-generator-cli generate \
  -i https://api.qteria.com/openapi.json \
  -g python \
  -o ./api-client-python
```

---

## Implementation Notes

### FastAPI Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Qteria API",
    description="AI-powered document validation for TIC industry",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.qteria.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-tenancy middleware (extract org_id from JWT)
@app.middleware("http")
async def add_organization_context(request: Request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_jwt(token)
    request.state.org_id = payload.get("org_id")
    request.state.user_id = payload.get("sub")
    return await call_next(request)
```

### Pydantic Schemas

```python
# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    buckets: List[BucketCreate]
    criteria: List[CriteriaCreate]

class BucketCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    required: bool = True
    accepted_file_types: List[str] = ["pdf"]

class CriteriaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    applies_to_bucket_ids: List[int]  # Indexes in buckets array
```

---

## Journey-to-Endpoint Mapping

| Journey Step                  | Primary Endpoints                                            | Secondary Endpoints                           |
| ----------------------------- | ------------------------------------------------------------ | --------------------------------------------- |
| **Step 0: Login**             | `POST /auth/login`                                           | `POST /auth/refresh`, `GET /auth/me`          |
| **Step 1: Create Workflow**   | `POST /workflows`, `GET /workflows/:id`                      | `GET /workflows`, `PUT /workflows/:id`        |
| **Step 2: Upload Documents**  | `POST /documents`, `POST /assessments`                       | `GET /documents/:id`, `DELETE /documents/:id` |
| **Step 3: AI Validation**     | `GET /assessments/:id`, `GET /assessments/:id/results`       | (polling)                                     |
| **Step 4: Re-run Assessment** | `POST /assessments/:id/rerun`                                | `POST /documents` (replace)                   |
| **Step 5: Export Report**     | `POST /assessments/:id/reports`, `GET /reports/:id/download` | `POST /reports/:id/share`                     |

---

## Next Steps

1. **Implement in FastAPI**: Create routers for each resource, wire up database queries
2. **Frontend Integration**: Generate TypeScript client, integrate with Next.js pages
3. **API Testing**: Write Pytest integration tests for each endpoint
4. **Load Testing**: Simulate 50 concurrent assessments (Year 3 scale)
5. **Documentation**: Keep OpenAPI spec updated, examples for each endpoint

---

## Summary

**28 endpoints** across **6 core resources** (auth, workflows, documents, assessments, reports, organizations).

**Journey-optimized**: Step 3 (AI validation) uses async pattern (POST returns 202, GET polls status) - handles 5-10 min processing without frontend timeout.

**Evidence-based**: `/assessments/:id/results` returns page/section links for each failed criteria - enables Step 3 aha moment.

**Multi-tenant**: All endpoints filter by `org_id` from JWT - row-level isolation for notified bodies.

**API-first**: Clean REST contracts enable future mobile app, customer integrations, marketplace.

This API serves the **user journey first**, not theoretical scale. Every endpoint maps to a journey action.
