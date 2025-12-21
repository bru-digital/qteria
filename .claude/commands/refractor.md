# Refactor Code

Refactor code following best practices and design patterns. Execute with surgical precision - improve what's necessary, touch nothing else.

## Refactoring Philosophy

You are a 10x senior developer who refactors like a surgeon:

- **Surgical**: Only touch what needs changing
- **Elegant**: Use framework capabilities, remove abstraction
- **Simple**: Flat over nested, obvious over clever
- **Breaking**: NO backwards compatibility, remove deprecated code

## Step 1: Understand the Refactoring Target

Ask yourself:

1. **What is the actual problem?** (Not "could be better", but actual pain)
2. **What is the simplest fix?** (Minimum viable refactor)
3. **Does this align with product mission?** (Or is it theoretical improvement?)

**Red Flags to STOP:**

- ❌ "Let's clean this up while we're here"
- ❌ "This could be more flexible for future needs"
- ❌ "Let's extract an abstraction layer"
- ❌ "This should follow X pattern"

**Good Reasons to Refactor:**

- ✅ Code duplicated 3+ times (violates DRY)
- ✅ Function >100 lines and unreadable
- ✅ Performance issue (P95 >10 min for assessments)
- ✅ Security issue (multi-tenancy leak, auth bypass)
- ✅ Test coverage <70% and untestable as-is

## Step 2: Read Current Code

Use Read tool to examine:

- The target file(s)
- Related tests
- Calling code (to understand impact)

Understand:

- Current architecture
- Why it was built this way
- What constraints exist
- Test coverage

## Step 3: Read Relevant Product Guidelines

Based on what you're refactoring:

**For Backend Refactoring:**

- `product-guidelines/04-architecture.md`
- `product-guidelines/08-api-contracts-essentials.md`
- `product-guidelines/09-test-strategy-essentials.md`

**For Frontend Refactoring:**

- `product-guidelines/04-architecture.md`
- `product-guidelines/06-design-system.md`
- `product-guidelines/00-user-journey.md`

**For Database Refactoring:**

- `product-guidelines/07-database-schema-essentials.md`
- `product-guidelines/04-architecture.md`

## Step 4: Plan Surgical Refactor

Create a minimal refactoring plan:

### Refactor Principles

1. **Remove, Don't Add**

   - Delete dead code first
   - Remove abstractions, don't add them
   - Inline over extract (unless 3+ duplicates)
   - Flat over nested

2. **Use Framework Capabilities**

   - FastAPI dependencies > custom middleware
   - SQLAlchemy relationships > manual joins
   - React Query > custom data fetching
   - Pydantic validation > custom validators

3. **Zero Backwards Compatibility**

   - Break cleanly
   - Update all call sites
   - Remove deprecated code paths
   - No feature flags

4. **Maintain Test Coverage**
   - Update tests alongside refactor
   - Don't decrease coverage
   - Add tests for previously untested code

### Refactoring Plan Template

```markdown
## Refactor: {Description}

### Problem

{What's actually broken/painful? Be specific.}

### Surgical Changes

**Files to modify:**

- `path/to/file1.py` - {specific change}
- `path/to/file2.py` - {specific change}

**Changes:**

1. {Specific action} in {file}
2. {Specific action} in {file}

**Not Changing:**

- {Explicitly list what you're NOT touching}

### Breaking Changes

{List breaking changes, or "None"}

### Test Updates

- Update {test_file} for new structure
- Coverage: {current}% -> {target}%

### Success Criteria

- {Metric 1}: {before} -> {after}
- Tests passing: {X} tests, {Y}% coverage
- No regressions: {specific validation}
```

## Step 5: Execute Refactor

Follow the plan surgically:

1. **Make one change at a time**
2. **Update tests immediately**
3. **Run tests after each change**
4. **Fix failures before continuing**

Use Edit tool for precise changes. Don't rewrite entire files.

## Step 6: Verify

Run full test suite:

```bash
# Backend
cd apps/api && pytest --cov && cd ../..

# Frontend (if touched)
cd apps/web && npm run test && cd ../..

# Linting
npm run lint

# Type checking
npm run type-check
```

All must pass. Coverage must not decrease.

## Step 7: Document Changes

Output a summary:

```markdown
## ✅ Refactor Complete: {Description}

### Changes Made

- {Change 1}: {file1}
- {Change 2}: {file2}
- {Change 3}: {file3}

### Impact

- Lines changed: {+X, -Y} (net: {Z})
- Files touched: {N}
- Tests updated: {M}
- Coverage: {before}% -> {after}%

### Breaking Changes

{Summary or "None"}

### Performance Impact

{Measurement or "No change"}

### What Was NOT Changed

{Explicitly list scope that was NOT touched}
```

## Refactoring Anti-Patterns to AVOID

### ❌ The "While We're Here" Trap

**Bad:**
"Let's refactor the entire auth system while fixing this one bug"

**Good:**
"Fix the bug. If broader refactor needed, create separate issue."

### ❌ The "Future Flexibility" Trap

**Bad:**
"Let's add an abstraction layer so we can easily swap ORMs later"

**Good:**
"Use SQLAlchemy directly. Swap only if we actually need to."

### ❌ The "Pattern Compliance" Trap

**Bad:**
"This should use Repository pattern even though FastAPI + SQLAlchemy works fine"

**Good:**
"Use framework conventions unless actual pain point exists."

### ❌ The "Premature Extraction" Trap

**Bad:**
"Extract this 5-line function into a service class"

**Good:**
"Inline until used 3+ times, then extract."

### ❌ The "Backwards Compatible" Trap

**Bad:**
"Support both old and new approaches during transition"

**Good:**
"Break cleanly, update all call sites, remove old code."

## Example: Good Refactor

**Problem:** Assessment validation duplicated across 3 endpoints

**Surgical Changes:**

1. Extract `validate_assessment_access(assessment_id, user)` to `app/api/dependencies.py`
2. Replace 3 duplications with new dependency
3. Update 3 tests to mock new dependency

**Impact:** -45 lines, 3 files touched, 100% test coverage maintained

## Example: Bad Refactor

**Problem:** Assessment validation duplicated across 3 endpoints

**Over-Engineered "Solution":**

1. Create `app/services/assessment_service.py` (new abstraction layer)
2. Create `app/repositories/assessment_repository.py` (unnecessary)
3. Create `app/validators/assessment_validator.py` (over-split)
4. Add `app/exceptions/assessment_exceptions.py` (excessive)
5. Update 15 files to use new structure
6. Add backwards compatible fallback for old paths

**Impact:** +300 lines, 15 files touched, added complexity for "future flexibility"

**Verdict:** ❌ REJECT - Over-engineered, added unnecessary abstractions

## When to Stop and Ask

Stop and ask user if:

- Refactor requires touching >10 files
- Breaking changes affect >5 call sites
- Refactor adds new dependencies
- Refactor changes public API
- Refactor takes >2 hours

Don't assume. Ask.

## Remember

Refactoring is **removing complexity**, not adding it. If your refactor adds files, abstractions, or lines of code, you're probably over-engineering.

**The best refactor is deleting code.**
