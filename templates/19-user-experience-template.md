# User Experience Design

> **Generated**: [Date]
> **Product**: [Product Name]
> **Status**: [Draft/In Progress/Final]

## Overview

This document defines the detailed UX design including research, information architecture, user flows, wireframes, and interaction specifications.

**Complements**: Session 4 Design System (product-guidelines/06-design-system.md)
- This doc: **UX structure and behavior** (what happens, how it works)
- Design system: **Visual language** (how it looks, design tokens, components)

---

## UX Research Summary

### User Segments

#### Primary Persona: [Name/Title]

**Demographics**:
- Role: [Job title]
- Company size: [Small/Medium/Large]
- Industry: [Industry]
- Experience level: [Beginner/Intermediate/Expert]

**Context**:
- **Where they work**: [Office/Remote/Field]
- **Devices**: [Desktop/Mobile/Tablet]
- **Time constraints**: [e.g., "Always rushed between meetings"]

**Pain Points**:
1. [Pain point 1]
2. [Pain point 2]
3. [Pain point 3]

**Jobs to Be Done**:
1. **When** [situation], **I want to** [motivation], **so I can** [expected outcome]
2. **When** [situation], **I want to** [motivation], **so I can** [expected outcome]
3. **When** [situation], **I want to** [motivation], **so I can** [expected outcome]

**Goals**:
- [Goal 1]
- [Goal 2]
- [Goal 3]

---

#### Secondary Persona: [Name/Title]

[Repeat structure]

---

### User Research Insights

**Research conducted**:
- [Method 1]: [What you learned]
- [Method 2]: [What you learned]
- [Method 3]: [What you learned]

**Key findings**:
1. **[Finding 1]**: [Insight + implication for design]
2. **[Finding 2]**: [Insight + implication]
3. **[Finding 3]**: [Insight + implication]

