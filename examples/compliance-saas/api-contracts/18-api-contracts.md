# API Contracts: Compliance Document Assessment Platform

> **Context**: This is a completed example from the Stack-Driven cascade. Your API contracts will be different based on your journey!

**Generated**: 2025-11-11
**Based on**: Sessions 1-7 outputs + database schema

---

## Overview

This API enables compliance officers to upload regulatory documents, assess them against compliance frameworks, and retrieve detailed results through a RESTful HTTP API.

**API Style**: REST
**Base URL**: `https://api.complianceassess.com`
**Authentication**: JWT Bearer tokens (via Clerk)
**Rate Limiting**: 100 requests/minute (free tier), 1000 requests/minute (pro tier)
**Documentation**: OpenAPI 3.0 with Swagger UI

**Endpoint Count**: 15 endpoints across 4 core resources

---

## API Architecture

### Why REST?

**Journey requirement**: Simple CRUD operations for documents, assessments, and results
- Upload document → POST
- Check status → GET
- Retrieve results → GET
- Delete document → DELETE

**Alternative considered**: GraphQL would add complexity without benefit. Compliance data is not deeply nested or graph-like. REST's predictable structure matches the linear journey (upload → assess → results).

**When to reconsider**: If mobile app requires precise data control or if UI needs highly variable data shapes across different views.

### Versioning Strategy

**Approach**: URL-based versioning (`/v1/`, `/v2/`)
**Current version**: v1
**Why**: Explicit, visible in logs, easier for developers to understand

**Breaking changes policy**:
- Minor changes (new optional fields) → No version bump
- Breaking changes (removing fields, changing types) → New version (`/v2/`)
- Maintain previous version for 6 months minimum

### Base URLs

```
Production:  https://api.complianceassess.com
Staging:     https://staging-api.complianceassess.com
Development: http://localhost:8000
```

---

## Authentication

**Method**: JWT Bearer tokens (Clerk)

**How it works**:
1. User signs in via Clerk on frontend
2. Frontend obtains Clerk session token
3. Include token in `Authorization` header: `Bearer <token>`
4. Backend validates token with Clerk API

**Token format**:
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token lifetime**: 1 hour (refreshed automatically by Clerk)

**Endpoints without auth**:
- `GET /public/reports/:token` - View shared assessment report (uses unique token)

**Authorization pattern**:
- User resources → Filter by `user_id` from JWT
- Team resources → Filter by `team_id` from user's team membership
- Admin operations → Check `role === 'admin'` claim in JWT

---

## Core Resources

### Documents

**Purpose**: User-uploaded compliance documents (PDFs, DOCX) for assessment

**Journey connection**: Step 1 - "Upload regulatory document"

**Endpoints**:

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/documents` | List user's documents | Required |
| POST | `/api/documents` | Upload new document | Required |
| GET | `/api/documents/:id` | Get document details | Required |
| DELETE | `/api/documents/:id` | Delete document | Required |
| GET | `/api/documents/:id/download` | Download original file | Required |

**Example: Upload Document**

```http
POST /api/documents
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: [binary PDF/DOCX]
name: "Privacy Policy 2025.pdf" (optional)
frameworks: ["fw_gdpr", "fw_soc2"] (optional)
```

**Response 201 Created:**
```json
{
  "id": "doc_abc123",
  "name": "Privacy Policy 2025.pdf",
  "fileSize": 2456789,
  "status": "processing",
  "uploadedAt": "2025-11-11T10:30:00Z",
  "userId": "user_xyz",
  "frameworks": ["fw_gdpr", "fw_soc2"]
}
```

**Design decisions**:
- **multipart/form-data**: Required for file uploads
- **Async processing**: Returns 201 immediately, processes in background
- **Status field**: Client polls `/api/documents/:id` for status updates
- **Why not streaming upload?**: 50MB file limit makes streaming unnecessary for MVP

---

### Frameworks

**Purpose**: System-defined compliance frameworks (SOC2, GDPR, HIPAA, etc.)

**Journey connection**: Step 2 - "Select compliance frameworks to assess against"

**Endpoints**:

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/frameworks` | List all frameworks | Required |
| GET | `/api/frameworks/:id` | Get framework details | Required |

