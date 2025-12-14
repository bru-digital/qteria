# Audit Guidelines Compliance

You are tasked with auditing code changes against product guidelines. Execute with surgical precision using a two-phase analysis approach.

**CRITICAL PRINCIPLES:**
- **High Signal, Low Noise:** Only report violations, not perfect compliance
- **Context Efficient:** Read only relevant guideline sections, not entire files
- **Actionable Findings:** Provide specific fixes with line numbers, not generic advice
- **Smart Selection:** Audit only guidelines affected by the changes

---

## Phase 1: Analyze Changes & Select Guidelines (5-10 minutes)

### Step 1.1: Understand What Changed

**Option A: Audit Recent Changes (Default)**
```bash
# Get recent commits
git log --oneline -10

# Get files changed in last commit
git diff --name-only HEAD~1 HEAD

# Or get uncommitted changes
git status --short
```

**Option B: Audit Specific Commit/PR**
```bash
# If user provided commit hash
git diff --name-only {commit-hash}~1 {commit-hash}

# If user provided PR number
gh pr view {pr-number} --json files --jq '.files[].path'
```

**Output:** List of changed files by category:
- Backend: `apps/api/**/*.py`
- Frontend: `apps/web/**/*.{ts,tsx}`
- Database: `apps/api/alembic/versions/*.py`
- Config: `*.json`, `*.toml`, `*.yml`

---

### Step 1.2: Identify Change Type & Affected Guidelines

**Analyze file patterns to determine change type:**

| Files Changed | Change Type | Affected Guidelines |
|---------------|-------------|---------------------|
| `apps/api/app/models/*.py` | Database Schema | 07-database-schema, 09-test-strategy (multi-tenancy) |
| `apps/api/alembic/versions/*.py` | Migration | 07-database-schema, 12-project-scaffold (migration patterns) |
| `apps/api/app/api/v1/endpoints/*.py` | API Endpoint | 08-api-contracts, 09-test-strategy, 04-architecture |
| `apps/api/app/core/auth.py` | Authentication | 08-api-contracts (JWT structure), 07-database-schema (RBAC) |
| `apps/api/app/services/*.py` | Business Logic | 04-architecture (fail-safe), 09-test-strategy |
| `apps/web/app/**/*.tsx` | Frontend UI | 06-design-system, 18-content-guidelines |
| `apps/web/app/api/v1/**/*.ts` | API Proxy | 08-api-contracts (auth, error format) |
| `apps/web/types/*.d.ts` | Type Definitions | 08-api-contracts (contracts match backend) |
| `apps/web/lib/*.ts` | Frontend Utilities | 04-architecture (if shared code) |
| `*.md` | Documentation | 18-content-guidelines (if user-facing) |

**Use intelligent pattern matching:**
```bash
# Check if changes touch multi-tenancy (CRITICAL - always audit)
git diff HEAD~1 HEAD | grep -i "organization_id\|organizationId" && echo "MULTI_TENANCY_AFFECTED"

# Check if changes touch authentication
git diff HEAD~1 HEAD | grep -i "jwt\|auth\|token" && echo "AUTH_AFFECTED"

# Check if changes touch error handling
git diff HEAD~1 HEAD | grep -i "error\|exception\|raise" && echo "ERROR_HANDLING_AFFECTED"

# Check if changes touch rate limiting / Redis
git diff HEAD~1 HEAD | grep -i "redis\|rate.limit\|cache" && echo "REDIS_AFFECTED"
```

**Output a focused audit scope:**
```markdown
### Audit Scope

**Change Type:** API Endpoint Modification (JWT authentication)
**Files Changed:** 3 files (workflows/documents/assessments routes)
**Affected Guidelines:**
- `08-api-contracts-essentials.md` (Authentication, Error Format)
- `09-test-strategy-essentials.md` (Auth tests, Coverage targets)

**Critical Patterns to Check:**
- [ ] Multi-tenancy isolation (if data access)
- [ ] Error code format (SCREAMING_SNAKE_CASE)
- [ ] JWT payload structure (snake_case vs camelCase)
- [ ] Test coverage (auth tests required)
```

**KEY: Don't audit ALL guidelines - only those affected by changes!**

---

## Phase 2: Audit Against Selected Guidelines (10-20 minutes)

