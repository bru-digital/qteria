# Content Guidelines: Qteria

> **Generated**: November 17, 2025
> **Brand**: Qteria
> **Status**: Final

## Overview

This comprehensive content style guide ensures consistency across all written communication - from UI microcopy to marketing materials to customer support. Qteria's content reflects our brand personality: professional, direct, trustworthy, and organized.

**Target Audience**: Project Handlers (power users validating 15-20 assessments/day), Process Managers (creating workflows), Certification Persons (receiving validation reports)

---

## Voice and Tone Foundation

### Our Voice

**Core voice attributes**: Clear, Professional, Evidence-Based, Efficient, Trustworthy

**Description**: Qteria communicates like a competent colleague who respects your time and expertise. We're the quality manager who always has the answer, delivers it clearly, and backs it up with evidence. We're professional but not stiff, direct but not curt, confident but not arrogant. We eliminate uncertainty with facts, not flowery language.

### Voice in Practice

**We sound like**:

- ✅ "Assessment complete in 8 minutes. All 12 criteria passed. View evidence links below."
- ✅ "Upload failed. File exceeds 50MB limit. Try compressing the PDF or splitting into sections."
- ✅ "Workflow saved. You can now assign documents and start validation."
- ✅ "3 criteria require attention. Review the evidence to determine next steps."
- ✅ "Processing documents. Estimated time: 7 minutes."

**We don't sound like**:

- ❌ "Woohoo! Your assessment is done!" (too casual, unprofessional)
- ❌ "An error has occurred. Please contact your system administrator." (too generic, unhelpful)
- ❌ "Congratulations! You've successfully completed the workflow creation process!" (too wordy, over-celebratory)
- ❌ "Hang tight! We're crunching the numbers..." (too informal for B2B compliance tool)
- ❌ "Error 500: Internal server error." (too technical, no guidance)

### Tone Variations

| Context                      | Tone Shift                       | Example                                                                                        |
| ---------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Default**                  | Clear, neutral, efficient        | "Select a workflow to begin validation."                                                       |
| **Welcome/Onboarding**       | Professional, helpful            | "Welcome to Qteria. Create your first workflow to start validating documents."                 |
| **Success**                  | Confident, factual               | "Assessment complete. All criteria passed."                                                    |
| **Error**                    | Direct, solution-focused         | "Unable to parse PDF. File may be corrupted. Try re-exporting from source."                    |
| **Warning**                  | Cautionary, clear                | "Workflow contains criteria with no assigned documents. Assessment results may be incomplete." |
| **Empty state**              | Instructive, actionable          | "No workflows yet. Create your first workflow to get started."                                 |
| **Loading**                  | Informative, expectation-setting | "Analyzing documents. This typically takes 5-10 minutes."                                      |
| **Sensitive (payment/data)** | Reassuring, precise              | "Your documents are encrypted at rest. We never train AI models on your data."                 |
| **Marketing**                | Benefit-focused, credible        | "Validate certification documents 400x faster with evidence-based AI assessments."             |
| **Support**                  | Patient, thorough                | "Let's troubleshoot this together. First, check that the PDF isn't password-protected."        |

---

## Grammar and Mechanics

### Style Guide Base

**Primary style guide**: Custom (prioritizes clarity and scannability over traditional editorial rules)

**When in doubt**: Choose the option that is faster to scan and easier to understand. Project Handlers run 15-20 assessments per day - every word counts.

### Capitalization

**Headlines and titles**: Sentence case

- ✅ Good: "Assessment results"
- ❌ Bad: "Assessment Results"

**Buttons**: Sentence case

- ✅ Good: "Start assessment"
- ❌ Bad: "Start Assessment"

**Product features**: Sentence case

- ✅ Good: "Evidence-based validation"
- ❌ Bad: "Evidence-Based Validation"

**Company name**: Qteria (always capitalized, never "qteria" or "QTERIA")

