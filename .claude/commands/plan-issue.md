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

Based on the issue content, intelligently determine which product-guidelines files are relevant. **Read ONLY what's necessary** to avoid context bloat.

### Smart Guideline Selection Rules

**For Database/Schema Changes:**
- `product-guidelines/07-database-schema-essentials.md` (multi-tenancy patterns, schema design)
- `product-guidelines/09-test-strategy-essentials.md` (multi-tenancy requires 100% test coverage)

**For API/Backend Changes:**
- `product-guidelines/08-api-contracts-essentials.md` (API standards, error formats, authentication)
- `product-guidelines/04-architecture.md` (API-first design, fail-safe patterns)
- `product-guidelines/09-test-strategy-essentials.md` (coverage targets)

**For Rate Limiting/Caching/Redis:**
- `product-guidelines/08-api-contracts-essentials.md` (rate limit specs, error format)
- `product-guidelines/04-architecture.md` (fail-safe patterns, graceful degradation)
- **Skip heavy files** - you'll research Redis patterns externally (Step 3.5)

**For Frontend/UI Changes:**
- `product-guidelines/06-design-system.md` (design tokens, components)
- `product-guidelines/18-content-guidelines.md` (if copy/messaging involved)

**For Testing Strategy:**
- `product-guidelines/09-test-strategy-essentials.md` (coverage targets, required tests)

**For Authentication/Authorization/RBAC:**
- `product-guidelines/07-database-schema-essentials.md` (user model, roles)
- `product-guidelines/08-api-contracts-essentials.md` (JWT structure, auth patterns)

**For Deployment/Infrastructure:**
- `product-guidelines/13-deployment-plan.md` (deployment strategy)
- `product-guidelines/04-architecture.md` (scaling triggers, infrastructure)

**For Background Jobs/Celery:**
- `product-guidelines/04-architecture.md` (background job patterns)
- **Skip heavy files** - you'll research Celery patterns externally (Step 3.5)

**For File Uploads:**
- `product-guidelines/08-api-contracts-essentials.md` (file upload limits, error handling)
- **Skip heavy files** - you'll research streaming upload patterns externally (Step 3.5)

**Always Read (Core Context):**
- `product-guidelines/00-user-journey.md` (to connect implementation to user value)
- `product-guidelines/09-test-strategy-essentials.md` (for test requirements)

**Conditionally Read:**
- `product-guidelines/04-architecture.md` - Only for backend/infrastructure issues
- If issue mentions "EPIC-03 (Workflow Management)" → Read journey Step 1
- If issue mentions "Journey Step X" → Read that specific section
- If issue involves data access → Include multi-tenancy patterns

**Key Principle:** Read guidelines for **standards and requirements** (error formats, test coverage, multi-tenancy). Research **implementation patterns** externally (Redis, Celery, file uploads).

## Step 3: Read Relevant Product Guidelines

Use the Read tool to read the selected product-guidelines files based on your analysis from Step 2.

## Step 3.5: Research Proven Patterns & Edge Cases ⭐ CRITICAL

**STOP!** Before designing your solution, research if this is a **solved problem**. Don't reinvent the wheel.

### Research Phase (15-30 minutes)

**Research by Issue Type:**

**Rate Limiting (Redis-based):**
- WebSearch: "Redis rate limiting patterns best practices 2024"
- WebSearch: "Redis INCR vs INCRBY race conditions"
- Key Questions: Increment-first or check-first? EXPIRE vs EXPIREAT? Connection pooling config?
- Look for: Atomic operations, TTL strategies, graceful degradation patterns

**Authentication/JWT:**
- WebSearch: "FastAPI JWT authentication best practices"
- Check codebase: `apps/api/app/core/auth.py` for existing patterns
- Key Questions: Token refresh strategy? Role-based claims? Expiration handling?

**File Uploads (Large Files):**
- WebSearch: "FastAPI streaming file upload best practices"
- WebSearch: "Vercel Blob storage upload patterns"
- Key Questions: Streaming vs buffering? Multipart handling? Progress tracking?

**Background Jobs (Celery):**
- WebSearch: "Celery best practices error handling retry"
- Check codebase: Look for existing Celery tasks
- Key Questions: Idempotency? Retry strategy? Dead letter queue?

