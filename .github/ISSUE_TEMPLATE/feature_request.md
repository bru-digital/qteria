---
name: Feature Request
about: Suggest a new feature or enhancement for Stack-Driven
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description

<!-- A clear and concise description of the feature you'd like to see -->

## Problem or Use Case

<!-- What problem does this solve? What use case does this enable? -->

**Current limitation:**
<!-- What can't you do today that this would enable? -->

**Example scenario:**
<!-- Describe a specific scenario where this would be useful -->

## Proposed Solution

<!-- How do you envision this working? -->

**Where in the cascade would this fit?**
- [ ] New core session (Sessions 1-14)
- [ ] New post-cascade extension (Sessions 15+)
- [ ] Enhancement to existing session
- [ ] Meta command
- [ ] Documentation improvement
- [ ] Other: ___________

**Which sessions would it read (inputs)?**
<!-- e.g., "Would read 00-user-journey.md and 02-tech-stack.md" -->

**What would it generate (outputs)?**
<!-- e.g., "Would generate XX-new-feature.md with [description]" -->

## Framework Philosophy Alignment

<!-- CRITICAL: How does this align with Stack-Driven philosophy? -->

**Does this serve the user journey?**
<!-- How does this trace back to user value? -->

**Is this generative or prescriptive?**
- [ ] Generative (adapts to different journeys → different outputs)
- [ ] Prescriptive (same output for everyone)

<!-- Generative is preferred. If prescriptive, explain why it's justified. -->

**Different journeys → different outputs?**
<!-- Would a compliance SaaS and a mobile game get different outputs from this feature? -->

## Alternatives Considered

<!-- What other approaches did you consider? -->

### Alternative 1: [Name]
**Description:**
**Pros:**
**Cons:**
**Why not:**

### Alternative 2: [Name]
**Description:**
**Pros:**
**Cons:**
**Why not:**

## Examples

<!-- Provide concrete examples of how this would work -->

**Example 1: Compliance SaaS**
<!-- How would this feature work for the compliance-saas example? -->

**Example 2: Your Product**
<!-- How would this work for your specific use case? -->

## Implementation Sketch

<!-- If you have ideas on implementation, share them -->

**Command structure:**
```markdown
# Session XX: [Command Name]

**Purpose:** [One sentence]
**When to run:** [After which session]
**Time required:** [Estimate]

## Inputs (What This Reads)
- product-guidelines/00-user-journey.md
- product-guidelines/XX-other.md

## Process
1. Step 1
2. Step 2
...

## Outputs
- product-guidelines/XX-new-output.md
```

## Additional Context

<!-- Add any other context, screenshots, mockups, or examples -->

## Similar Features in Other Tools

<!-- Are there similar features in other products that we can learn from? -->

## Willingness to Contribute

- [ ] I'm willing to implement this feature
- [ ] I can provide examples
- [ ] I can help with documentation
- [ ] I can test the implementation
- [ ] I'm just suggesting (can't contribute directly)

---

**Before submitting:**
- [ ] I've read [PHILOSOPHY.md](../../PHILOSOPHY.md)
- [ ] I've checked this doesn't already exist
- [ ] I've searched existing issues/PRs
- [ ] This aligns with user-first philosophy
- [ ] I've thought through cascade integration
