# Plan GitHub Issue

You are tasked with creating a detailed implementation plan for a GitHub issue. You will plan this like a 10x senior developer: surgical, elegant, clean, and simple. NEVER implement backwards compatibility.

## Step 1: Read the GitHub Issue

First, fetch the GitHub issue details:

```bash
gh issue view {issue-number} --repo bru-digital/qteria --json title,body,labels,comments
```

Analyze the issue to understand:
- What feature/bug is being addressed
- Technical requirements
- User journey step involved (if applicable)
- Constraints and dependencies

## Step 2: Identify Relevant Product Guidelines

Based on the issue content, intelligently determine which product-guidelines files are relevant. Use this mapping:

**For Database/Schema Changes:**
- `product-guidelines/07-database-schema-essentials.md` (multi-tenancy patterns, schema design)
- `product-guidelines/07-database-schema.md` (detailed schema specifications)

**For API/Backend Changes:**
- `product-guidelines/08-api-contracts-essentials.md` (API standards, error formats, authentication)
- `product-guidelines/04-architecture.md` (API-first design, fail-safe patterns)
- `product-guidelines/00-user-journey.md` (which journey step does this support?)

**For Frontend/UI Changes:**
- `product-guidelines/06-design-system.md` (design tokens, components)
- `product-guidelines/00-user-journey.md` (user journey context)
- `product-guidelines/18-content-guidelines.md` (if copy/messaging involved)

**For Testing Strategy:**
- `product-guidelines/09-test-strategy-essentials.md` (coverage targets, required tests)
- `product-guidelines/09-test-strategy.md` (detailed testing patterns)

**For Authentication/Authorization/RBAC:**
- `product-guidelines/07-database-schema-essentials.md` (user model, roles)
- `product-guidelines/08-api-contracts-essentials.md` (JWT structure, auth patterns)

**For Deployment/Infrastructure:**
- `product-guidelines/13-deployment-plan.md` (deployment strategy)
- `product-guidelines/04-architecture.md` (scaling triggers, infrastructure)

**For Brand/Design:**
- `product-guidelines/05-brand-strategy.md` (brand positioning)
- `product-guidelines/06-design-system.md` (visual design)

**For Product Strategy/Features:**
- `product-guidelines/00-user-journey.md` (user journey steps, value delivered)
- `product-guidelines/01-product-strategy.md` (product positioning)
- `product-guidelines/03-mission.md` (mission alignment)

**Always Read:**
- `product-guidelines/00-user-journey.md` (to connect implementation to user value)
- `product-guidelines/04-architecture.md` (for architectural principles)
- `product-guidelines/09-test-strategy-essentials.md` (for test requirements)

**Additional Context:**
- If issue mentions "EPIC-03 (Workflow Management)" → Read journey Step 1
- If issue mentions "Journey Step X" → Read that specific section
- If issue involves data access → Read multi-tenancy patterns

Read ONLY the relevant files. Do NOT read unnecessary guidelines.

## Step 3: Read Relevant Product Guidelines

Use the Read tool to read the selected product-guidelines files based on your analysis from Step 2.

## Step 4: Plan Like a 10x Senior Developer

Create a surgical, elegant implementation plan following these principles:

### Planning Principles

1. **Surgical Precision**
   - Minimal file changes
   - Touch only what's necessary
   - No refactoring outside scope
   - Single responsibility per change

2. **Elegant Design**
   - Follow existing patterns in codebase
   - Leverage framework capabilities (FastAPI, Next.js)
   - Use declarative over imperative
   - Compose, don't repeat

3. **Clean & Simple**
   - Obvious over clever
   - Remove code, don't add layers
   - Flat over nested
   - Explicit over magical

4. **NO Backwards Compatibility**
   - NEVER add compatibility layers
   - NEVER support old and new simultaneously
   - Break cleanly if needed
   - Migration over gradual transition
   - Remove deprecated code immediately

### Plan Structure

Your plan MUST include:

#### 1. Product Context & Guidelines (NEW - Always Include)
Connect the implementation to the broader product vision:

**User Journey Context:**
- Which journey step(s) does this support? (e.g., Step 1: Process Manager Creates Workflow)
- What user value does this deliver? (e.g., "Clear understanding of validation requirements")
- Reference: `product-guidelines/00-user-journey.md` (specific lines if possible)

**Relevant Product Guidelines:**
List ONLY the guidelines you actually read and used:
- `product-guidelines/08-api-contracts-essentials.md` - Multi-tenancy patterns (lines X-Y), Error format standards (lines A-B)
- `product-guidelines/09-test-strategy-essentials.md` - Coverage targets (lines C-D)
- `product-guidelines/04-architecture.md` - API-first design (lines E-F)

**Key Standards to Follow:**
Extract 2-4 specific standards from guidelines that apply to this issue:
- Multi-tenancy: Return 404 (not 403) for other org's resources
- Error format: Include `code`, `message`, `details`, `request_id`
- Testing: 80% coverage for API routes, 100% for multi-tenancy
- Performance: P95 <500ms, P99 <2s

#### 2. Technical Approach (2-3 sentences)
High-level strategy. What pattern are you using? Why is this the simplest approach?

#### 3. Files to Modify (Exhaustive List)
List EVERY file that will be touched with one-line reasoning:
- `apps/api/app/models/user.py` - Add role field to User model
- `apps/api/alembic/versions/xxx.py` - Migration for role field
- `apps/api/app/api/v1/endpoints/auth.py` - Return role in JWT payload
- `apps/web/app/types/user.ts` - Add role to User type

#### 3. Database Changes (If Applicable)
- New tables/columns with types
- Indexes to add
- Foreign keys
- Migration strategy (if breaking)

#### 4. API Changes (If Applicable)
- New/modified endpoints with method and path
- Request/response schema changes
- Breaking changes clearly marked
- **Compliance:** Reference which API contract standards from guidelines this follows

#### 5. Implementation Steps (Sequential)
Numbered steps in execution order:
1. Create Alembic migration for X
2. Update SQLAlchemy model Y
3. Add Pydantic schema Z
4. Implement service function A
5. Add API endpoint B
6. Add frontend type C
7. Implement UI component D
8. Write tests for E, F, G

#### 6. Testing Requirements
- Unit tests needed (specific functions)
- Integration tests needed (specific flows)
- E2E tests needed (specific user journeys)
- Multi-tenancy tests (if data access involved)
- Auth tests (if permissions involved)

#### 7. Breaking Changes & Migration
- List any breaking changes
- Migration steps for existing data
- NO backwards compatibility layers

#### 8. Success Criteria
- How to verify the implementation works
- Performance benchmarks (if applicable)
- Coverage targets

### Anti-Patterns to AVOID

- ❌ Generic plans ("Update the database", "Add frontend code")
- ❌ Backwards compatibility layers
- ❌ Feature flags for gradual rollout
- ❌ Abstraction layers "for future flexibility"
- ❌ Over-engineering for scale we don't have
- ❌ Adding code that's not directly required
- ❌ Premature optimization
- ❌ Breaking changes without clear migration path

### Example Output Format

