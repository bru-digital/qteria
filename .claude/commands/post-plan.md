# Post Implementation Plan to GitHub Issue

Post an implementation plan as a comment on a GitHub issue.

## Usage

```
/post-plan {issue-number} {plan-content}
```

## Execution

Simply post the provided plan content as a comment on the specified issue:

```bash
gh issue comment {issue-number} --repo bru-digital/qteria --body "{plan-content}"
```

## Output

Confirm the comment was posted and provide the issue URL:

```markdown
✅ Implementation plan posted to issue #{issue-number}

View: https://github.com/bru-digital/qteria/issues/{issue-number}
```

That's it. Simple utility command.