**Example: List Frameworks**

```http
GET /api/frameworks
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "data": [
    {
      "id": "fw_gdpr",
      "name": "GDPR (General Data Protection Regulation)",
      "description": "EU data protection and privacy law",
      "category": "data-privacy",
      "complexity": "high",
      "sections": 99,
      "averageAssessmentTime": "45 seconds"
    },
    {
      "id": "fw_soc2",
      "name": "SOC 2 Type II",
      "description": "Service Organization Control 2",
      "category": "security",
      "complexity": "high",
      "sections": 150,
      "averageAssessmentTime": "60 seconds"
    }
  ],
  "total": 12
}
```

**Design decisions**:
- **Read-only for users**: Admins manage frameworks via separate admin API
- **No pagination**: 10-20 frameworks total, fits in single response
- **averageAssessmentTime**: Helps users set expectations (from journey: "60 seconds to assess")

---

### Assessments

**Purpose**: Document assessment jobs and results

**Journey connection**:
- Step 3 - "AI assesses document against frameworks in 60 seconds"
- Step 4 - "Review detailed compliance report"

**Endpoints**:

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/assessments` | List user's assessments | Required |
| POST | `/api/assessments` | Create new assessment | Required |
| GET | `/api/assessments/:id` | Get assessment details & results | Required |
| POST | `/api/assessments/:id/cancel` | Cancel running assessment | Required |
| POST | `/api/assessments/:id/share` | Generate shareable link | Required |

**Example: Create Assessment**

```http
POST /api/assessments
Content-Type: application/json
Authorization: Bearer <token>

{
  "documentId": "doc_abc123",
  "frameworks": ["fw_gdpr", "fw_soc2"]
}
```

**Response 201 Created:**
```json
{
  "id": "asmt_def456",
  "documentId": "doc_abc123",
  "status": "pending",
  "progress": 0,
  "frameworks": ["fw_gdpr", "fw_soc2"],
  "createdAt": "2025-11-11T10:31:00Z",
  "estimatedCompletionAt": "2025-11-11T10:32:00Z"
}
```

**Example: Get Assessment Results**

```http
GET /api/assessments/asmt_def456
Authorization: Bearer <token>
```

**Response 200 OK (completed):**
```json
{
  "id": "asmt_def456",
  "documentId": "doc_abc123",
  "status": "completed",
  "progress": 100,
  "frameworks": ["fw_gdpr", "fw_soc2"],
  "results": {
    "overallScore": 85,
    "frameworkScores": {
      "fw_gdpr": 87,
      "fw_soc2": 83
    },
    "findings": [
      {
        "id": "find_001",
        "framework": "fw_gdpr",
        "article": "Article 32 - Security of Processing",
        "severity": "high",
        "issue": "Missing encryption specification for data at rest",
        "location": "Page 12, Section 4.2",
        "recommendation": "Add explicit statement about AES-256 encryption"
      },
      {
        "id": "find_002",
        "framework": "fw_soc2",
        "control": "CC6.1 - Logical Access",
        "severity": "medium",
        "issue": "No mention of multi-factor authentication",
        "location": "Page 18, Section 5.1",
        "recommendation": "Document MFA implementation for privileged accounts"
      }
    ],
    "summary": "Document demonstrates strong compliance foundation with 85% alignment. Two high-priority gaps identified in security controls that should be addressed before regulatory review.",
    "passFailThreshold": 80,
    "passed": true
  },
  "startedAt": "2025-11-11T10:31:00Z",
  "completedAt": "2025-11-11T10:32:15Z",
  "durationMs": 75000
}
```

**Response 200 OK (processing):**
```json
{
  "id": "asmt_def456",
  "documentId": "doc_abc123",
  "status": "processing",
  "progress": 45,
  "frameworks": ["fw_gdpr", "fw_soc2"],
  "createdAt": "2025-11-11T10:31:00Z",
  "estimatedCompletionAt": "2025-11-11T10:32:00Z"
}
```

**Design decisions**:
- **Async processing**: Assessment takes 30-90 seconds, too long for synchronous request
- **Status polling**: Client polls every 2-3 seconds until `status === 'completed'`
- **Why not WebSocket?**: Polling is simpler, 2-second delay acceptable for this use case
- **Detailed findings**: Compliance officers need specific page/section references (from journey)

---

### Shared Reports (Public)

**Purpose**: Public access to shared assessment reports

**Journey connection**: Step 4 - "Share assessment report with stakeholders"

**Endpoints**:

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/public/reports/:token` | View shared report | None |