```markdown
## Implementation Plan for Issue #{issue-number}: {Title}

### Product Context & Guidelines

**User Journey Context:**
- Supports Journey Step 1: Process Manager defines validation workflows
- Value Delivered: Ensures only authorized users (Process Managers) can create/modify workflows, preventing accidental changes by Project Handlers
- Reference: `product-guidelines/00-user-journey.md` (Step 1, lines 69-96)

**Relevant Product Guidelines:**
- `product-guidelines/08-api-contracts-essentials.md` - JWT structure (lines 422-432), Role-based access (lines 434-438)
- `product-guidelines/09-test-strategy-essentials.md` - Multi-tenancy security requires 100% coverage (line 26)
- `product-guidelines/04-architecture.md` - API-first design (lines 135-178)
- `product-guidelines/07-database-schema-essentials.md` - Users table has role field

**Key Standards to Follow:**
- Authentication: JWT Bearer tokens with `{sub, org_id, email, role}` payload
- Multi-tenancy: All queries filter by `organization_id`, 100% test coverage required
- Error responses: Return 403 Forbidden for insufficient permissions (not 401)
- RBAC roles: `process_manager`, `project_handler`, `admin`

### Technical Approach
We'll add RBAC by extending the User model with a `role` enum field, updating the JWT payload to include role, and adding middleware to check permissions. This leverages SQLAlchemy enums and FastAPI dependencies—no custom framework needed.

### Files to Modify
- `apps/api/app/models/user.py` - Add role enum field
- `apps/api/alembic/versions/xxx_add_user_role.py` - Migration for role field
- `apps/api/app/schemas/user.py` - Add role to UserResponse schema
- `apps/api/app/api/v1/endpoints/auth.py` - Include role in JWT payload
- `apps/api/app/api/dependencies.py` - Add get_current_user_with_role dependency
- `apps/api/app/api/v1/endpoints/workflows.py` - Protect with role check
- `apps/web/app/types/user.ts` - Add role to User type
- `apps/api/tests/test_rbac.py` - Comprehensive RBAC tests

### Database Changes
**Add column to `users` table:**
- `role` - VARCHAR (enum: process_manager, project_handler, admin), NOT NULL, default='project_handler'

**Migration Strategy:**
- Set all existing users to 'project_handler' role
- This is a breaking change—admins must manually promote users after deploy

### API Changes
**Modified endpoint:**
- `POST /v1/auth/login` - Response now includes `role` field

**Breaking Change:**
- JWT payload structure changes (adds `role` claim)
- Old tokens will be rejected (users must re-login)

### Implementation Steps
1. Create Alembic migration adding `role` column to users table
2. Update `User` SQLAlchemy model with role enum
3. Update `UserResponse` Pydantic schema to include role
4. Modify auth endpoint to include role in JWT payload
5. Create `get_current_user_with_role` dependency in dependencies.py
6. Add `require_role` dependency factory for permission checks
7. Protect workflow creation endpoint (process_manager only)
8. Update frontend User type to include role
9. Write unit tests for role assignment
10. Write integration tests for protected endpoints (401/403 cases)
11. Write multi-tenancy tests (role checks respect org boundaries)

### Testing Requirements
**Unit Tests:**
- `test_user_role_default()` - New users get project_handler role
- `test_jwt_includes_role()` - Login returns role in token

**Integration Tests:**
- `test_workflow_creation_requires_process_manager()` - 403 for project_handler
- `test_workflow_creation_allows_process_manager()` - 200 for process_manager
- `test_workflow_creation_respects_org_isolation()` - Can't access other org's workflows even as process_manager

**Coverage Target:** 100% for RBAC logic (multi-tenancy security)

### Breaking Changes & Migration
**Breaking Changes:**
1. JWT token structure changes (adds `role` claim)
2. All workflow creation endpoints now require process_manager role

**Migration:**
1. Deploy backend changes
2. All existing users default to project_handler role
3. Admin manually runs SQL to promote users: `UPDATE users SET role = 'process_manager' WHERE email IN (...)`
4. Users must re-login to get new JWT with role claim
5. NO backwards compatibility—old tokens immediately invalid

### Success Criteria
- Process managers can create workflows (200 response)
- Project handlers cannot create workflows (403 response)
- JWT tokens include role claim
- All RBAC tests pass with 100% coverage
- Multi-tenancy isolation still enforced
```

## Step 5: Output the Plan

Provide the complete implementation plan following the structure above. Be specific, surgical, and elegant. NO backwards compatibility.

**CRITICAL:** Always start with the "Product Context & Guidelines" section to connect the technical implementation to the broader product vision. This helps ensure:
- Implementation aligns with user journey and product strategy
- Standards from product guidelines are followed
- Testing coverage meets requirements
- Multi-tenancy and security patterns are applied correctly

The plan should be ready to hand off to another developer (or yourself) for implementation without further clarification needed.
