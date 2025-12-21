# Coordinate: Parallel Execution Strategy

**IMPORTANT: DO NOT CODE. ONLY ANALYZE AND PROVIDE RECOMMENDATIONS.**

You are the Tech Lead analyzing the issue backlog to determine optimal parallel execution strategy for AI agents. Your goal: **3x faster development with ZERO quality loss**.

## Context

The user has multiple AI coding agents (Claude Code, Cursor, etc.) that can work in parallel on separate git worktrees. Your job is to:

1. Analyze the issue backlog
2. Identify which issues can run in parallel (dependency analysis)
3. Recommend git worktree strategy for parallel development
4. Provide clear, actionable instructions for each agent
5. Ensure no quality loss through proper coordination

**Remember: You are in analysis mode. Do not write code, run formatters, or make commits.**

---

## Step 1: Fetch Issue Backlog

Fetch all open issues, prioritizing by labels and age:

```bash
gh issue list --repo bru-digital/qteria --limit 100 --state open --json number,title,labels,createdAt,comments
```

**Analysis Priority**:

1. **P0 (Critical)** - Deployment blockers, safety issues
2. **P1 (High)** - Core functionality, compliance
3. **P2 (Medium)** - Quality improvements, tech debt
4. **P3 (Low)** - Future enhancements

**Age Priority**:

- Oldest issues first (within same priority level)
- Exception: Blockers always take precedence regardless of age

---

## Step 2: Dependency Analysis

For each candidate issue, analyze:

### **A. Code Dependencies**

```bash
# Read the issue details
gh issue view {issue-number} --repo bru-digital/qteria

# Identify affected files (look at issue description or PR patterns)
# Check: Do multiple issues modify the SAME files?
```

**File Conflict Matrix**:

Create a mental map of which issues touch which files:

Example analysis:

- Issue #172: `models.py` (all models) - Low conflict risk (only this issue touches models)
- Issue #173: `conftest.py` (lines 1-50) - Medium conflict risk (overlaps with #166)
- Issue #166: `conftest.py` (lines 100+) - Medium conflict risk (overlaps with #173)
- Issue #174: `dependencies.py` - Low conflict risk (isolated)

**Conflict Resolution**:

- **No overlap**: Can run in parallel ✅
- **Different sections of same file**: Can run in parallel with coordination ⚠️
- **Same lines of same file**: MUST run sequentially ❌

### **B. Logical Dependencies**

Identify blocking relationships:

```
Issue A blocks Issue B if:
- B's tests require A's functionality to work
- B's implementation builds on A's changes
- B's acceptance criteria includes "after A is merged"
```

**Example Dependency Graph**:

```
#172 (NULL constraints) ──┬─→ #168 (Document upload tests)
                          ├─→ #169 (Error response format)
                          └─→ #162 (Edge cases)

#166 (Test fixtures) ─────→ #162 (RBAC edge cases)

#173 (Safety) ────────────→ (nothing - preventive measure)

#174 (Redis logging) ─────→ (nothing - quality improvement)
```

**Parallelization Rules**:

- Issues with NO dependencies can ALL run in parallel
- Issues with dependencies form "waves" (Wave 1 → Wave 2 → Wave 3)
- Within a wave, issues run in parallel
- Between waves, wait for completion

---

## Step 3: Create Execution Plan

### **Template Format**:

```markdown
## Wave 1: Parallel Execution (N agents)

### Agent 1: {Worktree Path} - #{Issue Number} {Title}

- **Duration**: X hours
- **Priority**: P{0-3}
- **Impact**: {What this fixes}
- **Files**: {Primary files modified}
- **Dependencies**: None
- **Conflicts**: {Any potential conflicts}
- **Blocks**: {What issues wait for this}

[Detailed implementation instructions]

### Agent 2: ...

[Continue for all parallel issues]

## Wave 2: Sequential Execution (After Wave 1)

[Issues that depend on Wave 1 completion]
```

---

## Step 4: Create Git Worktrees

For each issue in Wave 1 that can run in parallel:

```bash
# Create worktree for each issue
git worktree add -b {issue-number}-{slug} ../qteria-{issue-number} main

# Example:
git worktree add -b 172-fix-sqlalchemy-null-constraints ../qteria-172 main
```

**Naming Convention**:

- Branch: `{issue-number}-{kebab-case-description}`
- Directory: `../qteria-{issue-number}`
- Keep it short and recognizable

**Verify**:

```bash
git worktree list
```

---

## Step 5: Generate Agent Instructions

For each agent, provide:

### **A. Quick Start**

```bash
cd /path/to/worktree-{issue-number}

# One-line description of task
# See full details: https://github.com/bru-digital/qteria/issues/{number}
```

### **B. Implementation Checklist**

```markdown
1. **Understand**: Read issue #{number}
2. **Plan**: Review affected files and dependencies
3. **Implement**: Make changes following CLAUDE.md guidelines
4. **Test**: Run relevant test suite
5. **Verify**: Ensure no regressions
6. **Commit**: Use conventional commit format
7. **Push**: Create PR for review
```

### **C. Key Files to Modify**

```markdown
Primary:

- `path/to/file1.py` - {What to change}
- `path/to/file2.py` - {What to change}

Tests:

- `tests/test_*.py` - {What to verify}
```

### **D. Testing Strategy**

```bash
# Unit tests
pytest tests/test_specific_module.py -v

# Integration tests (if applicable)
pytest tests/test_integration.py -v

# Acceptance criteria
# ✅ {Criterion 1}
# ✅ {Criterion 2}
```

### **E. Conflict Warnings**

```markdown
⚠️ **Potential Conflicts**:

- Agent X also modifies `{file}` (lines Y-Z)
- Coordinate: Agent A works on top section, Agent B on bottom
- Merge order: #{issue1} → #{issue2} → #{issue3}
```

---

## Step 6: Quality Assurance Gates

### **Pre-PR Checklist (Each Agent)**

Every agent MUST verify before creating PR:

```bash
# 1. Code quality
npm run lint          # Frontend
ruff check .          # Backend
mypy app              # Backend type checking

# 2. Tests pass
pytest -v             # Backend
npm run test          # Frontend

# 3. No regressions
pytest tests/         # Full suite (optional but recommended)

# 4. CLAUDE.md compliance
# - Multi-tenancy tests (if applicable)
# - Error response format (SCREAMING_SNAKE_CASE)
# - Audit logging (if CRUD operations)
```

### **Merge Order Strategy**

To minimize conflicts:

1. **Smallest changes first** (reduces merge conflict surface area)
2. **Critical path next** (unblocks dependent issues)
3. **Independent changes last** (no rush, can rebase easily)

**Example**:

```
Merge Order:
1. #173 (1h task, top of conftest.py)
2. #172 (3h task, critical path, models.py)
3. #174 (30m task, dependencies.py)
4. #166 (3h task, bottom of conftest.py)
```

---

## Step 7: Progress Tracking

### **Timeline Estimation**

```markdown
## Estimated Timeline

T+0:00 - Wave 1 starts ({N} agents in parallel)
T+0:30 - Fastest agent done (shortest task)
T+1:00 - Next agent done
T+3:00 - Wave 1 complete (longest task) - Start Wave 2 ({M} agents)
T+4:00 - Wave 2 complete - Start Wave 3 (if applicable)
T+X:XX - ALL COMPLETE 🎉

**Total Elapsed**: ~X hours (vs Y hours sequential)
**Speedup**: Zx faster
```

### **Success Metrics**

```markdown
## Success Criteria

**After Wave 1**:

- ✅ {N} PRs created
- ✅ All Wave 1 tests passing
- ✅ 0 merge conflicts (proper coordination)
- ✅ {X}% test pass rate (up from {Y}%)

**After All Waves**:

- ✅ {Total} PRs merged
- ✅ 100% test pass rate (or target %)
- ✅ CI pipeline green
- ✅ Deployment unblocked (if P0 issues)
```

---

## Step 8: Create Roadmap Issue Update

Post a summary comment to the roadmap issue (if exists) or create a new one:

```bash
gh issue comment {roadmap-issue-number} --repo bru-digital/qteria --body "$(cat <<'EOF'
## 🚀 Parallel Execution Plan - Wave {N}

### Worktrees Created
[List of worktrees with paths]

### Wave 1: {N} Agents in Parallel
[Agent assignments with quick start commands]

### Timeline
[Estimated completion timeline]

### Success Criteria
[What "done" looks like]

### Next Steps
[What to do after Wave 1 completes]
EOF
)"
```

---

## Output Format

Provide the user with:

1. **Executive Summary** (3-5 sentences)

   - How many issues analyzed
   - How many can run in parallel (Wave 1)
   - Total estimated time savings
   - Critical path identified

2. **Worktrees Created** (table format)

   ```
   | Worktree | Issue | Priority | Duration | Status |
   |----------|-------|----------|----------|--------|
   | qteria-X | #X    | P0       | Xh       | Ready  |
   ```

3. **Wave Breakdown** (detailed per agent)

   - Quick start commands
   - Implementation instructions
   - Testing requirements
   - Conflict warnings

4. **Quality Gates** (checklist)

   - Pre-PR requirements
   - Merge order
   - Verification steps

5. **Timeline** (visual representation)
   - When each agent starts/finishes
   - Total elapsed time
   - Speedup factor

---

## Special Considerations

### **CLAUDE.md Compliance**

Always verify that parallel work maintains:

- ✅ **Multi-tenancy**: 100% test coverage required
- ✅ **Error responses**: SCREAMING_SNAKE_CASE format
- ✅ **Audit logging**: IP/User-Agent capture for CRUD
- ✅ **Test coverage**: 70% overall, higher for critical paths
- ✅ **Security**: No credentials in commits

### **Anti-Patterns to Avoid**

❌ **Don't parallelize if**:

- Issues modify exact same lines of code
- One issue's tests depend on another's implementation
- Merge conflicts would be complex to resolve
- Team is unfamiliar with git worktrees (training needed first)

❌ **Don't sacrifice quality for speed**:

- Every agent runs full test suite before PR
- Code review is still thorough (not rushed)
- CLAUDE.md guidelines still enforced
- Security checks still required

✅ **Do parallelize if**:

- Issues touch different files OR different sections
- Issues have zero logical dependencies
- Team is coordinated on conflict resolution
- Quality gates are automated (CI/CD)

---

## Example Execution

**User asks**: "Analyze issue backlog for parallel execution"

**Your response**:

1. Fetch issues: `gh issue list ...`
2. Analyze dependencies (show thought process)
3. Create dependency graph (ASCII art or mermaid)
4. Identify waves (Wave 1: 4 issues parallel, Wave 2: 2 issues after Wave 1)
5. Create worktrees: `git worktree add ...` (x4)
6. Generate agent instructions (detailed for each)
7. Provide quality gates checklist
8. Update roadmap issue with plan
9. Give user clear "START NOW" command for each agent

**Total output**: Comprehensive but actionable. User can immediately assign agents and begin parallel work.

---

## Final Checklist

Before finishing your analysis:

- [ ] All open P0/P1 issues analyzed
- [ ] Dependency graph created (visual or text)
- [ ] Worktrees created for all Wave 1 issues
- [ ] Each agent has clear instructions
- [ ] Conflict warnings documented
- [ ] Merge order specified
- [ ] Quality gates defined
- [ ] Timeline estimated
- [ ] Roadmap issue updated
- [ ] User has clear "next steps"

---

## Success Definition

**You've succeeded when**:

1. User can immediately assign N agents to worktrees
2. Each agent knows exactly what to do (no ambiguity)
3. Conflicts are anticipated and mitigated
4. Quality is maintained (not sacrificed for speed)
5. Timeline is realistic and achievable
6. Blockers are identified and prioritized
7. User feels confident in 3x speedup without quality loss

---

🎯 **Goal**: Transform serial development into parallel execution WITHOUT compromising code quality, test coverage, or CLAUDE.md compliance.

---

**Remember**: Speed is useless if it introduces bugs. Quality gates MUST be maintained. The tech lead's job is to **enable fast AND safe parallel development**.
