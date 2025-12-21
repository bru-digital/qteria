---
description: Execute full Stack-Driven framework automatically
---

# Run Cascade - Automated Framework Execution

You are orchestrating the Stack-Driven cascade. Your job is to **automatically execute sessions sequentially** from the current progress point, respecting dependencies and the sacred cascade order.

## Your Role

You will:

1. **Check current progress** - Determine which files exist
2. **Identify next sessions** - Based on cascade decision logic
3. **Execute sessions automatically** - Run slash commands in sequence
4. **Track progress** - Show status between sessions
5. **Stop at natural points** - Pause at logical milestones or user request

## Critical Philosophy

**The cascade order is sacred** - User journey comes first, everything flows from it. Never skip required dependencies. Each session reads outputs from previous sessions to maintain the generative cascade flow.

**This is automated execution** - Unlike `/cascade-status` which just shows status, this command RUNS the sessions for the user automatically.

## Execution Process

### Step 1: Check Current Progress

First, check which files exist in `product-guidelines/`:

```bash
ls -la product-guidelines/
```

Identify which sessions are complete based on these files:

- `00-user-journey.md` → Session 1 complete
- `01-product-strategy.md` + `11-product-strategy-essentials.md` → Session 2 complete
- `02-tech-stack.md` → Session 3 complete
- `03-mission.md` + `04-metrics.md` + `04-monetization.md` + `04-architecture.md` → Session 4 complete
- `05-brand-strategy.md` → Session 5 complete
- `06-design-system.md` → Session 6 complete
- `07-database-schema.md` → Session 7 complete
- `08-api-contracts.md` → Session 8 complete
- `09-test-strategy.md` → Session 9 complete
- `10-backlog/` directory → Session 10 complete
- `12-project-scaffold.md` → Session 12 complete
- `13-deployment-plan.md` → Session 13 complete
- `14-observability-strategy.md` → Session 14 complete

### Step 2: Determine Next Sessions to Run

Use this decision logic to determine what to execute:

**If no files exist:**

- Start with Session 1: `/refine-journey`
- Then ask user if they want to continue to Session 2

**If only 00-user-journey.md exists:**

- Run Session 2: `/create-product-strategy`
- Then ask user if they want to continue

**If 00-01-11 exist:**

- Run Session 3: `/choose-tech-stack`
- Then ask user if they want to continue

**If 00-02 exist:**

- Run Session 4: `/generate-strategy`
- Then ask user if they want to continue

**If 00-04 architecture exists (Session 4 complete):**

- Run Session 5: `/create-brand-strategy`
- Then ask user if they want to continue

**If 00-05 brand exists (Session 5 complete):**

- Run Session 6: `/create-design`
- Then ask user if they want to continue

**If 00-06 design exists (Session 6 complete):**

- User has reached first major milestone
- Ask: "Continue with Session 7 (/design-database-schema) or explore optional extensions?"
- Options:
  - Continue to Session 7 (database schema)
  - Run optional: `/design-user-experience`, `/setup-analytics`, `/design-growth-strategy`, `/create-financial-model`
  - Stop here

**If 00-07 exist:**

- Run Session 8: `/generate-api-contracts`
- Then ask user if they want to continue

**If 00-08 exist:**

- Run Session 9: `/create-test-strategy`
- Then ask user if they want to continue

**If 00-09 exist:**

- Run Session 10: `/generate-backlog`
- Then ask user if they want to continue

**If 00-10 backlog exists:**

- Ask user: "Run Session 11 to push to GitHub? (/create-gh-issues)"
- This requires GitHub access, so confirm first

**If 00-11 GitHub issues complete:**

- Run Session 12: `/scaffold-project`
- Then ask user if they want to continue

**If 00-12 scaffold exists:**

- Run Session 13: `/plan-deployment`
- Then ask user if they want to continue

**If 00-13 deployment exists:**

- Run Session 14: `/design-observability`
- After completion, celebrate - core cascade complete!

**If all 14 core sessions complete:**

- Congratulate user
- Suggest optional post-cascade extensions
- Suggest they start building

### Step 3: Execute Sessions with Progress Tracking

For each session you're about to run:

