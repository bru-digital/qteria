# Implement Comprehensive Authentication Testing (Phase 4)

## Context

Following the implementation of authentication in PR #60 and the security improvements in the follow-up PR, we need to add comprehensive test coverage for the authentication system. According to CLAUDE.md requirements:

- **Multi-tenancy security: 100% coverage required**
- **Authentication endpoints: 100% coverage required**
- **Overall target: 70% code coverage**

Currently, we have **0% test coverage** for authentication code.

## Related

- Implements testing requirements from PR #60 code review
- Follows up on security improvements from authentication hardening PR
- Required by: `product-guidelines/09-test-strategy-essentials.md`

## Objectives

Set up testing infrastructure and write comprehensive tests for authentication, authorization, and multi-tenancy security.

## Tasks

### 1. Set Up Vitest Test Infrastructure

**Files to create:**

- `apps/web/vitest.config.ts` - Vitest configuration
- `apps/web/vitest.setup.ts` - Test setup (mocks, global config)
- `apps/web/__tests__/setup.ts` - Test utilities and helpers

**Dependencies to install:**

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Add to `package.json` scripts:**

```json
{
  "test": "vitest run",
  "test:watch": "vitest",
  "test:coverage": "vitest run --coverage"
}
```

**Acceptance criteria:**

- [ ] Vitest configured with Next.js path aliases
- [ ] Test setup includes React Testing Library
- [ ] Can run `npm run test` successfully
- [ ] Coverage reports generated correctly

---

### 2. Write Authentication Unit Tests

**File:** `apps/web/__tests__/auth/login.test.tsx`

**Test cases:**

#### Login Form Tests

- [ ] Login form renders with email and password fields
- [ ] Submit button is disabled while loading
- [ ] Email input has proper validation (required, email format)
- [ ] Password input has proper validation (required)
- [ ] Form submission prevented with missing fields

#### Authentication Flow Tests

- [ ] Login with valid credentials succeeds and redirects to dashboard
- [ ] Login with invalid credentials shows error message
- [ ] Login with non-existent user shows generic error (no user enumeration)
- [ ] Login errors display user-friendly messages
- [ ] Login form shows loading state during authentication

#### Input Sanitization Tests

- [ ] Email is trimmed and lowercased before submission
- [ ] Special characters in email are handled correctly
- [ ] Password is sent as-is (not modified)

#### Callback URL Tests

- [ ] Redirects to dashboard by default after login
- [ ] Redirects to callback URL when provided in query params
- [ ] Handles invalid callback URLs safely

#### Session Persistence Tests

- [ ] Session persists across page refreshes
- [ ] Session data includes: id, email, role, organizationId
- [ ] Session expires after 7 days
- [ ] JWT token stored in httpOnly cookie (not localStorage)

#### Logout Tests

- [ ] Logout clears session successfully
- [ ] Logout redirects to login page
- [ ] Logout triggers audit log creation

---

### 3. Write Rate Limiting Tests

**File:** `apps/web/__tests__/auth/rate-limiting.test.tsx`

**Test cases:**

#### Failed Login Rate Limiting

- [ ] Allows up to 5 failed login attempts per email
- [ ] Blocks 6th failed attempt with rate limit error
- [ ] Error message includes retry-after time
- [ ] Rate limit resets after 15 minutes
- [ ] Successful login resets failed attempt counter
- [ ] Rate limit gracefully degrades if Redis unavailable

#### IP-Based Rate Limiting

- [ ] Allows up to 20 login attempts per IP per hour
- [ ] Blocks 21st attempt with rate limit error
- [ ] Different IPs have independent rate limits
- [ ] Rate limit counter increments on each attempt (success or failure)

---

### 4. Write Multi-Tenancy Security Tests

**File:** `apps/web/__tests__/auth/multi-tenancy.test.tsx`

**Test cases (100% coverage required):**

#### JWT Token Tests

- [ ] JWT includes correct organizationId for logged-in user
- [ ] JWT includes correct userId for logged-in user
- [ ] JWT includes correct role for logged-in user
- [ ] JWT cannot be tampered with (signature validation)
- [ ] Invalid JWT tokens are rejected

#### Role Validation Tests

- [ ] Only valid roles accepted: process_manager, project_handler, admin
- [ ] Invalid role in database prevents login
- [ ] Role validation happens before JWT creation
- [ ] Error logged when invalid role detected

#### Organization Isolation Tests

- [ ] User A cannot access User B's organization data (when implemented)
- [ ] API requests filter by organizationId from JWT (when implemented)
- [ ] Session data includes correct organizationId
- [ ] Cannot forge organizationId in client

---

### 5. Write Audit Logging Tests

**File:** `apps/web/__tests__/auth/audit-logging.test.tsx`

**Test cases:**

#### Login Success Logging

- [ ] Successful login creates audit log entry
- [ ] Audit log includes: userId, organizationId, action="login_success"
- [ ] Audit log includes: ipAddress, userAgent
- [ ] Audit log includes: email in actionMetadata

#### Login Failure Logging

- [ ] Failed login with valid user creates audit log
- [ ] Audit log includes reason: "invalid_credentials"
- [ ] Failed login with non-existent user attempts to log to System org
- [ ] Audit logging failure doesn't break login flow

#### Logout Logging

- [ ] Logout creates audit log entry with action="logout"
- [ ] Audit log includes correct user and organization IDs
- [ ] Audit log created before session cleared

---

### 6. Write Security Tests

**File:** `apps/web/__tests__/auth/security.test.tsx`

