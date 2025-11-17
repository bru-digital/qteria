# Test Strategy Essentials (For Backlog Generation)

> **Purpose**: Condensed testing requirements for Session 10 (backlog generation)
> **Full Details**: See `09-test-strategy.md` for complete testing strategy, examples, and setup instructions

---

## Risk Level & Philosophy

**Risk Level**: **HIGH** (compliance/certification industry - accuracy non-negotiable)

**Testing Approach**: Pragmatic TDD - test critical paths first, 70% overall coverage, fast feedback (<5 min)

**Core Principle**: Test what matters (critical paths, data accuracy, security boundaries), not everything

---

## Test Coverage Targets

**Overall Goal: 70% code coverage**

| Component | Coverage Target | Why |
|-----------|----------------|-----|
| AI Validation Logic | 95% | Critical business logic - false positives/negatives unacceptable |
| Evidence Extraction | 90% | Page/section linking must be precise (aha moment) |
| Multi-Tenancy Security | 100% | Zero tolerance for data leakage between organizations |
| PDF Parsing | 85% | Handles various formats, reliability critical |
| API Routes | 80% | High user interaction |
| Background Jobs (Celery) | 90% | Async processing must be reliable |
| Database Queries | 70% | Data integrity matters |
| Business Logic | 85% | Core app functionality |
| UI Components | 50% | Focus on complex components only |
| Utilities | 80% | Reused across app |

---

## Test Types by Story Type

### Backend Stories (API Endpoints, Business Logic)

**Required Tests:**
- **Unit tests**: Business logic functions (90%+ coverage for critical logic)
- **Integration tests**: API endpoint with database (80%+ coverage)
- **Security tests**: Authentication, authorization, multi-tenancy (100%)

**Example Story**: "As PM, create workflow via API"
- Unit test: Workflow validation logic
- Integration test: POST /v1/workflows with database
- Security test: Requires process_manager role, filters by org_id

---

### Frontend Stories (UI Components, User Flows)

**Required Tests:**
- **Component tests**: Complex UI components (50%+ coverage, focus on stateful components)
- **E2E tests**: Critical user flows only (Journey Steps 1-5)

**Example Story**: "As PH, view assessment results with evidence links"
- Component test: AssessmentResults component renders pass/fail, evidence links
- E2E test: Complete assessment flow (Journey Steps 2-4)

---

### AI/Data Processing Stories

**Required Tests:**
- **Unit tests**: Parsing, validation, scoring algorithms (95%+ coverage)
- **Integration tests**: Claude API integration with mocks (80%+ coverage)
- **Performance tests**: Processing time benchmarks (<10 min for assessments)

**Example Story**: "As System, extract evidence from PDF with page/section links"
- Unit test: Evidence extraction algorithm
- Integration test: End-to-end PDF → evidence flow
- Performance test: <5 seconds for 10MB PDF

---

### Database Stories (Schema, Queries)

**Required Tests:**
- **Integration tests**: Complex queries, transactions, constraints (70%+ coverage)
- **Security tests**: Multi-tenant isolation (100%)

**Example Story**: "As System, ensure multi-tenant data isolation"
- Integration test: User A cannot see User B's workflows (different orgs)
- Integration test: Cascading deletes work correctly (org → users)

---

## Testing Tools (From Tech Stack)

**Backend (Python/FastAPI)**:
- pytest (test runner)
- pytest-asyncio (async tests)
- pytest-cov (coverage reporting)
- FastAPI TestClient (API integration tests)
- pytest-postgresql (database tests)
- responses / pytest-mock (mocking Claude API, external services)

**Frontend (React/Next.js)**:
- Vitest (test runner, Jest-compatible)
- @testing-library/react (component testing)
- @testing-library/user-event (user interactions)
- MSW (API mocking)

**E2E Tests**:
- Playwright (cross-browser testing)

**Performance**:
- Locust (load testing)
- pytest-benchmark (benchmarking)

