# Implement GitHub Issue

You are tasked with implementing a GitHub issue that has an approved implementation plan. Execute with surgical precision following the plan exactly.

## Prerequisites

The issue MUST have an approved implementation plan (either in issue description or comments). If no plan exists, STOP and run `/plan-issue {issue-number}` first.

**CRITICAL - Context Already in Plan:**
- DO NOT read product-guidelines files during implementation
- DO NOT search for additional context beyond the plan
- The `/plan-issue` command already collected ALL relevant guidelines and context
- Everything you need is in the plan's "Product Context & Guidelines" section
- Trust the plan - it contains the necessary standards, patterns, and references

## Step 0: Sync with Main Branch

**CRITICAL**: Always sync with main before starting to prevent lost changes.

```bash
# Check current branch and status
git status

# Stash any uncommitted changes
git stash

# Switch to main branch
git checkout main

# Pull latest changes from remote
git pull origin main

# If you were on a different branch, switch back
# git checkout {previous-branch}
# git stash pop
```

This ensures you start with the latest code and prevents merge conflicts from outdated branches.

## Step 1: Fetch Issue with Plan

```bash
gh issue view {issue-number} --repo bru-digital/qteria --json title,body,labels,comments
```

Extract the implementation plan from either:
- Issue body (look for "## Implementation Plan" section)
- Latest comment containing the plan
- Linked comment with plan

## Step 2: Execute Implementation

Follow the plan's Implementation Steps EXACTLY. Do NOT deviate unless you discover a critical flaw.

### Execution Principles

1. **Follow the Plan Religiously**
   - Execute steps in exact order
   - Don't skip steps
   - Don't add extra steps
   - If plan is wrong, STOP and ask user to update plan first
   - DO NOT read product-guidelines - all context is already in the plan

2. **Surgical Implementation**
   - Only touch files listed in plan
   - Make minimal changes
   - Don't refactor outside scope
   - Keep changes atomic per step

3. **Test as You Go**
   - Run relevant tests after each major step
   - Fix issues immediately
   - Don't accumulate test debt

4. **Zero Backwards Compatibility**
   - Follow plan's migration strategy
   - Break cleanly as specified
   - Remove deprecated code immediately

### Implementation Workflow

For each step in the plan:

1. **Announce the step**: "Implementing step X: [description]"
2. **Make the change**: Use Edit/Write tools
3. **Verify syntax**: Run linter if applicable
4. **Run tests**: Execute relevant test suite
5. **Mark complete**: Move to next step

If ANY step fails:
- STOP immediately
- Report the failure with full error details
- Ask user: "Plan step X failed. Should I: (1) Debug and continue, (2) Stop and revise plan?"

## Step 3: Run Full Test Suite

After completing all implementation steps:

```bash
# Backend tests
cd apps/api && pytest --cov && cd ../..

# Frontend tests (if applicable)
cd apps/web && npm run test && cd ../..

# Linting
npm run lint

# Type checking
npm run type-check
```

All must pass. Fix any failures before proceeding.

## Step 4: Verify Success Criteria

Check each success criterion from the plan. Provide evidence:
- ✅ Criterion 1: [evidence - test output, screenshot, API response]
- ✅ Criterion 2: [evidence]
- ❌ Criterion 3: [failure reason]

If any criterion fails, implementation is incomplete.

## Step 5: Create Branch and Commit

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create feature branch from main
git checkout -b {issue-number}-{kebab-case-title}

# Stage changes
git add {files}

# Commit with conventional format
git commit -m "feat: {concise description} (closes #{issue-number})

{detailed explanation if needed}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push -u origin {issue-number}-{kebab-case-title}
```

## Step 6: Create Pull Request

```bash
gh pr create --repo bru-digital/qteria --title "feat: {title} (closes #{issue-number})" --body "$(cat <<'EOF'
## Summary
{2-3 sentence summary of changes}

## Implementation
Implements #{issue-number} following approved plan:
- Change 1
- Change 2
- Change 3

## Testing
- ✅ All unit tests passing ({X} tests)
- ✅ Integration tests passing ({Y} tests)
- ✅ Multi-tenancy tests passing (if applicable)
- ✅ RBAC tests passing (if applicable)
- ✅ Coverage target met ({Z}%)

## Breaking Changes
{List breaking changes and migration steps, or "None"}

## Success Criteria
{Copy success criteria from plan with evidence}

## Checklist
- [x] Implementation follows approved plan
- [x] All tests passing
- [x] No backwards compatibility added
- [x] Breaking changes documented
- [x] Migration path clear
- [x] Code linted and type-checked

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Step 7: Report Completion

Output a summary:

```markdown
## ✅ Issue #{issue-number} Implemented

**Branch:** {branch-name}
**PR:** {pr-url}

**Changes:**
- {file1}: {change}
- {file2}: {change}
- {file3}: {change}

**Tests:** {X} tests passing, {Y}% coverage
**Breaking Changes:** {Yes/No - summary}

**Next Steps:**
1. Review PR: {pr-url}
2. Merge when approved
3. {Migration step 1}
4. {Migration step 2}
```

## Error Handling

If implementation cannot be completed:
1. **Commit partial work** to feature branch with WIP marker
2. **Document blockers** clearly
3. **Update issue** with status comment
4. **Ask user** for guidance

Never leave uncommitted changes or untested code.

## Anti-Patterns to AVOID

- ❌ Deviating from approved plan without asking
- ❌ Adding "improvements" not in plan
- ❌ Skipping tests to "go faster"
- ❌ Committing untested code
- ❌ Adding backwards compatibility not in plan
- ❌ Creating PR with failing tests
- ❌ Ignoring success criteria
- ❌ Reading product-guidelines or searching for additional context (it's already in the plan!)

Remember: You're executing an approved plan. Surgical precision, zero creativity. The plan already contains all necessary context from product guidelines.
