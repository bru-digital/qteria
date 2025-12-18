# Test Strategy Essentials (For Backlog Generation)

> This is a condensed version for Session 10 (backlog generation).
> See `09-test-strategy.md` for complete testing strategy with examples, test data
> management, performance testing, security testing, and TDD/BDD workflows.

---

## Overview

**Product**: [Product name from journey]
**Risk Level**: [High/Medium/Low - based on journey]
**Testing Approach**: [TDD/BDD/Pragmatic]
**Overall Coverage Goal**: [70%]

**Journey Connection**:
This testing strategy ensures reliability for:

- Step 1: [Journey step] → [Test coverage]
- Step 2: [Journey step] → [Test coverage]
- Step 3: [Journey step] → [Test coverage]
- Step 4: [Journey step] → [Test coverage]

---

## Coverage Targets (for story estimation)

| Component           | Target Coverage | Test Type         | Story Impact          |
| ------------------- | --------------- | ----------------- | --------------------- |
| Business logic      | 90%+            | Unit tests        | Add 30-40% dev time   |
| API endpoints       | 70-80%          | Integration tests | Add 30-40% dev time   |
| Database operations | 70%             | Integration tests | Included in API tests |
| UI components       | 50-60%          | Unit + E2E tests  | Add 20-30% dev time   |
| Critical user flows | 100%            | E2E tests         | Separate E2E story    |

**Overall target**: 70% code coverage minimum

**Estimation guidance**:

- Add 30-40% to development time for test writing
- E2E tests take longer to write and maintain
- Integration tests require test database setup

---

## Test Types (for story scope)

### Unit Tests

**What gets unit tested:**

- ✓ Business logic and algorithms
- ✓ Validation rules and business rules
- ✓ Utilities and helpers
- ✓ Complex component logic
- ✗ Framework code
- ✗ Simple presentational components

**Story requirement**: Each story should specify which functions/components need unit tests

### Integration Tests

**What gets integration tested:**

- ✓ API endpoints (request/response, auth, errors)
- ✓ Database operations (queries, transactions, relationships)
- ✓ External service integrations (APIs, file storage)

**Story requirement**: Each API story must include integration tests for:

- Happy path (200/201 responses)
- Error cases (400/404/500 responses)
- Authentication/authorization
- Multi-tenant data isolation

### E2E Tests

**Critical user journeys** (from journey steps 1-3):

1. **[Journey 1 name]**: [Brief description]
2. **[Journey 2 name]**: [Brief description]
3. **[Journey 3 name]**: [Brief description]

**Story requirement**: Stories implementing critical user flows need E2E tests

---

## Testing Tools (from tech stack)

**Backend**:

- Test framework: [Pytest/Jest/etc. from tech stack]
- Mocking: [unittest.mock/Jest mocks]
- Coverage: [pytest-cov/c8/nyc]

**Frontend**:

- Test framework: [Vitest/Jest from tech stack]
- Component testing: [Testing Library/Enzyme]
- Mocking: [MSW/nock]

**E2E**:

- Framework: [Playwright/Cypress from tech stack]
- Test data: [Factories + database seeding]

---

## Quality Gates (for acceptance criteria)

### Blocking (must pass to merge)

Stories cannot be marked "Done" unless:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage >= 70% for new code
- [ ] No coverage decrease vs main branch
- [ ] No high/critical security vulnerabilities
- [ ] Code review approved

### Non-blocking (warnings)

- [ ] E2E tests pass (block on main, warn on PR)
- [ ] Performance tests pass (informational)
- [ ] Linting passes (can be fixed later)

---

## Test Requirements in Stories

Each story should include:

### 1. Unit Test Scope

**Question**: Which functions/components need unit tests?
**Example**: "Unit tests for `calculateScore()`, `validateInput()`, and `ScoreCard` component"

### 2. Integration Test Scope

**Question**: Which API endpoints or database operations need tests?
**Example**: "Integration tests for POST /api/assessments (happy path, validation errors, auth)"

### 3. E2E Test Scope

**Question**: Which user flows need E2E coverage (if applicable)?
**Example**: "E2E test for complete assessment submission flow (upload → process → view results)"

### 4. Acceptance Criteria (Testing)

All stories must include:

- [ ] Unit tests written and passing
- [ ] Integration tests written and passing (if applicable)
- [ ] E2E tests written and passing (if applicable)
- [ ] Code coverage >= 70% for new code
- [ ] All quality gates pass

---

## Notes for Backlog Generation

### Story Scoping Guidance

**Simple stories** (1-2 days + 30% test time):

- Single component or function
- Straightforward unit tests
- Example: "User can view their profile" → Component + unit tests

**Medium stories** (3-5 days + 40% test time):

- API endpoint with database operations
- Integration tests required
- Example: "User can create assessment" → API + integration tests + unit tests

**Complex stories** (5+ days - should be split):

- Multiple endpoints or complex business logic
- Integration + E2E tests
- Example: "User can complete full assessment flow" → Split into smaller stories

### Test Data Management

**For integration tests:**

- Use test database (Docker)
- Clean up after each test
- Use factories for realistic data

**For E2E tests:**

- Use database seeding
- Create test fixtures
- Ensure idempotent tests

### Testing Workflow

**Test-Driven Development (when applicable):**

1. Write failing test (Red)
2. Write minimal code to pass (Green)
3. Refactor (still Green)

**Recommended for**: New features, complex business logic

---

## Common Test Scenarios (for acceptance criteria)

### Authentication Testing

- [ ] Test invalid tokens (expired, malformed)
- [ ] Test token expiration and refresh
- [ ] Test rate limiting on auth endpoints

### Authorization Testing

- [ ] Test multi-tenant isolation (User A can't access User B's data)
- [ ] Test role-based access control
- [ ] Test API endpoints require authentication

### Input Validation Testing

- [ ] Test invalid input returns 400
- [ ] Test SQL injection prevention
- [ ] Test XSS prevention
- [ ] Test file upload validation (type, size)

### Error Handling Testing

- [ ] Test error responses (400/404/500)
- [ ] Test error messages are user-friendly
- [ ] Test errors are logged properly

---

## CI/CD Integration (for story acceptance)

**On pull request**:

1. Run unit tests (< 5 min) - BLOCKING
2. Run integration tests (< 5 min) - BLOCKING
3. Run E2E smoke tests (< 10 min) - WARNING
4. Report coverage - BLOCKING if < 70%

**Before merge to main**:

1. All tests must pass
2. Coverage check must pass
3. Security scan must pass

---

## References

For complete testing strategy including:

- Detailed test examples (unit, integration, E2E)
- Test data management strategies
- Performance testing scenarios
- Security testing details
- TDD/BDD workflow explanations
- Testing checklists
- Setup instructions
- CI/CD configuration examples
- "What We DIDN'T Choose" alternatives

See: `product-guidelines/09-test-strategy.md`
