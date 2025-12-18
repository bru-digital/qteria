---
description: Validate cascade outputs for quality and completeness
---

# Validate Outputs (Quality Assurance Tool)

You are helping the user validate their Stack-Driven cascade outputs for quality and completeness. This command checks that outputs meet the framework's quality standards.

## When to Use This

**Use during or after the cascade** when:

- You want to verify outputs meet Stack-Driven quality standards
- You're unsure if your outputs are specific enough (not generic)
- You want to check journey alignment before continuing
- You're preparing to share outputs with team or stakeholders
- You want to identify which sessions may need refinement

**This is a quality assurance tool** - use it to validate outputs at any point.

## Your Task

Systematically validate all cascade outputs against Stack-Driven's quality criteria and provide actionable recommendations.

### Steps to Execute

#### Step 1: Check Which Files Exist

Use Bash to list all outputs:

```bash
ls -la /home/user/stack-driven/product-guidelines/
```

Track which sessions are complete vs. incomplete.

#### Step 2: Read All Existing Outputs

Read all files that exist in `product-guidelines/`:

- Core cascade files (00-14)
- Post-cascade extensions (15-22)
- Backlog directory if exists
- Scaffold directory if exists

**Important**: Read ALL files before providing validation report.

#### Step 3: Validate Against Quality Criteria

For each output file that exists, check against these criteria:

### Quality Validation Framework

#### A. Journey Alignment (Critical)

**Check if outputs:**

- [ ] Reference specific user journey steps
- [ ] Trace decisions back to user value
- [ ] Include quantified value ratio (e.g., "4 hours → 60 seconds = 240x")
- [ ] Mention user persona by name/role
- [ ] Serve the critical path (Steps 1-3 of journey)

**Red flags:**

- Generic statements that could apply to any product
- Technology choices without journey justification
- Features that don't serve specific journey steps
- Missing references to user pain points or aha moment

#### B. Philosophy Adherence (Critical)

**Check if outputs demonstrate:**

- [ ] **User-first thinking**: Decisions trace to user value (not tech preferences)
- [ ] **Generative approach**: Specific to this product (not templated/prescriptive)
- [ ] **Journey-driven**: Tech/strategy chosen based on journey requirements
- [ ] **Traceability**: Every decision explains "why" with reasoning
- [ ] **Boring is beautiful**: Proven tech over exotic tech (unless journey requires it)

**Red flags:**

- "We chose X because it's trendy/new/cool"
- Technology-first thinking ("Let's use GraphQL" vs "Journey needs flexible queries → GraphQL")
- Resume-driven development (Kubernetes when not needed)
- Arbitrary decisions without justification

#### C. Completeness & Structure (Important)

**Check if outputs include:**

- [ ] All required sections from template
- [ ] "What We DIDN'T Choose" sections (minimum 2 alternatives)
- [ ] Decision rationale for major choices
- [ ] Examples or concrete implementations
- [ ] Next steps or how it cascades forward
- [ ] Trade-offs acknowledged

**Red flags:**

- Missing "What We DIDN'T Choose" sections
- Sections filled with placeholder text or "TBD"
- No alternatives considered
- Superficial analysis (1-2 sentences where depth needed)

#### D. Consistency Across Cascade (Important)

**Check cross-file consistency:**

- [ ] Tech choices (Session 3) align with journey requirements (Session 1)
- [ ] Mission statement (Session 4) promises value from aha moment (Session 1)
- [ ] Metrics (Session 4) measure mission fulfillment
- [ ] Design system (Session 6) serves brand strategy (Session 5)
- [ ] Database schema (Session 7) matches architecture principles (Session 4)
- [ ] API contracts (Session 8) align with database schema (Session 7)
- [ ] Backlog stories (Session 10) reference specific journey steps
- [ ] Test strategy (Session 9) covers critical journey paths

**Red flags:**

- Tech stack doesn't match journey requirements
- Mission doesn't align with aha moment
- Metrics don't measure mission
- Backlog features unrelated to journey
- Design system ignores brand strategy

#### E. Specificity vs. Genericity (Critical)

**Good (Specific):**

- "Compliance officers (user) spend 4 hours reviewing documents (pain) → 60 seconds with AI (solution) = 240x faster"
- "PostgreSQL chosen because journey needs complex compliance framework relationships with JSONB flexibility"
- "Blue color palette because brand personality is 'trustworthy professional' for compliance industry"

**Bad (Generic):**

- "Users want to save time" (which users? how much time?)
- "PostgreSQL is a good database" (why? what requirements?)
- "Blue is a nice color" (why blue? what does it communicate?)

**Check outputs for:**

- [ ] Specific user personas (not "users")
- [ ] Quantified improvements (not "better/faster")
- [ ] Named journey steps (not "improved experience")
- [ ] Concrete examples (not abstract concepts)

#### F. Technical Soundness (Important)

**For technical sessions (7-14), check:**