For each selected guideline, perform targeted checks using Grep + Read (efficient context loading).

### Step 2.1: Database Schema Guidelines (07-database-schema-essentials.md)

**When to audit:** Changes to `models/*.py`, `alembic/versions/*.py`

**Critical Checks:**

1. **Multi-Tenancy Isolation (CRITICAL - 100% Coverage Required)**
   ```bash
   # Check if new models have organization_id
   grep -n "class.*Base" apps/api/app/models/*.py | while read class; do
     file=$(echo $class | cut -d: -f1)
     if ! grep -q "organization_id" $file; then
       echo "❌ CRITICAL: $file missing organization_id for multi-tenancy"
     fi
   done

   # Check if queries filter by organization_id
   git diff HEAD~1 HEAD apps/api/app/api/v1/endpoints/*.py | grep "filter\|query" | grep -v "organization_id"
   ```

2. **Foreign Key Constraints**
   ```bash
   # Check migrations have proper cascades
   grep -n "ForeignKey" apps/api/alembic/versions/*.py | grep -v "ondelete"
   # Should have ondelete=CASCADE or ondelete=RESTRICT explicitly
   ```

3. **UUID Primary Keys**
   ```bash
   # Check new models use UUID, not Integer
   git diff HEAD~1 HEAD apps/api/app/models/*.py | grep "id.*=.*Column" | grep -v "UUID"
   ```

**Output Format:**
```markdown
### Database Schema Compliance

**CRITICAL VIOLATIONS:**
- ❌ `apps/api/app/models/workflow.py:15` - Missing organization_id column (multi-tenancy violation)
  - **Guideline:** 07-database-schema-essentials.md, line 89-105 (Multi-tenancy)
  - **Fix:** Add `organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)`

**HIGH VIOLATIONS:**
- ⚠️ `apps/api/alembic/versions/abc123.py:25` - ForeignKey missing ondelete (should be CASCADE or RESTRICT)
  - **Guideline:** 07-database-schema-essentials.md, line 150-160
  - **Fix:** Add `ondelete="CASCADE"` to ForeignKey definition

**PASSED:**
- ✅ All models use UUID primary keys
- ✅ Indexes on foreign keys
```

---

### Step 2.2: API Contracts Guidelines (08-api-contracts-essentials.md)

**When to audit:** Changes to `app/api/v1/endpoints/*.py`, `app/api/v1/**/*.ts`

**Critical Checks:**

1. **Authentication (JWT Structure)**
   ```bash
   # Check JWT payload field names (snake_case for backend)
   git diff HEAD~1 HEAD | grep -i "jwt\|payload" | grep -i "organizationId"
   # Should be org_id (snake_case) not organizationId (camelCase)

   # Check if shared JWT helper is used (DRY)
   grep -rn "generateJWT\|sign(" apps/web/app/api/v1/ | wc -l
   # Should be 0 (use shared helper) or 1 (shared helper location)
   ```

2. **Error Code Format**
   ```bash
   # Check error codes are SCREAMING_SNAKE_CASE
   git diff HEAD~1 HEAD | grep -i "error.*code" | grep -v "[A-Z_]*" | grep "[a-z-]"
   # Should have no matches (all SCREAMING_SNAKE_CASE)

   # Check error response structure
   git diff HEAD~1 HEAD apps/api/app/api/v1/endpoints/*.py | grep -A5 "HTTPException\|create_error_response"
   # Verify has: error_code, message, request_id
   ```

3. **Rate Limit Headers**
   ```bash
   # If changes touch rate limiting
   git diff HEAD~1 HEAD | grep -i "rate.limit" -A10 | grep -i "X-RateLimit"
   # Should have X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
   ```

4. **Multi-Tenancy in Endpoints**
   ```bash
   # Check if endpoints filter by organization_id
   git diff HEAD~1 HEAD apps/api/app/api/v1/endpoints/*.py | grep "filter\|query" -A5 | grep "organization_id"
   # Should exist for all data access

   # Check if 404 returned (not 403) for other org's data
   git diff HEAD~1 HEAD | grep "403\|FORBIDDEN"
   # Should use 404 for multi-tenancy isolation
   ```