**Test cases:**

#### Timing Attack Protection

- [ ] Login with non-existent user takes similar time as wrong password
- [ ] Bcrypt comparison always performed (even for non-existent users)
- [ ] No timing difference reveals user existence

#### Password Security

- [ ] Passwords never logged or exposed in errors
- [ ] Password validation utility rejects common passwords
- [ ] Password validation enforces 12+ character minimum
- [ ] Password validation requires character variety

#### Environment Variable Validation

- [ ] Missing NEXTAUTH_SECRET throws helpful error
- [ ] Missing DATABASE_URL throws helpful error
- [ ] Short NEXTAUTH_SECRET (<32 chars) shows warning
- [ ] Invalid DATABASE_URL format shows warning

---

### 7. Set Up Playwright E2E Tests

**File:** `apps/web/e2e/auth.spec.ts`

**Setup:**

```bash
npm install --save-dev @playwright/test
npx playwright install
```

**Create:** `apps/web/playwright.config.ts`

**Test cases:**

#### Complete Login Flow (E2E)

- [ ] Visit login page at /login
- [ ] Enter valid credentials
- [ ] Click submit button
- [ ] Verify redirect to /dashboard
- [ ] Verify user data displayed on dashboard

#### Session Persistence (E2E)

- [ ] Login successfully
- [ ] Navigate to different pages
- [ ] Refresh page
- [ ] Verify still authenticated (no redirect to login)

#### Route Protection (E2E)

- [ ] Visit /dashboard without authentication
- [ ] Verify redirect to /login
- [ ] Verify callback URL preserved (?callbackUrl=/dashboard)
- [ ] Login and verify redirect back to intended page

#### Complete Logout Flow (E2E)

- [ ] Login successfully
- [ ] Click "Sign out" button
- [ ] Verify redirect to /login
- [ ] Try accessing /dashboard
- [ ] Verify redirect to /login (session cleared)

---

## Test Coverage Requirements

### Target Coverage (from CLAUDE.md)

- **Overall:** 70% code coverage
- **Multi-tenancy security:** 100% (zero tolerance for data leakage)
- **Authentication logic:** 100% (false positives/negatives unacceptable)
- **Audit logging:** 90% (compliance requirement)
- **Rate limiting:** 85%

### Files Requiring Coverage

#### Critical (100% required)

- `apps/web/lib/auth.ts` - Authentication logic
- `apps/web/lib/auth-config-base.ts` - Auth configuration
- `apps/web/lib/audit.ts` - Audit logging
- `apps/web/app/actions/auth.ts` - Server actions

#### High Priority (80-90%)

- `apps/web/lib/rate-limit.ts` - Rate limiting
- `apps/web/lib/password-validation.ts` - Password validation
- `apps/web/lib/env.ts` - Environment validation

#### Medium Priority (70%)

- `apps/web/app/login/page.tsx` - Login UI
- `apps/web/app/dashboard/page.tsx` - Dashboard
- `apps/web/app/dashboard/logout-button.tsx` - Logout UI

---

## Quality Gates (CI/CD)

All PRs must pass:

- ✅ All unit + integration tests pass (<5 min)
- ✅ Code coverage >= 70% (not decreased vs main)
- ✅ E2E smoke tests pass (<10 min)
- ✅ No high/critical security vulnerabilities
- ✅ ESLint, Ruff linting passes
- ✅ TypeScript, MyPy type checking passes

---

## Testing Best Practices

### Mock Strategy

- Mock Prisma database calls with `vitest.mock()`
- Mock Redis client for rate limiting tests
- Mock Auth.js signIn/signOut for unit tests
- Use real Auth.js for E2E tests with test database

### Test Data

- Create test user fixtures with known credentials
- Use unique organization IDs per test to prevent conflicts
- Clean up test data after each test

### Assertion Examples

```typescript
// Authentication
expect(result.success).toBe(true)
expect(result.redirectTo).toBe('/dashboard')

// Multi-tenancy
expect(session.user.organizationId).toBe(testOrg.id)
expect(auditLog.organizationId).toBe(user.organizationId)

// Rate limiting
expect(result.rateLimitExceeded).toBe(true)
expect(result.retryAfterSeconds).toBeGreaterThan(0)
```

---

## Definition of Done

- [ ] All 7 task sections completed
- [ ] Test coverage >= 70% overall
- [ ] Multi-tenancy tests achieve 100% coverage
- [ ] Authentication tests achieve 100% coverage
- [ ] All tests pass in CI/CD
- [ ] E2E tests pass with real browser
- [ ] Test documentation added to README
- [ ] Coverage report generated and reviewed

---

## Estimated Effort

- **Task 1** (Setup): 1-2 hours
- **Task 2** (Auth tests): 3-4 hours
- **Task 3** (Rate limiting): 1-2 hours
- **Task 4** (Multi-tenancy): 2-3 hours
- **Task 5** (Audit logging): 1-2 hours
- **Task 6** (Security): 1-2 hours
- **Task 7** (E2E): 2-3 hours

**Total: 11-18 hours**

---

## References

- CLAUDE.md testing requirements: `product-guidelines/09-test-strategy-essentials.md`
- PR #60 code review comments
- Next.js testing guide: https://nextjs.org/docs/app/building-your-application/testing/vitest
- Playwright docs: https://playwright.dev/
- Vitest docs: https://vitest.dev/

---

## Labels

`testing`, `authentication`, `security`, `high-priority`, `technical-debt`