**Security**:
- Snyk / Dependabot (dependency scanning)
- Bandit (Python SAST)
- OWASP ZAP (DAST)

---

## Quality Gates (CI/CD)

**Blocking Gates** (Must pass to merge PR):
1. ✅ All unit tests pass (< 2 min)
2. ✅ All integration tests pass (< 5 min)
3. ✅ Code coverage >= 70% overall
4. ✅ Coverage not decreased vs main branch
5. ✅ E2E smoke tests pass (< 10 min)
6. ✅ No high/critical security vulnerabilities
7. ✅ Linting passes (ESLint, Ruff)
8. ✅ Type checking passes (TypeScript, MyPy)

**Warning Gates** (Informational, don't block):
- ⚠️ Performance regression detected (> 20% slower)
- ⚠️ Medium security vulnerabilities

**Nightly Gates** (Run off-hours):
- 🌙 Full E2E suite (< 30 min)
- 🌙 Performance benchmarks
- 🌙 DAST security scan

---

## Test Requirements in Story Acceptance Criteria

**Every backlog story should include:**

### Definition of Done (Testing)
- [ ] Unit tests written and passing
- [ ] Integration tests written (if API/database)
- [ ] E2E tests written (if critical user flow)
- [ ] Code coverage >= target for component type
- [ ] All tests pass in CI
- [ ] Security tests pass (if auth/authorization changes)

### Example Acceptance Criteria

**Story**: "As PM, create workflow with buckets and criteria"

**Acceptance Criteria:**
- [ ] POST /v1/workflows creates workflow in database
- [ ] Workflow includes nested buckets and criteria
- [ ] Requires process_manager or admin role (403 otherwise)
- [ ] Filters by organization_id from JWT (multi-tenant)
- [ ] Returns 201 with workflow object
- [ ] **Tests**:
  - [ ] Unit test: Workflow validation logic (95% coverage)
  - [ ] Integration test: POST endpoint with database (pass)
  - [ ] Integration test: Unauthorized returns 403 (pass)
  - [ ] Integration test: Multi-tenant isolation (pass)
  - [ ] E2E test: Workflow creation in browser (pass)

---

## Common Test Scenarios

### Authentication Tests
```python
# Every authenticated endpoint needs these tests
def test_endpoint_requires_authentication():  # 401 without token
def test_endpoint_rejects_expired_token():    # 401 with expired token
def test_endpoint_rejects_invalid_token():    # 401 with malformed token
```

### Authorization Tests
```python
# Role-based access tests
def test_endpoint_requires_correct_role():    # 403 for insufficient role
def test_project_handler_cannot_delete():     # 403 for non-admin action
```

### Multi-Tenancy Tests
```python
# Every resource needs isolation test
def test_user_cannot_access_other_org_data():  # 404 for different org
def test_list_filters_by_organization():       # Only returns user's org data
```

### Input Validation Tests
```python
# Every POST/PUT endpoint needs validation
def test_rejects_missing_required_fields():    # 400 for validation error
def test_rejects_invalid_field_format():       # 400 for email/UUID/etc
def test_prevents_xss_in_text_fields():        # Sanitizes HTML/scripts
```

### API Integration Tests
```python
# Every endpoint needs integration test
def test_create_resource_success():            # 201 with valid data
def test_create_resource_validation_error():   # 400 for invalid data
def test_get_resource_not_found():             # 404 for missing resource
```

---

## Story Estimation with Testing

**Testing effort by story complexity:**

| Story Complexity | Test Time (as % of dev time) | Notes |
|------------------|------------------------------|-------|
| Simple CRUD API | 50% | Unit + integration tests straightforward |
| Complex Business Logic | 100% | Test cases complex, many edge cases |
| AI/ML Integration | 150% | Mocking, edge cases, performance tests |
| Critical User Flow | 75% | Component + E2E tests required |
| Database Schema | 50% | Migration + constraint tests |
| Security Feature | 100% | Auth, authorization, penetration tests |

**Example:**
- Story: "Implement AI validation engine"
- Dev estimate: 5 points
- Test estimate: 5 points (100% of dev time)
- **Total: 10 points**

---

## Testing Workflow for Developers

**Test-Driven Development (TDD)**:
1. Write failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor code (GREEN stays)
4. Repeat

**When to Write Tests**:
- **Before coding**: For business logic, algorithms (TDD)
- **During coding**: For API endpoints, components (pragmatic)
- **After coding**: For bug fixes, edge cases (regression)

**Test File Organization**:
```
backend/app/assessment/
  engine.py              # Business logic
  engine.test.py         # Co-located unit tests

tests/
  integration/           # API + database tests
  e2e/                   # Playwright E2E tests
  fixtures/              # Test data (PDFs, JSON)
  factories.py           # Test data factories
  conftest.py            # Pytest fixtures
```

---

## Critical E2E Test Coverage (Journey Steps)

**Required E2E Tests** (from `00-user-journey.md`):

1. **Complete Assessment Flow** (Journey Steps 1-5):
   - Create/select workflow
   - Upload documents
   - Start assessment
   - Wait for completion (poll status)
   - View evidence-based results ⭐ **Aha Moment**
   - Download report

2. **Re-run Assessment After Fix** (Journey Step 4):
   - View failed assessment
   - Replace failing document
   - Re-run assessment
   - Verify pass after fix

3. **Multi-User Collaboration**:
   - Process Manager creates workflow
   - Project Handler uses workflow
   - Both see shared data

**E2E Test Execution**:
- Run on: Staging environment
- Frequency: Smoke tests on PR (<10 min), full suite on merge (<30 min)
- Browsers: Chrome, Firefox (desktop-first journey)

---

## Performance Test Requirements

**Load Testing Scenarios**:
- Document upload: 10 concurrent users, 100 uploads/min
- Assessment polling: 50 concurrent users, 500 requests/min
- Results retrieval: 20 concurrent users, 200 requests/min

**Success Criteria**:
- p95 latency < 500ms (API responses)
- p99 latency < 2s (API responses)
- 0% error rate under normal load

**Benchmark Tests**:
- PDF parsing: < 5s for 10MB PDF
- AI assessment: < 10 min for typical assessment
- Report generation: < 2s

---

## Security Test Requirements

**Required Security Tests**:
1. Authentication: Invalid/expired/missing tokens rejected (401)
2. Authorization: Role-based access enforced (403)
3. Multi-tenancy: Organization isolation (404 for other org's data)
4. Input validation: XSS/SQL injection prevented (400/sanitized)
5. File upload: Type/size validation (400/413)

**Dependency Scanning** (Automated in CI):
- Snyk / Dependabot: Daily scans
- Block PR if high/critical vulnerabilities

---

## For Backlog Story Writing

**When creating stories, include:**

1. **Testing acceptance criteria** (per story type above)
2. **Coverage target** (from table at top)
3. **Test estimation** (50-150% of dev time)
4. **Definition of Done** (includes passing tests)
5. **Security tests** (if auth/authorization/data access)

**Example Story Template**:

```markdown
## Story: [Title]

**As a** [persona]
**I want to** [action]
**So that** [value]

### Acceptance Criteria
- [ ] [Functional criterion 1]
- [ ] [Functional criterion 2]

### Testing Requirements
- [ ] Unit tests: [Scope] (Target: X% coverage)
- [ ] Integration tests: [Scope]
- [ ] E2E tests: [Only if critical flow]
- [ ] Security tests: [If applicable]
- [ ] Performance tests: [If applicable]

### Definition of Done
- [ ] Feature complete and working
- [ ] All tests written and passing
- [ ] Code coverage >= X%
- [ ] Code reviewed and approved
- [ ] Merged to main

### Estimate: X points (Y points dev + Z points testing)
```

---

**Complete Testing Details**: See `09-test-strategy.md` for full strategy, examples, test data management, CI/CD workflows, setup instructions, and "What We DIDN'T Choose" analysis.
