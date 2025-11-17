---
description: Session 8 - Generate comprehensive API contracts with OpenAPI specification
---

# Generate API Contracts (Session 8)

You are helping the user create comprehensive API contracts including OpenAPI/Swagger specifications, endpoint definitions, request/response schemas, authentication patterns, and error handling. This happens after defining the database schema (Session 7), but BEFORE generating the backlog, so that backlog items can be informed by the API surface area.

## When to Use This

**This is Session 8** in the core Stack-Driven cascade. Run it:
- After Session 7 (`/design-database-schema` - data model)
- Before Session 10 (`/generate-backlog` - implementation planning)
- When you need to define your API contracts based on journey, architecture, and data model

**Skip this** if:
- You're building a frontend-only application (no backend)
- Your product doesn't expose APIs
- You prefer to evolve APIs incrementally during development

## Your Task

Create comprehensive API contracts including:
- OpenAPI 3.0 specification
- Endpoint definitions with HTTP methods, paths, and parameters
- Request and response schemas with validation rules
- Authentication and authorization patterns
- Error handling and status codes
- Rate limiting and pagination strategies
- Versioning approach
- API documentation with examples

---

## Process

### Step 1: Read Previous Outputs

**Required inputs:**

```
Read: product-guidelines/00-user-journey.md
Read: product-guidelines/02-tech-stack.md
Read: product-guidelines/04-architecture.md
Read: product-guidelines/07-database-schema-essentials.md (from previous session)
```

**Context Optimization**: We read the essentials version of database schema for significant context reduction (~56% smaller). It contains table list, ERD, relationships, and data access patterns—sufficient for API design without column details, indexes, and migrations.

**Optional inputs (if available):**

```
Read: product-guidelines/10-backlog/BACKLOG.md (if exists - backlog comes after API contracts in Session 10)
Read: product-guidelines/12-project-scaffold.md (if exists - scaffold comes after in Session 12)
```

**Extract from Journey**:
- What user actions require API endpoints?
- What data flows through the system?
- What are the critical path operations?
- What integration points exist with external systems?

**Extract from Tech Stack**:
- Backend framework (FastAPI, Express, NestJS, Django, etc.)
- Authentication method (JWT, OAuth, API keys, Clerk, Auth0)
- API style preference (REST, GraphQL, gRPC)
- Documentation tools (Swagger UI, Redoc, Postman)

**Extract from Architecture**:
- API design patterns (REST principles, HATEOAS, etc.)
- Security requirements
- Rate limiting strategy
- Caching approach
- Multi-tenancy implementation

**Extract from Backlog (if available)**:
- What features need what endpoints?
- What data operations are required (CRUD, search, bulk)?
- What integrations are planned (webhooks, third-party APIs)?
- Note: Backlog is generated AFTER this session, so focus on journey and architecture if backlog doesn't exist yet

**Extract from Database Schema (required):**
- What entities exist?
- What relationships need API exposure?
- What query patterns should be supported?

**Example**: compliance-saas needs document upload, framework selection, assessment results, report sharing → FastAPI REST API with JWT auth, multi-tenant, rate-limited

---

### Step 2: Identify Core Resources

**Decision Tree - Resource Identification:**

```
For each entity in database schema or backlog, ask:

1. Does this entity need CRUD operations via API?
   - YES → Create resource endpoints (/api/resources)
   - NO → Skip or create specialized endpoints only

2. Is this a user-owned resource?
   - YES → Add authentication + ownership filtering
   - NO → It's a system resource (may be public or admin-only)

3. Does this resource have relationships?
   - YES → Decide on nested routes vs query params
   - NO → Simple flat resource structure

4. Does this resource need special operations beyond CRUD?
   - YES → Add custom action endpoints
   - NO → Standard REST operations suffice
```

**Example**: compliance-saas journey → Resources: `/api/documents` (upload, CRUD), `/api/frameworks` (read-only), `/api/assessments` (create, poll status, results), `/api/teams` (multi-tenancy), special endpoints for sharing (`/api/assessments/:id/share`, `/public/reports/:token`)

---

### Step 3: Define Endpoint Structure

**Endpoint Naming Conventions:**

**Decision Tree - REST Resource Design:**

