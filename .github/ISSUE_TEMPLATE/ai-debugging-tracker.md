---
name: AI Debugging Tracker
about: Track complex debugging sessions with AI assistants for better resolution
title: '[AI-DEBUG] '
labels: 'debugging, ai-assisted, technical-debt'
assignees: ''
---

<!--
This template helps track debugging sessions with AI assistants (Claude, Copilot, ChatGPT).
It ensures we capture context, avoid repeated mistakes, and learn from each debugging session.
-->

## 🎯 Problem Statement
<!-- Be specific about the SYMPTOM you're seeing -->
**What's broken:**
**Error message (if any):**
**When it started:**
**Impact level:** 🔴 Critical / 🟡 High / 🟢 Medium / ⚪ Low

## 📊 Initial Context
<!-- Help the AI understand the full picture -->
**CI/Test Status:**
- [ ] Tests passing locally
- [ ] CI pipeline status:
- [ ] Specific test failures:

**Recent Changes:**
- Last working commit:
- Recent PRs merged:
- Configuration changes:

**Environment:**
- Development / Staging / Production
- Dependencies changed: Yes/No
- Database migrations: Yes/No

## 🔍 Investigation Layers
<!-- Track your debugging journey to avoid circular reasoning -->

### Layer 1: Surface Symptom
**What you see:**
**Initial assumption:**
**AI agent used:** Claude / Copilot / ChatGPT / Other
**Result:** ✅ Solved / ❌ Deeper issue found

### Layer 2: First Root Cause Attempt
**What you found:**
**New hypothesis:**
**AI agent query:**
<!-- Paste the exact prompt you used with the AI -->
```
[Your prompt here]
```
**Result:** ✅ Solved / ❌ Deeper issue found

### Layer 3: [Continue as needed]
<!-- Add more layers as you dig deeper -->

## 🧪 Reproduction Steps
<!-- Critical for AI to help effectively -->
1.
2.
3.
**Expected:**
**Actual:**

## 📝 Error Logs
<!-- FULL logs, not just the error line -->
<details>
<summary>Full Error Output</summary>

```
[Paste complete error logs here]
```

</details>

<details>
<summary>Related Test Output</summary>

```
[Paste test failures here]
```

</details>

## 🤖 AI Assistant Interactions
<!-- Track what worked and what didn't -->

### Effective Prompts
<!-- What questions/prompts got useful results? -->
-

### Ineffective Prompts
<!-- What led to wrong directions? -->
-

### Context Limitations Hit
<!-- Did you exceed token limits? Lose context? -->
-

## 🎭 False Leads
<!-- Document wrong paths to prevent repetition -->
**What seemed like the cause but wasn't:**
1.
2.

**Why it was misleading:**

## 🔬 Root Cause Analysis
<!-- The ACTUAL cause, not the symptoms -->

**The Real Problem:**
- **Symptom cascade:** A → caused B → caused C → caused error
- **True root cause:**
- **Why it was hard to find:**

## ✅ Solution
<!-- What actually fixed it -->

**Fix Applied:**
```diff
[Code changes]
```

**Why it works:**

**PR/Commit:**

## 📚 Lessons Learned
<!-- Prevent similar issues in future -->

### For Humans
-

### For AI Assistance
<!-- How to better use AI for similar issues -->
-

### Codebase Improvements Needed
- [ ] Add logging here:
- [ ] Add test for:
- [ ] Documentation needed for:
- [ ] Refactor needed:

## 🚦 Verification
<!-- Ensure it's actually fixed -->
- [ ] Original error resolved
- [ ] All tests passing
- [ ] CI pipeline green
- [ ] No new errors introduced
- [ ] Performance impact checked

## 🏷️ Metadata
<!-- For tracking patterns -->
**Debug time:** [hours]
**AI tools used:**
**False paths taken:** [count]
**Commits to fix:** [count]

## 🔗 Related Issues
<!-- Link similar problems -->
-

---

### 📋 Post-Mortem Checklist
<!-- Complete after resolution -->
- [ ] Root cause documented above
- [ ] Solution verified in production/staging
- [ ] Tests added to prevent regression
- [ ] Documentation updated if needed
- [ ] Team notified of resolution
- [ ] Consider adding to troubleshooting guide

---

<!--
TIPS FOR EFFECTIVE AI DEBUGGING:
1. Give FULL context - AI can't see what you don't show
2. Share COMPLETE error logs, not just the line that failed
3. Mention what you've already tried
4. If AI gives wrong answer, explain WHY it's wrong
5. Use different AI tools for different purposes:
   - Claude: Complex debugging, root cause analysis
   - Copilot: Quick fixes, implementation
   - ChatGPT: Architecture questions, explanations
-->