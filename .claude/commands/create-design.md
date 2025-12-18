---
description: Session 6 - Create design system optimized for user journey
---

# Session 6: Create Design System

This is **Session 6** of the cascade. You'll create a design system that serves the user journey and brings your brand strategy to life. This is not a generic component library, but a design system optimized for your specific journey and brand.

## Your Role

Infer design needs from journey context and create a system optimized for the specific user flows.

## Process

### Step 1: Read Previous Outputs

```
Read: product-guidelines/00-user-journey.md (for user context, interaction needs)
Read: product-guidelines/11-product-strategy-essentials.md (for positioning)
Read: product-guidelines/02-tech-stack.md (for technical constraints)
Read: product-guidelines/05-brand-strategy.md (for brand personality, values, visual direction)
Read: product-guidelines/04-architecture.md (for architecture principles)
```

**Context Optimization**: We read the essentials version of product strategy (~65% smaller). It contains the positioning statement needed for design decisions without detailed market analysis.

### Step 2: Extract Brand Personality & Visual Direction

**From Brand Strategy** (`product-guidelines/05-brand-strategy.md`):

- **Brand Personality**: What attributes are defined? (Professional, playful, trustworthy, innovative, etc.)
- **Core Values**: What values should the design express? (Speed, clarity, trust, creativity, etc.)
- **Visual Direction**: What aesthetic guidance is provided? (Color preferences, mood, style)
- **Brand Promise**: What should users always experience?

Use these as the foundation for design decisions. Don't infer brand—read it from Session 5 output.

### Step 3: Map Brand to Design Needs

**Apply Brand Personality to Design**:

- Trustworthy + Professional → Blues, clear hierarchy, conservative spacing
- Playful + Creative → Vibrant colors, organic shapes, generous whitespace
- Efficient + Technical → Monochrome + accent, tight spacing, monospace fonts

**Component Requirements** (from journey steps):

- Step 1 (Upload)? → File upload component, drag-drop zone
- Step 3 (AI processing)? → Progress indicators, status displays
- Step 4 (Results review)? → Data tables, filtering, expandable cards

**Interaction Patterns**:

- Fast/efficiency-focused? → Keyboard shortcuts, minimal animations
- Exploratory? → Hover states, progressive disclosure
- Careful/high-stakes? → Confirmation dialogs, undo capabilities

**Accessibility**:

- Industry standards? (Healthcare/finance often require WCAG AA)
- User needs? (Older users, accessibility-first contexts)

**Accessibility Requirements** (detailed in Step 6 below):

- WCAG 2.1 AA compliance for most products
- WCAG AAA for government/healthcare
- Color contrast ratios: 4.5:1 (text), 3:1 (large text/UI)
- Keyboard navigation for all journey-critical actions
- Screen reader support with semantic HTML and ARIA labels

### Step 4: Define Design Tokens

**Colors**: Implement brand personality from Session 5

- Trust-focused? → Blues
- Creative? → Vibrant multi-color
- Efficient? → Monochrome + accent

**Typography**: Match use case

- Dense information? → High legibility (Inter, etc.)
- Marketing-heavy? → Distinctive brand fonts
- Technical? → Monospace for code/data

**Typography Scale** (modular scale approach):

Choose scale ratio based on brand personality:

- **1.125 (Major Second)**: Conservative, dense (B2B tools, dashboards)
- **1.250 (Major Third)**: Balanced (most products)
- **1.333 (Perfect Fourth)**: Moderate contrast (content-heavy)
- **1.5 (Perfect Fifth)**: High contrast (marketing, creative)
- **1.618 (Golden Ratio)**: Maximum contrast (landing pages)

**Example Scale (1.250 ratio, 16px base)**:

```
xs:   12px (0.75rem)  → Captions, helper text
sm:   14px (0.875rem) → Secondary text, labels
base: 16px (1rem)     → Body text, forms
lg:   20px (1.25rem)  → Subheadings, card titles
xl:   25px (1.563rem) → Section headings
2xl:  31px (1.953rem) → Page titles
3xl:  39px (2.441rem) → Hero headings
```

**Journey Mapping**:

- Step instructions: `lg` (20px) - needs visibility
- Form labels: `sm` (14px) - standard
- Button text: `base` (16px) - readable at distance
- Error messages: `sm` (14px) with bold weight