```
1. What type of operation?
   ├─ CRUD on collection → Use standard REST verbs
   │  - GET /api/resources (list)
   │  - POST /api/resources (create)
   │  - GET /api/resources/:id (read)
   │  - PUT /api/resources/:id (update)
   │  - DELETE /api/resources/:id (delete)
   │
   ├─ Action on resource → Use POST with action name
   │  - POST /api/resources/:id/action
   │  - Example: POST /api/assessments/:id/cancel
   │
   └─ Complex query → Use GET with query params
      - GET /api/resources?filter=value&sort=field
      - Example: GET /api/documents?status=ready&sort=-created_at

2. Should endpoints be nested?
   ├─ Strong parent-child relationship → Nest
   │  - GET /api/documents/:id/assessments
   │  - "Get all assessments for this document"
   │
   └─ Loose relationship → Flat with filtering
      - GET /api/assessments?document_id=123
      - "Get assessments, optionally filtered by document"
```

**Example**: compliance-saas endpoints:
- Documents: GET/POST `/api/documents`, GET/DELETE `/api/documents/:id`
- Frameworks: GET `/api/frameworks`, GET `/api/frameworks/:id`
- Assessments: GET/POST `/api/assessments`, GET/POST `/api/assessments/:id/{cancel,share}`
- Public: GET `/public/reports/:token` (no auth)
- Teams: GET/PATCH `/api/teams/:id`, GET `/api/teams/:id/usage`

---

### Step 4: Define Request and Response Schemas

For EACH endpoint, define:
- **Request schema** (path params, query params, headers, body)
- **Response schema** (success and error cases)
- **Validation rules** (required fields, formats, constraints)

**Decision Tree - Schema Design:**

```
1. What data format?
   ├─ Simple CRUD → JSON request/response
   ├─ File upload → multipart/form-data
   ├─ Bulk operations → JSON array or newline-delimited JSON
   └─ Real-time updates → WebSocket or Server-Sent Events

2. What validation is needed?
   ├─ Required fields → Mark as required in schema
   ├─ Format validation → Use JSON Schema formats (email, url, uuid)
   ├─ Business rules → Document in description, implement in backend
   └─ Cross-field validation → Note dependencies in schema

3. How to handle pagination?
   ├─ Offset-based → ?page=1&limit=20
   ├─ Cursor-based → ?cursor=xyz&limit=20 (better for large datasets)
   └─ Default: Cursor-based if >10K records expected, else offset

4. How to handle errors?
   ├─ Use standard HTTP status codes
   ├─ Consistent error response format
   └─ Include actionable error messages
```

**Example schemas:**

```yaml
# Document Upload
POST /api/documents (multipart/form-data)
→ 201: {id, name, fileSize, status, uploadedAt, userId, frameworks}
→ 400: {error: {code: "INVALID_FILE_TYPE", message, field}}
→ 413: {error: {code: "FILE_TOO_LARGE", message, limit, received}}

# Assessment Status
GET /api/assessments/:id
→ 200: {id, documentId, status, progress, frameworks, results: {score, findings[], summary}, timing}
→ 404: {error: {code: "ASSESSMENT_NOT_FOUND", message}}
```

---

### Step 5: Define Authentication and Authorization

**Authentication Strategy:**

**Decision Tree - Auth Method:**

```
From tech stack, determine auth method:

1. What's the auth provider?
   ├─ Clerk → Use Clerk session tokens
   ├─ Auth0 → Use Auth0 JWT
   ├─ Custom JWT → Implement JWT signing/verification
   ├─ API Keys → Implement API key management
   └─ OAuth 2.0 → Implement OAuth flow

2. Where is the token sent?
   ├─ Header → Authorization: Bearer <token> (recommended)
   ├─ Cookie → Set-Cookie with HttpOnly, Secure flags
   └─ Query param → ?api_key=xxx (only for public read endpoints)

3. What's the token lifetime?
   ├─ Short-lived (15min-1hr) + refresh token → High security
   ├─ Medium (1-7 days) → Balance
   └─ Long-lived (30+ days) → Convenience over security

4. How to handle authorization?
   ├─ User owns resource → Check userId matches
   ├─ Team resource → Check user belongs to team
   ├─ Admin only → Check user role
   └─ Public → No auth required
```

**Example auth**: Clerk JWT in `Authorization: Bearer <token>` header, applied to all endpoints except `/public/*`

**Authorization patterns:**
- User-owned: `WHERE user_id = :current_user_id`
- Team resource: `WHERE team_id = :current_user_team_id`
- Admin only: `WHERE role = 'admin' OR team_id = :id`
- Rate limit: Check `usage < plan_limits`

---

### Step 6: Define Error Handling

**Error Response Format:**

**Standardize all errors:**