**Product name**: Qteria (same as company name)

**Journey terms** (capitalize when referring to specific concepts):

- "Workflow" (the object users create)
- "Bucket" (document category)
- "Criteria" (validation rule)
- "Assessment" (validation run)
- "Project Handler" (role)
- "Process Manager" (role)

### Punctuation

**Serial comma**: Yes

- ✅ "Upload test reports, technical files, and certificates."

**Contractions**: Avoid entirely

- ❌ "You're", "We'll", "Can't"
- ✅ "You are", "We will", "Cannot"
- **Rationale**: Qteria serves international audiences (Balkans, EU). Contractions are harder to translate and can sound informal in compliance contexts.

**Exclamation points**: Avoid entirely

- ❌ "Assessment complete!"
- ✅ "Assessment complete."
- **Rationale**: Professional B2B tool. Users care about speed and accuracy, not enthusiasm. Exclamation points undermine credibility in quality management context.

**Ampersands (&)**: Avoid

- Only use in established abbreviations: "Q&A", "R&D"
- Never in body text: "Documents and evidence" (not "Documents & evidence")

**Ellipsis (...)**: Use sparingly

- Acceptable in loading states: "Processing..."
- Avoid in instructional text: "Then upload documents" (not "Then upload documents...")

**Em dashes (—)**: Use for emphasis or clarification

- "Evidence-based validation — linking AI results to exact pages and sections — builds trust in automated assessments."

### Numbers

**Numbers 1-9**: Use numerals
**Numbers 10+**: Use numerals

**All numbers are numerals** for faster scanning in UI context.

**Exceptions**:

- Percentages: 95% (always numeral)
- Currency: $0.21 per assessment (always numeral, 2 decimal places)
- Dates: Nov 17, 2025 (written format)
- Time: 2:30 PM (12-hour format with space before AM/PM)
- Measurements: 50MB, 10 minutes, 3.2MB (always numeral)

**Examples**:

- ✅ "3 documents uploaded"
- ✅ "Assessment takes 5-10 minutes"
- ✅ "12 criteria checked"
- ❌ "Three documents uploaded"

### Dates and Times

**Date format**: Written format (Month D, YYYY)

- Example: November 17, 2025
- In compact UI: Nov 17, 2025
- In data tables: 11/17/2025 (for alignment)

**Time format**: 12-hour with AM/PM

- Example: 2:30 PM
- Include space before AM/PM
- Use "noon" and "midnight" instead of 12:00 PM/AM when possible

**Timezone**: Include when ambiguous

- Example: "Assessment started at 2:30 PM EST"
- Default to user's local time (no timezone needed)

**Relative time** (preferred for recent events):

- "2 minutes ago"
- "Uploaded 1 hour ago"
- "Created yesterday"
- After 7 days, switch to absolute date: "Nov 10, 2025"

---

## Word List

### Preferred Terms

| Instead of... | We say...                                        | Because...                                           |
| ------------- | ------------------------------------------------ | ---------------------------------------------------- |
| Validate      | Check, assess, validate (context-dependent)      | "Validate" is industry term, but mix for readability |
| User          | Project Handler, Process Manager (role-specific) | More precise, respects user's expertise              |
| Submit        | Start, upload, create (specific action)          | "Submit" is generic, doesn't indicate what happens   |
| Dashboard     | Home, Overview                                   | "Dashboard" implies analytics; we show workflow list |
| Success       | Complete, passed                                 | "Success" is vague; be specific about outcome        |
| Failed        | Did not pass, requires attention                 | "Failed" sounds harsh; focus on next action          |
| Click         | Select, choose (for links/buttons)               | Device-agnostic (touch, keyboard)                    |
| File          | Document                                         | Industry term for compliance documents               |
| Folder        | Bucket                                           | Our product term for document categories             |
| Settings      | Preferences                                      | "Settings" is standard, no need to change            |

### Terms to Avoid

