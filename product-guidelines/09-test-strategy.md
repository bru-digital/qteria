# Testing Strategy: Qteria

> **Derived from**: Journey critical paths, FastAPI + Next.js tech stack, async architecture, 28 API endpoints
> **Risk Level**: HIGH (compliance/certification industry - accuracy is non-negotiable)
> **Philosophy**: Test what matters - critical paths, data accuracy, security boundaries

---

## Testing Philosophy

### Risk Assessment

**Product Risk Level**: **HIGH**

**Why High Risk**:

- Customers (TIC notified bodies) depend on accurate document validation for certification decisions
- False negatives (missing real issues) = customer embarrassment, certification failures, reputational damage
- False positives (flagging non-issues) = wasted time, loss of trust in AI
- Data privacy = compliance documents contain confidential information
- Multi-tenant isolation = one organization must never see another's data

**Journey Critical Path** (Must Work Perfectly):

- **Step 3**: AI validation with evidence-based results (Aha moment)
  - Parse PDFs correctly (extract text, detect pages/sections)
  - Validate criteria accurately (<5% false positives, <1% false negatives)
  - Link evidence precisely (exact page/section references)
  - Process in <10 minutes (user expectation)

**Testing Mindset**: **Pragmatic TDD**

- Write tests for critical paths FIRST (TDD for business logic)
- Test user value delivery, not framework internals
- 70% coverage overall, 95%+ for critical modules
- Fast feedback loop (unit + integration tests < 5 min)

---

## Testing Principles

### 1. Test Critical Paths, Not Everything

**Priority 1 (Must Test):**

- AI validation accuracy (assessment scoring, criteria evaluation)
- Evidence extraction (page/section linking)
- Multi-tenant data isolation (security boundary)
- PDF parsing reliability (handles various formats)
- API authentication/authorization
- Background job processing (Celery task execution)

**Priority 2 (Should Test):**

- API endpoint request/response validation
- Database query correctness (CRUD operations)
- Workflow creation logic
- Document upload validation
- Error handling and edge cases

**Priority 3 (Nice to Test):**

- UI component rendering
- Utility functions
- Configuration files

**Don't Test:**

- Framework code (FastAPI, Next.js internals)
- External libraries (SQLAlchemy, Pydantic)
- Simple getters/setters
- Constants and configuration

---

### 2. Fast Feedback Over Complete Coverage

**Speed Targets:**

- Unit tests: < 2 minutes (run on every save)
- Integration tests: < 5 minutes (run on every commit)
- E2E smoke tests: < 10 minutes (run on every PR)
- Full E2E suite: < 30 minutes (run on merge to main)

**Trade-off**: 70% coverage with fast feedback beats 100% coverage with 30-minute test runs.

---

### 3. Test Behavior, Not Implementation

**Good Test** (tests behavior):

```python
def test_assessment_fails_when_criteria_not_met():
    """Assessment should fail if any required criteria fails"""
    assessment = create_assessment(criteria_results=[
        {"criteria_id": "1", "pass": True},
        {"criteria_id": "2", "pass": False},  # One failure
    ])

    assert assessment.overall_pass == False
```

**Bad Test** (tests implementation):

```python
def test_assessment_calls_calculate_score_method():
    """Don't test internal method calls"""
    assessment = create_assessment(...)

    assert assessment.calculate_score.called  # Implementation detail
```

**Why**: Behavior tests survive refactoring, implementation tests break.

---

## Unit Testing Strategy

### Scope

**What to Unit Test:**

1. **AI Validation Logic** (95% coverage target):
   - `assessment_engine.py`: Score calculation, pass/fail determination
   - `evidence_extractor.py`: Page/section detection from PDFs
   - `criteria_evaluator.py`: Match criteria to document content
   - `confidence_scorer.py`: High/medium/low confidence classification

2. **Business Logic** (90% coverage target):
   - `workflow_validator.py`: Workflow creation rules
   - `document_validator.py`: File type, size validation
   - `multi_tenancy.py`: Organization isolation logic
   - `usage_limiter.py`: Subscription tier limits

3. **Utilities** (80% coverage target):
   - `pdf_parser.py`: Extract text, detect sections
   - `formatters.py`: Date, currency, file size formatting
   - `validators.py`: Email, UUID, file type validation

4. **API Logic** (60% coverage target):
   - Route handlers: Test business logic, not FastAPI framework
   - Pydantic models: Test custom validators only

5. **UI Components** (50% coverage target):
   - Complex components: Results display, workflow builder
   - Skip simple presentational components

---

### Unit Test Patterns

**Arrange-Act-Assert (AAA):**

```python
def test_evidence_extractor_finds_correct_page():
    # Arrange: Set up test data
    pdf_text = load_fixture("test-report.pdf")
    search_term = "Test Results Summary"

    # Act: Execute function
    evidence = extract_evidence(pdf_text, search_term)

    # Assert: Verify result
    assert evidence.page == 8
    assert evidence.section == "3.2 Test Results"
    assert "summary" in evidence.text_snippet.lower()
```

**Test File Organization:**

```
backend/
  app/
    assessment/
      engine.py              # Business logic
      engine.test.py         # Co-located tests
    evidence/
      extractor.py
      extractor.test.py
  tests/
    unit/                    # Additional unit tests
    integration/             # Integration tests
    e2e/                     # E2E tests
    fixtures/                # Test data
      sample.pdf
      api-responses.json
    factories.py             # Test data factories
    conftest.py              # Pytest fixtures
```

**Naming Conventions:**

```python
# Good: Descriptive test names
def test_assessment_score_is_zero_when_all_criteria_fail():
def test_evidence_extractor_returns_none_for_missing_term():
def test_workflow_creation_requires_process_manager_role():

# Bad: Vague test names
def test_assessment():
def test_evidence():
def test_workflow():
```