```json
{
  "error": {
    "code": "ERROR_CODE",              // Machine-readable constant
    "message": "Human-readable error", // User-facing message
    "details": {},                     // Optional: additional context
    "field": "fieldName",              // Optional: which field caused error
    "requestId": "req_abc123"          // Optional: for support debugging
  }
}
```

**HTTP Status Codes:**

```
Success:
200 OK           - Successful GET, PATCH, DELETE
201 Created      - Successful POST (resource created)
202 Accepted     - Async operation started
204 No Content   - Successful DELETE (no body)

Client Errors:
400 Bad Request          - Invalid input (validation failed)
401 Unauthorized         - Missing or invalid auth token
403 Forbidden            - Valid token but insufficient permissions
404 Not Found            - Resource doesn't exist
409 Conflict             - Resource state conflict (e.g., duplicate)
413 Payload Too Large    - Request body/file too large
422 Unprocessable Entity - Semantic error (valid format, invalid business logic)
429 Too Many Requests    - Rate limit exceeded

Server Errors:
500 Internal Server Error - Unexpected server error
502 Bad Gateway           - Upstream service failed
503 Service Unavailable   - Temporary unavailable (maintenance, overload)
504 Gateway Timeout       - Upstream service timeout
```

**Example errors**: All use format `{error: {code, message, details?, field?, requestId?}}`
- 400: `VALIDATION_ERROR` (invalid input)
- 401: `INVALID_TOKEN` (auth failed)
- 429: `RATE_LIMIT_EXCEEDED` (includes limit, remaining, resetAt)
- 422: `INSUFFICIENT_CREDITS` (business logic error)

---

### Step 7: Define Rate Limiting and Pagination

**Rate Limiting Strategy:**

**Decision Tree - Rate Limiting:**

```
1. What's the pricing model?
   ├─ Free tier → Aggressive limits (10 req/min)
   ├─ Paid tier → Generous limits (100-1000 req/min)
   └─ Enterprise → Custom limits or no limits

2. What's the limiting strategy?
   ├─ Per user → Limit by user_id
   ├─ Per team → Limit by team_id (better for multi-user teams)
   ├─ Per IP → Limit by IP (for unauthenticated endpoints)
   └─ Sliding window → More accurate than fixed window

3. What endpoints need stricter limits?
   ├─ Expensive operations (AI, file processing) → Lower limit
   ├─ Read operations (GET) → Higher limit
   └─ Public endpoints → Strictest limit (prevent abuse)
```

**Example**: Headers `X-RateLimit-{Limit,Remaining,Reset}` on all responses. Limits by tier: Free (100 req/min), Pro (1000 req/min), Enterprise (unlimited). Expensive ops (uploads, assessments) have stricter per-hour/day limits.

**Pagination Strategy:**

**Decision Tree - Pagination:**

```
1. How many total records?
   ├─ <1K records → Simple offset pagination
   ├─ 1K-100K records → Cursor pagination (recommended)
   └─ >100K records → Cursor + search optimization

2. Do results change frequently?
   ├─ YES → Cursor pagination (stable)
   ├─ NO → Offset pagination (simpler)

3. Do users need random page access?
   ├─ YES → Offset pagination (supports page=5)
   ├─ NO → Cursor pagination (next/previous only)
```

**Example**: Cursor-based for large datasets (`?cursor=abc&limit=20` → `{data[], pagination: {nextCursor, prevCursor, hasMore}}`), offset-based for small datasets (`?page=1&limit=20` → `{data[], pagination: {page, limit, total, totalPages}}`)

---

### Step 8: Generate OpenAPI Specification

Create complete OpenAPI 3.0 specification. Use template at `templates/08-api-contracts-template.md` for detailed structure.

**Key sections to include:**
- `info`: title, description (with auth/rate limit/error conventions), version, contact
- `servers`: production, staging, local development URLs
- `tags`: group endpoints by resource type
- `paths`: each endpoint with summary, description, tags, security, parameters, requestBody, responses
- `components`: securitySchemes (bearerAuth), schemas (all data models), responses (reusable error responses)

**Best practices:**
- Use `$ref` for reusable schemas and responses
- Include examples in schemas
- Mark required fields explicitly
- Use JSON Schema validation (formats, min/max, enums)
- Document all error responses (4xx, 5xx)

---

### Step 9: Document API Design Decisions

Write `product-guidelines/08-api-contracts.md` with:
- **Overview**: API style, base URLs, versioning strategy, endpoint count
- **Authentication**: Method and how to use it
- **Core Resources**: For each resource: purpose (journey connection), endpoints table, key design decisions
- **Patterns**: Rate limiting, error handling, pagination
- **OpenAPI Spec**: Link to `openapi.yaml` file
- **Testing**: Example curl/httpie commands
- **"What We DIDN'T Choose"**: Alternatives considered (GraphQL, gRPC, etc.) with reasoning