**Output Format:**
```markdown
### API Contracts Compliance

**CRITICAL VIOLATIONS:**
- ❌ `apps/web/app/api/v1/workflows/route.ts:53` - JWT payload uses `organizationId` (should be `org_id`)
  - **Guideline:** 08-api-contracts-essentials.md, line 89-95 (JWT Authentication)
  - **Reason:** Backend expects snake_case per Python conventions (apps/api/app/core/auth.py:177)
  - **Fix:**
    ```typescript
    // Before
    organizationId: session.user.organizationId,

    // After
    org_id: session.user.organizationId,
    ```

**HIGH VIOLATIONS:**
- ⚠️ `apps/api/app/api/v1/endpoints/workflows.py:89` - Error code uses kebab-case `"workflow-not-found"`
  - **Guideline:** 08-api-contracts-essentials.md, line 450-470 (Error Code Format)
  - **Fix:** Change to `"WORKFLOW_NOT_FOUND"` (SCREAMING_SNAKE_CASE)

**MEDIUM VIOLATIONS:**
- ⚠️ Duplicate JWT generation in 3 files (DRY violation)
  - **Guideline:** 04-architecture.md, line 45-60 (Compose, don't repeat)
  - **Fix:** Create shared `apps/web/lib/backend-jwt.ts` helper

**PASSED:**
- ✅ Error responses include request_id
- ✅ Multi-tenancy queries filter by organization_id
```

---

### Step 2.3: Test Strategy Guidelines (09-test-strategy-essentials.md)

**When to audit:** ALL code changes (tests are always required)

**Critical Checks:**

1. **Test Coverage Targets**
   ```bash
   # Get coverage for changed files
   pytest --cov=app --cov-report=term-missing | grep -A5 "TOTAL"
   # Should be >=70% overall, >=80% for API routes, 100% for multi-tenancy
   ```

2. **Required Test Types**
   ```bash
   # Check if API changes have auth tests
   if git diff HEAD~1 HEAD --name-only | grep "app/api/v1/endpoints"; then
     # Should have tests for: 401 (no token), 401 (invalid token), 403 (wrong role)
     git diff HEAD~1 HEAD | grep "test.*auth\|test.*401\|test.*403"
   fi

   # Check if data access has multi-tenancy tests
   if git diff HEAD~1 HEAD | grep "organization_id"; then
     # Should have test for 404 when accessing other org's data
     git diff HEAD~1 HEAD | grep "test.*multi.tenancy\|test.*organization.*isolation"
   fi
   ```

3. **AI Validation Tests (Critical Path)**
   ```bash
   # If changes touch AI validation
   if git diff HEAD~1 HEAD --name-only | grep "validation\|assessment\|claude"; then
     # Should have >=95% coverage (false positives/negatives unacceptable)
     echo "⚠️ AI validation changes - require 95% coverage"
   fi
   ```

**Output Format:**
```markdown
### Test Strategy Compliance

**CRITICAL VIOLATIONS:**
- ❌ Missing multi-tenancy tests for new endpoint
  - **Guideline:** 09-test-strategy-essentials.md, line 45-60 (100% multi-tenancy coverage)
  - **Required Tests:**
    1. `test_workflow_access_denied_for_other_org()` - Returns 404 (not 403)
    2. `test_workflow_list_filtered_by_organization()`
  - **Fix:** Add to `tests/test_workflows_api.py`

**HIGH VIOLATIONS:**
- ⚠️ Coverage dropped from 78% to 72% (below 70% target)
  - **Guideline:** 09-test-strategy-essentials.md, line 15-20
  - **Files Under 70%:** `app/api/v1/endpoints/documents.py` (65%)
  - **Fix:** Add tests for error cases (file size limit, invalid type)

**MEDIUM VIOLATIONS:**
- ⚠️ Missing authentication tests (401/403)
  - **Guideline:** 09-test-strategy-essentials.md, line 89-105
  - **Required Tests:**
    1. `test_create_workflow_requires_authentication()` - 401 without token
    2. `test_create_workflow_requires_process_manager_role()` - 403 for project_handler

**PASSED:**
- ✅ Overall coverage at 75%
- ✅ API routes have integration tests
```

---

### Step 2.4: Architecture Guidelines (04-architecture.md)

**When to audit:** Backend services, shared utilities, infrastructure changes