---

### Backend Unit Tests (Python/FastAPI)

**Tools:**

- pytest (test runner)
- pytest-asyncio (async test support)
- pytest-cov (coverage reporting)
- pytest-mock (mocking)
- faker (test data generation)

**Example: AI Validation Logic**

```python
# app/assessment/engine.test.py
import pytest
from app.assessment.engine import AssessmentEngine
from app.models import Criteria, Document

@pytest.fixture
def assessment_engine():
    """Fixture: Create assessment engine instance"""
    return AssessmentEngine()

@pytest.fixture
def test_criteria():
    """Fixture: Sample validation criteria"""
    return [
        Criteria(id="1", name="Document must be signed", required=True),
        Criteria(id="2", name="Test summary must be present", required=True),
        Criteria(id="3", name="Risk matrix complete", required=False),
    ]

def test_assessment_passes_when_all_required_criteria_met(assessment_engine, test_criteria):
    """Assessment should pass if all required criteria pass"""
    results = [
        {"criteria_id": "1", "pass": True},   # Required - PASS
        {"criteria_id": "2", "pass": True},   # Required - PASS
        {"criteria_id": "3", "pass": False},  # Optional - FAIL (ignored)
    ]

    overall_pass = assessment_engine.evaluate_overall(test_criteria, results)

    assert overall_pass == True

def test_assessment_fails_when_required_criteria_fails(assessment_engine, test_criteria):
    """Assessment should fail if any required criteria fails"""
    results = [
        {"criteria_id": "1", "pass": True},
        {"criteria_id": "2", "pass": False},  # Required - FAIL
    ]

    overall_pass = assessment_engine.evaluate_overall(test_criteria, results)

    assert overall_pass == False

def test_assessment_score_calculates_percentage_correctly(assessment_engine):
    """Score should be (passed / total) * 100"""
    results = [
        {"criteria_id": "1", "pass": True},
        {"criteria_id": "2", "pass": True},
        {"criteria_id": "3", "pass": False},
        {"criteria_id": "4", "pass": False},
        {"criteria_id": "5", "pass": True},
    ]

    score = assessment_engine.calculate_score(results)

    assert score == 60  # 3/5 = 60%

@pytest.mark.asyncio
async def test_evidence_extractor_finds_page_and_section():
    """Evidence extractor should locate exact page and section"""
    from app.evidence.extractor import extract_evidence

    pdf_content = """
    Page 1: Introduction
    Page 8: Section 3.2 Test Results
    The test summary shows all tests passed.
    """

    evidence = await extract_evidence(
        pdf_content,
        search_term="test summary",
        context_window=50
    )

    assert evidence.page == 8
    assert evidence.section == "3.2 Test Results"
    assert "test summary" in evidence.text_snippet.lower()
    assert evidence.confidence == "high"
```

**Example: Multi-Tenancy Security**

```python
# app/auth/multi_tenancy.test.py
import pytest
from app.auth.multi_tenancy import filter_by_organization
from app.models import Workflow, User

def test_user_can_only_access_own_organization_workflows():
    """Users should only see workflows from their organization"""
    user = User(id="user_1", organization_id="org_a")
    workflows = [
        Workflow(id="wf_1", organization_id="org_a"),
        Workflow(id="wf_2", organization_id="org_a"),
        Workflow(id="wf_3", organization_id="org_b"),  # Different org
    ]

    filtered = filter_by_organization(workflows, user.organization_id)

    assert len(filtered) == 2
    assert all(wf.organization_id == "org_a" for wf in filtered)

def test_admin_cannot_bypass_organization_isolation():
    """Even admins are bound by organization isolation"""
    admin = User(id="admin_1", organization_id="org_a", role="admin")
    workflows = [
        Workflow(id="wf_1", organization_id="org_a"),
        Workflow(id="wf_2", organization_id="org_b"),  # Different org
    ]

    filtered = filter_by_organization(workflows, admin.organization_id)

    assert len(filtered) == 1  # Only org_a workflow
```

---

### Frontend Unit Tests (React/Next.js)

**Tools:**

- Vitest (test runner, Jest-compatible)
- @testing-library/react (component testing)
- @testing-library/user-event (user interactions)
- MSW (API mocking)

**Example: Assessment Results Display**

```typescript
// src/components/AssessmentResults.test.tsx
import { render, screen } from '@testing-library/react';
import { AssessmentResults } from './AssessmentResults';

describe('AssessmentResults', () => {
  const mockResults = {
    overall_pass: false,
    criteria_passed: 4,
    criteria_failed: 1,
    results: [
      {
        criteria_name: 'All documents must be signed',
        pass: true,
        confidence: 'high',
        evidence: null,
      },
      {
        criteria_name: 'Test summary must be present',
        pass: false,
        confidence: 'high',
        evidence: {
          document_name: 'test-report.pdf',
          page: 8,
          section: '3.2 Test Results',
          text_snippet: 'Summary section is missing...',
        },
      },
    ],
  };

  it('displays overall pass/fail status with correct styling', () => {
    render(<AssessmentResults results={mockResults} />);

    const status = screen.getByTestId('overall-status');
    expect(status).toHaveTextContent('FAIL');
    expect(status).toHaveClass('text-red-600');
  });

  it('displays passed and failed criteria counts', () => {
    render(<AssessmentResults results={mockResults} />);

    expect(screen.getByText('4/5 criteria passed')).toBeInTheDocument();
  });

  it('shows evidence link for failed criteria', () => {
    render(<AssessmentResults results={mockResults} />);

    const evidenceLink = screen.getByText(/test-report\.pdf, page 8/i);
    expect(evidenceLink).toBeInTheDocument();
    expect(evidenceLink).toHaveAttribute('href', '/documents/doc_id?page=8');
  });

  it('shows checkmark icon for passed criteria', () => {
    render(<AssessmentResults results={mockResults} />);

    const passedCriteria = screen.getByText('All documents must be signed');
    const checkmark = passedCriteria.parentElement?.querySelector('[data-icon="check"]');
    expect(checkmark).toBeInTheDocument();
  });

  it('does not show evidence link for passed criteria', () => {
    render(<AssessmentResults results={mockResults} />);

    // Only one evidence link (for failed criteria)
    const evidenceLinks = screen.queryAllByText(/\.pdf, page \d+/i);
    expect(evidenceLinks).toHaveLength(1);
  });
});
```