---

### Step 10: Create Essentials Version for Backlog Generation

**IMPORTANT**: Create a condensed essentials version optimized for Session 10 (backlog generation).

Use template at `templates/08-api-contracts-essentials-template.md` to create `product-guidelines/08-api-contracts-essentials.md` with:

**What to include** (target: 100-150 lines):
- API configuration (style, auth, pagination, rate limiting)
- Endpoint lists organized by journey step
- Brief description for each endpoint (one line)
- Common patterns (pagination params, response codes)
- Story scoping guidance for backlog generation

**What to EXCLUDE** (these belong in full `08-api-contracts.md`):
- Complete OpenAPI 3.0 specification
- Request/response schemas
- Error response definitions
- Authentication flow details
- Component schemas
- Example requests/responses
- Validation rules
- Rate limit headers

**Why**: Session 10 (backlog generation) only needs the endpoint list to create stories. Loading the full 782-line OpenAPI spec bloats context by ~3,128 tokens when only ~280 tokens are needed.

**Format**:
```markdown
# API Contracts Essentials (For Backlog Generation)

> See `08-api-contracts.md` for complete OpenAPI 3.0 specification

## API Configuration
- API Style: [REST/GraphQL]
- Authentication: [JWT/OAuth]
...

## Endpoints by Journey Step

### Authentication (Journey Step 0)
- `POST /api/auth/login` - User login
...

### [Resource] Endpoints (Journey Step X)
- `POST /api/[resource]` - Create [resource]
- `GET /api/[resource]` - List [resource] (paginated)
...
```

---

### Step 11: Validate API Design

**Quality Checklist:**

**Journey Alignment:**
- [ ] All journey actions have corresponding API endpoints
- [ ] Critical path (Steps 1-3) fully supported by API
- [ ] No endpoints that don't serve journey steps
- [ ] API enables all features in backlog

**Consistency:**
- [ ] Naming conventions consistent (camelCase vs snake_case)
- [ ] Error format consistent across all endpoints
- [ ] Pagination format consistent
- [ ] Authentication method consistent

**Completeness:**
- [ ] All CRUD operations defined where needed
- [ ] All request schemas have validation rules
- [ ] All responses include success and error cases
- [ ] Authentication and authorization documented
- [ ] Rate limiting specified
- [ ] Error codes documented

**Tech Stack Alignment:**
- [ ] API style matches tech stack decision (REST/GraphQL/etc.)
- [ ] Auth method matches tech stack choice
- [ ] Framework-specific features leveraged
- [ ] OpenAPI format compatible with chosen tools

**Security:**
- [ ] Authentication required on protected endpoints
- [ ] Authorization checks documented
- [ ] Sensitive data not exposed in URLs
- [ ] Rate limiting prevents abuse
- [ ] CORS policy considered
- [ ] HTTPS enforced in production

**Performance:**
- [ ] Pagination prevents large payloads
- [ ] Heavy operations are async (return 202 Accepted)
- [ ] Caching headers specified for cacheable endpoints
- [ ] File uploads support chunking/resumable uploads

---

## What We DIDN'T Choose (And Why)

### GraphQL API
**What**: Query language letting clients request exact data needed
**Why not**: Journey has simple CRUD (not complex graphs), team knows REST better, no over-fetching problem
**Reconsider if**: Mobile app needs bandwidth optimization, UI needs highly variable data shapes, 50+ optional fields per entity

### gRPC API
**What**: High-performance RPC with Protocol Buffers (binary)
**Why not**: Web-based journey (browsers need grpc-web proxy), no network bottleneck, REST/JSON easier to debug
**Reconsider if**: Microservices with service-to-service calls, need bidirectional streaming, internal-only APIs

### Header-Based API Versioning
**What**: Version in `Accept: application/vnd.myapi.v2+json` header instead of URL
**Why not**: URL versioning (`/v1/`, `/v2/`) is simpler, more explicit, easier to debug
**Reconsider if**: Building hypermedia API (HATEOAS), version applies to entire surface

### Full OAuth 2.0 Server
**What**: OAuth with authorization code flow, client credentials, refresh tokens
**Why not**: B2B SaaS uses Clerk/Auth0 (not app authorization), high complexity, no third-party app integrations yet
**Reconsider if**: Building platform with third-party apps (Slack/GitHub-style), need programmatic API access