**Critical Checks:**

1. **Fail-Safe Patterns**
   ```bash
   # Check if Redis/external services have graceful degradation
   git diff HEAD~1 HEAD | grep -i "redis\|celery\|claude" -A10 | grep "try\|except\|catch"
   # Should have error handling with fail-open or fail-closed strategy
   ```

2. **DRY Violations**
   ```bash
   # Find duplicate functions
   for func in $(git diff HEAD~1 HEAD | grep "^+.*def " | awk '{print $2}' | cut -d'(' -f1); do
     count=$(grep -rn "def $func(" apps/ | wc -l)
     if [ $count -gt 1 ]; then
       echo "⚠️ Duplicate function: $func (found $count times)"
     fi
   done
   ```

3. **Magic Numbers**
   ```bash
   # Check for hardcoded limits/timeouts
   git diff HEAD~1 HEAD | grep -E "[^a-zA-Z_](100|1000|3600|86400)[^0-9]"
   # Should use named constants (UPLOAD_LIMIT, RATE_LIMIT_HOUR, etc.)
   ```

**Output Format:**
```markdown
### Architecture Compliance

**HIGH VIOLATIONS:**
- ⚠️ Redis errors not handled gracefully
  - **Guideline:** 04-architecture.md, line 89-105 (Fail-safe architecture)
  - **Location:** `apps/api/app/core/dependencies.py:45`
  - **Issue:** Redis connection failure crashes request (should fail-open)
  - **Fix:**
    ```python
    try:
        redis_client.incrby(key, count)
    except redis.ConnectionError:
        logger.error("Redis unavailable - failing open", exc_info=True)
        # Allow request to proceed (availability > strict enforcement)
        return RateLimitResult(allowed=True, fail_open=True)
    ```

**MEDIUM VIOLATIONS:**
- ⚠️ Magic number 100 hardcoded (should be constant)
  - **Location:** `apps/api/app/api/v1/endpoints/documents.py:67`
  - **Fix:** Extract to `settings.UPLOAD_RATE_LIMIT_PER_HOUR = 100`

**PASSED:**
- ✅ Background jobs have retry logic
- ✅ No duplicate service functions
```

---

### Step 2.5: Design System Guidelines (06-design-system.md)

**When to audit:** Frontend UI changes (`apps/web/app/**/*.tsx`)

**Critical Checks:**

1. **Component Usage**
   ```bash
   # Check if custom components instead of shadcn/ui
   git diff HEAD~1 HEAD apps/web/app/**/*.tsx | grep "<button\|<input\|<select" | grep -v "shadcn"
   # Should use Button, Input, Select from shadcn/ui
   ```

2. **Design Tokens**
   ```bash
   # Check for hardcoded colors/spacing
   git diff HEAD~1 HEAD apps/web/app/**/*.tsx | grep "className" | grep -E "#[0-9a-fA-F]{6}|rgb\(|px-[0-9]+|text-\[.*\]"
   # Should use Tailwind design tokens
   ```

**Output Format:**
```markdown
### Design System Compliance

**MEDIUM VIOLATIONS:**
- ⚠️ Hardcoded button instead of shadcn/ui Button
  - **Location:** `apps/web/app/workflows/new/page.tsx:45`
  - **Fix:** Replace `<button className="...">` with `<Button variant="default">`
```

---

### Step 2.6: Content Guidelines (18-content-guidelines.md)

**When to audit:** User-facing copy changes (error messages, UI text)

**Critical Checks:**

1. **Error Message Tone**
   ```bash
   # Check error messages are user-friendly
   git diff HEAD~1 HEAD | grep "message.*:" | grep -i "invalid\|error\|fail"
   # Should be actionable, not technical jargon
   ```

**Output Format:**
```markdown
### Content Guidelines Compliance

**MEDIUM VIOLATIONS:**
- ⚠️ Technical error message exposed to user
  - **Location:** `apps/web/app/api/v1/workflows/route.ts:73`
  - **Current:** "JWT validation failed: invalid signature"
  - **Fix:** "Your session has expired. Please log in again."
```

---

## Phase 3: Generate Findings Report (5 minutes)

### Step 3.1: Aggregate Findings by Severity

