# Contributing to Stack-Driven

Thank you for your interest in contributing to Stack-Driven! This document provides guidelines and information for contributors.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Framework Philosophy](#framework-philosophy)
5. [Contributing Guidelines](#contributing-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Documentation Standards](#documentation-standards)
8. [Testing Your Changes](#testing-your-changes)
9. [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race, ethnicity, or nationality
- Age
- Religion or lack thereof

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards other community members

**Unacceptable behaviors:**
- Trolling, insulting/derogatory comments, personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of unacceptable behavior may be reported by opening an issue or contacting the maintainers. All complaints will be reviewed and investigated promptly and fairly.

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
1. Check the [FAQ](FAQ.md) and [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search existing [GitHub Issues](../../issues) to see if it's already reported
3. Try to reproduce the issue with the latest version

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Stack-Driven version
- AI assistant being used
- Relevant command outputs or error messages
- Contents of relevant files (if applicable)

**Template:**
```markdown
**Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Run `/refine-journey`
2. Complete session
3. Run `/choose-tech-stack`
4. Error appears

**Expected Behavior:**
Tech stack should be generated

**Actual Behavior:**
Error: Cannot read product-guidelines/00-user-journey.md

**Environment:**
- Stack-Driven version: 2.0.0
- AI Assistant: Claude Code
- OS: macOS 14.0

**Additional Context:**
[Any other relevant information]
```

---

### Suggesting Enhancements

**Before suggesting an enhancement:**
1. Check if it aligns with [framework philosophy](PHILOSOPHY.md)
2. Search existing issues for similar suggestions
3. Consider if it's a core feature or post-cascade extension

**When suggesting an enhancement, include:**
- Clear, descriptive title
- Detailed description of the proposed feature
- Why this enhancement would be useful
- How it aligns with the user-first philosophy
- Potential implementation approach
- Examples of how it would work

**Key questions:**
- Does this serve the user journey?
- Is it generative (adapts to journey) or prescriptive (one-size-fits-all)?
- Where in the cascade would this fit?
- What previous sessions would it read?
- What outputs would it generate?

---

### Contributing Code

We welcome contributions! Here are areas where you can help:

**1. New Example Implementations**
- Complete cascade runs for different product types
- Shows how different journeys → different stacks
- Currently have: compliance-saas
- Needed: mobile apps, real-time games, e-commerce, B2C, etc.

**2. Command Improvements**
- Enhance existing slash commands
- Add decision trees for complex choices
- Improve AI prompting quality
- Add more examples and edge cases

**3. New Post-Cascade Extensions**
- Create optional deep-dive sessions
- Must read previous sessions (generative approach)
- Must trace back to user journey
- See [IMPLEMENTATION-PROMPT.md](IMPLEMENTATION-PROMPT.md)

**4. Documentation**
- Improve clarity of existing docs
- Add more examples
- Create video tutorials or guides
- Translate documentation (future)

**5. Bug Fixes**
- Fix issues with cascade execution
- Improve error handling
- Fix template formatting
- Correct typos or outdated information

---

### Contributing Documentation

Documentation is critical! We especially need:

**High Priority:**
- More example implementations
- Video walkthroughs of cascade
- Case studies of real products built with Stack-Driven
- Translations (future consideration)

**Always Welcome:**
- Clarification of confusing sections
- Additional examples in command files
- FAQ additions
- Troubleshooting entries

---

## Development Setup

### Prerequisites

1. **Git**
   ```bash
   git --version
   ```

2. **AI Assistant with slash command support**
   - Claude Code (recommended)
   - Or compatible alternative

3. **GitHub CLI** (optional, for `/create-gh-issues`)
   ```bash
   gh --version
   ```

### Fork and Clone

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/stack-driven.git
   cd stack-driven
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/bru-digital/stack-driven.git
   ```

4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Testing Your Changes

Before submitting:

1. **Test the cascade:**
   ```bash
   # Run a complete cascade to verify nothing breaks
   /cascade-status
   /refine-journey
   # ... continue through cascade
   ```

2. **Verify file formats:**
   ```bash
   # Check markdown syntax
   # Ensure files follow template structure
   ```

3. **Test examples:**
   ```bash
   # If you modified commands, update examples
   ls examples/compliance-saas/
   ```

4. **Check links:**
   ```bash
   # Ensure all internal documentation links work
   # Test relative paths in markdown
   ```

---

## Framework Philosophy

**CRITICAL:** Read [PHILOSOPHY.md](PHILOSOPHY.md) before contributing.

### Core Axiom

**User Experience is the Core of Every Product.**

Every contribution must align with this principle:
- Does it serve the user journey?
- Does it trace back to user value?
- Is it generative (adapts) or prescriptive (one-size-fits-all)?

### The Cascade Direction

Water flows downhill. User journey is the source. Everything else flows from it.

**Acceptable:**
- ✅ "This command reads journey and derives X"
- ✅ "Different journeys → different outputs"
- ✅ "This adapts recommendations based on journey requirements"

**Not acceptable:**
- ❌ "This command runs before understanding users"
- ❌ "This prescribes technology X for everyone"
- ❌ "This doesn't reference the user journey"

### Quality Standards

Every command must include:
- Clear inputs (what it reads from previous sessions)
- Clear process (step-by-step instructions)
- Clear outputs (what files it generates)
- Decision trees (for complex choices)
- Examples (preferably from compliance-saas)
- "What We DIDN'T Choose" section (alternatives with reasoning)
- Quality checklist
- AI agent guidelines (for edge cases)

See [IMPLEMENTATION-PROMPT.md](IMPLEMENTATION-PROMPT.md) for detailed standards.

---

## Contributing Guidelines

### Creating New Commands

**Process:**

1. **Read existing commands for style:**
   ```bash
   cat .claude/commands/refine-journey.md
   cat .claude/commands/generate-strategy.md
   ```

2. **Create command file:**
   ```bash
   vim .claude/commands/your-command.md
   ```

   Follow structure:
   - Session header
   - Purpose, when to run, time required
   - Inputs (what it reads)
   - Process (step-by-step)
   - Outputs (what it generates)
   - Examples
   - "What We DIDN'T Choose"
   - Quality checklist
   - Next steps

3. **Create template file:**
   ```bash
   vim templates/your-template.md
   ```

4. **Update cascade-status:**
   ```bash
   vim .claude/commands/cascade-status.md
   # Add your command to the session list
   ```

5. **Update README:**
   ```bash
   vim README.md
   # Add command to cascade flow
   ```

6. **Create example output:**
   ```bash
   # Generate example for compliance-saas
   # Or create new example directory
   vim examples/compliance-saas/your-output.md
   ```

### Modifying Existing Commands

**Process:**

1. **Understand current behavior:**
   - Run the command
   - Read its template
   - Check example outputs

2. **Make changes:**
   - Preserve existing structure
   - Maintain backwards compatibility if possible
   - Update template if needed

3. **Update examples:**
   ```bash
   # Regenerate example outputs if command logic changed
   vim examples/compliance-saas/[relevant-file].md
   ```

4. **Update documentation:**
   - README.md
   - COMMAND-REFERENCE.md
   - Any references to the command

### Adding Examples

**We need more examples!** Currently only have `compliance-saas`.

**Good example candidates:**
- Mobile-first app (shows different tech stack)
- Real-time collaboration (shows WebSockets + different architecture)
- E-commerce marketplace (shows different journey)
- B2C consumer app (shows different metrics, monetization)
- Developer tools (shows different user persona)

**Example structure:**
```
examples/your-example/
├── README.md (overview of the product)
├── foundation/
│   ├── 00-user-journey.md
│   ├── 01-mission.md
│   ├── 02-metrics.md
│   ├── 03-monetization.md
├── stack/
│   ├── 04-tech-stack.md
│   ├── 05-architecture.md
├── design/
│   ├── 06-design-system.md
├── database/
│   ├── 07-database-schema.md
├── api-contracts/
│   ├── 08-api-contracts.md
├── testing/
│   ├── 09-test-strategy.md
└── backlog/
    ├── P0-*.md
    ├── P1-*.md
    └── P2-*.md
```

**Requirements:**
- Complete cascade (Sessions 1-10 minimum)
- High quality outputs (follow templates)
- Different from existing examples
- Include README explaining the product and why tech choices were made

---

## Pull Request Process

### Before Submitting

- [ ] Code/documentation follows style guidelines
- [ ] Tested changes (ran cascade if applicable)
- [ ] Updated relevant documentation
- [ ] Added examples if creating new commands
- [ ] Verified no breaking changes (or documented them)
- [ ] Commits have clear messages

### Commit Messages

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, typos
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat: Add financial model post-cascade extension

- Create /create-financial-model command
- Add financial-model-template.md
- Update cascade-status with new session
- Add example to compliance-saas

Closes #42
```

```
fix: Update tech stack decision tree for mobile apps

- Add React Native vs Flutter decision criteria
- Include performance considerations
- Update examples with mobile use case

Fixes #38
```

```
docs: Expand FAQ with team collaboration questions

- Add "Can multiple people use Stack-Driven together?"
- Add "What roles should be involved?"
- Add "How do we resolve disagreements about outputs?"
```

### Pull Request Template

When you open a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Example addition
- [ ] Breaking change

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing Performed
- [ ] Ran complete cascade
- [ ] Tested specific commands
- [ ] Verified examples
- [ ] Checked documentation links

## Checklist
- [ ] Follows framework philosophy
- [ ] Code/docs follow style guidelines
- [ ] Updated relevant documentation
- [ ] Added examples if needed
- [ ] No breaking changes (or documented)

## Related Issues
Closes #XX
```

### Review Process

1. **Automated checks** (if configured)
   - Markdown linting
   - Link checking
   - Format validation

2. **Maintainer review**
   - Philosophy alignment
   - Code quality
   - Documentation completeness
   - Example quality

3. **Feedback and iteration**
   - Address review comments
   - Update as needed
   - Maintain discussion

4. **Merge**
   - Once approved, maintainers will merge
   - Your contribution will be in the next release!

---

## Documentation Standards

### Markdown Style

**Headings:**
```markdown
# H1 - Top level (page title)
## H2 - Major sections
### H3 - Subsections
#### H4 - Minor subsections (rarely needed)
```

**Lists:**
```markdown
- Unordered list
- Item 2
  - Nested item

1. Ordered list
2. Item 2
   1. Nested item
```

**Code blocks:**
````markdown
```bash
# Code with syntax highlighting
/refine-journey
```
````

**Links:**
```markdown
[Link text](URL)
[Internal link](README.md)
[Heading link](#section-name)
```

**Emphasis:**
```markdown
**Bold** for emphasis
*Italic* for terminology
`Code` for commands/filenames
```

### File Organization

**Root level docs:**
- `README.md` - Framework overview
- `GETTING-STARTED.md` - Quick start
- `PHILOSOPHY.md` - Core principles
- `CONTRIBUTING.md` - This file
- `CHANGELOG.md` - Version history
- `COMMAND-REFERENCE.md` - All commands
- `FAQ.md` - Common questions
- `TROUBLESHOOTING.md` - Common issues
- `GLOSSARY.md` - Terminology
- `QUICK-REFERENCE.md` - Cheat sheet

**Commands:** `.claude/commands/*.md`
**Templates:** `templates/*.md`
**Examples:** `examples/[name]/`

### Writing Style

**Be clear and concise:**
- ✅ "Run `/refine-journey` to define your user journey"
- ❌ "You should probably consider running the journey refinement command if you want to get started"

**Use examples:**
- Every major concept should have an example
- Prefer real examples from compliance-saas
- Show, don't just tell

**Be specific:**
- ✅ "Sessions 1-4 take approximately 3 hours"
- ❌ "The initial sessions don't take too long"

**User-focused:**
- ✅ "You'll create a mission statement"
- ❌ "The system generates a mission statement"

---

## Testing Your Changes

### Manual Testing Checklist

- [ ] **Commands work:**
  ```bash
  /your-new-command
  # Verify it generates correct output
  ```

- [ ] **Cascade integration:**
  ```bash
  /cascade-status
  # Verify your command appears correctly
  ```

- [ ] **Dependencies:**
  ```bash
  # Verify your command can read required inputs
  # Verify downstream commands can read your outputs
  ```

- [ ] **Examples:**
  ```bash
  ls examples/compliance-saas/
  # Verify example output exists and is complete
  ```

- [ ] **Documentation:**
  ```bash
  # Verify all links work
  # Check for typos
  # Ensure consistent formatting
  ```

### Quality Checks

**For new commands:**
- [ ] Includes all required sections
- [ ] Has decision trees for complex choices
- [ ] Has examples (preferably from compliance-saas)
- [ ] Has "What We DIDN'T Choose" section (2-4 alternatives)
- [ ] Has quality checklist
- [ ] Traces decisions back to journey
- [ ] Reads appropriate previous sessions
- [ ] Generates well-structured output

**For documentation:**
- [ ] Clear and concise
- [ ] Uses examples
- [ ] Follows markdown style guide
- [ ] All links work
- [ ] No typos or grammatical errors
- [ ] Consistent with existing documentation

**For examples:**
- [ ] Complete cascade (at least Sessions 1-10)
- [ ] Follows template structure
- [ ] High quality outputs
- [ ] Different from existing examples
- [ ] Includes README explaining product and decisions

---

## Community

### Where to Get Help

**Documentation:**
- README.md
- FAQ.md
- TROUBLESHOOTING.md
- PHILOSOPHY.md

**GitHub:**
- [Issues](../../issues) - Bug reports, feature requests
- [Discussions](../../discussions) - Questions, ideas, showcase

**Contributing:**
- This document (CONTRIBUTING.md)
- IMPLEMENTATION-PROMPT.md (for command development)

### Showcase Your Work

Built something with Stack-Driven? We'd love to see it!

**Options:**
1. **Add as example:**
   - Submit PR with complete cascade
   - Helps future users see diverse use cases

2. **Share in Discussions:**
   - Post in "Show and Tell"
   - Share your experience and learnings

3. **Write a case study:**
   - Document your process
   - Share what worked and what didn't
   - Help others learn from your experience

---

## Recognition

**Contributors will be:**
- Listed in CHANGELOG.md
- Credited in relevant documentation
- Featured in community showcases (with permission)

**Significant contributors may become:**
- Maintainers (with commit access)
- Core team members (shaping framework direction)

---

## Questions?

**Not sure about something?**
1. Check [FAQ.md](FAQ.md)
2. Search [existing issues](../../issues)
3. Open a [discussion](../../discussions)
4. Ask in your PR

**Remember:** There are no dumb questions. We were all new once!

---

## Thank You

Your contributions make Stack-Driven better for everyone. Whether you:
- Fix a typo
- Add an example
- Create a new command
- Improve documentation

**Every contribution matters.** Thank you for being part of the Stack-Driven community! 🚀

---

**Last Updated:** 2025-11-14
**Version:** 2.0.0
**License:** Apache 2.0
