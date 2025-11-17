---
description: DEV-TIME - Guide code review with comprehensive framework
---

# Review Code (Development Tool)

You are helping the user review code using a comprehensive code review framework. This is a development-time tool, not part of the cascade.

## When to Use This

**Use during development** when:
- You're reviewing a pull request
- You want to apply consistent review standards
- You need a checklist for thorough code review
- You're mentoring junior developers on code quality

**This is NOT part of the cascade** - it's a tool you use during development.

## Your Task

Guide the user through code review using the framework in `/prompts/technical/code-review.md`.

### Steps to Execute

1. **Read the code review prompt**:
   ```bash
   Read /prompts/technical/code-review.md
   ```

2. **Ask what to review**:
   - GitHub PR URL (if `gh` CLI available)
   - File paths to review
   - Specific concerns (performance? security? style?)

3. **Read the code** to be reviewed:
   ```bash
   Read [files to review]
   ```

4. **Apply the code review framework**:
   - **Correctness**: Does it work? Are there bugs?
   - **Architecture**: Does it fit the system design?
   - **Readability**: Can others understand it?
   - **Performance**: Are there inefficiencies?
   - **Security**: Any vulnerabilities? (SQL injection, XSS, etc.)
   - **Testing**: Are there tests? Do they cover edge cases?
   - **Error handling**: What happens when things fail?
   - **Documentation**: Are complex parts explained?
   - **Style**: Does it follow project conventions?

5. **Provide structured feedback**:
   - **Critical** (must fix before merge)
   - **Important** (should fix, but not blocking)
   - **Nit** (nice to have, style preference)
   - **Praise** (what's done well)

6. **Output the review**:
   - Summarize findings
   - Provide specific line-by-line feedback
   - Suggest improvements
   - Highlight security concerns
   - Recommend approval or changes

## No Output File

This command does NOT write to `/product-guidelines`. It provides immediate feedback in the conversation.

## Code Review Checklist

Use the comprehensive checklist from `/prompts/technical/code-review.md`:

### 1. Correctness
- [ ] Does the code do what it's supposed to do?
- [ ] Are there any obvious bugs?
- [ ] Are edge cases handled?
- [ ] Are there off-by-one errors?

### 2. Architecture & Design
- [ ] Does this fit the system architecture?
- [ ] Are abstractions appropriate?
- [ ] Is it modular and reusable?
- [ ] Are dependencies reasonable?

### 3. Readability & Maintainability
- [ ] Can someone understand this in 6 months?
- [ ] Are names descriptive?
- [ ] Is the logic clear or convoluted?
- [ ] Are functions appropriately sized?

### 4. Performance
- [ ] Are there N+1 queries?
- [ ] Are there unnecessary loops?
- [ ] Is caching used appropriately?
- [ ] Are large datasets handled efficiently?

### 5. Security
- [ ] SQL injection vulnerabilities?
- [ ] XSS vulnerabilities?
- [ ] Authentication/authorization correct?
- [ ] Sensitive data logged or exposed?
- [ ] Input validation?

### 6. Testing
- [ ] Are there tests?
- [ ] Do tests cover happy path?
- [ ] Do tests cover edge cases?
- [ ] Are tests readable and maintainable?

### 7. Error Handling
- [ ] Are errors caught appropriately?
- [ ] Are error messages helpful?
- [ ] Are failures logged?
- [ ] Are resources cleaned up on error?

### 8. Documentation
- [ ] Are complex parts explained?
- [ ] Are public APIs documented?
- [ ] Are assumptions stated?
- [ ] Are TODOs tracked?

### 9. Style & Conventions
- [ ] Does it follow project style guide?
- [ ] Is formatting consistent?
- [ ] Are there linting violations?

## Key Principles

1. **Be specific** - Don't say "improve this"; suggest exactly how
2. **Be kind** - Critique code, not people
3. **Explain why** - Help reviewee learn, don't just demand changes
4. **Prioritize** - Separate critical from nice-to-have
5. **Praise good work** - Positive feedback motivates
6. **Focus on impact** - Security > performance > style

## Example Prompt Flow

```
You: I'll help you review this code. What should I look at? A PR URL, file paths, or paste the code directly?

User: [Provides code or PR]

You: Thanks! Let me review this systematically...

[Read code]

You: Here's my review using the comprehensive framework:

## Summary
This PR adds [functionality]. Overall [positive aspect], but there are [X] critical issues and [Y] suggestions.

## Critical Issues (Must Fix)

### 1. SQL Injection Vulnerability (Security)
**File**: `src/api/users.ts:42`
**Issue**: User input is directly interpolated into SQL query
```typescript
// Current (DANGEROUS)
const query = `SELECT * FROM users WHERE email = '${email}'`;

// Fix
const query = 'SELECT * FROM users WHERE email = ?';
const result = await db.query(query, [email]);
```

**Why**: This allows attackers to inject malicious SQL. Always use parameterized queries.

### 2. Missing Error Handling (Correctness)
**File**: `src/api/users.ts:67`
**Issue**: Database query has no error handling
```typescript
// Current
const user = await db.query(query);
return user.rows[0];

// Fix
try {
  const user = await db.query(query);
  if (!user.rows[0]) {
    throw new NotFoundError('User not found');
  }
  return user.rows[0];
} catch (error) {
  logger.error('Failed to fetch user', { email, error });
  throw error;
}
```

**Why**: Unhandled errors crash the server. Always handle DB errors.

## Important Suggestions (Should Fix)

### 3. N+1 Query Problem (Performance)
**File**: `src/api/users.ts:89`
**Issue**: Loop makes individual DB calls
```typescript
// Current (N+1)
for (const userId of userIds) {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
  users.push(user);
}

// Fix
const users = await db.query('SELECT * FROM users WHERE id IN (?)', [userIds]);
```

**Why**: 100 user IDs = 100 DB queries. One query with IN is much faster.

## Nits (Nice to Have)

### 4. Naming (Readability)
**File**: `src/api/users.ts:23`
**Issue**: Variable name `d` is unclear
```typescript
// Current
const d = new Date();

// Suggestion
const createdAt = new Date();
```

**Why**: Descriptive names make code self-documenting.

## What's Done Well ✨

- **Tests**: Great test coverage including edge cases
- **Validation**: Input validation is thorough
- **Types**: TypeScript types are well-defined
- **Comments**: Complex logic is well-explained

## Recommendation

**Request Changes** - Fix the 2 critical issues (SQL injection, error handling) before merging. The performance and naming suggestions can be addressed in a follow-up PR if you prefer.

Let me know if you'd like me to explain any of these in more detail!
```

## After This Session

**Next steps**:
1. Address critical issues
2. Discuss important suggestions
3. Decide on nits (fix now or later?)
4. Update PR and re-review if needed

---

**Remember**: Code review is a learning opportunity for both reviewer and reviewee. Be thorough but kind, specific but not pedantic, critical but encouraging.