**Severity Levels:**
- 🔴 **CRITICAL:** Security, data leakage, multi-tenancy violations → Block deployment
- 🟠 **HIGH:** Contract violations, missing tests, fail-safe issues → Fix before merge
- 🟡 **MEDIUM:** DRY violations, magic numbers, style issues → Fix in follow-up
- 🟢 **LOW:** Documentation, comments, minor improvements → Optional

### Step 3.2: Output Final Report

```markdown
# Guidelines Audit Report

**Scope:** Recent changes (commit {hash} or last {N} commits)
**Files Audited:** {count} files across {categories}
**Guidelines Checked:** {list}

---

## Executive Summary

**🔴 CRITICAL:** {count} violations (MUST FIX before deployment)
**🟠 HIGH:** {count} violations (SHOULD FIX before merge)
**🟡 MEDIUM:** {count} violations (CAN FIX in follow-up)
**🟢 LOW:** {count} suggestions (OPTIONAL improvements)

**Overall Compliance:** {percentage}% ({passed}/{total} checks passed)

**DEPLOYMENT RECOMMENDATION:** {BLOCK | WARN | PASS}

---

## Critical Violations (🔴 MUST FIX)

### 1. Multi-Tenancy Isolation Missing
- **File:** `apps/api/app/models/workflow.py:15`
- **Guideline:** 07-database-schema-essentials.md, line 89-105
- **Issue:** Missing organization_id column
- **Impact:** Data leakage between organizations (GDPR violation)
- **Fix:**
  ```python
  organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
  ```
- **Tests Required:**
  - `test_workflow_filtered_by_organization()`
  - `test_workflow_access_denied_for_other_org()`

### 2. JWT Field Name Mismatch
- **File:** `apps/web/app/api/v1/workflows/route.ts:53`
- **Guideline:** 08-api-contracts-essentials.md, line 89-95
- **Issue:** Using `organizationId` (camelCase), backend expects `org_id` (snake_case)
- **Impact:** Authentication fails with 401 (blocks all authenticated requests)
- **Fix:**
  ```typescript
  // Change
  organizationId: session.user.organizationId,
  // To
  org_id: session.user.organizationId,
  ```
- **Tests Required:**
  - Integration test validating JWT payload structure

---

## High Violations (🟠 SHOULD FIX)

### 1. Error Code Format Violation
- **File:** `apps/api/app/api/v1/endpoints/workflows.py:89`
- **Guideline:** 08-api-contracts-essentials.md, line 450-470
- **Issue:** Using kebab-case `"workflow-not-found"` instead of SCREAMING_SNAKE_CASE
- **Impact:** Inconsistent error handling, breaks frontend error parsing
- **Fix:** `"WORKFLOW_NOT_FOUND"`

### 2. Missing Authentication Tests
- **Files:** All new endpoints in `apps/api/app/api/v1/endpoints/`
- **Guideline:** 09-test-strategy-essentials.md, line 89-105
- **Issue:** No tests for 401/403 scenarios
- **Impact:** Security vulnerabilities undetected
- **Tests Required:**
  - `test_endpoint_requires_authentication()` - 401 without token
  - `test_endpoint_requires_role()` - 403 for insufficient permissions

---

## Medium Violations (🟡 CAN FIX)

### 1. DRY Violation - Duplicate JWT Generation
- **Files:** 3 copies in `apps/web/app/api/v1/*/route.ts`
- **Guideline:** 04-architecture.md, line 45-60
- **Issue:** Same `generateJWTFromSession()` function copied 3 times
- **Impact:** Bug propagates to all copies (current field name mismatch in all 3)
- **Fix:** Create shared `apps/web/lib/backend-jwt.ts` helper

### 2. Magic Number - Hardcoded Rate Limit
- **File:** `apps/api/app/core/dependencies.py:67`
- **Guideline:** 04-architecture.md, line 120-135
- **Issue:** Hardcoded `100` instead of named constant
- **Fix:** Extract to `settings.UPLOAD_RATE_LIMIT_PER_HOUR = 100`

---

## Low Priority Suggestions (🟢 OPTIONAL)

### 1. Error Message Improvement
- **File:** `apps/web/app/api/v1/workflows/route.ts:73`
- **Guideline:** 18-content-guidelines.md
- **Suggestion:** Replace technical "JWT validation failed" with user-friendly "Your session has expired"

---

## Summary by Guideline

| Guideline | Critical | High | Medium | Low | Status |
|-----------|----------|------|--------|-----|--------|
| 07-database-schema | 1 | 0 | 0 | 0 | 🔴 FAIL |
| 08-api-contracts | 1 | 2 | 1 | 1 | 🔴 FAIL |
| 09-test-strategy | 0 | 2 | 0 | 0 | 🟠 WARN |
| 04-architecture | 0 | 1 | 2 | 0 | 🟡 PASS |
| 06-design-system | 0 | 0 | 0 | 0 | ✅ PASS |

---

## Recommended Actions

**Before Deployment:**
1. Fix all 2 CRITICAL violations (multi-tenancy, JWT field name)
2. Add 4 required tests (multi-tenancy, auth)
3. Re-run audit to verify fixes

**Before Merge:**
1. Fix all 4 HIGH violations (error codes, auth tests)
2. Achieve 70%+ test coverage

**Follow-Up Issue:**
1. Create issue for 3 MEDIUM violations (DRY, magic numbers)
2. Target next sprint

**Optional Improvements:**
1. Consider LOW priority suggestions for polish

---

## Prevention Strategies

**To prevent future violations:**

1. **Add Pre-Commit Hook:**
   ```bash
   # .husky/pre-commit
   # Check JWT field names
   if grep -r "organizationId:" apps/web/app/api/v1/; then
     echo "❌ JWT payload uses 'organizationId' (should be 'org_id')"
     exit 1
   fi
   ```

2. **Add Contract Test:**
   ```python
   # tests/integration/test_contracts.py
   def test_jwt_payload_structure():
       """Validate JWT from frontend matches backend."""
       assert "org_id" in payload
       assert "organizationId" not in payload
   ```

3. **Use Shared Types:**
   ```typescript
   // types/api-contracts.ts
   export interface BackendJWTPayload {
     org_id: string  // Enforced by TypeScript
   }
   ```

4. **Update `/plan-issue` Command:**
   - Add "Step 3.5: Contract Validation" phase
   - Explicitly check existing patterns before planning

---

**Audit completed in {duration} minutes.**
**Next: Fix CRITICAL violations, re-run audit, deploy.**
```

---

## Usage Examples

**Audit recent changes:**
```bash
/audit-guidelines
```

**Audit specific commit:**
```bash
/audit-guidelines abc123f
```

**Audit specific PR:**
```bash
/audit-guidelines --pr 82
```

**Audit specific files:**
```bash
/audit-guidelines apps/web/app/api/v1/workflows/route.ts
```

---

## Anti-Patterns to AVOID

- ❌ Reading entire guideline files (use Grep with context)
- ❌ Auditing all guidelines (only relevant ones)
- ❌ Reporting what's already correct (focus on violations)
- ❌ Generic findings ("read the docs") → Provide specific fixes
- ❌ Missing line numbers and code snippets
- ❌ No severity classification (everything seems equally important)
- ❌ No actionable remediation steps

---

## Context Efficiency Checklist

Before reading a guideline file, ask:
- [ ] Is this guideline affected by the changes? (file patterns match)
- [ ] Can I use Grep to find relevant sections? (search for keywords)
- [ ] Can I check violations without reading? (automated grep/diff checks)
- [ ] Is there a specific line range to read? (not entire 500-line file)

**Read only what's necessary. Grep first, Read targeted sections second.**

---

## Output Requirements

**Every violation MUST include:**
1. ✅ Severity level (CRITICAL/HIGH/MEDIUM/LOW)
2. ✅ File path and line number
3. ✅ Guideline reference (file, line numbers)
4. ✅ Specific issue explanation
5. ✅ Impact/consequences
6. ✅ Exact fix (code diff or steps)
7. ✅ Required tests (if applicable)

**Reports MUST include:**
1. ✅ Executive summary with counts
2. ✅ Deployment recommendation (BLOCK/WARN/PASS)
3. ✅ Prevention strategies (pre-commit hooks, tests)
4. ✅ Summary by guideline (compliance table)

---

**Remember: High signal, low noise. Actionable findings with specific fixes. Context-efficient analysis.**
