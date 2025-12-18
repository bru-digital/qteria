# E2E Testing - Follow-up Task

## Overview

The code review identified the need for E2E tests to verify admin page authorization. This document outlines the required test coverage.

## Required Test Coverage (P0 - Security Critical)

### 1. Admin Page Authorization Tests

Test that admin pages properly enforce role-based access control at runtime.

**Test Cases:**

- `/admin/users` - Should redirect non-admin/non-process-manager to `/dashboard`
- `/admin/settings` - Should redirect non-admin/non-process-manager to `/dashboard`
- `/admin/audit-logs` - Should redirect non-admin/non-process-manager to `/dashboard`
- Admin users should have access to all admin pages
- Process managers should have access to all admin pages

### 2. TopNav Role-Based Rendering Tests

Test that the TopNav component correctly shows/hides admin navigation based on user role.

**Test Cases:**

- Admin users should see "Admin" dropdown menu
- Process managers should see "Admin" dropdown menu
- Project handlers should NOT see "Admin" dropdown menu

### 3. Multi-Tenancy Security Tests (100% Coverage Required)

Per CLAUDE.md: "Zero tolerance for data leakage between organizations"

**Test Cases:**

- User from Org A cannot access workflows from Org B
- User from Org A cannot access assessments from Org B
- API requests with spoofed organization_id should fail with 403

## Implementation Plan

### Setup Required

1. **Install Playwright**

   ```bash
   cd apps/web
   npm install -D @playwright/test
   npx playwright install
   ```

2. **Create Test Database**
   - Use separate Neon database instance for E2E tests
   - Seed with test users in different organizations
   - Configure DATABASE_URL in `.env.test`

3. **Authentication Helper**
   - Create `tests/helpers/auth.ts` with login helpers for different roles
   - Mock NextAuth session for E2E tests

4. **Test Structure**
   ```
   apps/web/
     tests/
       e2e/
         admin-authorization.spec.ts
         topnav-rbac.spec.ts
         multi-tenancy.spec.ts
       helpers/
         auth.ts
         db.ts
   ```

## Example Test

```typescript
// tests/e2e/admin-authorization.spec.ts
import { test, expect } from '@playwright/test'
import { loginAs } from '../helpers/auth'

test.describe('Admin Page Authorization', () => {
  test('project handler cannot access admin users page', async ({ page }) => {
    await loginAs(page, 'project_handler')
    await page.goto('/admin/users')
    await expect(page).toHaveURL('/dashboard')
  })

  test('admin can access admin users page', async ({ page }) => {
    await loginAs(page, 'admin')
    await page.goto('/admin/users')
    await expect(page).toHaveURL('/admin/users')
    await expect(page.locator('h1')).toContainText('User Management')
  })

  test('process manager can access admin users page', async ({ page }) => {
    await loginAs(page, 'process_manager')
    await page.goto('/admin/users')
    await expect(page).toHaveURL('/admin/users')
  })
})
```

## Current Status

### ✅ Implemented

- Server-side authorization checks in all admin pages
- RBAC utility functions with 100% unit test coverage
- Proper TypeScript typing for user roles

### ⚠️ Missing

- E2E tests to verify authorization at runtime
- Multi-tenancy security tests
- Integration tests for role-based UI rendering

## Priority

**P0 - Security Critical** - Should be implemented before production launch.

## Estimated Effort

- Playwright setup: 2 hours
- Admin authorization tests: 2-3 hours
- Multi-tenancy tests: 3-4 hours
- Total: ~8 hours

## References

- CLAUDE.md: Testing Strategy (line 324)
- Code Review: PR #114 (December 8, 2025)
- RBAC Implementation: `apps/web/lib/rbac.ts`
