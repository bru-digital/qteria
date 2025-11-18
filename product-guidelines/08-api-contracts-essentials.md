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

**Implementation**: Auth.js (NextAuth v5) with JWT-only session strategy

**Frontend Endpoints**:
- `POST /api/auth/signin` - User login with credentials
- `POST /api/auth/signout` - User logout
- `GET /api/auth/session` - Get current session (includes user + JWT)
- `GET /api/auth/csrf` - Get CSRF token (for form submissions)

**Server Actions** (recommended over direct API calls):
- `loginWithAudit(email, password, callbackUrl?)` - Login with audit logging + rate limiting
- `logoutWithAudit(userId, organizationId, email)` - Logout with audit logging

#### POST /api/auth/signin

**Request**:
```json
{
  "email": "test@qteria.com",
  "password": "password123",
  "redirect": false  // Don't auto-redirect (for client-side handling)
}
```

**Response (Success - 200)**:
```json
{
  "ok": true,
  "url": null  // No redirect when redirect: false
}
```

**Response (Failure - 401)**:
```json
{
  "ok": false,
  "error": "CredentialsSignin"
}
```

**Security Features**:
- Rate limiting: 5 failed attempts per email per 15 min, 20 attempts per IP per hour
- Timing attack protection (constant-time responses)
- Audit logging (success + failure)
- Password hashing with bcrypt (salt rounds = 12)
- Role validation before JWT creation

**Rate Limit Response (429)**:
```json
{
  "success": false,
  "error": "Too many failed login attempts. Please try again in 12 minutes.",
  "rateLimitExceeded": true,
  "retryAfterSeconds": 720
}
```

---

#### POST /api/auth/signout

**Request**: No body required

**Response (200)**: Clears session cookie and redirects to `/login`

**Security Features**:
- Audit logging (records logout event)
- Session invalidation (JWT removed from httpOnly cookie)

---

#### GET /api/auth/session

**Response (Authenticated - 200)**:
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@qteria.com",
    "name": "Test User",
    "role": "admin",
    "organizationId": "123e4567-e89b-12d3-a456-426614174001"
  },
  "expires": "2025-11-25T12:00:00.000Z"
}
```

**Response (Unauthenticated - 200)**:
```json
{
  "user": null
}
```

**Note**: Returns 200 even when unauthenticated (not 401). Check `user` field to determine auth state.

---

#### Session Configuration

**JWT Payload**:
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",  // User ID
  "email": "test@qteria.com",
  "name": "Test User",
  "role": "admin",                                 // process_manager, project_handler, admin
  "organizationId": "123e4567-e89b-12d3-a456-426614174001",
  "iat": 1732176000,                              // Issued at
  "exp": 1732780800                               // Expires (7 days from iat)
}
```

**Session Storage**: JWT-only (no database sessions)
**Token Location**: httpOnly cookie (name: `authjs.session-token`)
**Token Expiry**: 7 days
**CSRF Protection**: Enabled by default (Auth.js built-in)

---

#### Authentication Flow

**Login Flow**:
```
1. User submits email + password to login page
2. Frontend calls loginWithAudit() server action
3. Rate limit check (email + IP)
4. Credentials validated via Auth.js
5. Timing-safe password comparison with bcrypt
6. Role validation (must be: process_manager, project_handler, or admin)
7. JWT token created and stored in httpOnly cookie
8. Audit log created (login_success or login_failed)
9. Redirect to callback URL or /dashboard
```

**Session Validation Flow** (on each protected route):
```
1. Middleware checks for authjs.session-token cookie
2. JWT signature validated with NEXTAUTH_SECRET
3. Expiry checked (must be within 7 days)
4. User data extracted from JWT (no database query)
5. Request allowed if valid, redirected to /login if invalid
```

**Logout Flow**:
```
1. User clicks "Sign out" button
2. Frontend calls logoutWithAudit() server action
3. Audit log created (logout event)
4. Auth.js signOut() clears session cookie
5. Redirect to /login page
```

---

#### Error Codes

**Authentication Errors**:
- `CredentialsSignin` - Invalid email or password
- `CallbackRouteError` - Error during authentication callback
- `SessionRequired` - Protected route accessed without valid session