**Caching Strategies:**
- WebSearch: "Redis caching patterns TTL eviction"
- Key Questions: Cache-aside vs write-through? TTL strategy? Invalidation approach?

**Database Migrations:**
- Check codebase: `apps/api/alembic/versions/` for migration patterns
- Key Questions: Data backfill needed? Index creation strategy? Downgrade support?

**Frontend State Management:**
- Check codebase: `apps/web/` for existing Zustand patterns
- Key Questions: Global vs local state? Persistence needed? Optimistic updates?

**General Research Protocol:**
1. **Is this a solved problem?** (Yes for rate limiting, auth, caching, file uploads)
2. **What patterns exist in our codebase?** (grep for similar features)
3. **What are known edge cases?** (search "X common mistakes" or "X pitfalls")
4. **What are concurrency issues?** (race conditions, atomic operations)
5. **What infrastructure is needed?** (connection pooling, timeouts, retries)

### Edge Case Identification Checklist

**For API Endpoints:**
- [ ] Concurrent requests (race conditions, atomic operations)
- [ ] Missing/malformed input (validation, error messages)
- [ ] Authentication edge cases (expired token, invalid signature, no token)
- [ ] Multi-tenancy isolation (404 for other org's data, not 403)
- [ ] Rate limiting (at boundary: 99→100→101)
- [ ] Large payloads (file size limits, batch operations)
- [ ] Timeout scenarios (database down, external API slow, Redis unavailable)

**For Background Jobs:**
- [ ] Job failure mid-execution (rollback, cleanup, idempotency)
- [ ] Retry logic (exponential backoff, max retries, jitter)
- [ ] Dead letter queue (failed jobs handling)
- [ ] Long-running jobs (progress tracking, cancellation)
- [ ] Duplicate job execution (at-least-once vs exactly-once)

**For Database Operations:**
- [ ] Connection pool exhaustion
- [ ] Transaction rollback on error
- [ ] Unique constraint violations
- [ ] Foreign key cascades (delete implications)
- [ ] Large result sets (pagination, memory limits)
- [ ] Migration rollback (downgrade support)

**For Caching/Redis:**
- [ ] Cache miss handling (thundering herd)
- [ ] TTL expiration during operation
- [ ] Connection failures (graceful degradation, fail-open vs fail-closed)
- [ ] Key naming collisions
- [ ] Memory limits (eviction policy: LRU, LFU)
- [ ] Stale data (invalidation strategy)

**For File Operations:**
- [ ] File size limits (upload/download)
- [ ] Concurrent uploads/downloads (same file)
- [ ] Partial uploads (resume, cleanup orphaned files)
- [ ] Storage quota exceeded
- [ ] File type validation bypass (magic bytes, not extension)
- [ ] Path traversal attacks

**For Frontend/UI:**
- [ ] Loading states (skeleton, spinner, optimistic updates)
- [ ] Error states (network failure, validation errors)
- [ ] Empty states (no data, no results)
- [ ] Accessibility (keyboard navigation, screen readers)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Browser compatibility

### Research Output Template

Document your findings in this format:

```markdown
### Research Findings

**Proven Pattern Identified:**
- **Pattern Name:** [e.g., "Increment-First Rate Limiting"]
- **Source:** [URL or codebase file reference]
- **Algorithm:**
  [2-4 sentences explaining the approach step-by-step]
- **Why This Pattern:**
  [Explains how it handles edge cases better than alternatives]

**Edge Cases Identified & Mitigations:**
1. **[Edge case]** → [How we'll handle it]
2. **[Edge case]** → [How we'll handle it]
3. **[Edge case]** → [How we'll handle it]
[... list all identified edge cases]

**Infrastructure/Configuration Requirements:**
- [Specific config, e.g., "Redis: max_connections=10-20, socket_keepalive=True"]
- [Dependencies, e.g., "Requires Redis 7+ for EXPIREAT command"]
- [Performance tuning, e.g., "Timeout: socket_timeout=5s, connect_timeout=2s"]
```

**Example for Rate Limiting:**

```markdown
### Research Findings

**Proven Pattern Identified:**
- **Pattern Name:** Increment-First Rate Limiting with Atomic Rollback
- **Source:** https://redis.io/docs/manual/patterns/rate-limiter/
- **Algorithm:**
  1. Atomically increment counter using Redis pipeline (INCRBY + EXPIREAT)
  2. Check if new count exceeds limit
  3. If exceeded: Atomically rollback using DECRBY + EXPIREAT, return 429
  4. If not exceeded: Return success with count
- **Why This Pattern:**
  Prevents TOCTOU (Time-Of-Check-Time-Of-Use) race conditions. Traditional "check-then-increment" fails when multiple concurrent requests all see count=99 and proceed to 101. Increment-first ensures exactly one request succeeds at limit boundary (100).

**Edge Cases Identified & Mitigations:**
1. **Concurrent requests at 99/100 limit** → Increment-first ensures one succeeds (100), others rollback and fail (still 100)
2. **TTL reset on every request extends window beyond 1 hour** → Use EXPIREAT with absolute timestamp, not EXPIRE with relative seconds
3. **Batch uploads (20 files) count as 1 request** → Pass file_count parameter to INCRBY, not hardcoded 1
4. **Redis connection pool exhausted under load** → Configure max_connections=10-20 with socket_keepalive
5. **Redis unavailable mid-request** → Graceful degradation: fail-open (allow request) with error logging for availability
6. **Hour boundary edge case (23:59 → 00:00)** → Use timedelta for next hour calculation, not hour+1 arithmetic (avoids ValueError)
7. **Mock tests don't match implementation** → Ensure mocks use same Redis methods as implementation (incrby not incr)

**Infrastructure/Configuration Requirements:**
- **Redis connection pool:** max_connections=10, socket_keepalive=True, health_check_interval=30s
- **Redis commands:** INCRBY (not INCR), EXPIREAT (not EXPIRE), use pipeline for atomicity
- **Error handling:** Fail-open on Redis errors (availability over enforcement), audit logging on rate limit exceeded
- **Key pattern:** `rate_limit:upload:{user_id}:{YYYY-MM-DD-HH}` for per-user hourly buckets
```

### When to Skip Research

**Skip research if:**
- Issue is purely cosmetic (color change, copy update)
- Following established pattern in codebase (e.g., "add another API endpoint like /workflows")
- Simple CRUD operation with existing examples

**Always research if:**
- Implementing security features (auth, rate limiting, RBAC)
- Working with external systems (Redis, Celery, S3)
- Handling concurrency or race conditions
- New technology/pattern not in codebase

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

#### 1. Product Context & Guidelines
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

#### 2. Research Findings & Proven Patterns ⭐ REQUIRED

**Proven Pattern:**
- **Pattern Name:** [e.g., "Increment-First Rate Limiting"]
- **Source:** [URL or codebase file reference]
- **Algorithm:** [2-4 sentences explaining the approach step-by-step]
- **Why This Pattern:** [How it handles edge cases better than alternatives]

**Edge Cases & Mitigations:**
1. **[Edge case]** → [How we'll handle it]
2. **[Edge case]** → [How we'll handle it]
3. **[Edge case]** → [How we'll handle it]
[... list all identified edge cases from Step 3.5]

**Infrastructure/Configuration Requirements:**
- [Specific config needed, e.g., "Redis: max_connections=10-20, socket_keepalive=True"]
- [Dependencies, e.g., "Requires Redis 7+ for EXPIREAT command"]
- [Performance tuning, e.g., "Timeout: socket_timeout=5s, connect_timeout=2s"]

**Note:** If you skipped research (see Step 3.5 "When to Skip Research"), state: "Research skipped - following established CRUD pattern from [reference]"

#### 3. Technical Approach (2-3 sentences)
High-level strategy. What pattern are you using? Why is this the simplest approach?

#### 4. Files to Modify (Exhaustive List)
List EVERY file that will be touched with one-line reasoning:
- `apps/api/app/models/user.py` - Add role field to User model
- `apps/api/alembic/versions/xxx.py` - Migration for role field
- `apps/api/app/api/v1/endpoints/auth.py` - Return role in JWT payload
- `apps/web/app/types/user.ts` - Add role to User type

#### 5. Database Changes (If Applicable)
- New tables/columns with types
- Indexes to add
- Foreign keys
- Migration strategy (if breaking)

#### 6. API Changes (If Applicable)
- New/modified endpoints with method and path
- Request/response schema changes
- Breaking changes clearly marked
- **Compliance:** Reference which API contract standards from guidelines this follows

#### 7. Implementation Steps (Sequential)
Numbered steps in execution order:
1. Create Alembic migration for X
2. Update SQLAlchemy model Y
3. Add Pydantic schema Z
4. Implement service function A
5. Add API endpoint B
6. Add frontend type C
7. Implement UI component D
8. Write tests for E, F, G

#### 8. Testing Requirements
- Unit tests needed (specific functions)
- Integration tests needed (specific flows)
- E2E tests needed (specific user journeys)
- Multi-tenancy tests (if data access involved)
- Auth tests (if permissions involved)
- **Edge case tests:** List each edge case from Section 2 that needs a test

#### 9. Implementation Checklist ⭐ FOR IMPLEMENTATION AGENT

Create a checklist the implementation agent will use for self-review before committing:

**Pre-Implementation:**
- [ ] Reviewed proven pattern documentation/source from Section 2
- [ ] Identified all edge cases from research (Section 2)
- [ ] Checked for similar implementations in codebase
- [ ] Read relevant product guidelines (Section 1)

**During Implementation:**
- [ ] Following proven pattern from research (not custom solution)
- [ ] Handling all identified edge cases from Section 2
- [ ] [Specific requirement 1 from research, e.g., "Using INCRBY not INCR"]
- [ ] [Specific requirement 2 from research, e.g., "Using EXPIREAT not EXPIRE"]
- [ ] [Specific requirement 3 from research, e.g., "Connection pooling configured"]
- [ ] Atomic operations for race conditions (if applicable)
- [ ] Error handling with graceful degradation
- [ ] Audit logging for security events (if applicable)
- [ ] Multi-tenancy isolation (if data access)
- [ ] Extract magic numbers to constants (no hardcoded values)

**Testing:**
- [ ] Unit tests for happy path
- [ ] Unit tests for EACH edge case from Section 2
- [ ] Integration tests for concurrent scenarios (if applicable)
- [ ] Mock tests use same methods as implementation
- [ ] Multi-tenancy tests with 100% coverage (if data access)
- [ ] All tests passing locally

**Before Committing:**
- [ ] Self-review against this entire checklist
- [ ] Error responses match API contract format (SCREAMING_SNAKE_CASE codes)
- [ ] Logging includes contextual metadata (user_id, org_id, etc.)
- [ ] No TODO comments or console.log statements
- [ ] Documentation/comments explain WHY not WHAT

**Note:** Customize this checklist based on the specific issue. Add issue-specific items from research findings.

#### 10. Breaking Changes & Migration
- List any breaking changes
- Migration steps for existing data
- NO backwards compatibility layers

#### 11. Success Criteria
- How to verify the implementation works
- Performance benchmarks (if applicable)
- Coverage targets
- All edge cases from Section 2 handled correctly

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
## Implementation Plan for Issue #93: Implement Rate Limiting for Document Uploads

### 1. Product Context & Guidelines

**User Journey Context:**
- Supports Journey Step 2: Project Handler uploads documents
- Value Delivered: Prevents abuse, protects storage costs ($), ensures fair usage across all users
- Reference: `product-guidelines/08-api-contracts-essentials.md` (Rate limiting spec, lines 369-380)

**Relevant Product Guidelines:**
- `product-guidelines/08-api-contracts-essentials.md` - Rate limiting: 100 uploads/hour per user (line 369), Error format (lines 450-470)
- `product-guidelines/04-architecture.md` - Fail-safe architecture: graceful degradation (lines 89-105)
- `product-guidelines/09-test-strategy-essentials.md` - Coverage targets: 80% for API routes (line 15)

**Key Standards to Follow:**
- Rate limit: 100 uploads/hour per user (not per organization)
- Error code: RATE_LIMIT_EXCEEDED (SCREAMING_SNAKE_CASE)
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- Fail-safe: Fail-open if Redis unavailable (availability over strict enforcement)

### 2. Research Findings & Proven Patterns

**Proven Pattern:**
- **Pattern Name:** Increment-First Rate Limiting with Atomic Rollback
- **Source:** https://redis.io/docs/manual/patterns/rate-limiter/
- **Algorithm:**
  1. Atomically increment counter using Redis pipeline (INCRBY + EXPIREAT)
  2. Check if new count exceeds limit
  3. If exceeded: Atomically rollback using DECRBY + EXPIREAT, return 429
  4. If not exceeded: Return success with updated count
- **Why This Pattern:**
  Prevents TOCTOU (Time-Of-Check-Time-Of-Use) race conditions. Traditional "check-then-increment" fails when multiple concurrent requests all see count=99 and proceed to 101. Increment-first ensures exactly one request succeeds at limit boundary (100).

**Edge Cases & Mitigations:**
1. **Concurrent requests at 99/100 limit** → Increment-first ensures one succeeds (100), others rollback and fail (still 100)
2. **TTL reset on every request extends window beyond 1 hour** → Use EXPIREAT with absolute timestamp, not EXPIRE with relative seconds
3. **Batch uploads (20 files) count as 1 request** → Pass file_count parameter to INCRBY, not hardcoded 1
4. **Redis connection pool exhausted under load** → Configure max_connections=10-20 with socket_keepalive
5. **Redis unavailable mid-request** → Graceful degradation: fail-open (allow request) with error logging for availability
6. **Hour boundary edge case (23:59 → 00:00)** → Use timedelta for next hour calculation, not hour+1 arithmetic (avoids ValueError)
7. **Mock tests don't match implementation** → Ensure mocks use same Redis methods as implementation (incrby not incr)

**Infrastructure/Configuration Requirements:**
- **Redis connection pool:** max_connections=10, socket_keepalive=True, health_check_interval=30s
- **Redis commands:** INCRBY (not INCR), EXPIREAT (not EXPIRE), use pipeline for atomicity
- **Error handling:** Fail-open on Redis errors (availability over enforcement), audit logging on rate limit exceeded
- **Key pattern:** `rate_limit:upload:{user_id}:{YYYY-MM-DD-HH}` for per-user hourly buckets

### 3. Technical Approach
Implement Redis-based rate limiting using increment-first pattern to prevent race conditions. Use Redis pipeline for atomic INCRBY + EXPIREAT operations. Gracefully degrade if Redis unavailable (fail-open for availability). Return 429 with standardized error format and X-RateLimit-* headers per API contract.

### 4. Files to Modify
- `apps/api/app/core/dependencies.py` - Add check_upload_rate_limit() function, initialize_redis_client()
- `apps/api/app/core/config.py` - Add REDIS_URL, REDIS_MAX_CONNECTIONS, UPLOAD_RATE_LIMIT_PER_HOUR settings
- `apps/api/app/api/v1/endpoints/documents.py` - Add rate limit dependency to upload endpoint
- `apps/api/app/main.py` - Call initialize_redis_client() on startup
- `apps/api/tests/test_documents_api.py` - Add 9 rate limiting test cases

### 5. Database Changes
None (uses Redis for rate limiting state, not PostgreSQL)

### 6. API Changes
**Modified endpoint:**
- `POST /v1/documents` - Now includes rate limiting (100/hour per user)
  - New headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
  - New error: 429 with RATE_LIMIT_EXCEEDED code when limit exceeded

**No breaking changes** (graceful addition of rate limiting)

### 7. Implementation Steps
1. Add REDIS_URL, REDIS_MAX_CONNECTIONS, UPLOAD_RATE_LIMIT_PER_HOUR to config.py
2. Create initialize_redis_client() in dependencies.py with connection pooling
3. Add check_upload_rate_limit() function using increment-first pattern
4. Call initialize_redis_client() in main.py startup event
5. Add rate limit dependency to POST /v1/documents endpoint
6. Write 9 comprehensive tests (edge cases, concurrency, graceful degradation)
7. Verify mock tests use same methods as implementation (incrby not incr)

### 8. Testing Requirements
**Unit Tests (9 test cases):**
- `test_rate_limit_enforced_at_100_uploads()` - Rejects 101st upload
- `test_rate_limit_allows_99_uploads()` - Allows 99/100
- `test_batch_uploads_count_per_file()` - 20 files = 20 uploads, not 1
- `test_rate_limit_per_user_isolation()` - User A limit doesn't affect User B
- `test_rate_limit_headers_present()` - X-RateLimit-* headers on success
- `test_rate_limit_counter_increments()` - Redis INCRBY called with file_count
- `test_redis_unavailable_graceful_degradation()` - Allows upload if Redis down
- `test_retry_after_header_accurate()` - Retry-After seconds matches next hour
- `test_error_response_format()` - 429 response matches API contract

**Edge Case Tests (from Section 2):**
- Concurrent requests at limit boundary
- TTL behavior (EXPIREAT not EXPIRE)
- Batch upload counting
- Connection pool exhaustion handling
- Redis unavailable scenario
- Hour boundary (23:59 → 00:00)
- Mock/implementation consistency

**Coverage Target:** 80% for new code (rate limiting logic)

### 9. Implementation Checklist

**Pre-Implementation:**
- [ ] Reviewed Redis rate limiting pattern documentation (redis.io)
- [ ] Identified all 7 edge cases from research (Section 2)
- [ ] Checked if similar Redis patterns exist in codebase

**During Implementation:**
- [ ] Using increment-first pattern (not check-then-increment)
- [ ] Using EXPIREAT with absolute timestamp (not EXPIRE)
- [ ] Using INCRBY with file_count parameter (not INCR)
- [ ] Configured connection pooling (max_connections=10, keepalive=True)
- [ ] Atomic operations via Redis pipeline (INCRBY + EXPIREAT together)
- [ ] Graceful degradation on Redis errors (fail-open with logging)
- [ ] Audit logging when rate limit exceeded
- [ ] Extract UPLOAD_RATE_LIMIT_PER_HOUR constant (no magic number 100)

**Testing:**
- [ ] Test concurrent requests (race condition coverage)
- [ ] Test each of 7 edge cases identified in research
- [ ] Mock tests use incrby (matches implementation, not incr)
- [ ] Integration test with real Redis (optional but recommended)
- [ ] Verified TTL doesn't reset on each request (use EXPIREAT)
- [ ] All 9 tests passing locally

**Before Committing:**
- [ ] Self-review against this entire checklist
- [ ] All 9 tests passing
- [ ] No magic numbers (UPLOAD_RATE_LIMIT_PER_HOUR constant used)
- [ ] Error response matches API contract (RATE_LIMIT_EXCEEDED code)
- [ ] Logging includes user_id, file_count, hour_bucket metadata
- [ ] Connection pooling configured correctly
- [ ] Reviewed for all 7 edge cases handled

### 10. Breaking Changes & Migration
No breaking changes (rate limiting is additive feature)

### 11. Success Criteria
- 101st upload returns 429 with RATE_LIMIT_EXCEEDED
- X-RateLimit-* headers present on all upload responses
- Concurrent requests handled correctly (no race conditions)
- Redis unavailable: uploads still work (fail-open)
- All 9 tests pass with 80%+ coverage
- Batch uploads count per-file (20 files = 20 uploads)
- All 7 edge cases from Section 2 verified
```

## Step 5: Output the Plan

Provide the complete implementation plan following the structure above. Be specific, surgical, and elegant. NO backwards compatibility.

**CRITICAL REQUIREMENTS:**

1. **Section 2 (Research Findings) is MANDATORY** - This is where you prevent reinventing the wheel:
   - If you skipped research (cosmetic changes, simple CRUD), explicitly state why
   - If you researched, document the proven pattern and ALL edge cases
   - The implementation agent will follow this pattern, not create their own

2. **Section 9 (Implementation Checklist) must be specific** - Customize based on research:
   - Include specific requirements from Section 2 (e.g., "Use INCRBY not INCR")
   - Add issue-specific items (not just generic boilerplate)
   - Implementation agent will self-review against this before committing

3. **Section 1 (Product Context) connects to user value:**
   - Implementation aligns with user journey and product strategy
   - Standards from product guidelines are followed
   - Testing coverage meets requirements
   - Multi-tenancy and security patterns are applied correctly

**Quality Check Before Outputting:**
- [ ] Section 2 includes proven pattern OR explicit statement why research was skipped
- [ ] All edge cases from research are listed with mitigations
- [ ] Section 9 checklist is customized for this specific issue
- [ ] Implementation steps reference the pattern from Section 2
- [ ] Testing requirements cover all edge cases from Section 2

The plan should be ready to hand off to the implementation agent without further clarification needed. The implementation agent should be able to follow the proven pattern from Section 2 and self-review using the checklist in Section 9.
