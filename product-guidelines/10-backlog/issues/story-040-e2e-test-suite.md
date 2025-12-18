# [STORY-040] E2E Test Suite (Playwright)

**Epic**: EPIC-10 - Testing & Quality Assurance
**Priority**: P0 (MVP Critical)
**Estimated Effort**: 3 days
**Journey Step**: Cross-Cutting - Quality

---

## User Story

**As a** developer
**I want to** have comprehensive E2E tests for the complete user journey
**So that** I can deploy confidently without breaking critical flows

---

## Acceptance Criteria

- [ ] E2E tests cover Journey Steps 1-5 (complete flow)
- [ ] Tests for multi-tenant isolation
- [ ] Tests for role-based access control
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Test suite runs in <30 minutes
- [ ] Smoke tests run in <5 minutes (for CI)
- [ ] E2E test stability >95% (not flaky)

---

## Technical Details

**Tech Stack**:

- Framework: Playwright
- Language: TypeScript
- CI: GitHub Actions

**Test Coverage**:

**1. Complete Assessment Flow**:

```typescript
test('complete assessment flow', async ({ page }) => {
  // Step 1: Login as Process Manager
  await loginAs(page, 'process-manager@tuvsud.com')

  // Step 1: Create workflow
  await page.goto('/workflows/create')
  await page.fill('[name="workflow_name"]', 'Medical Device - Class II')
  await page.click('button:text("Add Bucket")')
  await page.fill('[name="bucket_name"]', 'Technical File')
  await page.click('button:text("Add Criteria")')
  await page.fill('[name="criteria_text"]', 'All documents have valid signatures')
  await page.click('button:text("Save Workflow")')

  // Verify workflow created
  await expect(page.locator('text=Workflow created')).toBeVisible()

  // Step 2: Login as Project Handler
  await loginAs(page, 'handler@tuvsud.com')

  // Step 2: Upload documents
  await page.goto('/assessments/new')
  await page.selectOption('[name="workflow_id"]', { label: 'Medical Device - Class II' })
  await page.setInputFiles('[name="document"]', 'test-fixtures/technical-file.pdf')
  await page.click('button:text("Start Assessment")')

  // Step 3: Poll status
  await expect(page.locator('text=Assessment queued')).toBeVisible()
  await page.waitForSelector('text=Assessment complete', { timeout: 600000 }) // 10 min max

  // Step 3: View results
  await expect(page.locator('text=passed')).toBeVisible()
  await page.click('text=technical-file.pdf (page 3)')

  // Verify PDF opens
  const [newPage] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('text=technical-file.pdf'),
  ])
  await expect(newPage.locator('embed[type="application/pdf"]')).toBeVisible()

  // Step 5: Download report
  await page.click('button:text("Export Report")')
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('button:text("Download Report")'),
  ])
  expect(download.suggestedFilename()).toContain('qteria-report')
})
```

**2. Re-Assessment Flow**:

```typescript
test('re-assessment flow', async ({ page }) => {
  // ... create workflow and run initial assessment ...

  // Step 4: Replace failing document
  await page.click('button:text("Replace Document")')
  await page.setInputFiles('[name="document"]', 'test-fixtures/updated-technical-file.pdf')
  await page.click('button:text("Upload")')

  // Step 4: Re-run assessment
  await page.click('button:text("Re-run Assessment")')
  await page.waitForSelector('text=Assessment complete', { timeout: 600000 })

  // Verify criteria now pass
  await expect(page.locator('text=5/5 criteria passed')).toBeVisible()
})
```

**3. Multi-Tenant Isolation**:

```typescript
test('multi-tenant isolation', async ({ page }) => {
  // Login as User A (TÜV SÜD)
  await loginAs(page, 'user-a@tuvsud.com')
  await createWorkflow(page, 'Workflow A')

  // Login as User B (BSI)
  await loginAs(page, 'user-b@bsi.com')
  await page.goto('/workflows')

  // Verify User B cannot see Workflow A
  await expect(page.locator('text=Workflow A')).not.toBeVisible()
})
```

**4. Role-Based Access Control**:

```typescript
test('RBAC - project handler cannot create workflows', async ({ page }) => {
  // Login as Project Handler
  await loginAs(page, 'handler@tuvsud.com')

  // Attempt to create workflow
  await page.goto('/workflows/create')

  // Verify 403 Forbidden or redirect
  await expect(page.locator('text=Access denied')).toBeVisible()
})

test('RBAC - process manager can create workflows', async ({ page }) => {
  // Login as Process Manager
  await loginAs(page, 'manager@tuvsud.com')

  // Create workflow
  await page.goto('/workflows/create')
  await expect(page.locator('form')).toBeVisible()
})
```

**CI Integration** (GitHub Actions):

```yaml
# .github/workflows/e2e-tests.yml

name: E2E Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  e2e-smoke:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Node.js
      - Install dependencies
      - Install Playwright browsers
      - Run smoke tests (critical flows only, <5 min)

  e2e-full:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' # Only on merge
    steps:
      - Checkout code
      - Setup Node.js
      - Install dependencies
      - Install Playwright browsers
      - Run full E2E suite (<30 min)
```

---

## RICE Score

**RICE**: (100 × 3 × 0.90) ÷ 3 = **90**

---

## Definition of Done

- [ ] E2E tests cover Journey Steps 1-5
- [ ] Multi-tenant isolation tests pass
- [ ] RBAC tests pass
- [ ] Cross-browser tests pass (Chrome, Firefox, Safari)
- [ ] Smoke tests run in <5 minutes
- [ ] Full suite runs in <30 minutes
- [ ] Test stability >95% (not flaky)
- [ ] CI integration working (GitHub Actions)
- [ ] Tests run on every PR
- [ ] Code reviewed and merged

---

## Notes

E2E tests are NON-NEGOTIABLE in compliance industry. False negatives (missed issues) would destroy trust and reputation with TÜV SÜD.

**Reference**: `product-guidelines/09-test-strategy.md`