**Font Pairing**:

- **Headings**: Inter (B2B), Poppins (friendly), IBM Plex Sans (technical)
- **Body**: Inter, system fonts, or Source Sans Pro
- **Monospace**: Fira Code, JetBrains Mono (for code/data display)

**Spacing**: Match information density needs

- Power users? → Tighter spacing (more on screen)
- Casual users? → Generous spacing (less overwhelming)

**Spacing Scale** (8px base system):

```
0:   0px      → No spacing
1:   4px      → Tight (icon + label)
2:   8px      → Compact (between form elements)
3:   12px     → Default (paragraph spacing)
4:   16px     → Comfortable (between sections)
5:   24px     → Loose (between major sections)
6:   32px     → Spacious (between journey steps)
8:   48px     → Extra spacious (page margins)
10:  64px     → Maximum (hero sections)
```

**Journey Step Spacing**:

- Within forms (Step 1, 2): `space-4` (16px) between fields
- Between journey steps: `space-6` (32px) visual separation
- Card padding: `space-4` (mobile), `space-5` (desktop)
- Page margins: `space-6` to `space-8` depending on density needs

### Step 5: Map Components to Journey

Create table showing:
| Journey Step | UI Components Needed | Design Priority |
|--------------|---------------------|-----------------|
| Step 1 | Upload zone, file list | Large touch targets, clear feedback |
| Step 2 | Checkbox list, search | Smart defaults, fast selection |
| Step 3 | Progress bar, status | Real-time updates, clear ETA |
| Step 4 | Data cards, filters | Scannable, information density |

### Step 6: Component Decision Trees

Apply these rules to determine when to create reusable components vs inline implementations:

**Component Creation Rules**:

```
Does this pattern appear 3+ times in the journey?
├─ YES → Create reusable component
└─ NO ─→ Does it vary by only 1-2 props?
          ├─ YES → Create component with variants
          └─ NO ─→ Is it highly context-specific?
                   ├─ YES → Inline/page-specific component
                   └─ NO ─→ Create component (future reuse likely)
```

**Variant vs New Component**:

```
Does new design differ only in:
  • Color/size?
  • Icon/label?
  • Layout direction (horizontal/vertical)?

├─ YES → Add variant to existing component
└─ NO ─→ Create new component
```

**Examples from Compliance SaaS Journey**:

- **Button** (appears everywhere) → Core component with variants
  - Primary: Main journey actions ("Generate Assessment")
  - Secondary: Cancel, back actions
  - Danger: Delete, remove actions

- **File Upload** (Step 1 only) → Dedicated component (critical path)
  - Multiple props: accept types, max size, drag-drop
  - Complex states: uploading, error, success

- **Framework Selector** (Step 2) → Page-specific component
  - Only used once in journey
  - Highly specific to compliance frameworks
  - Don't over-engineer for reuse

- **Assessment Card** (Step 4 results) → Reusable component
  - Used in dashboard, history, results
  - Variants: collapsed, expanded, with-actions

- **Progress Indicator** (Step 3) → Core component
  - Reused: AI processing, document analysis, export generation
  - States: determinate, indeterminate, with ETA

**Decision Matrix**:
| Pattern | Usage Count | Variance | Decision |
|---------|-------------|----------|----------|
| Form Input | 10+ | Style only | Core component + variants |
| Upload Zone | 1 | N/A | Dedicated component (critical) |
| Status Badge | 8 | Color/text | Core component |
| Onboarding Card | 1 | High context | Inline component |
| Modal Dialog | 5+ | Content | Core component + slots |

### Step 7: Accessibility Standards & Implementation

Accessibility is non-negotiable for journey-critical actions. Define standards based on your user context:

**WCAG Compliance Level** (choose based on context):

- **WCAG 2.1 AA**: Standard for most B2B/B2C products
- **WCAG 2.1 AAA**: Required for government, healthcare, education
- **Section 508**: US federal accessibility requirements

**Color Contrast Requirements**:

```
Text Contrast (WCAG AA):
  • Normal text (< 18pt): 4.5:1 minimum
  • Large text (≥ 18pt or 14pt bold): 3:1 minimum
  • UI components & graphics: 3:1 minimum

Journey-Critical Elements:
  • Primary CTA buttons: 4.5:1 minimum (treat as text)
  • Error messages: 4.5:1 minimum
  • Status indicators: 3:1 + icon/pattern (don't rely on color alone)
```

