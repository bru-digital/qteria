---
description: Session 11 - Push backlog issues to GitHub
---

# Session 11: Create GitHub Issues

This is **Session 11** of the cascade. You'll push the generated backlog to GitHub for execution.

## Your Role

You're pushing issues from `product-guidelines/10-backlog/issues/*.md` to GitHub using the `gh` CLI.

## Process

### Step 1: Read Backlog Files

```
Read: product-guidelines/10-backlog/BACKLOG.md (summary)
Read: product-guidelines/10-backlog/issues/*.md (all issue files)
```

### Step 2: Dry Run (Show What Will Be Created)

**Before creating anything**, show the user:

```
📋 Ready to create GitHub issues

I found [X] issues in product-guidelines/10-backlog/issues/:

Epics:
- EPIC-01: Onboarding
- EPIC-02: Core Value Delivery
- EPIC-03: Results & Actions
... (list all)

Stories (showing first 10):
- STORY-001: OAuth-based signup (P0, Epic-01)
- STORY-002: Document upload to S3 (P0, Epic-01)
- STORY-003: Framework selection UI (P0, Epic-02)
... (continue)

Total: [X] epics, [Y] stories

This will create [Z] total GitHub issues.

Proceed? (I'll wait for your confirmation before creating anything)
```

### Step 3: Await User Confirmation

**CRITICAL**: Do NOT create issues without explicit user confirmation.

Wait for user to say "yes", "go ahead", "proceed", etc.

### Step 4: Create Issues (After Confirmation)

Use `gh issue create` for each issue:

```bash
gh issue create \
  --title "[EPIC-01] Onboarding" \
  --body "$(cat product-guidelines/10-backlog/issues/epic-01-onboarding.md)" \
  --label "epic"
```

```bash
gh issue create \
  --title "[STORY-001] OAuth-based signup" \
  --body "$(cat product-guidelines/10-backlog/issues/story-001-oauth-signup.md)" \
  --label "story,priority:P0"
```

**Labels to Apply**:

- Epic: `epic`
- Story: `story`
- Priority: `priority:P0`, `priority:P1`, `priority:P2`
- Journey step: `journey:step-1`, `journey:step-2`, etc.

### Step 5: Link Dependencies (If Possible)

After creating issues, if dependencies are clear:

- Note which issue numbers were created
- Add comments linking blocked/blocks relationships
- Or manually suggest user links them

### Step 6: Output Results

Show URLs of created issues:

```
✅ GitHub issues created!

Epics:
- EPIC-01: https://github.com/[org]/[repo]/issues/1
- EPIC-02: https://github.com/[org]/[repo]/issues/2
...

Stories (first 10):
- STORY-001: https://github.com/[org]/[repo]/issues/3
- STORY-002: https://github.com/[org]/[repo]/issues/4
...

All [Z] issues created. View your board:
https://github.com/[org]/[repo]/issues
```

## After Generation

```
✅ Session 8 complete! GitHub issues created.

Your issues are now on GitHub, ready for development!

Next, you can optionally generate a working development environment with:
/scaffold-project

Or start building immediately with your prioritized backlog!

What's next?
1. 🚀 Run /scaffold-project to generate working dev environment (Session 9)
2. 💻 Or start building! Your backlog is prioritized (P0 stories first)
3. 📊 Track metrics: Implement metrics from product-guidelines/04-metrics.md
4. 🔄 Iterate: Run /refine-journey if your understanding evolves
5. 💰 Validate pricing: Test monetization from product-guidelines/04-monetization.md

Check cascade anytime: /cascade-status
```

## Important Guidelines

1. **ALWAYS dry run first**: Never create issues without showing user what will be created
2. **Wait for confirmation**: User must explicitly approve
3. **Show URLs**: Return issue URLs so user can click through
4. **Handle errors gracefully**: If `gh` fails (not authenticated, etc.), give clear instructions

## Fallback

If `gh` CLI not available or fails:

```
❌ GitHub CLI not available

Option 1: Install gh CLI
brew install gh (macOS)
Then run: gh auth login

Option 2: Manual Import
I've created all issues in product-guidelines/10-backlog/issues/
You can manually create GitHub issues from these markdown files.

Option 3: CSV Export
I can convert backlog to CSV for bulk import via GitHub UI.
```

---

**Now, read the backlog and push to GitHub (after user confirmation)!**