**Research gaps**:
- [Gap 1]: [What you don't know yet]
- [Gap 2]: [What you need to validate]

---

## Information Architecture

### Site Map

```
[Product Name]
│
├── [Section 1]
│   ├── [Sub-section 1.1]
│   ├── [Sub-section 1.2]
│   └── [Sub-section 1.3]
│
├── [Section 2]
│   ├── [Sub-section 2.1]
│   └── [Sub-section 2.2]
│
├── [Section 3]
│   ├── [Sub-section 3.1]
│   ├── [Sub-section 3.2]
│   ├── [Sub-section 3.3]
│   └── [Sub-section 3.4]
│
└── [Section 4]
    ├── [Sub-section 4.1]
    └── [Sub-section 4.2]
```

### Navigation Structure

**Primary navigation**: [Where + what]
- [Nav item 1]
- [Nav item 2]
- [Nav item 3]
- [Nav item 4]

**Secondary navigation**: [Where + what]
- [Nav item 1]
- [Nav item 2]

**Utility navigation**: [Where + what]
- [Nav item 1]
- [Nav item 2]
- [Nav item 3]

### Content Organization Principles

1. **[Principle 1]**: [How content is grouped - e.g., "By user task, not internal structure"]
2. **[Principle 2]**: [How hierarchy is created]
3. **[Principle 3]**: [How navigation is prioritized]

---

## User Flows

### Flow 1: [Core Action - e.g., "Sign Up and Onboard"]

**Trigger**: [What starts this flow]

**Success criteria**: [What defines success]

**Steps**:

```
1. [Starting point] (Entry)
   ↓
2. [Step 2]
   ↓ [Decision point: User has account?]
   ├─→ Yes: Skip to Step 5
   └─→ No: Continue
   ↓
3. [Step 3]
   ↓ [Validation point]
   ├─→ Valid: Continue
   └─→ Invalid: Show error, return to Step 3
   ↓
4. [Step 4]
   ↓
5. [Step 5] (Success)

   [Alternative path: User abandons]
   → Save progress, send reminder email
```

**Edge cases**:
- [Edge case 1]: [How handled]
- [Edge case 2]: [How handled]

**Screen transitions**: [How user moves between screens]

**Error handling**: [What happens when things go wrong]

---

### Flow 2: [Key Action]

**Trigger**: [What starts this flow]

**Success criteria**: [What defines success]

**Steps**:
[Repeat structure with decision points, validation, errors]

---

### Flow 3: [Key Action]

[Repeat structure]

---

*[Include 5-10 critical flows]*

---

## Wireframes

### Screen 1: [Screen Name - e.g., "Dashboard"]

**Purpose**: [What this screen helps user accomplish]

**Content elements**:
- [Element 1]: [What it shows/does]
- [Element 2]: [What it shows/does]
- [Element 3]: [What it shows/does]

**Wireframe** (Low/Mid fidelity):

```
┌─────────────────────────────────────────────┐
│  [Logo]    Navigation Items    [Profile]    │
├─────────────────────────────────────────────┤
│                                             │
│  [Page Title]                  [CTA Button] │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │             │  │             │          │
│  │   Card 1    │  │   Card 2    │          │
│  │             │  │             │          │
│  └─────────────┘  └─────────────┘          │
│                                             │
│  [Table/List]                               │
│  ┌───────────────────────────────────────┐ │
│  │ Row 1                          [Action]│ │
│  │ Row 2                          [Action]│ │
│  │ Row 3                          [Action]│ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

**Interactions**:
- [Action 1]: [What happens]
- [Action 2]: [What happens]

**States**:
- Loading: [What shows]
- Empty: [What shows]
- Error: [What shows]
- Success: [What shows]

---

### Screen 2: [Screen Name]

[Repeat structure with wireframe]

---

*[Include 10-15 key screens]*

---

## Interaction Specifications

### Component: [Component Name - e.g., "Primary Button"]

**States**:
- Default: [Appearance]
- Hover: [What changes]
- Active/Pressed: [What changes]
- Disabled: [What changes]
- Loading: [What shows]
- Success: [What shows - if applicable]
- Error: [What shows - if applicable]

**Behavior**:
- Click/tap: [What happens]
- Keyboard: [How keyboard navigation works]
- Focus: [Focus indicator]

**Animations**:
- [Transition 1]: [Duration, easing]
- [Transition 2]: [Duration, easing]

---

### Pattern: [Interaction Pattern - e.g., "Infinite Scroll"]

**When to use**: [Context]

**How it works**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Loading behavior**: [What user sees]

**Error handling**: [What happens if loading fails]

**Accessibility**: [How to make accessible]

---

*[Document 10-15 key interactions]*

---

## Responsive Strategy

### Breakpoints

| Breakpoint | Width | Purpose |
|------------|-------|---------|
| Mobile S | < 375px | Small phones |
| Mobile M | 375px - 767px | Standard phones |
| Tablet | 768px - 1023px | Tablets, small laptops |
| Desktop S | 1024px - 1439px | Standard desktops |
| Desktop L | 1440px+ | Large screens |

### Responsive Patterns

**Navigation**: [How it adapts]
- Mobile: [Pattern - e.g., "Hamburger menu"]
- Tablet: [Pattern]
- Desktop: [Pattern]

**Data tables**: [How they adapt]
- Mobile: [Pattern - e.g., "Card view"]
- Tablet: [Pattern]
- Desktop: [Pattern]

**Forms**: [How they adapt]
- Mobile: [Pattern - e.g., "Single column"]
- Tablet: [Pattern]
- Desktop: [Pattern]

### Mobile-First Considerations

1. **[Consideration 1]**: [How mobile experience differs]
2. **[Consideration 2]**: [How mobile experience differs]
3. **[Consideration 3]**: [How mobile experience differs]

---

## Accessibility Requirements

### WCAG Compliance

**Target level**: [A / AA / AAA]

**Key requirements**:

#### Perceivable
- [ ] Text alternatives for non-text content
- [ ] Captions and alternatives for multimedia
- [ ] Content can be presented in different ways
- [ ] Sufficient color contrast (4.5:1 for text)

#### Operable
- [ ] All functionality available from keyboard
- [ ] Enough time to read and use content
- [ ] No content that causes seizures
- [ ] Ways to help users navigate and find content

#### Understandable
- [ ] Text is readable and understandable
- [ ] Content appears and operates in predictable ways
- [ ] Help users avoid and correct mistakes

#### Robust
- [ ] Compatible with current and future tools
- [ ] Valid HTML/ARIA markup

### Keyboard Navigation

**Tab order**: [How tab moves through interface]

**Key commands**:
- `Tab`: [Action]
- `Shift+Tab`: [Action]
- `Enter`: [Action]
- `Escape`: [Action]
- `Arrow keys`: [Action]
- `Space`: [Action]

### Screen Reader Support

**ARIA labels**: [Where used and why]

**Announcements**: [What gets announced and when]

**Landmarks**: [Page regions defined]

### Focus Management

**Focus indicators**: [How focus is shown visually]

**Focus trapping**: [Where focus is trapped - modals, dropdowns]

**Focus restoration**: [How focus returns after actions]

---

## Micro-interactions

### Interaction 1: [Name - e.g., "Like Animation"]

**Trigger**: [What causes it]

**Animation**: [What animates]
- Duration: [ms]
- Easing: [ease-in-out, etc.]

**Feedback**: [What user perceives]

---

### Interaction 2: [Name]

[Repeat structure]

---

*[Document 5-10 delightful micro-interactions]*

---

## Empty States and Error Handling

### Empty State: [Context - e.g., "No Projects"]

**Visual**: [What shows]

**Message**: [Text copy]

**Action**: [CTA button]

**Example**:
```
┌─────────────────────────────────┐
│                                 │
│          [Icon/Illustration]    │
│                                 │
│   No projects yet               │
│   Create your first project     │
│   to get started.               │
│                                 │
│       [Create Project]          │
│                                 │
└─────────────────────────────────┘
```

---

### Error State: [Context]

**When**: [What causes this error]

**Visual**: [What shows]

**Message**: [Error text]

**Action**: [How user can recover]

**Example**: [Show error UI]

---

*[Document 8-10 common empty/error states]*

---

## Prototyping Plan

### What to Prototype

**High priority** (must validate before building):
1. [Flow 1]: [Why needs prototype]
2. [Flow 2]: [Why needs prototype]
3. [Interaction 1]: [Why needs prototype]

**Medium priority** (nice to validate):
1. [Flow 3]: [Why prototype]
2. [Interaction 2]: [Why prototype]

### Fidelity

**Low fidelity**: [Which flows - for concept validation]

**Mid fidelity**: [Which flows - for flow validation]

**High fidelity**: [Which flows - for usability testing]

### Tools

**Prototyping tool**: [Figma / Framer / Adobe XD / Code]

**Interactivity level**: [Click-through / Full interactions]

---

## Usability Testing Plan

### Research Questions

1. [Question 1]: [What you want to learn]
2. [Question 2]: [What you want to learn]
3. [Question 3]: [What you want to learn]

### Test Scenarios

**Scenario 1**: [Task description]
- **Success criteria**: [How to measure success]
- **What to observe**: [Behaviors to watch for]

**Scenario 2**: [Task description]
- **Success criteria**: [How to measure]
- **What to observe**: [Behaviors]

**Scenario 3**: [Task description]
- **Success criteria**: [How to measure]
- **What to observe**: [Behaviors]

### Participants

**Number**: [5-8 recommended]

**Criteria**:
- [Criterion 1 - e.g., "Current user of competitor product"]
- [Criterion 2]
- [Criterion 3]

**Recruitment**: [How to find participants]

### Testing Method

**Format**: [Moderated / Unmoderated]

**Location**: [In-person / Remote]

**Duration**: [45-60 minutes recommended]

**Compensation**: [$ or gift card]

---

## Next Steps

- [ ] Review with design team
- [ ] Validate with user research
- [ ] Create prototypes for high-priority flows
- [ ] Conduct usability testing
- [ ] Iterate based on findings
- [ ] Create design system (Session 4) if not done yet
- [ ] Begin implementation with engineering

---

## Document Control

**Status**: [Draft/In Progress/Final]
**Last Updated**: [Date]
**Next Review**: [Date]
**Owner**: [Name/Role - Designer]
**Contributors**: [Names]
