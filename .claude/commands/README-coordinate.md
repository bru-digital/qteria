# Coordinate - Quick Reference

## Purpose
Analyze issue backlog to determine optimal parallel execution strategy for AI agents, enabling 3x faster development with zero quality loss.

## Usage

```bash
/coordinate
```

## What It Does

1. **Analyzes Issue Backlog**
   - Fetches all open issues from GitHub
   - Prioritizes by labels (P0 → P1 → P2 → P3)
   - Considers age (oldest first within priority)

2. **Performs Dependency Analysis**
   - Code dependencies (file conflicts)
   - Logical dependencies (blocking relationships)
   - Creates dependency graph (waves)

3. **Creates Git Worktrees**
   - One worktree per parallel task
   - Proper naming convention: `qteria-{issue-number}`
   - Branch: `{issue-number}-{slug}`

4. **Generates Agent Instructions**
   - Quick start commands
   - Implementation checklists
   - Testing requirements
   - Conflict warnings
   - Quality gates

5. **Provides Timeline Estimation**
   - Wave breakdown (parallel vs sequential)
   - Total elapsed time
   - Speedup factor vs sequential

6. **Updates Roadmap Issue**
   - Posts execution plan to GitHub
   - Links to all created worktrees
   - Provides success criteria

## Output Structure

```
📊 Executive Summary
├─ Issues analyzed
├─ Parallel execution plan (waves)
└─ Estimated speedup

🔧 Worktrees Created
├─ qteria-173 (Agent 1)
├─ qteria-172 (Agent 2)
├─ qteria-174 (Agent 3)
└─ qteria-166 (Agent 4)

🚀 Wave 1: Parallel Execution
├─ Agent 1 instructions
├─ Agent 2 instructions
├─ Agent 3 instructions
└─ Agent 4 instructions

⏱️ Timeline
├─ T+0:00 - Start
├─ T+0:30 - Agent 3 done
├─ T+1:00 - Agent 1 done
└─ T+3:00 - Wave 1 complete

✅ Quality Gates
├─ Pre-PR checklist
├─ Merge order
└─ Success criteria
```

## Example Workflow

```bash
# 1. Run tech lead consultation
/coordinate

# 2. Review the plan (output shows 4 agents can work in parallel)

# 3. Spin up 4 AI agents (Cursor, Claude Code, etc.)
#    - Agent 1: cd qteria-173
#    - Agent 2: cd qteria-172
#    - Agent 3: cd qteria-174
#    - Agent 4: cd qteria-166

# 4. Each agent follows plan → implement → test → PR

# 5. Review PRs in specified merge order

# 6. Merge Wave 1, start Wave 2
```

## Key Benefits

- ⚡ **3x faster development** - Parallel execution vs serial
- 🎯 **Zero quality loss** - Quality gates enforced per agent
- 🔍 **Dependency awareness** - No merge conflicts
- 📋 **Clear instructions** - Each agent knows exactly what to do
- 🚦 **Critical path identified** - Prioritize blockers
- 🔗 **CLAUDE.md compliant** - Guidelines enforced

## Quality Assurance

Every agent MUST:
- ✅ Run full test suite before PR
- ✅ Follow CLAUDE.md guidelines
- ✅ Pass linting/type checking
- ✅ Include multi-tenancy tests (if applicable)
- ✅ Use conventional commit format

## Merge Strategy

Issues merged in order:
1. Smallest changes first (reduce conflict surface)
2. Critical path next (unblock dependencies)
3. Independent changes last (can rebase easily)

## When to Use

- Starting a new sprint with multiple backlog items
- Unblocking deployment with multiple P0 issues
- Accelerating development before a deadline
- Have multiple AI agents available for parallel work

## When NOT to Use

- Single issue to work on (overkill)
- Complex issues requiring deep collaboration
- Team unfamiliar with git worktrees
- Issues with tight coupling (must be sequential)

## Pro Tips

💡 **Assign priority roles to agents**:
- Fastest agent → shortest task (they finish first, help with reviews)
- Most experienced agent → critical path (blocks everything else)
- Newest agent → isolated task (low risk if delayed)

💡 **Monitor progress**:
- Check in every hour (agents report status)
- Adjust timeline if critical path delayed
- Reassign agents after Wave 1 completes

💡 **Coordinate conflicts early**:
- If 2 agents touch same file, coordinate section splits
- Specify merge order upfront
- First agent pushes, second agent rebases

## Troubleshooting

**Q: Agents report merge conflicts?**
A: Check merge order - critical path should merge first, others rebase

**Q: Tests fail after merging Wave 1?**
A: Wave 2 likely had dependency on Wave 1 - verify dependency graph was correct

**Q: Timeline longer than estimated?**
A: Critical path was underestimated - adjust future estimates based on actual time

**Q: Quality issues in PRs?**
A: Reinforce quality gates - each agent must run full test suite before PR

## Related Commands

- `/plan-issue {number}` - Plan individual issue (used by agents)
- `/implement-issue {number}` - Implement issue (used by agents)
- `/review-code` - Review PR (used after agent creates PR)

---

**Remember**: The goal is **fast AND safe** parallel development. Never sacrifice quality for speed.