1. **Announce the session:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Executing Session X: [Session Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 Reading cascade inputs:
- [List files this session reads]

📤 Will create:
- [List files this session creates]

⏱️ Estimated time: [X] minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

2. **Execute the session using SlashCommand tool:**

   - Use the SlashCommand tool to run the appropriate command
   - Examples: `/refine-journey`, `/create-product-strategy`, etc.

3. **After session completes, show progress:**

```
✅ Session X Complete!

Created:
- [List new files]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Overall Progress: X of 14 core sessions complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

4. **Ask about continuation:**

```
Continue to next session? (yes/no/status)
- yes: Continue to Session [X+1]
- no: Stop here (you can resume later with /run-cascade)
- status: Show full cascade status
```

### Step 4: Handle Natural Stopping Points

**Major Milestones** (pause and ask user):

1. **After Session 1** - Journey defined, ask if ready to continue
2. **After Session 4** - Tactical foundation complete, continue to brand
3. **After Session 6** - Brand & design complete, offer optional extensions or continue
4. **After Session 10** - Backlog complete, offer optional marketing extensions or continue
5. **After Session 14** - Core cascade complete, celebrate!

**Between other sessions** - Quick confirmation to continue

### Step 5: Handle Edge Cases

**If user says "stop" or "pause":**

```
⏸️ Cascade paused after Session X

You can resume anytime by running /run-cascade again.
It will pick up right where you left off.

Current status:
✅ Sessions 1-X complete
❌ Sessions [X+1]-14 remaining

To see full status: /cascade-status
To continue: /run-cascade
```

**If session encounters an error:**

```
⚠️ Session X encountered an issue

Error: [Describe what happened]

Options:
1. Fix the issue and re-run /run-cascade (it will retry Session X)
2. Run the session manually: /[session-command]
3. Stop here: Check /cascade-status for current state
```

**If user has skipped sessions (missing files):**

```
⚠️ Warning: Cascade order broken

Expected files from previous sessions are missing:
- [List missing files]

The cascade works best sequentially because each session reads previous outputs.

Options:
1. Run missing sessions first (recommended)
2. Continue anyway (later sessions won't have full context)
3. Start over from Session 1

What would you like to do?
```

## Important Guidelines

1. **Actually execute commands** - Don't just tell the user what to run, USE the SlashCommand tool to run commands automatically
2. **Respect dependencies** - Never skip required prerequisites
3. **Show progress clearly** - User should always know where they are
4. **Pause at milestones** - Give user chance to breathe and review
5. **Handle interruptions gracefully** - User can stop anytime and resume later
6. **Be encouraging** - This is a journey, celebrate each milestone
7. **Track time** - Let user know estimated time for each session

## Execution Modes

### Default Mode (Sequential from Current Point)

When user runs `/run-cascade` with no arguments:

- Check current progress
- Start from next incomplete session
- Execute sessions one by one with confirmations
- Stop at major milestones

### Batch Mode (User Specifies Range)

If user says "run sessions X to Y" or "complete the cascade":

- Confirm the range
- Execute sessions in sequence
- Still pause at major milestones
- Show consolidated progress

### Resume Mode (Auto-detect)

When `/run-cascade` is run after a pause:

- Detect where user left off
- Offer to resume
- Continue from that point

## Communication Style

**Be concise but clear:**

- Show what's happening now
- Show what's next
- Show overall progress
- Ask clear yes/no questions

**Progress indicators:**

```
Core Cascade Progress: ████████░░░░░░ 57% (8/14 sessions)
```

**Visual separation:**
Use `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━` to separate sections

## Example Execution Flow

Here's what a typical run looks like:

```
Checking cascade progress...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Current Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Session 1: User Journey (00-user-journey.md)
✅ Session 2: Product Strategy (01-product-strategy.md, 11-essentials)
✅ Session 3: Tech Stack (02-tech-stack.md)
❌ Session 4: Tactical Foundation (not started)
❌ Sessions 7-14: Pending

Progress: ███░░░░░░░░░░░ 21% (3/14 sessions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next up: Session 4 - Generate Strategy
This will create mission, metrics, monetization, and architecture.

Ready to continue? (yes/no)
```

User: yes

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Executing Session 4: Generate Strategy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 Reading:
- product-guidelines/00-user-journey.md
- product-guidelines/01-product-strategy.md
- product-guidelines/11-product-strategy-essentials.md
- product-guidelines/02-tech-stack.md

📤 Will create:
- product-guidelines/03-mission.md
- product-guidelines/04-metrics.md
- product-guidelines/04-monetization.md
- product-guidelines/04-architecture.md

⏱️ Estimated time: 15-20 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Execute /generate-strategy command]

[... Session runs interactively ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Session 4 Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Created:
- product-guidelines/03-mission.md
- product-guidelines/04-metrics.md
- product-guidelines/04-monetization.md
- product-guidelines/04-architecture.md

📊 Progress: ████░░░░░░░░░░ 29% (4/14 sessions)

🎉 Major Milestone: Tactical Foundation Complete!

You now have:
✅ User journey validated
✅ Market strategy defined
✅ Tech stack chosen
✅ Mission, metrics, monetization, and architecture established

Next: Session 5 - Create Brand Strategy
Continue? (yes/no)
```

## Reference

**Core cascade order:**

1. `/refine-journey` → 00-user-journey.md
2. `/create-product-strategy` → 01, 11
3. `/choose-tech-stack` → 02
4. `/generate-strategy` → 03-mission, 04-metrics, 04-monetization, 04-architecture
5. `/create-brand-strategy` → 05-brand-strategy
6. `/create-design` → 06-design-system
7. `/design-database-schema` → 07-database-schema
8. `/generate-api-contracts` → 08-api-contracts
9. `/create-test-strategy` → 09-test-strategy
10. `/generate-backlog` → 10-backlog/
11. `/create-gh-issues` → GitHub
12. `/scaffold-project` → 12-project-scaffold
13. `/plan-deployment` → 13-deployment-plan
14. `/design-observability` → 14-observability-strategy

**Optional extensions** (offer after Session 6 or 10):

- `/design-user-experience`, `/setup-analytics`, `/design-growth-strategy`, `/create-financial-model`
- `/discover-naming`, `/define-messaging`, `/design-brand-identity`, `/create-content-guidelines`

## Implementation Notes

**Key Differences from /cascade-status:**

- `/cascade-status` = SHOWS progress, recommends next step
- `/run-cascade` = EXECUTES sessions automatically in sequence

**Use SlashCommand tool:**
When executing a session, use: `SlashCommand` tool with the command name

**Track state:**
Keep checking filesystem between sessions to track progress

**User control:**
Always give user control - they can stop anytime

Now, check the current progress and begin automatic cascade execution!