**Custom Error Responses** (from server actions):
```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

```json
{
  "success": false,
  "error": "Too many login attempts from your network. Please try again in 45 minutes.",
  "rateLimitExceeded": true,
  "retryAfterSeconds": 2700
}
```

---

#### Audit Logging

All authentication events are logged to `audit_logs` table:

**Login Success**:
```json
{
  "organizationId": "123e4567-e89b-12d3-a456-426614174001",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "action": "login_success",
  "actionMetadata": {
    "email": "test@qteria.com",
    "name": "Test User"
  },
  "ipAddress": "192.168.1.1",
  "userAgent": "Mozilla/5.0...",
  "createdAt": "2025-11-18T12:00:00.000Z"
}
```

**Login Failed**:
```json
{
  "organizationId": "123e4567-e89b-12d3-a456-426614174001",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "action": "login_failed",
  "actionMetadata": {
    "email": "test@qteria.com",
    "reason": "invalid_credentials"
  },
  "ipAddress": "192.168.1.1",
  "userAgent": "Mozilla/5.0...",
  "createdAt": "2025-11-18T12:00:00.000Z"
}
```

**Logout**:
```json
{
  "organizationId": "123e4567-e89b-12d3-a456-426614174001",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "action": "logout",
  "actionMetadata": {
    "email": "test@qteria.com"
  },
  "ipAddress": "192.168.1.1",
  "userAgent": "Mozilla/5.0...",
  "createdAt": "2025-11-18T12:00:00.000Z"
}
```

---

#### Protected Routes

**Middleware Configuration** (`middleware.ts`):
```typescript
export const config = {
  matcher: [
    "/dashboard/:path*",
    "/workflows/:path*",
    "/assessments/:path*"
  ]
}
```

**Behavior**:
- Unauthenticated requests to protected routes → Redirect to `/login?callbackUrl={original_path}`
- After login, redirect back to original path via callback URL
- Server components can check auth with `await auth()`
- Client components can check auth with `useSession()` (from `next-auth/react`)

---

#### Frontend Usage

**Server Component** (recommended):
```typescript
import { auth } from "@/lib/auth-middleware"
import { redirect } from "next/navigation"

export default async function ProtectedPage() {
  const session = await auth()

  if (!session?.user) {
    redirect("/login")
  }

  // session.user contains: id, email, name, role, organizationId
  return <div>Hello {session.user.email}</div>
}
```

**Client Component**:
```typescript
"use client"
import { useSession } from "next-auth/react"

export default function ClientComponent() {
  const { data: session, status } = useSession()

  if (status === "loading") return <div>Loading...</div>
  if (status === "unauthenticated") return <div>Not logged in</div>

  return <div>Hello {session.user.email}</div>
}
```

**Login Form**:
```typescript
"use client"
import { loginWithAudit } from "@/app/actions/auth"

async function handleSubmit(email: string, password: string) {
  const result = await loginWithAudit(email, password)

  if (result.success) {
    router.push(result.redirectTo)
  } else {
    setError(result.error)
  }
}
```

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
- Authentication: Auth.js setup, `loginWithAudit()` server action, login/dashboard pages
- Workflow builder: `POST /workflows` (with nested buckets + criteria)
- Document upload: `POST /documents` (multipart/form-data)
- Assessment start: `POST /assessments` → polling `GET /assessments/:id`
- Results display: `GET /assessments/:id/results` (evidence links to `GET /documents/:id?page=X`)
- Report export: `POST /assessments/:id/reports` → `GET /reports/:id/download`

### Backend Stories
- Implement endpoints per resource (Workflows, Documents, Assessments, Reports)
- JWT validation middleware for `/v1/*` endpoints (validate Auth.js JWT from cookie)
- Multi-tenancy enforcement (filter by `organizationId` from JWT)
- Celery background job for `POST /assessments` (enqueue AI validation task)
- PDF parsing + Claude API integration in Celery worker
- Evidence extraction (page/section detection)
- Report generation (PDF using ReportLab/WeasyPrint)

**Note**: Authentication (login/logout/session) handled by Auth.js on frontend. Backend only validates JWT tokens.

### Integration Stories
- Generate TypeScript client from OpenAPI spec
- Frontend API client setup (axios interceptors for JWT)
- Error boundary for API errors (401 → redirect to login, 429 → show rate limit message)
- Polling logic for assessments (30s interval, timeout after 15 min)

---

## Endpoint Count Summary

- **Authentication**: 4 endpoints (Auth.js frontend routes)
- **Workflows**: 5 endpoints
- **Documents**: 3 endpoints
- **Assessments**: 6 endpoints
- **Reports**: 5 endpoints
- **Organizations/Users**: 3 endpoints
- **Public**: 1 endpoint

**Total**: 27 endpoints across 6 core resources

**Note**: Authentication is handled by Auth.js (NextAuth) on the frontend (`/api/auth/*`) rather than backend `/v1/auth/*` endpoints.

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