| Word/Phrase                     | Why to Avoid                                | Alternative                                    |
| ------------------------------- | ------------------------------------------- | ---------------------------------------------- |
| "Easy", "Simple", "Just"        | Minimizes user effort, can be condescending | Describe the action: "Select a workflow"       |
| "Please"                        | Sounds like begging, weakens authority      | Direct instruction: "Upload documents"         |
| "Oops", "Uh-oh"                 | Too casual for compliance tool              | State the issue: "Upload failed"               |
| "Obviously", "Clearly"          | Implies user should already know            | Explain directly: "Criteria require documents" |
| "Utilize"                       | Pretentious, use simpler word               | "Use"                                          |
| "Leverage"                      | Business jargon                             | "Use", "apply", "benefit from"                 |
| "Synergy", "Paradigm", "Robust" | Meaningless buzzwords                       | Specific descriptions                          |

### Industry/Product Terms

| Term            | Definition                                         | Example Usage                                                |
| --------------- | -------------------------------------------------- | ------------------------------------------------------------ |
| Workflow        | Validation template with buckets and criteria      | "Create a workflow for medical device certifications."       |
| Bucket          | Document category in a workflow                    | "Upload test reports to the Technical Documentation bucket." |
| Criteria        | Validation rule to check                           | "All 12 criteria passed."                                    |
| Assessment      | Single validation run                              | "Assessment complete in 8 minutes."                          |
| Evidence        | AI's proof of pass/fail (page, section, reasoning) | "View evidence: test-report.pdf, page 8, section 3.2"        |
| Project Handler | User validating documents                          | "Project Handlers run 15-20 assessments per day."            |
| Process Manager | User creating workflows                            | "Process Managers define validation criteria."               |
| Notified Body   | Certification organization (customer)              | "Qteria serves notified bodies in the Balkans and EU."       |

---

## Microcopy Patterns

### Buttons

**Primary action buttons**: Specific, verb-led

- ✅ Good: "Start assessment", "Create workflow", "Upload documents"
- ❌ Bad: "Submit", "OK", "Click here"

**Secondary action buttons**: Clear, context-specific

- ✅ Good: "Cancel", "Go back", "Skip this step"
- ❌ Bad: "No", "Close", "Exit"

**Destructive actions**: Explicit about consequence

- ✅ Good: "Delete workflow", "Remove document", "Cancel assessment"
- ❌ Bad: "Delete", "Remove", "OK"

**Common buttons**:

- Save: "Save workflow" (specific), "Save changes" (if editing)
- Cancel: "Cancel" (acceptable, universally understood)
- Submit: Avoid - use specific action instead
- Continue: "Continue to upload" (specific next step)
- Back: "Go back" or "Back to workflows"
- Delete: "Delete [object]" - always specify what
- Confirm: "Confirm deletion", "Confirm and start"

### Form Labels and Instructions

**Label style**: Sentence case

- Example: "Workflow name", "Email address"

**Required field indicator**: \* (asterisk, red)

- Example: Workflow name\*
- Helper text below: "Required fields are marked with \*"

**Optional field indicator**: (optional) in gray

- Example: Description (optional)

**Placeholder text**: Instructive example

- ✅ Good: "Medical Device - Class II" (for workflow name)
- ✅ Good: "Enter your work email address"
- ❌ Bad: "Name" (not helpful)
- ❌ Bad: "Email" (redundant with label)

**Helper text**: Appears below field, gray text, concise

- Example: "Choose a descriptive name. You can change this later."
- Example: "Max 50MB per document. PDF and DOCX formats supported."

### Error Messages

**Structure**: [What went wrong] [What to do about it]

- Template: "Unable to [action]. [Specific reason]. [Solution]."

**Examples**:

- ✅ "Unable to upload document. File exceeds 50MB limit. Try compressing the PDF or splitting into sections."
- ✅ "Email address is invalid. Check for typos and try again."
- ✅ "Password must be at least 8 characters. Include letters and numbers."
- ✅ "Cannot delete workflow. Active assessments are in progress. Wait for completion or cancel assessments first."
- ❌ "Error 400: Bad Request" (too technical)
- ❌ "Invalid input" (not specific)
- ❌ "Something went wrong. Please try again." (not helpful)

**Common errors**:

- **Email invalid**: "Email address is invalid. Check for typos and try again."
- **Password too short**: "Password must be at least 8 characters. Include letters and numbers."
- **Required field empty**: "[Field name] is required. Enter [description] to continue."
- **Form validation failed**: "Cannot save. Fix errors marked in red above."
- **Network error**: "Unable to connect. Check your internet connection and try again."
- **Permission denied**: "You do not have permission to [action]. Contact your organization admin to request access."

### Success and Confirmation Messages

**Structure**: [What happened] [What's next (if applicable)]

**Examples**:

- ✅ "Workflow saved. You can now upload documents and start validation."
- ✅ "Assessment complete in 8 minutes. View results below."
- ✅ "Document uploaded. Add more documents or start assessment."
- ✅ "Changes saved."
- ❌ "Success!" (vague)
- ❌ "Done" (not informative)
- ❌ "Your workflow has been successfully saved to the database!" (too wordy)

**Common success messages**:

- **Account created**: "Account created. Check your email to verify your address."
- **Settings saved**: "Settings saved."
- **Item deleted**: "[Item] deleted."
- **Email sent**: "Email sent to [email address]."
- **Upload complete**: "Document uploaded. [File name], 3.2MB."

### Empty States

**Structure**: [Explanation] [Action]

**Examples**:

- ✅ "No workflows yet. Create your first workflow to start validating documents."
- ✅ "No documents uploaded. Upload PDFs or Word documents to begin assessment."
- ✅ "All criteria passed. No issues found."
- ❌ "No results found." (not actionable)
- ❌ "Empty" (not helpful)

**Common empty states**:

- **No search results**: "No workflows match '[query]'. Try different keywords or create a new workflow."
- **No items in list**: "No [items] yet. [Action to create first item]."
- **No data yet**: "No assessments yet. Start your first assessment to see results here."
- **Assessment complete - all pass**: "All criteria passed. No issues found. Export report or start new assessment."

### Loading States

**Short loads** (< 3 seconds): Simple message or spinner only

- Example: "Loading..." or just spinner (no text)

**Long loads** (> 3 seconds): Descriptive message with context

- Example: "Analyzing documents. This typically takes 5-10 minutes."
- Example: "Processing 8 documents against 12 criteria. Estimated time: 7 minutes."

**Progress indicators**: Percentage + phase description

- Example: "45% complete. Checking criteria..."
- Example: "Parsing PDFs. 3 of 8 documents complete."

**Critical for Step 3** (AI validation):

- Show current phase: "Parsing PDFs", "Checking criteria", "Extracting evidence"
- Update progress every 2-3 seconds
- Show time estimate: "Estimated time: 7 minutes"
- Provide cancel option: "Cancel assessment" (rare use, but accessible)

### Navigation and Headings

**Page titles**: Sentence case, descriptive

- Example: "Assessment results", "Create workflow", "Account settings"

**Section headings**: Sentence case, scannable

- Example: "Document buckets", "Validation criteria", "Evidence links"

**Navigation labels**: Short, clear, no articles

- Example: "Workflows", "Assessments", "Settings" (not "My Workflows", "View Assessments")

---

## Email and Notification Templates

### Email Structure

**Subject lines**:

- Character limit: < 60 characters (mobile preview)
- Style: Clear, specific, actionable
- Include key info: "[Qteria] Assessment complete - 12/12 criteria passed"
- ✅ Good: "Assessment complete - Action required"
- ✅ Good: "Workflow '[name]' created successfully"
- ❌ Bad: "Notification from Qteria" (vague)
- ❌ Bad: "You have a new message!" (spammy)

**Email greeting**:

- Default: "Hi [First Name],"
- Formal: "Hello [First Name]," (rarely needed)
- Casual: Never use ("Hey", "Hi there")

**Email closing**:

- Default: "Best regards,\nThe Qteria Team"
- Transactional emails: No closing needed (system notification)

### Common Email Templates

**Welcome email**:

- Subject: "Welcome to Qteria - Get started with your first workflow"
- Body:

  ```
  Hi [Name],

  Welcome to Qteria. Your account is ready.

  Get started:
  1. Create your first workflow
  2. Upload documents
  3. Start validation

  [Button: Create workflow]

  Questions? Reply to this email or visit our help center.

  Best regards,
  The Qteria Team
  ```

**Password reset**:

- Subject: "Reset your Qteria password"
- Body:

  ```
  Hi [Name],

  You requested a password reset for your Qteria account.

  [Button: Reset password]

  This link expires in 1 hour.

  Did not request this? Ignore this email. Your password will not change.

  Best regards,
  The Qteria Team
  ```

**Assessment complete**:

- Subject: "Assessment complete - [X/Y] criteria passed"
- Body:

  ```
  Hi [Name],

  Your assessment "[Workflow name]" is complete.

  Results:
  - 12 of 12 criteria passed
  - Processing time: 8 minutes
  - Documents analyzed: 8

  [Button: View results]

  Best regards,
  The Qteria Team
  ```

**Assessment requires attention**:

- Subject: "Assessment complete - Action required"
- Body:

  ```
  Hi [Name],

  Your assessment "[Workflow name]" is complete. 3 criteria require attention.

  Results:
  - 9 of 12 criteria passed
  - 3 criteria require review
  - Processing time: 9 minutes

  [Button: View results]

  Review the evidence links to determine next steps.

  Best regards,
  The Qteria Team
  ```

### In-App Notifications

**Toast notifications**: Brief, 5 words or less when possible

- ✅ Good: "Workflow saved"
- ✅ Good: "Document uploaded"
- ✅ Good: "Assessment started"
- ❌ Bad: "Your workflow has been successfully saved to your account" (too long)

**Push notifications**: Brief, actionable, < 120 characters

- Example: "Assessment complete. 12/12 criteria passed. View results."
- Example: "3 criteria require attention. Review evidence now."

---

## Accessibility Considerations

### Alt Text for Images

**Structure**: Describe what's happening + context if needed

- ✅ Good: "Assessment results showing 12 criteria passed, 0 failed"
- ✅ Good: "Upload progress at 45%, 3 of 8 documents processed"
- ✅ Good: "Evidence link to test-report.pdf, page 8, section 3.2"
- ❌ Bad: "Chart" (not descriptive)
- ❌ Bad: "Image" (useless)

**Decorative images**: Use alt="" (empty alt attribute)

- Example: Background patterns, ornamental icons

### Link Text

**Rule**: Links must be descriptive when read out of context

- ✅ Good: "View assessment results"
- ✅ Good: "Read the privacy policy"
- ✅ Good: "Download validation report (PDF, 2.3MB)"
- ❌ Bad: "Click here to view results"
- ❌ Bad: "Learn more" (without context)
- ❌ Bad: "Read more" (without specifying what)

### ARIA Labels

**When to use**: When visible text is not sufficient for screen readers

- Icon buttons: `<button aria-label="Delete workflow">🗑</button>`
- Status indicators: `<div role="status" aria-live="polite">Processing...</div>`
- Progress bars: `<div role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100">45%</div>`

### Reading Level

**Target**: 8th grade or lower (Flesch-Kincaid)

**Tools**: Hemingway App (aim for grade 8 or lower)

**Guidelines**:

- Use short sentences (15-20 words average)
- Prefer simple words: "use" not "utilize", "help" not "facilitate"
- Avoid jargon unless industry-standard and unavoidable
- Define technical terms on first use: "Criteria (validation rules)"

---

## Localization Guidance

### Translation-Friendly Writing

**Do**:

- ✅ Use complete sentences: "Document uploaded successfully" (not "Document uploaded ✓")
- ✅ Avoid slang and idioms: "Review results" (not "Take a look at results")
- ✅ Be explicit: "Click the blue Start button" (not "Click the button below")
- ✅ Use consistent terminology: Always "workflow", never "template" or "process"

**Don't**:

- ❌ Use culturally-specific references: "Home run feature" (baseball term)
- ❌ Concatenate strings programmatically: `"You have " + count + " documents"` (word order varies by language)
- ❌ Use text in images: All text should be HTML/CSS, not baked into graphics
- ❌ Assume left-to-right reading: Design for RTL languages (Arabic, Hebrew)

### Cultural Considerations

**Dates**: Different formats globally

- US: MM/DD/YYYY
- EU: DD/MM/YYYY
- ISO: YYYY-MM-DD
- Solution: Use written format ("Nov 17, 2025") or let user choose preference

**Numbers**: Decimal separators vary

- US: 1,000.50 (comma thousands, period decimal)
- EU: 1.000,50 (period thousands, comma decimal)
- Solution: Use system locale settings

**Currency**: Multiple currencies for international expansion

- Always specify currency: "$0.21 USD" not just "$0.21"
- Use 3-letter ISO codes: USD, EUR, GBP

**Names**: Name formats vary globally

- Don't assume "First Last" structure
- Use single "Full name" field when possible
- Never require "middle name"

---

## Content Review Checklist

Before publishing any content, verify:

### Clarity

- [ ] Can someone understand this in 5 seconds?
- [ ] Is it written at 8th grade reading level or below? (Check with Hemingway App)
- [ ] Are there any jargon words that need definition?
- [ ] Is the action or next step obvious?

### Voice and Tone

- [ ] Does this sound like us? (Clear, professional, evidence-based, efficient, trustworthy)
- [ ] Is the tone appropriate for the context? (Neutral default, solution-focused for errors)
- [ ] Does it match our voice attributes (professional but not stiff, direct but not curt)?
- [ ] Did we avoid casual language? (No "Oops", "Hang tight", "Woohoo")

### Accuracy

- [ ] Are all facts correct?
- [ ] Are all links working?
- [ ] Is the information up-to-date?
- [ ] Are technical terms used correctly?

### Grammar

- [ ] Spell-check complete?
- [ ] Grammar check complete?
- [ ] Consistent capitalization? (Sentence case for headings, buttons)
- [ ] Proper punctuation? (Serial commas, no contractions, no exclamation points)
- [ ] Numbers formatted correctly? (Always numerals)

### Accessibility

- [ ] Alt text for images?
- [ ] Descriptive link text? (No "click here")
- [ ] Appropriate heading hierarchy? (H1 → H2 → H3, no skips)
- [ ] Color not the only way to convey info? (Icon + text + background for status)
- [ ] ARIA labels for icon buttons?

### Brand

- [ ] Follows content guidelines?
- [ ] Uses preferred terminology? (Workflow, bucket, criteria, assessment, evidence)
- [ ] Aligns with design system? (Matches professional, direct, trustworthy personality)
- [ ] Avoids buzzwords? (No "leverage", "synergy", "paradigm")

---

## Examples: Before and After

### Example 1: Error Message

**Before (Generic)**:
"An error occurred. Please try again."

**After (Specific + Helpful)**:
"Unable to upload document. File exceeds 50MB limit. Try compressing the PDF or splitting into sections."

**Why better**: Explains what went wrong, why, and how to fix it.

---

### Example 2: Button

**Before (Vague)**:
"Submit"

**After (Clear)**:
"Start assessment"

**Why better**: Tells user exactly what will happen when they click.

---

### Example 3: Empty State

**Before (Unhelpful)**:
"No data."

**After (Actionable)**:
"No workflows yet. Create your first workflow to start validating documents."

**Why better**: Explains why it is empty and what to do next.

---

### Example 4: Success Message

**Before (Too enthusiastic)**:
"Congratulations! Your workflow has been successfully saved to your account!"

**After (Professional + Concise)**:
"Workflow saved. You can now upload documents and start validation."

**Why better**: Respects user's time, states what happened, guides next step.

---

### Example 5: Loading State

**Before (Vague)**:
"Processing..."

**After (Informative)**:
"Analyzing documents. This typically takes 5-10 minutes."

**Why better**: Sets expectations, reduces anxiety about wait time.

---

### Example 6: Evidence Link

**Before (Technical)**:
"Source: doc_8472.pdf, p.8"

**After (Clear)**:
"Evidence: test-report.pdf, page 8, section 3.2"

**Why better**: Uses readable file name, clear labels, full words (not abbreviations).

---

## Microcopy Library (Common Patterns)

### Validation Results Status

- Pass: "[X] of [Y] criteria passed"
- All pass: "All criteria passed. No issues found."
- Some fail: "[X] criteria require attention. Review evidence below."
- Processing: "Analyzing documents. [X]% complete. Estimated time: [Y] minutes."

### Upload Feedback

- Success: "Document uploaded. [Filename], [size]MB."
- Error - size: "Unable to upload. File exceeds 50MB limit. Try compressing the PDF."
- Error - format: "Unable to upload. Format not supported. Upload PDF or DOCX files."
- Error - network: "Upload failed. Check your internet connection and try again."

### Form Validation

- Required field: "[Field name] is required."
- Invalid email: "Email address is invalid. Check for typos and try again."
- Password strength: "Password must be at least 8 characters. Include letters and numbers."
- Duplicate name: "Workflow name already exists. Choose a unique name."

### Actions

- Save success: "Workflow saved."
- Delete confirmation: "Delete [item]? This cannot be undone."
- Delete success: "[Item] deleted."
- Cancel: "Discard changes? Unsaved changes will be lost."

### Navigation

- Breadcrumbs: "Home > Workflows > [Workflow name]"
- Back link: "← Back to workflows"
- Pagination: "Showing [X]-[Y] of [Z] workflows"

---

## Updating These Guidelines

**Review frequency**: Quarterly (every 3 months) or after major product changes

**How to propose changes**:

1. Open issue in GitHub: "Content guidelines update: [topic]"
2. Provide rationale and examples
3. Get approval from product owner
4. Submit PR to this document

**Who approves**: Founder (current), Marketing Lead (future)

**Change log**:

- November 17, 2025: Initial version created

---

## Resources

**Brand messaging**: product-guidelines/10-brand-messaging.md (not yet created - expand voice/tone from this document)

**Design system**: product-guidelines/06-design-system.md (visual design aligns with content personality)

**Writing tools**:

- Hemingway Editor - Check readability (target: grade 8 or lower)
- Grammarly - Grammar and spell check
- WAVE - Accessibility checker for web content
- axe DevTools - ARIA label validation

**Questions**: Email founder or open GitHub issue with "Content question" label

---

## Document Control

**Status**: Final
**Last Updated**: November 17, 2025
**Next Review**: February 17, 2026 (quarterly)
**Owner**: Founder
**Contributors**: Design system reference (Session 6), User journey context (Session 1), Brand personality (Session 5)

---

## Summary

Qteria's content is clear, professional, evidence-based, efficient, and trustworthy. We communicate like a competent colleague who respects users' time and expertise. We eliminate uncertainty with facts, not flowery language. We write in sentence case, avoid contractions and exclamation points, use numerals for all numbers, and provide specific, actionable guidance in all contexts. Every word serves the user's goal: validate documents quickly with confidence.