**Example: Form Validation**

```typescript
// src/components/WorkflowForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkflowForm } from './WorkflowForm';

describe('WorkflowForm', () => {
  it('prevents submission with empty workflow name', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<WorkflowForm onSubmit={onSubmit} />);

    const submitButton = screen.getByRole('button', { name: /create workflow/i });
    await user.click(submitButton);

    expect(screen.getByText(/workflow name is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('validates workflow name length (max 255 chars)', async () => {
    const user = userEvent.setup();
    render(<WorkflowForm onSubmit={vi.fn()} />);

    const nameInput = screen.getByLabelText(/workflow name/i);
    await user.type(nameInput, 'a'.repeat(256));  // 256 characters

    expect(screen.getByText(/name must be 255 characters or less/i)).toBeInTheDocument();
  });

  it('requires at least one bucket', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<WorkflowForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/workflow name/i), 'Test Workflow');
    await user.click(screen.getByRole('button', { name: /create workflow/i }));

    expect(screen.getByText(/at least one document bucket is required/i)).toBeInTheDocument();
  });
});
```

---

## Integration Testing Strategy

### Scope

**What to Integration Test:**

1. **API Endpoints** (80% coverage target):
   - All 28 REST endpoints from `08-api-contracts.md`
   - Request validation (400 errors for invalid input)
   - Response format (correct JSON structure)
   - Authentication (401 for missing/invalid JWT)
   - Authorization (403 for insufficient permissions)
   - Multi-tenant isolation (can't access other org's data)

2. **Database Operations** (70% coverage target):
   - Complex queries (JOINs, filters, pagination)
   - Transaction handling (rollback on error)
   - Cascading deletes (org deleted → users deleted)
   - Data integrity constraints (unique emails, foreign keys)

3. **External Service Integration** (80% coverage target):
   - Claude API integration (mock responses)
   - Vercel Blob storage (upload/download)
   - Email service (mock in test mode)
   - Background jobs (Celery task execution)

4. **Background Job Processing** (90% coverage target):
   - Assessment creation triggers Celery task
   - PDF parsing completes successfully
   - AI validation executes and stores results
   - Status updates correctly (pending → processing → completed)

---

### Integration Test Setup

**Test Database:**

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine("postgresql://postgres:postgres@localhost:5433/qteria_test")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_db(test_engine):
    """Create test database session with cleanup"""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        # Clean up all tables
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()

@pytest.fixture
def client(test_db):
    """FastAPI test client with test database"""
    from app.dependencies import get_db

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    return TestClient(app)
```

---

### API Integration Tests

**Example: Workflow CRUD**

```python
# tests/integration/test_workflow_api.py
import pytest
from tests.factories import UserFactory, OrganizationFactory

@pytest.fixture
def auth_headers(test_db):
    """Create authenticated user and return JWT headers"""
    org = OrganizationFactory(id="org_test")
    user = UserFactory(organization_id=org.id, role="process_manager")
    token = generate_jwt_token(user_id=user.id, org_id=org.id)
    return {"Authorization": f"Bearer {token}"}