### WebSocket for Real-Time
**What**: Persistent bidirectional connection
**Why not**: Polling every 2-5 seconds is acceptable for document processing, WebSocket adds complexity (scaling, connection mgmt)
**Reconsider if**: Need <500ms updates (real-time collab), many users watching same resource, mobile app (battery)

### API Gateway (Kong, AWS)
**What**: Centralized gateway for rate limiting, auth, logging, routing
**Why not**: MVP stage (single service), framework middleware sufficient, operational complexity, cost
**Reconsider if**: Microservices architecture, advanced rate limiting needs, detailed API analytics

---

## Setup Instructions

**FastAPI**: `pip install fastapi[all]` → auto-generated docs at `/docs` (Swagger) and `/redoc`
**Express**: `npm i swagger-ui-express yamljs` → serve with `app.use('/api-docs', swaggerUi.setup(openapi))`
**Django**: `pip install drf-spectacular` → configure in settings → `python manage.py spectacular`
**Client SDKs**: Use `openapi-generator-cli generate -i openapi.yaml -g typescript-axios` (or python, java, etc.)

---

## Output Files

1. **`product-guidelines/08-api-contracts.md`**: Full documentation (architecture, design decisions, endpoints, auth, errors, testing, OpenAPI spec)
2. **`product-guidelines/08-api-contracts-essentials.md`**: Condensed version for Session 10 (backlog generation) - endpoint lists only (~150 lines)
3. **`product-guidelines/08-api-contracts/openapi.yaml`**: Complete OpenAPI 3.0 spec (all endpoints, schemas, security)
4. **`product-guidelines/08-api-contracts/postman-collection.json`** (optional): Postman/Insomnia collection with pre-configured requests

---

## Quality Checklist

Before completing this session, verify:

**Journey Alignment:**
- [ ] All user actions from journey have API endpoints
- [ ] Critical path (journey steps 1-3) fully supported
- [ ] No endpoints exist that don't serve a journey step
- [ ] API enables all features in backlog

**Completeness:**
- [ ] All CRUD operations defined where needed
- [ ] Request and response schemas complete
- [ ] Validation rules specified
- [ ] Error cases documented
- [ ] Authentication and authorization clear
- [ ] Rate limiting and pagination specified

**Technical Quality:**
- [ ] OpenAPI 3.0 specification valid (use validator)
- [ ] Consistent naming conventions
- [ ] Consistent error format
- [ ] HTTP status codes used correctly
- [ ] Security best practices followed (HTTPS, auth, rate limits)

**Tech Stack Alignment:**
- [ ] API style matches tech stack decision
- [ ] Auth method from tech stack implemented
- [ ] Framework-specific patterns leveraged
- [ ] Documentation tool compatible with stack

**Documentation:**
- [ ] "What We DIDN'T Choose" section complete (3+ alternatives)
- [ ] Each endpoint has purpose explanation
- [ ] Design decisions reference journey
- [ ] Testing examples provided
- [ ] Setup instructions clear

**Essentials Version (for backlog generation):**
- [ ] Essentials file created at `08-api-contracts-essentials.md`
- [ ] All endpoints listed with journey step mapping
- [ ] File is 100-200 lines (not bloated with schemas)
- [ ] Includes API config, pagination patterns, response codes
- [ ] References full file for complete specification

---

## After This Session

**Next steps**: Copy `openapi.yaml` to project → set up Swagger/ReDoc UI → generate client SDKs → implement endpoints → write API tests

**Use contracts for**: Backend implementation, frontend dev (know available APIs), API docs, client SDK generation, contract testing

**Future extensions**: Webhooks for async events, GraphQL layer if complexity grows, API versioning for breaking changes, API gateway for microservices

---

## Remember

**Every endpoint must serve the user journey.**

Don't create endpoints "just in case". Design APIs based on:
1. What user actions require API support? → Endpoints
2. What data flows through the system? → Schemas
3. How do users interact with features? → Request/response patterns
4. What security is needed? → Auth and rate limiting

If you can't trace an endpoint back to a journey step or backlog feature, you probably don't need it.

**Reference files:**
- Journey: `product-guidelines/00-user-journey.md`
- Tech stack: `product-guidelines/02-tech-stack.md`
- Architecture: `product-guidelines/04-architecture.md`
- Database schema: `product-guidelines/07-database-schema.md` (from previous session)
- Backlog: `product-guidelines/10-backlog/BACKLOG.md` (generated AFTER this session in Session 10)

---

**Now, read previous outputs and design API contracts that serve your users' journey!**
