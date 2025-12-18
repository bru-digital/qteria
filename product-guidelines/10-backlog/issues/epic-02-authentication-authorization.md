# [EPIC-02] Authentication & Authorization

**Type**: Epic
**Journey Step**: Foundation (Secures All Access)
**Priority**: P0 (Critical - Blocks All User Features)

---

## Epic Overview

Implement secure user authentication with Auth.js (NextAuth), JWT-based session management, role-based access control (RBAC), and multi-tenant isolation. Every authenticated endpoint must verify user identity and enforce permissions.

**Value**: Secure access control ensures only authorized users can access workflows and assessments, with organization-level data isolation (TÜV SÜD cannot see BSI data).

---

## Success Criteria

- [ ] Users can log in with email/password or Google OAuth
- [ ] JWT tokens issued and validated on every API request
- [ ] RBAC enforced (Process Manager, Project Handler, Admin roles)
- [ ] Multi-tenancy enforced (users only see their organization's data)
- [ ] Sessions persist across browser refreshes
- [ ] Logout invalidates tokens
- [ ] Password reset flow working (optional for MVP)

---

## Stories in This Epic

### STORY-005: User Login with Auth.js [P0, 2 days]

Implement Auth.js (NextAuth) authentication with email/password provider, JWT sessions, and login/logout flows. Store sessions in PostgreSQL.

**RICE**: R:100 × I:3 × C:100% ÷ E:2 = **150**

### STORY-006: Google OAuth Integration [P1, 1 day]

Add Google OAuth provider to Auth.js for easy enterprise SSO. Users can "Sign in with Google" for frictionless onboarding.

**RICE**: R:80 × I:2 × C:80% ÷ E:1 = **128**

### STORY-007: Role-Based Access Control (RBAC) [P0, 2 days]

Implement role checking in FastAPI middleware. Roles: `process_manager` (can create/edit workflows), `project_handler` (can run assessments), `admin` (full access).

**RICE**: R:100 × I:2 × C:100% ÷ E:2 = **100**

### STORY-008: Multi-Tenant Isolation Middleware [P0, 1 day]

Create FastAPI middleware that extracts `organization_id` from JWT and filters all database queries by organization. Ensures TÜV SÜD cannot see BSI data.

**RICE**: R:100 × I:3 × C:100% ÷ E:1 = **300** (Critical for data security)

---

## Total Estimated Effort

**6 person-days** (1.5 weeks for solo founder)

**Breakdown**:

- Frontend: 1.5 days (login UI, Auth.js setup)
- Backend: 3 days (JWT validation, RBAC, multi-tenancy)
- Testing: 1.5 days (security tests - 100% coverage required)

---

## Dependencies

**Blocks**:

- EPIC-03: Workflow Management (requires authenticated users)
- EPIC-04: Document Processing (requires authenticated uploads)
- ALL user-facing features (everything needs auth)

**Blocked By**:

- STORY-001: Database schema (needs users, organizations tables)

---

## Technical Approach

**Tech Stack**:

- Frontend Auth: Auth.js (NextAuth) in Next.js
- Backend Auth: JWT validation in FastAPI middleware
- Session Storage: PostgreSQL (NextAuth database adapter)
- OAuth Provider: Google (for enterprise SSO)

**Authentication Flow**:

1. User enters email/password on login page (Next.js)
2. Auth.js validates credentials, creates session in PostgreSQL
3. JWT token returned to frontend (stored in httpOnly cookie)
4. Every API request includes JWT in `Authorization: Bearer <token>` header
5. FastAPI middleware validates JWT, extracts user_id + organization_id
6. All database queries filtered by organization_id

**JWT Token Payload**:

```json
{
  "sub": "user_123",
  "org_id": "org_tuv_sud",
  "email": "handler@tuvsud.com",
  "role": "project_handler"
}
```

**Role Permissions**:

- `process_manager`: Create/edit/delete workflows, view assessments
- `project_handler`: Upload documents, start assessments, view results
- `admin`: All permissions + user management

**Reference**: `product-guidelines/08-api-contracts.md` for auth endpoints

---

## Success Metrics

**Security Metrics**:

- 100% of authenticated endpoints check JWT validity
- 100% of queries filtered by organization_id
- Zero unauthorized access incidents

**User Experience Metrics**:

- Login success rate: >95%
- Session persistence: >99% (users stay logged in across refreshes)
- OAuth success rate: >90% (Google login works reliably)

---

## Definition of Done

- [ ] Login page UI working (email/password)
- [ ] Google OAuth flow working
- [ ] JWT tokens issued and validated
- [ ] RBAC enforced on protected endpoints (403 for insufficient role)
- [ ] Multi-tenancy tested (org A cannot see org B data)
- [ ] Session persists across browser refreshes
- [ ] Logout invalidates token
- [ ] Security tests pass (100% coverage)
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: JWT token leaked (XSS attack)

- **Mitigation**: Store JWT in httpOnly cookie (not localStorage), implement CSRF protection

**Risk**: Multi-tenancy filter bypassed (user sees other org's data)

- **Mitigation**: Enforce at middleware level (automatic filtering), 100% test coverage

**Risk**: Auth.js configuration errors (sessions not persisting)

- **Mitigation**: Test thoroughly with database adapter, follow Next.js auth best practices

---

## Testing Requirements

**Security Tests** (100% coverage required):

- [ ] Unauthenticated request returns 401
- [ ] Invalid JWT returns 401
- [ ] Expired JWT returns 401
- [ ] Insufficient role returns 403 (project_handler tries to delete workflow)
- [ ] Multi-tenant isolation (user A cannot GET user B's workflows)
- [ ] Admin role can access all endpoints
- [ ] Process manager can create workflows, project handler cannot

**Integration Tests**:

- [ ] Login with email/password works
- [ ] Login with Google OAuth works
- [ ] Session persists across refreshes
- [ ] Logout invalidates session

**E2E Tests**:

- [ ] Complete login → dashboard flow
- [ ] Role-based UI (process manager sees "Create Workflow", project handler doesn't)

---

## Next Epic

After completing this epic, proceed to **EPIC-03: Workflow Management** to enable Process Managers to create validation workflows.