def test_create_workflow_success(client, auth_headers):
    """POST /v1/workflows creates workflow with buckets and criteria"""
    payload = {
        "name": "Medical Device - Class II",
        "description": "Validation workflow for Class II devices",
        "buckets": [
            {
                "name": "Technical Documentation",
                "required": True,
                "accepted_file_types": ["pdf", "docx"]
            },
            {
                "name": "Test Reports",
                "required": True,
                "accepted_file_types": ["pdf"]
            }
        ],
        "criteria": [
            {
                "name": "All documents must be signed",
                "applies_to_bucket_ids": [0, 1]
            }
        ]
    }

    response = client.post("/v1/workflows", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Medical Device - Class II"
    assert len(data["buckets"]) == 2
    assert len(data["criteria"]) == 1
    assert "id" in data

def test_create_workflow_requires_authentication(client):
    """POST /v1/workflows returns 401 without auth token"""
    payload = {"name": "Test", "buckets": [], "criteria": []}

    response = client.post("/v1/workflows", json=payload)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"

def test_create_workflow_requires_process_manager_role(client, test_db):
    """POST /v1/workflows returns 403 for project_handler role"""
    user = UserFactory(role="project_handler")
    token = generate_jwt_token(user_id=user.id, org_id=user.organization_id)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": "Test", "buckets": [], "criteria": []}
    response = client.post("/v1/workflows", json=payload, headers=headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

def test_list_workflows_shows_only_user_organization(client, test_db):
    """GET /v1/workflows filters by organization_id from JWT"""
    # Create workflows for two different organizations
    org_a = OrganizationFactory(id="org_a")
    org_b = OrganizationFactory(id="org_b")
    user_a = UserFactory(organization_id=org_a.id)

    WorkflowFactory(organization_id=org_a.id, name="Workflow A1")
    WorkflowFactory(organization_id=org_a.id, name="Workflow A2")
    WorkflowFactory(organization_id=org_b.id, name="Workflow B1")  # Different org

    token = generate_jwt_token(user_id=user_a.id, org_id=org_a.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/workflows", headers=headers)

    assert response.status_code == 200
    workflows = response.json()["data"]
    assert len(workflows) == 2  # Only org_a workflows
    assert all(wf["name"].startswith("Workflow A") for wf in workflows)
```

**Example: Assessment Execution**

```python
# tests/integration/test_assessment_api.py
import pytest
from unittest.mock import patch
from tests.factories import WorkflowFactory, DocumentFactory

def test_create_assessment_starts_background_job(client, auth_headers, test_db):
    """POST /v1/assessments returns 202 and enqueues Celery task"""
    workflow = WorkflowFactory()
    documents = [DocumentFactory() for _ in range(3)]

    payload = {
        "workflow_id": workflow.id,
        "documents": [
            {"bucket_id": workflow.buckets[0].id, "document_ids": [documents[0].id]},
            {"bucket_id": workflow.buckets[1].id, "document_ids": [documents[1].id, documents[2].id]},
        ]
    }

    with patch('app.tasks.process_assessment.delay') as mock_task:
        response = client.post("/v1/assessments", json=payload, headers=auth_headers)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "pending"
    assert data["workflow_id"] == workflow.id
    assert "id" in data
    mock_task.assert_called_once()

def test_get_assessment_status_returns_progress(client, auth_headers, test_db):
    """GET /v1/assessments/:id returns current status and progress"""
    assessment = AssessmentFactory(status="processing", progress_percent=60)

    response = client.get(f"/v1/assessments/{assessment.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["progress_percent"] == 60
    assert "estimated_completion_at" in data

def test_get_assessment_results_requires_completed_status(client, auth_headers, test_db):
    """GET /v1/assessments/:id/results returns 409 if still processing"""
    assessment = AssessmentFactory(status="processing")

    response = client.get(f"/v1/assessments/{assessment.id}/results", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ASSESSMENT_NOT_READY"
```

---

### Database Integration Tests

**Example: Multi-Tenant Isolation**

```python
# tests/integration/test_multi_tenancy.py
import pytest
from app.models import Workflow, Assessment
from tests.factories import OrganizationFactory, UserFactory, WorkflowFactory

def test_workflows_isolated_by_organization(test_db):
    """Workflows from different organizations are isolated"""
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()

    wf_a = WorkflowFactory(organization_id=org_a.id)
    wf_b = WorkflowFactory(organization_id=org_b.id)

    # Query for org_a workflows
    org_a_workflows = test_db.query(Workflow).filter(
        Workflow.organization_id == org_a.id
    ).all()

    assert len(org_a_workflows) == 1
    assert org_a_workflows[0].id == wf_a.id

def test_cascading_delete_organization_deletes_users(test_db):
    """Deleting organization cascades to users (GDPR compliance)"""
    org = OrganizationFactory()
    user1 = UserFactory(organization_id=org.id)
    user2 = UserFactory(organization_id=org.id)

    # Delete organization
    test_db.delete(org)
    test_db.commit()

    # Users should be deleted
    remaining_users = test_db.query(User).filter(
        User.organization_id == org.id
    ).all()
    assert len(remaining_users) == 0

def test_workflow_with_assessments_cannot_be_deleted(test_db):
    """RESTRICT prevents deleting workflow that has assessments"""
    workflow = WorkflowFactory()
    assessment = AssessmentFactory(workflow_id=workflow.id)

    # Attempt to delete workflow
    with pytest.raises(IntegrityError):
        test_db.delete(workflow)
        test_db.commit()

    test_db.rollback()
```

---

## E2E Testing Strategy

### Critical Journeys

**Journey-Based E2E Tests** (from `00-user-journey.md`):

1. **Complete Assessment Flow** (Journey Steps 1-5):
   - Process Manager creates workflow
   - Project Handler uploads documents
   - Project Handler starts assessment
   - System processes assessment (AI validation)
   - Project Handler views evidence-based results
   - Project Handler downloads report

2. **Re-run Assessment Flow** (Journey Step 4):
   - Project Handler sees failed criteria
   - Project Handler replaces failing document
   - Project Handler re-runs assessment
   - Assessment passes after fix

3. **Multi-User Collaboration**:
   - Process Manager creates workflow
   - Process Manager shares workflow with team
   - Project Handler uses shared workflow
   - Both users see assessment history

---

### E2E Test Setup

**Tools:**

- Playwright (cross-browser E2E testing)
- Test database (seeded with realistic data)
- Mock Claude API (fast, deterministic responses)

**Configuration:**

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 3 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    // Mobile tests optional (journey is desktop-first)
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

---

### E2E Test Examples

**Example: Complete Assessment Flow**

```typescript
// tests/e2e/complete-assessment-flow.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Complete Assessment Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Seed test database with user and workflow
    await setupTestData()

    // Login
    await page.goto('/login')
    await page.fill('[data-testid="email"]', 'handler@test.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('project handler completes full assessment workflow', async ({ page }) => {
    // Step 1: Select existing workflow
    await page.click('[data-testid="workflow-card"]')
    await expect(page).toHaveURL(/\/workflows\/.+/)

    // Verify workflow details displayed
    await expect(page.locator('h1')).toContainText('Medical Device - Class II')
    await expect(page.getByText('Technical Documentation')).toBeVisible()
    await expect(page.getByText('Test Reports')).toBeVisible()

    // Step 2: Upload documents
    await page.click('[data-testid="start-assessment-button"]')

    // Upload to bucket 1 (Technical Documentation)
    const bucket1Input = page.locator('[data-testid="bucket-0-upload"]')
    await bucket1Input.setInputFiles('tests/fixtures/technical-spec.pdf')
    await expect(page.getByText('technical-spec.pdf')).toBeVisible()

    // Upload to bucket 2 (Test Reports)
    const bucket2Input = page.locator('[data-testid="bucket-1-upload"]')
    await bucket2Input.setInputFiles('tests/fixtures/test-report.pdf')
    await expect(page.getByText('test-report.pdf')).toBeVisible()

    // Step 3: Start assessment
    await page.click('[data-testid="submit-assessment-button"]')

    // Verify redirect to assessment status page
    await expect(page).toHaveURL(/\/assessments\/.+/)
    await expect(page.getByText('Assessment in progress')).toBeVisible()

    // Wait for completion (mock Claude API returns quickly)
    await page.waitForSelector('[data-testid="assessment-complete"]', {
      timeout: 30000,
    })

    // Step 4: View results (Aha moment!)
    await expect(page.getByText('Assessment Complete')).toBeVisible()

    // Verify overall status
    const overallStatus = page.locator('[data-testid="overall-status"]')
    await expect(overallStatus).toContainText(/PASS|FAIL/)

    // Verify criteria results displayed
    await expect(page.getByText('All documents must be signed')).toBeVisible()
    await expect(page.getByText('Test summary must be present')).toBeVisible()

    // Check for evidence link (if any criteria failed)
    const failedCriteria = page.locator('[data-testid="criteria-fail"]')
    if ((await failedCriteria.count()) > 0) {
      // Evidence link should be present
      const evidenceLink = page.locator('[data-testid="evidence-link"]').first()
      await expect(evidenceLink).toContainText(/page \d+/i)

      // Click evidence link
      await evidenceLink.click()

      // Verify PDF viewer opens (new tab or modal)
      const pdfViewer = page.locator('[data-testid="pdf-viewer"]')
      await expect(pdfViewer).toBeVisible()
    }

    // Step 5: Download report
    await page.goto(`/assessments/${await getAssessmentId(page)}`)
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="download-report-button"]')
    const download = await downloadPromise
    expect(download.suggestedFilename()).toContain('assessment-report')
    expect(download.suggestedFilename()).toContain('.pdf')
  })
})
```

**Example: Re-run Assessment After Fix**

```typescript
// tests/e2e/rerun-assessment.spec.ts
import { test, expect } from '@playwright/test'

test('project handler fixes issues and re-runs assessment', async ({ page }) => {
  // Use pre-seeded assessment with one failed criteria
  await page.goto('/assessments/test-assessment-failed')

  // Verify failed status
  await expect(page.locator('[data-testid="overall-status"]')).toContainText('FAIL')

  // See failed criteria with evidence
  const failedCriteria = page.locator('[data-testid="criteria-fail"]').first()
  await expect(failedCriteria).toContainText('Test summary must be present')
  await expect(failedCriteria).toContainText('test-report.pdf, page 8')

  // Click "Re-run Assessment" button
  await page.click('[data-testid="rerun-assessment-button"]')

  // Replace failing document
  await page
    .locator('[data-testid="replace-document-test-report"]')
    .setInputFiles('tests/fixtures/test-report-fixed.pdf')

  // Submit re-run
  await page.click('[data-testid="submit-rerun-button"]')

  // Wait for new assessment to complete
  await page.waitForSelector('[data-testid="assessment-complete"]', {
    timeout: 30000,
  })

  // Verify assessment now passes
  await expect(page.locator('[data-testid="overall-status"]')).toContainText('PASS')

  // Previously failed criteria should now pass
  const previouslyFailedCriteria = page.getByText('Test summary must be present')
  await expect(previouslyFailedCriteria.locator('[data-testid="criteria-status"]')).toContainText(
    'PASS'
  )
})
```

---

## Test Coverage and Quality Gates

### Coverage Targets

**Overall Coverage Goal: 70%**

**Coverage by Component:**

| Component           | Target | Rationale                                 |
| ------------------- | ------ | ----------------------------------------- |
| AI Validation Logic | 95%    | Critical business logic, accuracy matters |
| Evidence Extraction | 90%    | Accuracy critical for aha moment          |
| Multi-Tenancy       | 100%   | Security boundary, zero tolerance         |
| PDF Parsing         | 85%    | Reliability critical, handles edge cases  |
| API Routes          | 80%    | High user interaction                     |
| Background Jobs     | 90%    | Async processing must be reliable         |
| Database Queries    | 70%    | Data integrity matters                    |
| Business Logic      | 85%    | Core app functionality                    |
| UI Components       | 50%    | Focus on complex components               |
| Utilities           | 80%    | Reused across app                         |

**Coverage by Test Type:**

- Unit tests: ~60% of codebase
- Integration tests: ~20% (overlaps with unit)
- E2E tests: ~10% (critical paths only)

---

### Quality Gates (CI/CD)

**Blocking Gates** (Must Pass to Merge):

1. ✅ All unit tests pass (< 2 min)
2. ✅ All integration tests pass (< 5 min)
3. ✅ Code coverage >= 70% (overall)
4. ✅ Coverage not decreased vs main branch
5. ✅ No high/critical security vulnerabilities (Snyk/Dependabot)
6. ✅ All E2E smoke tests pass (< 10 min)
7. ✅ Linting passes (ESLint, Ruff)
8. ✅ Type checking passes (TypeScript, MyPy)

**Warning Gates** (Informational, Don't Block):

1. ⚠️ Performance regression detected (> 20% slower)
2. ⚠️ Coverage decreased in specific modules
3. ⚠️ Medium security vulnerabilities found

**Nightly Gates** (Run Off-Hours):

1. 🌙 Full E2E test suite (< 30 min)
2. 🌙 Performance benchmark tests
3. 🌙 DAST security scan (OWASP ZAP)
4. 🌙 Dependency updates check

---

### CI/CD Integration

**GitHub Actions Workflow:**

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  pull_request:
  push:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run unit tests
        run: pytest tests/unit --cov=app --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unit
          name: unit-tests

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: qteria_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5433:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6380:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run migrations
        run: alembic upgrade head
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5433/qteria_test

      - name: Run integration tests
        run: pytest tests/integration --cov=app --cov-append --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5433/qteria_test
          REDIS_URL: redis://localhost:6380

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run E2E smoke tests
        run: npx playwright test --grep @smoke

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Snyk security scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Run Bandit (Python SAST)
        run: |
          pip install bandit
          bandit -r app/ -f json -o bandit-report.json

  coverage-check:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    steps:
      - name: Download coverage reports
        uses: actions/download-artifact@v3

      - name: Check coverage threshold
        run: |
          COVERAGE=$(python -c "import xml.etree.ElementTree as ET; print(ET.parse('coverage.xml').getroot().attrib['line-rate'])")
          if (( $(echo "$COVERAGE < 0.70" | bc -l) )); then
            echo "Coverage $COVERAGE is below 70% threshold"
            exit 1
          fi
```

**Nightly Workflow:**

```yaml
# .github/workflows/nightly.yml
name: Nightly Tests

on:
  schedule:
    - cron: '0 2 * * *' # 2 AM UTC

jobs:
  full-e2e-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: npm ci
      - name: Run full E2E suite
        run: npx playwright test
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-full-report
          path: playwright-report/

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run load tests
        run: |
          pip install locust
          locust -f tests/performance/locustfile.py --headless --users 50 --spawn-rate 5 --run-time 5m

  dast-scan:
    runs-on: ubuntu-latest
    steps:
      - name: OWASP ZAP Scan
        uses: zaproxy/action-full-scan@v0.4.0
        with:
          target: 'https://staging.qteria.com'
```

---

## Test Data Management

### Test Database Setup

**Database per Test Suite:**

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app

# Use Docker PostgreSQL for tests
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/qteria_test"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine (once per test session)"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create clean database session for each test"""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db = TestingSessionLocal()

    # Begin transaction
    connection = test_engine.connect()
    transaction = connection.begin()

    yield db

    # Rollback transaction (cleanup)
    transaction.rollback()
    connection.close()
    db.close()
```

---

### Test Data Factories

**FactoryBoy for Python:**

```python
# tests/factories.py
import factory
from faker import Faker
from app.models import Organization, User, Workflow, Bucket, Criteria, Assessment

fake = Faker()

class OrganizationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Organization
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: f"org_{n}")
    name = factory.Faker('company')
    subscription_tier = "professional"
    subscription_status = "active"

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker('email')
    name = factory.Faker('name')
    role = "project_handler"
    organization_id = factory.LazyFunction(lambda: OrganizationFactory().id)

class WorkflowFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Workflow

    id = factory.Sequence(lambda n: f"workflow_{n}")
    name = factory.Faker('catch_phrase')
    description = factory.Faker('sentence')
    organization_id = factory.LazyFunction(lambda: OrganizationFactory().id)
    created_by = factory.LazyFunction(lambda: UserFactory().id)
    is_active = True

class BucketFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Bucket

    id = factory.Sequence(lambda n: f"bucket_{n}")
    name = factory.Faker('word')
    workflow_id = factory.LazyFunction(lambda: WorkflowFactory().id)
    required = True
    accepted_file_types = ["pdf"]
    order_index = factory.Sequence(lambda n: n)

class CriteriaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Criteria

    id = factory.Sequence(lambda n: f"criteria_{n}")
    name = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('paragraph')
    workflow_id = factory.LazyFunction(lambda: WorkflowFactory().id)
    applies_to_bucket_ids = factory.LazyFunction(lambda: [BucketFactory().id])

class AssessmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Assessment

    id = factory.Sequence(lambda n: f"assessment_{n}")
    workflow_id = factory.LazyFunction(lambda: WorkflowFactory().id)
    organization_id = factory.LazyFunction(lambda: OrganizationFactory().id)
    created_by = factory.LazyFunction(lambda: UserFactory().id)
    status = "pending"
```

**Usage:**

```python
# tests/test_example.py
from tests.factories import WorkflowFactory, AssessmentFactory

def test_create_assessment():
    # Create test workflow with realistic data
    workflow = WorkflowFactory(name="Medical Device - Class II")

    # Create assessment
    assessment = AssessmentFactory(workflow_id=workflow.id)

    assert assessment.workflow_id == workflow.id
    assert assessment.status == "pending"
```

---

### Test Fixtures

**Sample Test Files:**

```
tests/
  fixtures/
    documents/
      sample.pdf              # 10-page sample document
      test-report.pdf         # Test report with pass/fail
      test-report-fixed.pdf   # Fixed version (for re-run test)
      risk-assessment.pdf     # Risk matrix document
      large-document.pdf      # 100-page stress test
    api-responses/
      claude-api-success.json # Mock Claude API response
      claude-api-error.json   # Mock error response
    database/
      seed-data.sql           # E2E test database seed
```

**Loading Fixtures:**

```python
# tests/utils.py
import json
from pathlib import Path

def load_fixture(filename):
    """Load test fixture file"""
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / filename, 'r') as f:
        if filename.endswith('.json'):
            return json.load(f)
        return f.read()

# Usage
def test_parse_pdf():
    pdf_content = load_fixture("documents/sample.pdf")
    result = parse_pdf(pdf_content)
    assert result is not None
```

---

## Performance Testing

### Load Testing Strategy

**Tool**: Locust (Python-based load testing)

**Scenarios:**

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random

class QteriaUser(HttpUser):
    wait_time = between(1, 5)  # 1-5 seconds between requests

    def on_start(self):
        """Login before starting tests"""
        response = self.client.post("/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "testpassword"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_workflows(self):
        """List workflows (common operation)"""
        self.client.get("/v1/workflows", headers=self.headers)

    @task(2)
    def get_workflow_details(self):
        """Get workflow details"""
        workflow_id = random.choice(self.workflow_ids)
        self.client.get(f"/v1/workflows/{workflow_id}", headers=self.headers)

    @task(1)
    def create_assessment(self):
        """Start assessment (expensive operation)"""
        self.client.post("/v1/assessments", json={
            "workflow_id": random.choice(self.workflow_ids),
            "documents": [...]
        }, headers=self.headers)

    @task(4)
    def poll_assessment_status(self):
        """Poll assessment status (frequent operation)"""
        assessment_id = random.choice(self.assessment_ids)
        self.client.get(f"/v1/assessments/{assessment_id}", headers=self.headers)
```

**Load Test Execution:**

```bash
# Ramp up to 50 concurrent users over 10 seconds
locust -f tests/performance/locustfile.py \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --host https://staging.qteria.com

# Success criteria:
# - p95 latency < 500ms (API responses)
# - p99 latency < 2s (API responses)
# - 0% error rate under normal load
# - <5% error rate under 2x load
```

---

### Benchmark Testing

**Critical Operations:**

```python
# tests/performance/benchmark_pdf_parsing.py
import pytest
from app.pdf_parser import parse_pdf

@pytest.mark.benchmark
def test_pdf_parsing_speed(benchmark):
    """PDF parsing should complete in <5 seconds for 10MB file"""
    pdf_content = load_fixture("large-document.pdf")  # 10MB, 100 pages

    result = benchmark(parse_pdf, pdf_content)

    assert benchmark.stats['mean'] < 5.0  # Mean < 5 seconds
    assert result is not None

@pytest.mark.benchmark
def test_assessment_scoring_speed(benchmark):
    """Assessment scoring should be fast (<100ms)"""
    criteria_results = [{"pass": random.choice([True, False])} for _ in range(50)]

    result = benchmark(calculate_assessment_score, criteria_results)

    assert benchmark.stats['mean'] < 0.1  # Mean < 100ms
```

---

## Security Testing

### Authentication Testing

```python
# tests/security/test_auth.py
import pytest
from datetime import datetime, timedelta
from app.auth import create_token, verify_token

def test_expired_token_rejected():
    """Expired JWT tokens should be rejected"""
    # Create token that expired 1 hour ago
    expired_token = create_token(
        user_id="user_123",
        org_id="org_456",
        expires_at=datetime.utcnow() - timedelta(hours=1)
    )

    with pytest.raises(TokenExpiredError):
        verify_token(expired_token)

def test_malformed_token_rejected():
    """Malformed JWT tokens should be rejected"""
    malformed_token = "not.a.valid.jwt.token"

    with pytest.raises(InvalidTokenError):
        verify_token(malformed_token)

def test_token_with_wrong_signature_rejected():
    """Tokens signed with wrong key should be rejected"""
    # Create token with different secret
    wrong_token = jwt.encode({"sub": "user_123"}, "wrong_secret", algorithm="HS256")

    with pytest.raises(InvalidSignatureError):
        verify_token(wrong_token)
```

### Authorization Testing

```python
# tests/security/test_authorization.py
def test_user_cannot_access_other_organization_data(client):
    """Users should not see data from other organizations"""
    user_org_a = UserFactory(organization_id="org_a")
    user_org_b = UserFactory(organization_id="org_b")

    workflow_org_b = WorkflowFactory(organization_id="org_b")

    # User A tries to access Org B's workflow
    token_a = generate_jwt_token(user_id=user_org_a.id, org_id="org_a")
    headers = {"Authorization": f"Bearer {token_a}"}

    response = client.get(f"/v1/workflows/{workflow_org_b.id}", headers=headers)

    assert response.status_code == 404  # Not found (security: don't reveal existence)

def test_project_handler_cannot_delete_workflows(client):
    """Project handlers should not be able to delete workflows"""
    user = UserFactory(role="project_handler")
    workflow = WorkflowFactory(organization_id=user.organization_id)

    token = generate_jwt_token(user_id=user.id, org_id=user.organization_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/v1/workflows/{workflow.id}", headers=headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
```

### Input Validation Testing

```python
# tests/security/test_input_validation.py
def test_workflow_name_prevents_xss(client, auth_headers):
    """Workflow name should sanitize XSS attempts"""
    payload = {
        "name": "<script>alert('XSS')</script>",
        "buckets": [],
        "criteria": []
    }

    response = client.post("/v1/workflows", json=payload, headers=auth_headers)

    assert response.status_code == 201
    workflow = response.json()
    # Script tags should be escaped or stripped
    assert "<script>" not in workflow["name"]

def test_file_upload_validates_file_type(client, auth_headers):
    """File upload should reject non-PDF/DOCX files"""
    with open("tests/fixtures/malicious.exe", "rb") as f:
        response = client.post(
            "/v1/documents",
            files={"file": ("malicious.exe", f, "application/x-msdownload")},
            headers=auth_headers
        )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"

def test_sql_injection_prevented(client, auth_headers):
    """SQL injection attempts should be prevented"""
    # Attempt SQL injection in workflow name
    payload = {
        "name": "'; DROP TABLE workflows; --",
        "buckets": [],
        "criteria": []
    }

    response = client.post("/v1/workflows", json=payload, headers=auth_headers)

    # Should succeed (parameterized queries prevent injection)
    assert response.status_code == 201

    # Verify workflows table still exists
    response = client.get("/v1/workflows", headers=auth_headers)
    assert response.status_code == 200
```

### Dependency Scanning

```bash
# Run Snyk vulnerability scan
snyk test --severity-threshold=high

# Run npm audit
npm audit --audit-level=high

# Run Python safety check
pip install safety
safety check --json
```

---

## Testing Workflows

### Test-Driven Development (TDD)

**TDD Workflow:**

1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while keeping tests green

**Example:**

```python
# Step 1: RED - Write failing test
def test_assessment_calculates_percentage_score():
    """Assessment score should be (passed / total) * 100"""
    results = [
        {"pass": True},
        {"pass": True},
        {"pass": False},
    ]

    score = calculate_assessment_score(results)

    assert score == 67  # 2/3 = 67%

# Run test → FAILS (function doesn't exist)

# Step 2: GREEN - Write minimal code
def calculate_assessment_score(results):
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    return int((passed / total) * 100)

# Run test → PASSES

# Step 3: REFACTOR - Clean up
def calculate_assessment_score(results):
    """Calculate assessment score as percentage of passed criteria"""
    if not results:
        return 0

    passed_count = sum(1 for result in results if result["pass"])
    total_count = len(results)

    return round((passed_count / total_count) * 100)

# Run test → STILL PASSES
```

---

### Regression Testing

**Regression Workflow:**

1. Bug reported in production
2. Write test reproducing bug (test fails)
3. Fix bug (test passes)
4. Test stays in suite forever (prevents regression)

**Example:**

```python
# Bug: Assessment score wrong when all criteria pass
def test_issue_123_assessment_score_is_100_when_all_criteria_pass():
    """Regression test for issue #123: Score was 99% instead of 100%"""
    results = [{"pass": True} for _ in range(10)]

    score = calculate_assessment_score(results)

    assert score == 100  # Was incorrectly 99 due to float rounding

# Tag with issue number for traceability
```

---

## What We DIDN'T Choose (And Why)

### 100% Test Coverage

**What**: Require every line of code to be tested

**Why Not**:

- Diminishing returns (last 20% takes 80% of effort)
- Coverage ≠ quality (can have 100% coverage with bad tests)
- Slows development (testing getters/setters wasteful)
- Journey focus > completeness (70% on critical paths better than 100% superficial)

**Reconsider If**: Safety-critical system (medical devices), regulatory requirement

---

### Mutation Testing

**What**: Automatically modify code to verify tests catch changes

**Why Not**:

- Very slow (10-100x longer than normal tests)
- High effort for edge case findings
- Better to test critical paths well than find every possible bug
- More useful for mature products, not MVP

**Reconsider If**: Safety-critical, stable codebase, have time/resources

---

### Property-Based Testing

**What**: Generate random inputs to test properties (e.g., "sorting always returns sorted list")

**Why Not**:

- Harder to write and understand
- Overkill for CRUD operations (predictable inputs)
- Better for algorithms/libraries than business logic
- Team learning curve

**Reconsider If**: Complex algorithms (parsers, compilers), many edge cases, team experienced

---

### Full E2E Suite on Every PR

**What**: Run all E2E tests on every pull request

**Why Not**:

- Too slow (20-30 min delays feedback)
- Expensive CI minutes
- Most PRs don't affect entire flow
- Pragmatic: Smoke tests on PR, full suite on merge

**Reconsider If**: E2E tests < 5 min, high bug rate, few PRs/day

---

### Visual Regression Testing for Every Component

**What**: Screenshot every component, detect visual changes

**Why Not**:

- Maintenance burden (update screenshots on every design change)
- Flaky (timing, fonts, rendering differences)
- Expensive (Percy/Chromatic cost money)
- Selective approach better (test critical components only)

**Reconsider If**: Design system library, frequent visual bugs, large team

---

### Contract Testing (Pact)

**What**: Test API contracts between consumer and provider

**Why Not**:

- Monolith architecture (frontend + backend owned by same team)
- Integration tests cover API contracts
- More useful for microservices with multiple teams
- Added complexity not justified

**Reconsider If**: Microservices, multiple teams, public API for third parties

---

### Chaos Engineering (Production Testing)

**What**: Deliberately inject failures in production

**Why Not**:

- Too risky for small team (one mistake = downtime)
- MVP stage (premature optimization)
- Better to test resilience in staging first
- Netflix-scale problem, not 10-customer SaaS

**Reconsider If**: >100 customers, distributed system, experienced SRE team

---

## Summary

**Testing Philosophy**: Test what matters (critical paths, data accuracy, security), not everything.

**Coverage Targets**:

- Overall: 70%
- AI validation: 95%
- Evidence extraction: 90%
- Multi-tenancy: 100%
- API routes: 80%
- UI components: 50%

**Test Types**:

- Unit tests: Business logic, utilities (60% coverage)
- Integration tests: API, database, services (20% coverage)
- E2E tests: Critical journeys (10% coverage, all steps)

**Quality Gates**:

- All unit/integration tests pass (< 5 min)
- Coverage >= 70%, no decrease vs main
- E2E smoke tests pass (< 10 min on PR)
- No high/critical vulnerabilities

**Tools**:

- Backend: Pytest + pytest-asyncio + pytest-cov
- Frontend: Vitest + Testing Library
- E2E: Playwright (cross-browser)
- Load testing: Locust
- Security: Snyk + Bandit + OWASP ZAP

**Speed Targets**:

- Unit tests: < 2 min
- Integration tests: < 5 min
- E2E smoke: < 10 min
- Full E2E: < 30 min

This strategy ensures quality without slowing development, focused on delivering reliable AI validation with evidence-based results.