**Keyboard Navigation Patterns**:

Map to journey steps:

1. **Tab order** follows journey flow (Step 1 → Step 2 → Step 3)
2. **Journey-critical actions** accessible via keyboard:
   - File upload: `Enter` to trigger, `Esc` to cancel
   - Form submission: `Enter` on input, `Cmd/Ctrl+Enter` in textarea
   - Results filtering: Arrow keys, `Space` to select
3. **Focus indicators**: Visible 2px outline on all interactive elements
4. **Skip links**: "Skip to results" for Step 4, "Skip to upload" for Step 1

**ARIA Labels for Journey Actions**:

Label patterns by journey step:

- **Step 1 (Upload)**: `aria-label="Upload compliance documents"`, `aria-describedby="file-requirements"`
- **Step 2 (Selection)**: `aria-label="Select frameworks for assessment"`, `role="listbox"`
- **Step 3 (Processing)**: `role="status"`, `aria-live="polite"` for progress updates
- **Step 4 (Results)**: `aria-label="Assessment results"`, `role="region"` for result cards

**Screen Reader Considerations**:

- Use semantic HTML: `<button>`, `<nav>`, `<main>`, `<aside>`
- Don't use `div` with `onclick` → Use `<button>`
- Loading states: Announce "Processing assessment" to screen readers
- Error messages: `role="alert"` for journey-blocking errors

**Testing Checklist**:

- [ ] All journey steps navigable with keyboard only
- [ ] Color contrast passes for all text/UI elements
- [ ] Screen reader announces journey progress
- [ ] Focus never trapped (can always Esc or Tab out)
- [ ] Error messages are announced and clear

### Step 8: Responsive Strategy & Breakpoints

Define responsive behavior based on which journey steps happen on mobile vs desktop:

**Journey Step Analysis**:

```
Which steps happen on mobile?
├─ ALL steps → Mobile-first approach
├─ First 1-2 steps → Progressive enhancement
└─ Desktop-only → Desktop-first (with mobile fallback)
```

**Compliance SaaS Example**:

- Step 1 (Upload): Mostly desktop (uploading large policy docs)
- Step 2 (Selection): Both (mobile for quick selections, desktop for detailed)
- Step 3 (Processing): Both (passive waiting)
- Step 4 (Results): Desktop-primary (reviewing detailed assessments)

**Decision: Desktop-first with mobile support for Steps 2-3**

**Breakpoint Philosophy**:

**Mobile-First** (progressive enhancement):

- Base styles: 320px+ (mobile)
- Tablet: 768px+ (add columns, expand spacing)
- Desktop: 1024px+ (full feature set)

**Desktop-First** (graceful degradation):

- Base styles: 1440px (desktop)
- Tablet: 1024px and down (simplify layouts)
- Mobile: 768px and down (single column, essential features)

**Responsive Component Behavior** (map to journey):

| Component          | Mobile Behavior                | Desktop Behavior    |
| ------------------ | ------------------------------ | ------------------- |
| File Upload        | Camera + file picker           | Drag-drop zone      |
| Framework Selector | Accordion (collapsed)          | Multi-column grid   |
| Progress Indicator | Full-width bar                 | Inline with details |
| Assessment Card    | Stack (single column)          | Grid (2-3 columns)  |
| Data Table         | Horizontal scroll OR card view | Full table          |
| Navigation         | Hamburger menu                 | Full horizontal nav |

**Responsive Patterns**:

1. **Information Density**:
   - Mobile: 1 key metric per screen
   - Desktop: Dashboard with 6-8 metrics

2. **Navigation**:
   - Mobile: Bottom tab bar (thumb-friendly)
   - Desktop: Sidebar or top nav

3. **Forms** (Step 1, 2):
   - Mobile: Full-width inputs, larger touch targets (44px min)
   - Desktop: Multi-column forms, keyboard shortcuts

4. **Data Display** (Step 4):
   - Mobile: Card-based list view
   - Desktop: Table with sorting/filtering

**Breakpoint Values** (choose based on journey):

