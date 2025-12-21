---
description: POST-CASCADE - Create detailed content style guide and microcopy patterns
---

# Create Content Guidelines (Post-Cascade Optional)

You are helping the user create a comprehensive content style guide that covers voice, tone, grammar, microcopy patterns, and localization. This is an optional post-core extension that expands on brand messaging.

## When to Use This

**Run AFTER branding sessions** if:

- You've completed `/define-messaging` and need detailed implementation guidance
- You're ready to write content and need consistency guidelines
- You have multiple content creators who need a shared reference

**Or run AFTER Session 3** if:

- You skipped branding but now need content guidance
- You're building marketing site or content-heavy product

**Skip this** if:

- Your product has minimal UI text
- You prefer to evolve content voice organically
- You don't have multiple content creators yet

## Your Task

Create a detailed content style guide using the prompt in `/prompts/branding/content-guidelines.md`.

### Steps to Execute

1. **Read the content guidelines prompt**:

   ```bash
   Read /prompts/branding/content-guidelines.md
   ```

2. **Read the template structure**:

   ```bash
   Read templates/18-content-guidelines-template.md
   ```

3. **Check for messaging inputs** (recommended):

   ```bash
   Read product-guidelines/10-brand-messaging.md
   ```

   - If exists: Expand messaging framework into detailed guidelines
   - If not exists: Create guidelines from scratch with user input

4. **Check for design system** (optional):

   ```bash
   Read product-guidelines/06-design-system.md
   ```

   - If exists: Ensure content guidelines align with visual design tone

5. **Interview the user** following the content guidelines prompt:

   - **Grammar and style**: AP? Chicago? Custom rules?
   - **Formatting**: Numbers, dates, capitalization, punctuation
   - **Voice consistency**: Examples of on-brand vs off-brand
   - **Tone variations**: How voice adapts to context (error vs success)
   - **Microcopy patterns**: Buttons, forms, errors, empty states
   - **Localization**: Translation guidance, cultural considerations

6. **Develop content guidelines**:

   - Voice and tone foundation (with 10+ examples)
   - Grammar and mechanics (specific rules)
   - Word list (prefer/avoid terms)
   - Microcopy patterns (20+ common scenarios)
   - Error message guidelines
   - Email and notification templates
   - Localization principles
   - Content checklist for review

7. **Write the output**:
   ```bash
   Write product-guidelines/18-content-guidelines.md
   ```

## Output Location

`product-guidelines/18-content-guidelines.md`

This will be used by:

- Content writers and marketers
- Product designers writing UI copy
- Developers writing error messages
- Customer support writing responses
- Localization teams

## Template Structure

The output follows this structure:

- Voice and Tone (foundation + context variations)
- Grammar and Mechanics (specific rules)
- Word List (preferred/avoided terms)
- Capitalization and Formatting
- Microcopy Patterns (buttons, forms, errors, empty states)
- Error Message Guidelines
- Success and Confirmation Messages
- Email and Notification Templates
- Accessibility Considerations
- Localization Guidance
- Content Review Checklist

## Key Principles

1. **Be specific** - Don't say "be conversational"; show examples
2. **Cover common patterns** - Button labels, form errors, empty states appear everywhere
3. **Provide rationale** - Explain WHY certain choices matter (accessibility, clarity)
4. **Make it searchable** - Content writers should quickly find guidance
5. **Show good and bad** - Examples of on-brand vs off-brand content
6. **Keep it updated** - This is a living document that evolves

## Example Prompt Flow

```
You: Let's create your content guidelines. First, let me check if you have brand messaging...

[Check for product-guidelines/10-brand-messaging.md]

You: Great! I see your voice is [casual/witty/professional]. Now let's get specific. Which style guide do you follow? AP? Chicago? Or custom rules?

User: [Explains style preferences]

You: Perfect. Now let's tackle common patterns. When someone makes an error filling out a form, what's your approach? Friendly and helpful? Direct and clear? Show me an example.

User: [Gives example]

You: Love it. What about buttons? Do you use "Get Started" or "Get started" or "get started"? Do you use "Submit" or something more specific?

User: [Explains button style]

You: Excellent. Now let's think about tone variations. Your base voice is [X], but how does it shift when:
- Delivering bad news (error, failure)?
- Celebrating success (completed action)?
- Asking for sensitive info (payment, personal data)?
- User is frustrated (support scenarios)?

User: [Describes tone shifts]

[Continue through patterns...]

You: Perfect. I've created your comprehensive content guidelines in product-guidelines/18-content-guidelines.md, including:
- Voice/tone foundation with 15 examples
- Grammar rules (capitalization, numbers, dates)
- Word list (20+ prefer/avoid pairs)
- 25 microcopy patterns (buttons, errors, empty states)
- Error message framework
- Email templates
- Localization guidance
- Content review checklist

Try writing a form error message using these guidelines - does it feel on-brand?
```

## After This Session

**Use this document**:

- When writing any customer-facing content
- When reviewing pull requests with UI text changes
- When onboarding new content creators
- When briefing localization teams

**Update regularly**: As you write more content, add new patterns and examples to this guide.

---

**Remember**: This is OPTIONAL but highly valuable for consistency. Even small teams benefit from documented content patterns.