- [ ] Database schema has proper relationships and indexes
- [ ] API contracts include error responses (not just happy path)
- [ ] Test strategy covers multiple levels (unit, integration, E2E)
- [ ] Deployment plan includes rollback procedures
- [ ] Observability includes SLO/SLI definitions (not just "monitoring")
- [ ] Architecture principles are actionable (not buzzwords)

**Red flags:**

- Missing error handling in API contracts
- No indexes in database schema
- Test strategy says "write tests" without specifics
- Deployment plan missing environments or rollback
- Observability is just "use Datadog" without metrics

#### G. Depth vs. Superficiality (Important)

**Sufficient depth includes:**

- [ ] Analysis of multiple options (not just one)
- [ ] Trade-offs explained for major decisions
- [ ] Cost implications considered
- [ ] Performance implications documented
- [ ] Edge cases addressed
- [ ] Migration/transition plans for technical changes

**Red flags:**

- Single-sentence explanations for major decisions
- No trade-offs discussed
- "Just use X" without considering alternatives
- No cost analysis for infrastructure decisions
- Missing edge cases in schemas/APIs

### Step 4: Generate Quality Report

Provide a comprehensive quality report with this structure:

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Stack-Driven Outputs Quality Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary

✅ Outputs validated: [X] files
⚠️ Issues found: [Y] critical, [Z] important
🎯 Overall quality: [Excellent / Good / Needs Improvement / Needs Significant Work]

## Critical Issues (Must Address)

### 1. [Issue Title]

**File**: `product-guidelines/[filename]`
**Problem**: [Specific issue description]
**Impact**: [Why this matters]
**Fix**: [Specific recommendation]

[Repeat for each critical issue]

## Important Suggestions (Should Address)

### 1. [Issue Title]

**File**: `product-guidelines/[filename]`
**Problem**: [Specific issue description]
**Recommendation**: [How to improve]

[Repeat for each important suggestion]

## Quality Checklist Results

### Journey Alignment ✅/⚠️/❌

- [✅/⚠️/❌] References specific user journey
- [✅/⚠️/❌] Decisions trace to user value
- [✅/⚠️/❌] Quantified value ratio included
- [✅/⚠️/❌] Serves critical path (Steps 1-3)

### Philosophy Adherence ✅/⚠️/❌

- [✅/⚠️/❌] User-first thinking (not tech-first)
- [✅/⚠️/❌] Generative (specific, not generic)
- [✅/⚠️/❌] Journey-driven decisions
- [✅/⚠️/❌] Decisions include reasoning
- [✅/⚠️/❌] Boring is beautiful (proven tech)

### Completeness ✅/⚠️/❌

- [✅/⚠️/❌] All template sections filled
- [✅/⚠️/❌] "What We DIDN'T Choose" sections (2+ alternatives)
- [✅/⚠️/❌] Decision rationale provided
- [✅/⚠️/❌] Examples included
- [✅/⚠️/❌] Trade-offs acknowledged

### Consistency ✅/⚠️/❌

- [✅/⚠️/❌] Tech aligns with journey requirements
- [✅/⚠️/❌] Mission promises aha moment value
- [✅/⚠️/❌] Metrics measure mission fulfillment
- [✅/⚠️/❌] Cross-file references correct
- [✅/⚠️/❌] No contradictions between sessions

### Specificity ✅/⚠️/❌

- [✅/⚠️/❌] Specific personas (not "users")
- [✅/⚠️/❌] Quantified improvements
- [✅/⚠️/❌] Concrete examples
- [✅/⚠️/❌] Named journey steps
- [✅/⚠️/❌] Could NOT apply to different product

### Technical Soundness ✅/⚠️/❌

(Only for technical sessions 7-14)

- [✅/⚠️/❌] Database: relationships, indexes, constraints
- [✅/⚠️/❌] APIs: error responses, validation
- [✅/⚠️/❌] Tests: multiple levels, edge cases
- [✅/⚠️/❌] Deployment: environments, rollback
- [✅/⚠️/❌] Observability: SLO/SLI, not just tools

## File-by-File Assessment

### 00-user-journey.md [✅/⚠️/❌]

**Quality**: [Excellent/Good/Needs Improvement]
**Strengths**:

- [What's done well]

**Areas to Improve**:

- [Specific improvements needed]

[Repeat for each file]

## What's Done Well ✨

[Highlight strong aspects across all outputs]

- [Specific praise]
- [What demonstrates quality]
- [Good examples to maintain]

## Recommended Actions

### Priority 1: Critical (Do First)

1. [Specific action for critical issue]
2. [Another critical action]

### Priority 2: Important (Do Soon)

1. [Specific action for important issue]
2. [Another important action]

### Priority 3: Enhancements (Nice to Have)

1. [Optional improvement]
2. [Another enhancement]

## Sessions to Regenerate

Based on issues found, consider re-running these sessions:

**Must regenerate**:

- `/[command]` - [Reason why]

**Should regenerate**:

- `/[command]` - [Reason why]

**Optional refinement**:

- `/[command]` - [Reason why]

## Overall Assessment

[Detailed summary of output quality]

**Strengths**:

- [What's working well]

**Weaknesses**:

- [What needs work]

**Next Steps**:

1. [Most important action]
2. [Second most important]
3. [Third priority]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need help addressing issues? You can:

- Re-run specific sessions: `/[command]`
- Check examples: `examples/compliance-saas/`
- Review philosophy: Read PHILOSOPHY.md
- Check cascade status: `/cascade-status`
```

### Step 5: Provide Specific Examples

When identifying issues, always provide:

1. **What's wrong** - Quote the problematic text
2. **Why it's wrong** - Explain the quality issue
3. **How to fix** - Provide specific replacement or approach

**Example:**

```
### Critical Issue: Generic Journey Description

**File**: `product-guidelines/00-user-journey.md`

**Problem**: Journey description is too generic:
> "Users want to manage their tasks more efficiently"

**Why this is wrong**: This could describe any todo app. Stack-Driven requires specific personas, quantified pain points, and unique value.

**Fix**: Be specific about WHO, WHAT pain, and HOW MUCH improvement:
> "Compliance officers (WHO) spend 4 hours manually reviewing 100-page policy documents against 12 frameworks (PAIN) → Upload PDF, select frameworks, receive comprehensive assessment report in 60 seconds (SOLUTION) = 240x faster (VALUE)"

**To regenerate**: Run `/refine-journey` and provide specific user research, quantified pain points, and concrete improvement metrics.
```

## Validation Principles

1. **Be thorough** - Read all outputs completely
2. **Be specific** - Point to exact lines/sections with issues
3. **Be constructive** - Always suggest how to fix
4. **Be principled** - Reference framework philosophy (user-first, journey-driven, etc.)
5. **Be realistic** - Separate critical from nice-to-have
6. **Be encouraging** - Highlight what's done well
7. **Be actionable** - Provide clear next steps

## What Makes "Excellent" vs "Needs Work"

### Excellent Output Characteristics

- **Journey alignment**: Every paragraph references specific journey steps
- **Quantified value**: Specific metrics (e.g., "4h → 60s = 240x")
- **Named personas**: "Compliance officers" not "users"
- **Reasoned choices**: "We chose X because journey requires Y (evidence from journey)"
- **Alternatives considered**: "What We DIDN'T Choose" has 2-3 alternatives with trade-offs
- **Specific examples**: Concrete implementation details, not abstract concepts
- **Consistency**: References match across files
- **Technical depth**: Schemas have indexes, APIs have error handling, etc.

### Needs Work Output Characteristics

- **Generic**: Could apply to any product
- **Vague**: "Users want better experience" without specifics
- **Unjustified**: "We chose X" without explaining why
- **No alternatives**: Only one option considered
- **Abstract**: "Good architecture" without specifics
- **Inconsistent**: Tech stack doesn't match journey needs
- **Superficial**: Single sentences where depth needed
- **Incomplete**: Missing required sections

## Edge Cases

### If No Outputs Exist Yet

**Message**:

```
No cascade outputs found in product-guidelines/ directory.

You haven't started the cascade yet. Run `/cascade-status` to see how to begin, or `/refine-journey` to start Session 1.

Can't validate what doesn't exist yet! 😊
```

### If Only Some Sessions Complete

**Message**:

```
Partial cascade detected. Validating [X] completed sessions...

Note: Sessions [Y, Z] are not complete, so I can't validate cross-file consistency for those dependencies yet.

Run `/cascade-status` to see which sessions remain.
```

### If Outputs Are Excellent

**Message**:

```
🎉 Excellent Quality!

Your cascade outputs demonstrate strong adherence to Stack-Driven principles:
- Journey-driven decisions ✅
- Specific, not generic ✅
- Well-reasoned choices ✅
- Alternatives considered ✅
- Technical depth ✅

[Still provide detailed checklist and specific praise]

Your outputs are ready to share with team/stakeholders. Consider continuing the cascade or (if complete) start building!
```

## Important Notes

1. **Read before validating** - Never guess what's in files; always read them
2. **Compare to examples** - Reference `examples/compliance-saas/` for quality benchmarks
3. **Check philosophy** - Reference `PHILOSOPHY.md` for framework principles
4. **Be specific** - Quote problematic text, don't just say "improve this"
5. **Prioritize** - Separate critical (journey alignment) from nice-to-have (formatting)
6. **Provide paths forward** - Tell user exactly which commands to re-run

## No Output File

This command does NOT write to `/product-guidelines`. It provides an immediate quality report in the conversation.

---

**Remember**: Validation is about helping users create excellent outputs that truly serve their users. Be thorough but encouraging, critical but constructive, specific but not pedantic.