```
Standard (B2B tools):
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1280px

Content-Heavy (documentation, reading):
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1440px (wider for readability)
```

### Step 9: Component Patterns & States (Compliance SaaS Examples)

Expand beyond basic components with real journey-specific patterns:

**1. File Upload Component (Step 1 - Upload Documents)**

States & Variants:

- **Default**: Drag-drop zone with "Upload policy documents" label
- **Dragging**: Border highlight, "Drop files here" feedback
- **Uploading**: Progress bar, filename, cancel button
- **Success**: Green checkmark, file size, "Upload another" action
- **Error**: Red border, "File too large (max 10MB)" message
- **Disabled**: Grayed out (when processing Step 3)

Design tokens:

- Border: 2px dashed, color: `gray-300` (default) / `blue-500` (dragging)
- Padding: `space-6` (48px) for large hit area
- Min height: 200px (easy targeting)

**2. Framework Selector (Step 2 - Choose Compliance Frameworks)**

Pattern: Multi-select checkbox grid with search

- **Component**: `<FrameworkCard>` with checkbox, logo, description
- **Layout**: CSS Grid, 3 columns (desktop) / 1 column (mobile)
- **States**:
  - Unselected: Gray border, `bg-white`
  - Hovered: Blue border, `shadow-sm`
  - Selected: Blue border, `bg-blue-50`, checkmark icon
  - Disabled: Grayed out (e.g., "Premium framework - Upgrade required")

Design considerations:

- Each card shows: Framework name, description (2 lines), estimated time
- Selected count: "3 frameworks selected" sticky header
- Quick filters: "Show all", "Popular", "My saved"

**3. Processing Status (Step 3 - AI Assessment)**

Pattern: Indeterminate → Determinate progress

- **Phase 1**: Spinner + "Initializing assessment..."
- **Phase 2**: Progress bar + "Analyzing documents (45% complete)"
- **Phase 3**: Status updates:
  - "Parsing policies..."
  - "Checking SOC 2 requirements..."
  - "Generating gap analysis..."
- **Complete**: Success animation → Auto-transition to Step 4

Design tokens:

- Progress bar: Height 8px, rounded, animated gradient
- Status text: `text-sm`, `text-gray-600`, updates every 2-3 seconds
- Container: `space-8` padding, centered on page

**4. Assessment Results Card (Step 4 - Review Results)**

Variant patterns:

- **Collapsed**: Framework name, overall score (83%), expand icon
- **Expanded**: Requirements list, gap analysis, action items
- **With Actions**: "Export PDF", "Share", "Start remediation"

Visual hierarchy:

- Score badge: Large (48px), color-coded (red <60%, yellow 60-80%, green >80%)
- Requirements: Nested checklist with icons (✓ pass, ⚠ partial, ✗ fail)
- Action buttons: Secondary (ghost), aligned right

**5. Empty States**

Journey-specific empty states:

- **No documents uploaded**: "Upload your first policy document to get started"
  - Illustration: Document icon
  - Primary CTA: "Upload document"
- **No frameworks selected**: "Select frameworks to assess compliance"
  - Helper text: "Popular: SOC 2, ISO 27001, GDPR"
- **Processing**: Not empty, but loading state
- **No results**: "Assessment complete - no gaps found!" (positive empty state)

## Generating the Output

Use `/templates/06-design-system-template.md`.

**Key Sections**:

1. **Design Philosophy** (derived from user context)
2. **Brand Personality** (based on journey context, not arbitrary)
3. **Color System** (with rationale)
4. **Typography** (with use case justification)
5. **Spacing System**
6. **Component Library** (journey-mapped)
   - For each key journey step, define needed components
   - Include states (default, hover, error, loading)
   - Interaction patterns