**Example: Share Assessment**

```http
POST /api/assessments/asmt_def456/share
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "shareToken": "share_xyz789abc",
  "shareUrl": "https://app.complianceassess.com/public/reports/share_xyz789abc",
  "expiresAt": "2025-12-11T10:30:00Z"
}
```

**Example: View Shared Report**

```http
GET /public/reports/share_xyz789abc
```

**Response 200 OK:**
```json
{
  "assessment": {
    "documentName": "Privacy Policy 2025.pdf",
    "assessedAt": "2025-11-11T10:32:15Z",
    "frameworks": ["GDPR", "SOC 2"],
    "overallScore": 85,
    "frameworkScores": {
      "GDPR": 87,
      "SOC 2": 83
    },
    "findings": [...],
    "summary": "..."
  },
  "sharedBy": "Compliance Team",
  "expiresAt": "2025-12-11T10:30:00Z"
}
```

**Design decisions**:
- **No auth required**: Public sharing via unique token
- **Cryptographically secure token**: Prevents guessing (256-bit random)
- **Expiration**: 30-day default, prevents indefinite exposure
- **Why SEO-friendly?**: Shared reports are indexable for marketing (from architecture)

---

## Rate Limiting

**Strategy**: Token bucket per team

**Limits by tier**:

| Tier | GET requests/min | POST requests/min | Assessments/month |
|------|------------------|-------------------|-------------------|
| Free | 100 | 10 | 50 |
| Pro | 1000 | 100 | 1000 |
| Enterprise | 10000 | 1000 | Unlimited |

**Rate limit headers** (included in all responses):
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1699704000
```

**Rate limit exceeded response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded your rate limit",
    "details": {
      "limit": 100,
      "remaining": 0,
      "resetAt": "2025-11-11T11:00:00Z"
    }
  }
}
```

**Why per-team?**: Multi-tenant architecture, teams share quota across members

---

## Error Handling

**Standard error format:**

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "field": "fieldName",
    "requestId": "req_abc123"
  }
}
```

**Common error codes:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | Request validation failed |
| 400 | `INVALID_FILE_TYPE` | File must be PDF or DOCX |
| 401 | `INVALID_TOKEN` | Auth token invalid or expired |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `DUPLICATE_ASSESSMENT` | Assessment already running for this document |
| 413 | `FILE_TOO_LARGE` | File exceeds 50MB limit |
| 422 | `INSUFFICIENT_CREDITS` | Team has insufficient credits |
| 429 | `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

**Example validation error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "file": "File is required",
      "frameworks": "At least one framework must be selected"
    },
    "requestId": "req_abc123"
  }
}
```

---

## Pagination

**Strategy**: Cursor-based (more stable than offset for large datasets)

**Query parameters**:
- `cursor` (string): Pagination cursor from previous response
- `limit` (integer): Results per page (default: 20, max: 100)

**Example request:**
```http
GET /api/documents?cursor=abc123&limit=20
Authorization: Bearer <token>
```

**Example response:**
```json
{
  "data": [
    { "id": "doc_001", "name": "Policy.pdf", ... },
    { "id": "doc_002", "name": "Agreement.pdf", ... }
  ],
  "pagination": {
    "nextCursor": "def456",
    "prevCursor": "xyz789",
    "hasMore": true
  }
}
```

**Why cursor-based?**: Documents can be deleted while paginating, offset pagination would skip/duplicate results

---

## Testing Examples

**Upload document with curl:**
```bash
curl -X POST https://api.complianceassess.com/api/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@policy.pdf" \
  -F "name=Privacy Policy 2025" \
  -F "frameworks[]=fw_gdpr" \
  -F "frameworks[]=fw_soc2"
