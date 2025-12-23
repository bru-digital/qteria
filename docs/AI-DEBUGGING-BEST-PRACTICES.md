# AI-Assisted Debugging Best Practices

> Based on lessons learned from Issue #223-229 and industry research (2024)

## 🎯 Core Principles

### 1. The Golden Rule: Symptoms vs Causes

**Always ask:** "Is this the CAUSE or the EFFECT?"

Most debugging failures happen when we fix effects instead of causes:

- ❌ Error message says "Database connection failed" → Add retry logic
- ✅ Error message says "Database connection failed" → Find out WHY it failed

### 2. Layer Your Investigation

Never trust the first error. Use our **Investigation Layers** approach:

```
Layer 1: Surface Symptom (what you see)
    ↓ (dig deeper)
Layer 2: Direct Cause (what triggered it)
    ↓ (dig deeper)
Layer 3: Root Cause (why it exists)
    ↓ (dig deeper)
Layer 4: Systemic Issue (what allowed this to happen)
```

### 3. Document Everything

AI assistants lose context. You lose context. Your team loses context. Write it down.

## 🤖 Using AI Assistants Effectively

### Choose the Right Tool for the Job

| Task                    | Best Tool      | Why                                             |
| ----------------------- | -------------- | ----------------------------------------------- |
| Complex debugging       | Claude         | Better at reasoning through cause-effect chains |
| Quick implementation    | GitHub Copilot | Faster at code completion and patterns          |
| Architecture questions  | ChatGPT        | Good at high-level explanations                 |
| Large codebase analysis | Claude         | Superior context retention (47min avg)          |
| Error pattern analysis  | Claude         | Better at finding subtle connections            |

### Effective Prompting for Debugging

#### ✅ GOOD Prompt

```
I'm seeing error X when running test Y.
Here's the full error log: [paste]
Here's the test that fails: [paste]
Here's what I've tried: [list]
Recent changes: [commits]
What could be causing this?
```

#### ❌ BAD Prompt

```
Tests are failing, help me fix it.
```

### Context Management

AI assistants have context windows. Use them wisely:

1. **Start with the big picture** - Explain the system architecture
2. **Provide full logs** - Not just the error line
3. **Include recent changes** - Last 3-5 commits
4. **Show related code** - Not just the failing function
5. **Mention what you've tried** - Prevent circular suggestions

## 🔍 Debugging Workflow with AI

### Step 1: Gather Context

```bash
# Collect all relevant information BEFORE asking AI
git log --oneline -10  # Recent commits
git diff HEAD~1       # Recent changes
npm test 2>&1 | tee test.log  # Full test output
```

### Step 2: Initial AI Query

Use the template:

```
Environment: [dev/staging/prod]
Symptom: [what's broken]
Started: [when]
Full error: [paste complete log]
Recent changes: [paste git log]

Question: What's the root cause?
```

### Step 3: Verify AI Suggestions

**Never trust, always verify:**

- Test each suggestion in isolation
- Check if the explanation matches your logs
- Look for side effects

### Step 4: Document False Leads

When AI is wrong, explain WHY:

```
Claude suggested X because it saw Y in the logs.
However, Y is actually caused by Z, not X.
The real issue is...
```

## 🚫 Common Pitfalls

### 1. The Cascade Trap

**Problem:** Fixing symptoms creates more symptoms

```
Original: Config loading fails
"Fix" #1: Add fallback values → Tests pass with wrong config
"Fix" #2: Force reload config → Race conditions
"Fix" #3: Add locks → Deadlocks
Real fix: Fix the config loading
```

### 2. The Context Loss Spiral

**Problem:** Losing track of what you're actually fixing

```
Start: Fix test failure
→ AI suggests: Update dependency
→ New error: Type mismatch
→ AI suggests: Change types
→ New error: Breaking change
→ Lost: What were we fixing again?
```

**Solution:** Use the Investigation Layers template

### 3. The Bandaid Accumulation

**Problem:** Each "quick fix" adds technical debt

```
Quick fix #1: Skip failing test
Quick fix #2: Add retry logic
Quick fix #3: Increase timeout
Quick fix #4: Add global flag
Result: Unmaintainable mess
```

**Solution:** If you need more than one bandaid, stop and fix properly

## 📊 Tracking and Learning

### After Each Debugging Session

1. **Create an AI-DEBUG issue** using our template
2. **Document what worked** - Build your prompt library
3. **Document what failed** - Prevent repetition
4. **Share with team** - Collective learning

### Monthly Review

- Which AI tool was most effective?
- What patterns keep appearing?
- Where did we waste time?
- What can we automate?

## 🎓 Real Example: The Lazy Loading Fiasco

**Symptom:** "DATABASE_URL points to PRODUCTION database!"

**Layer 1 Investigation:**

- Error seems clear - must be database config issue
- AI suggests: Fix environment variables
- Result: Still fails

**Layer 2 Investigation:**

- Found earlier error: `test_settings_lazy_initialization` fails
- AI suggests: The lazy loading is broken
- Result: Getting closer

**Layer 3 Investigation:**

- Root cause: Python global variable namespace issue
- `config_module._settings` vs `_settings` confusion
- Result: Found it!

**Layer 4 Investigation:**

- Systemic issue: No test isolation
- Tests contaminate each other
- Result: Need proper fixtures

**Lessons:**

1. First error ≠ Root cause
2. Error messages can mislead
3. Test contamination causes bizarre failures
4. AI needs full context to help effectively

## 🛠️ Tooling Recommendations

### For Error Tracking

- **Sentry** - Automatic error grouping and AI analysis
- **Datadog** - Full observability with AI insights
- **Langfuse** - Specialized for AI agent debugging

### For Local Debugging

- **VS Code + Copilot** - Inline debugging assistance
- **Claude Desktop** - Full codebase analysis
- **pytest --random-order** - Catch test isolation issues

### For Documentation

- **GitHub Issues** - Use our AI-DEBUG template
- **Confluence/Notion** - Team knowledge base
- **README files** - Document gotchas immediately

## 📚 References

- [Investigation Layers Template](.github/ISSUE_TEMPLATE/ai-debugging-tracker.md)
- [Example: Issue #223-229](https://github.com/bru-digital/qteria/issues/223)
- [Claude vs Copilot for Debugging](https://markaicode.com/claude-code-vs-github-copilot-context-debugging-comparison/)
- [AI Agent Observability Guide](https://www.vellum.ai/blog/understanding-your-agents-behavior-in-production)

---

**Remember:** AI assistants are powerful but not magic. They're only as good as the context you provide and the questions you ask. When debugging with AI, be the detective - let AI be your forensics lab.