7. **Component-Journey Mapping** (table)
8. **Accessibility Standards**
9. **Responsive Behavior** (if multi-device)
10. **Design Decisions & Trade-offs** (what we didn't choose and why)

## Design Decisions: What We DIDN'T Choose (And Why)

Document the decisions you made and alternatives you rejected. This prevents future debates and explains the rationale:

**1. Styling Approach: Custom CSS-in-JS vs Tailwind vs Component Library**

**What we chose**: [Based on tech stack from Session 2]

Examples:

- **Tailwind CSS**: Utility-first, fast prototyping, small bundle
  - ✅ Choose if: Speed-focused, startup, small team
  - ❌ Avoid if: Need strict design consistency, complex themes

- **Styled Components / Emotion**: CSS-in-JS, component-scoped styles
  - ✅ Choose if: React-heavy, dynamic theming, complex logic
  - ❌ Avoid if: Concerned about runtime cost, server-side rendering

- **CSS Modules**: Scoped CSS, framework-agnostic
  - ✅ Choose if: Want traditional CSS, avoid JS dependencies
  - ❌ Avoid if: Need dynamic styles or theming

**Decision for Compliance SaaS**: Tailwind CSS

- Rationale: Fast iteration, design tokens via config, team familiar
- Trade-off: Less custom styling, utility class proliferation

**2. Design Tokens: Hard-coded vs Design Token System**

**What we chose**: Design token system (CSS variables or Tailwind config)

Why tokens matter:

- **With tokens**: Change `--color-primary` once → updates everywhere
- **Without tokens**: Find/replace 47 instances of `#3B82F6` (error-prone)

**Decision**: Tailwind theme config as source of truth

- Colors, spacing, typography defined centrally
- Can export to Figma tokens for designer handoff

**3. Component Library: MUI / Chakra / shadcn/ui vs Custom**

**Options**:

- **Material UI (MUI)**: Full component library, opinionated design
  - ✅ Choose if: Need rapid development, Material Design acceptable
  - ❌ Avoid if: Need custom brand, concerned about bundle size

- **Chakra UI**: Accessible, composable, flexible
  - ✅ Choose if: Accessibility priority, need flexibility
  - ❌ Avoid if: Don't need that many components

- **shadcn/ui**: Copy-paste components, full control
  - ✅ Choose if: Want control, can maintain components
  - ❌ Avoid if: Team too small to maintain

- **Custom Components**: Built from scratch
  - ✅ Choose if: Unique brand, specific needs, have design resources
  - ❌ Avoid if: Small team, tight timeline

**Decision for Compliance SaaS**: shadcn/ui + custom journey components

- Rationale: Flexibility for unique journey flows (upload, assessment)
- Use shadcn for generic (buttons, forms), custom for journey-specific
- Trade-off: More maintenance, but full control over critical path

**4. Icon System: Icon Font vs SVG Components vs Icon Library**

**Options**:

- **Heroicons / Lucide**: SVG component library
  - ✅ Choose if: React/Vue, want tree-shaking, modern approach
- **Font Awesome**: Icon font, wide selection
  - ✅ Choose if: Need huge variety, legacy compatibility
- **Custom SVG sprites**: Minimal, only icons you need
  - ✅ Choose if: Performance-critical, limited icon needs

**Decision**: Lucide React

- Rationale: Tree-shakeable, consistent style, good coverage
- Journey needs: Upload, check, alert, loading, download (~15 icons)

**5. Animation Strategy: Framer Motion vs CSS vs None**

**Philosophy**: Animations should serve journey clarity, not delight

**Decision**: Minimal CSS transitions + loading states

- Button hover: 150ms ease
- Modal enter/exit: 200ms fade
- Loading states: Spinner for <2s, progress bar for >2s
- **No** page transitions (distraction from workflow)
- **No** microinteractions (business tool, not consumer app)

Rationale: B2B users prioritize speed over delight

## Validation

- [ ] Design personality matches brand strategy from Session 5?
- [ ] Colors, typography, and visual style align with brand?
- [ ] Every component maps to a journey step?
- [ ] Information density matches user needs?
- [ ] Accessibility standards appropriate for industry?

## After Generation

```
✅ Session 6 complete! Design system created.

Your design brings your brand to life and optimizes for [journey context]:
- Brand Personality (from Session 5): [Attributes]
- Visual Expression: [Colors, typography aligned with brand]
- Key components for journey Step [X]
- Accessibility: [Standard]

File created: product-guidelines/06-design-system.md

Next, we'll design your database schema.

When ready, run: /design-database-schema
Or check progress: /cascade-status
```

## Reference

- Template: `/templates/06-design-system-template.md`
- Example: `/examples/compliance-saas/design/06-design-system.md`

---

**Now, create a design system optimized for this specific journey!**