```

**Check assessment status:**
```bash
curl https://api.complianceassess.com/api/assessments/asmt_def456 \
  -H "Authorization: Bearer $TOKEN"
```

**Poll until complete:**
```bash
while true; do
  STATUS=$(curl -s https://api.complianceassess.com/api/assessments/asmt_def456 \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  echo "Status: $STATUS"
  sleep 2
done
```

---

## Design Decisions Explained

### Why multipart/form-data for uploads?

**Decision**: Document upload uses `multipart/form-data`

**Alternative**: Base64-encode file in JSON request

**Why multipart**:
- File size overhead: Base64 adds 33% size, would exceed 50MB limit for larger files
- Framework support: FastAPI/Express have built-in multipart parsing
- Standard practice: Multipart is HTTP standard for file uploads

**When to reconsider**: If building mobile app with restricted upload capabilities, consider chunked uploads

### Why async assessments (not synchronous)?

**Decision**: POST `/api/assessments` returns immediately with `status: "pending"`

**Alternative**: Wait for assessment to complete, return results in POST response

**Why async**:
- Processing time: 30-90 seconds is too long for HTTP request (risk of timeout)
- User experience: Client can show progress bar while polling
- Scalability: Background workers can process assessments independently

**When to reconsider**: If AI assessment time drops below 5 seconds consistently

### Why token-based sharing (not user-to-user)?

**Decision**: Shared reports use cryptographic tokens, not user invitations

**Alternative**: User invites specific email addresses to view report

**Why token-based**:
- Journey requirement: "Share with audit firm partners" - unknown email addresses
- Simplicity: No account creation required for report viewers
- SEO: Shared reports are publicly accessible for marketing (from architecture)

**When to reconsider**: If enterprise customers require audit trails of who viewed reports

---

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
- **File**: `./openapi.yaml`
- **Interactive docs**: https://api.complianceassess.com/docs (Swagger UI)
- **ReDoc**: https://api.complianceassess.com/redoc

The specification includes:
- All 15 endpoints with full request/response schemas
- Authentication configuration
- Reusable components (schemas, responses, parameters)
- Example requests and responses
- Error definitions

---

## Implementation Notes

**Backend framework**: FastAPI (Python)
**Why FastAPI**:
- From tech stack decision: Python ecosystem for document processing + AI
- Built-in OpenAPI generation
- Async support for background tasks
- Strong type validation with Pydantic

**Authentication**: Clerk JWT validation
**File storage**: AWS S3 (signed URLs for downloads)
**Background jobs**: Celery with Redis
**Rate limiting**: FastAPI middleware with Redis backend

---

## Changelog

### v1.0.0 (2025-11-11)
- Initial API release
- Core resources: Documents, Frameworks, Assessments
- JWT authentication via Clerk
- Rate limiting by tier
- Public report sharing

### Future considerations
- Webhooks for assessment completion (avoid polling)
- Batch document upload (upload 10 documents at once)
- GraphQL layer if mobile app requires flexible queries
- API key authentication for programmatic access (CI/CD pipelines)

---

## Reference Files

- Journey: `examples/compliance-saas/foundation/00-user-journey.md`
- Tech stack: `examples/compliance-saas/stack/02-tech-stack.md`
- Architecture: `examples/compliance-saas/stack/05-architecture.md`
- Backlog: `examples/compliance-saas/backlog/BACKLOG.md`
- Database schema: `examples/compliance-saas/database/07-database-schema.md`

---

**Every endpoint traces back to the user journey. No endpoint exists "just in case."**
