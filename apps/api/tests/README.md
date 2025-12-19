# Test Architecture Guide

This document describes the test architecture patterns used in the Qteria API test suite.

## Test Pattern: Integration Tests vs Unit Tests

### Integration Test Pattern (PREFERRED)

**When to use**: All API endpoint tests, database operations, and multi-tenancy tests.

**Key characteristics**:
- Use **real database** via `client` fixture
- Mock **only external services** (Vercel Blob, Claude API, python-magic)
- Use **real test data** seeded in the database
- Auth middleware accesses real database (no get_db mocking)

**Working Example** (`test_workflow_api.py`):
```python
def test_create_workflow_success(
    client: TestClient,
    process_manager_token: str,
    mock_audit_service,
):
    """Process manager can create workflow."""
    response = client.post(
        "/v1/workflows",
        headers={"Authorization": f"Bearer {process_manager_token}"},
        json={
            "name": "Medical Device - Class II",
            "buckets": [...],
            "criteria": [...]
        }
    )

    assert response.status_code == 201
```

### ❌ Broken Pattern (DO NOT USE)

**Problem**: Mocking `get_db` causes authentication middleware to fail with 500 errors because auth needs real database access to validate JWT tokens.

**Broken Example**:
```python
def test_upload_pdf(client, token):
    # ❌ WRONG: Mocking get_db breaks authentication
    with patch("app.api.v1.endpoints.documents.get_db", return_value=iter([MagicMock()])):
        response = client.post("/v1/documents", ...)
    # This fails with 500 because auth middleware can't access DB
```

## Test Fixtures

### Database Fixtures

**`test_organization`** - Returns seeded Organization A from database
**`test_user`** - Returns seeded Admin User A from database
**`db_session`** - Provides SQLAlchemy session for creating test data

### Token Fixtures

**`admin_token`** - JWT token for admin role (uses seeded TEST_USER_A_ID)
**`process_manager_token`** - JWT token for process manager role
**`project_handler_token`** - JWT token for project handler role
**`org_a_admin_token`** - Admin token for Organization A
**`org_b_admin_token`** - Admin token for Organization B

### Document Test Fixtures (apps/api/tests/conftest.py)

**`test_workflow_with_bucket`** - Creates workflow with bucket in Org A
```python
def test_upload_with_bucket_id(
    client,
    test_workflow_with_bucket,  # Real workflow+bucket in DB
    mock_blob_storage,
):
    workflow_id, bucket_id = test_workflow_with_bucket
    response = client.post(
        "/v1/documents",
        files={"files": ("test.pdf", pdf_file, "application/pdf")},
        data={"bucket_id": bucket_id},  # Real bucket ID
    )
    assert response.status_code == 201
```

**`test_document_in_org_a`** - Creates document in Organization A
**`test_document_in_org_b`** - Creates document in Organization B (for multi-tenancy tests)
**`test_workflow_with_bucket_org_b`** - Creates workflow with bucket in Org B (for multi-tenancy tests)

## Seeded Test Data

The test database is seeded once per pytest session with organizations and users that match the UUIDs used in JWT tokens.

**Seeded Organizations**:
- `TEST_ORG_A_ID = "f52414ec-67f4-43d5-b25c-1552828ff06d"`
- `TEST_ORG_B_ID = "f171ee72-38bd-4a10-9682-a0c483ae365e"`

**Seeded Users**:
- `TEST_USER_A_ID` - Admin in Org A
- `TEST_USER_A_PM_ID` - Process Manager in Org A
- `TEST_USER_A_PH_ID` - Project Handler in Org A
- `TEST_USER_B_ID` - Admin in Org B
- `TEST_USER_B_PM_ID` - Process Manager in Org B
- `TEST_USER_B_PH_ID` - Project Handler in Org B

## What to Mock

### ✅ Mock External Services

**Always mock**:
- `BlobStorageService` - Vercel Blob upload/download/delete
- `python-magic` - MIME type detection
- `AuditService` - Audit log writes (use `mock_audit_service` fixture)
- Claude API calls (when implemented)

**Example**:
```python
@pytest.fixture
def mock_blob_storage(self):
    with patch("app.api.v1.endpoints.documents.BlobStorageService") as mock:
        mock.upload_file = AsyncMock(return_value="https://blob.url/test.pdf")
        yield mock
```

### ❌ Never Mock These

**DO NOT mock**:
- `get_db` - Authentication middleware needs real database
- Database models (User, Organization, Workflow, etc.)
- SQLAlchemy sessions
- JWT token validation

## Multi-Tenancy Testing

All authenticated endpoints must test multi-tenancy isolation:

```python
def test_download_multi_tenancy_enforcement(
    client,
    test_document_in_org_b,  # Document in Org B
):
    # User from Org A tries to access Org B's document
    token = create_test_token(organization_id=TEST_ORG_A_ID)

    response = client.get(
        f"/v1/documents/{test_document_in_org_b.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return 404 (not 403) to avoid info leakage
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
```

## Running Tests

```bash
# Run all document API tests
pytest apps/api/tests/test_documents_api.py -v

# Run specific test class
pytest apps/api/tests/test_documents_api.py::TestDocumentUpload -v

# Run with coverage
pytest apps/api/tests/test_documents_api.py --cov=app.api.v1.endpoints.documents

# Run only integration tests (skip unit tests)
pytest apps/api/tests/ -v
```

## Test Database Setup

Tests require a seeded test database. The `pytest_sessionstart` hook in `conftest.py` automatically seeds the database before tests run.

**Environment variable required**:
```bash
DATABASE_URL=postgresql://user:pass@host/qteria_test
```

**Manual seeding** (if needed):
```bash
cd apps/api
DATABASE_URL=postgresql://...neon.tech/qteria_test python scripts/seed_test_data.py
```

## Coverage Targets

Per `product-guidelines/09-test-strategy.md`:

- **Overall**: 70% code coverage
- **API Routes**: 80% coverage target
- **Multi-Tenancy**: 100% coverage (zero tolerance)
- **Auth/Authorization**: 100% coverage

## Common Issues

### Issue: Tests fail with 500 Internal Server Error

**Cause**: Test is mocking `get_db` which breaks authentication middleware.

**Solution**: Remove `patch("app.api.v1.endpoints.documents.get_db")` and use `client` fixture directly. Auth will use real database.

### Issue: Tests fail with "Organization not found" or "User not found"

**Cause**: Test database not seeded with required organizations/users.

**Solution**:
1. Ensure `DATABASE_URL` points to `qteria_test` database
2. Run `python scripts/seed_test_data.py` manually if needed
3. Check `pytest_sessionstart` hook executed successfully

### Issue: Tests pass locally but fail in CI

**Cause**: Different database state between local and CI.

**Solution**:
1. CI uses ephemeral Neon database (seeded fresh each run)
2. Local dev may have stale data - run `python scripts/clear_test_data.py` then reseed
3. Ensure tests clean up created data (or use transaction rollback)

## Migration from Unit to Integration Tests

This test suite was migrated from unit tests (mocking `get_db`) to integration tests (real database) to fix authentication issues. See issue #160 for details.

**Changes made**:
1. Removed all `patch("app.api.v1.endpoints.documents.get_db")` calls (41 instances)
2. Created real test fixtures: `test_workflow_with_bucket`, `test_document_in_org_a`, `test_document_in_org_b`
3. Simplified tests to use `client` fixture directly
4. Kept mocking for external services only (Vercel Blob, python-magic, audit service)

**Result**: Tests now run as true integration tests with real database access, matching the working pattern from `test_workflow_api.py`.
