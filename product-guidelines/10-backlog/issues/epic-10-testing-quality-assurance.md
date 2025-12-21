# [EPIC-10] Testing & Quality Assurance

**Type**: Epic
**Journey Step**: Cross-Cutting (Protects All Features)
**Priority**: P0/P1 (Critical for Reliability)

---

## Epic Overview

Implement comprehensive test suite (unit, integration, E2E) and CI/CD automation to ensure code quality, prevent regressions, and maintain "it just works" reliability principle. Testing is non-negotiable in compliance industry.

**User Value**: Users trust Qteria because it's reliable - false negatives (missed issues) would destroy trust and reputation in certification industry.

---

## Success Criteria

- [ ] Code coverage >70% overall (95% for critical AI logic)
- [ ] All tests run in CI/CD (GitHub Actions)
- [ ] E2E tests cover complete user journey (Steps 1-5)
- [ ] Performance benchmarks tracked
- [ ] No high/critical security vulnerabilities
- [ ] Test suite runs in <10 minutes

---

## Stories in This Epic

### STORY-040: E2E Test Suite (Playwright) [P0, 3 days]

Implement E2E tests for complete user journey: Login → Create workflow → Upload documents → Start assessment → View results → Download report. Use Playwright for cross-browser testing.

**RICE**: R:100 × I:3 × C:90% ÷ E:3 = **90**

### STORY-041: CI/CD Pipeline (GitHub Actions) [P0, 2 days]

Set up GitHub Actions workflow: Run tests on PR, enforce coverage >70%, deploy to staging on merge to main, deploy to production on release tag.

**RICE**: R:100 × I:2 × C:100% ÷ E:2 = **100**

---

## Total Estimated Effort

**5 person-days** (1 week for solo founder)

**Breakdown**:

- Testing: 3 days (E2E suite, coverage)
- DevOps: 2 days (CI/CD setup)

---

## Dependencies

**Blocks**: Nothing (enables safe development)

**Blocked By**: Nothing (can start anytime, but best after core features built)

---

## Technical Approach

**Tech Stack**:

- Unit Tests: pytest (backend), Vitest (frontend)
- Integration Tests: FastAPI TestClient, pytest-postgresql
- E2E Tests: Playwright (cross-browser)
- CI/CD: GitHub Actions
- Coverage: pytest-cov, Vitest coverage

**E2E Test Coverage** (STORY-040):

1. **Test: Complete Assessment Flow**

   - Login as Process Manager
   - Create workflow with 2 buckets, 3 criteria
   - Login as Project Handler
   - Upload 3 documents
   - Start assessment
   - Poll status until completed
   - View results (pass/fail with evidence)
   - Download report

2. **Test: Re-assessment Flow**

   - View failed assessment
   - Replace failing document
   - Re-run assessment
   - Verify criteria now pass

3. **Test: Multi-Tenant Isolation**

   - Login as User A (org TÜV SÜD)
   - Create workflow
   - Login as User B (org BSI)
   - Verify cannot see User A's workflow

4. **Test: Role-Based Access**
   - Login as Project Handler
   - Attempt to create workflow → 403 Forbidden
   - Login as Process Manager
   - Create workflow → Success

**CI/CD Pipeline** (STORY-041):

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Python + Node.js
      - Install dependencies
      - Run linters (ESLint, Ruff, MyPy)
      - Run unit tests (pytest, Vitest)
      - Run integration tests (FastAPI TestClient)
      - Check coverage (>70% required)
      - Run E2E smoke tests (critical flows only, <5 min)

  deploy-staging:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - Deploy to Railway (backend)
      - Deploy to Vercel (frontend)

  deploy-production:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: test
    runs-on: ubuntu-latest
    steps:
      - Deploy to production (same as staging, different env vars)
```

**Quality Gates**:

- ✅ All unit tests pass (< 2 min)
- ✅ All integration tests pass (< 5 min)
- ✅ Code coverage >= 70% overall, >= 95% for AI validation
- ✅ E2E smoke tests pass (< 5 min)
- ✅ Linting passes (ESLint, Ruff)
- ✅ Type checking passes (TypeScript, MyPy)
- ✅ No high/critical security vulnerabilities (Snyk)

**Reference**: `product-guidelines/09-test-strategy.md` (complete testing strategy)

---

## Success Metrics

**Testing Metrics**:

- Code coverage: >70% overall (95% AI validation, 100% security)
- Test suite execution time: <10 minutes (CI/CD)
- E2E test stability: >95% (not flaky)

**Quality Metrics**:

- Production bugs per release: <2 (caught by tests)
- Regression bugs: 0 (E2E tests prevent)
- Security vulnerabilities: 0 high/critical

---

## Definition of Done

- [ ] E2E tests cover Journey Steps 1-5
- [ ] CI/CD pipeline runs on every PR
- [ ] Coverage gates enforce >70% overall
- [ ] Smoke tests run in <5 min
- [ ] Full E2E suite runs in <30 min (nightly)
- [ ] Security scanning automated (Snyk/Dependabot)
- [ ] Code quality gates enforced (ESLint, Ruff, MyPy)
- [ ] Deployment automated (main → staging, tags → production)
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: E2E tests flaky (fail intermittently)

- **Mitigation**: Explicit waits (not sleep), retry logic, stable test data

**Risk**: Test suite too slow (>10 min)

- **Mitigation**: Parallelize tests, run smoke tests on PR (full suite nightly)

**Risk**: False positives (tests pass but code broken)

- **Mitigation**: Test real workflows with TÜV SÜD data, manual QA before release

---

## Testing Requirements

**E2E Tests** (Playwright):

- [ ] Complete assessment flow (Journey Steps 1-5)
- [ ] Re-assessment flow (Journey Step 4)
- [ ] Multi-tenant isolation (security)
- [ ] Role-based access (security)
- [ ] Error handling (invalid inputs, API failures)

**CI/CD Automation**:

- [ ] GitHub Actions workflow configured
- [ ] Tests run on every PR
- [ ] Coverage gates enforced
- [ ] Deployment automated (staging + production)
- [ ] Security scanning automated

---

## Next Steps

After completing all 10 epics, the backlog is complete and ready for implementation. Start with **EPIC-01: Database & Infrastructure Setup** to lay the foundation.
