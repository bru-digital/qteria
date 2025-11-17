# Design System: Compliance Assessment Platform

> **Context**: This is a completed example. Design derived from user journey context and brand needs.

---

## Design Philosophy

**Trust & Professionalism**: Compliance officers work in regulated, risk-averse environments. Design must communicate reliability, clarity, and authority.

**Efficiency Over Delight**: Users want to get work done quickly. Minimize friction, maximize clarity. No unnecessary animations or "delightful" interactions that slow down power users.

**Information Density**: Compliance officers review complex data. Design must present dense information clearly without overwhelming.

---

## Brand Personality (Derived from Journey Context)

**Primary Attributes**:
1. **Trustworthy**: Financial/healthcare compliance = high stakes
2. **Expert**: System is a compliance expert assistant
3. **Efficient**: Speed is core value proposition

**Secondary Attributes**:
4. **Modern**: But not trendy (classic modern, timeless)
5. **Accessible**: WCAG AA minimum (many enterprise customers require it)

**NOT**:
- ❌ Playful (wrong for compliance context)
- ❌ Minimalist to extreme (need information density)
- ❌ Cutting-edge/experimental (need stability)

---

## Color System

### Primary Palette

**Primary Blue** (Trust, authority):
- `blue-900`: #0F172A (Dark text, headers)
- `blue-700`: #1E40AF (Primary actions)
- `blue-500`: #3B82F6 (Links, interactive elements)
- `blue-100`: #DBEAFE (Light backgrounds, hover states)

**Semantic Colors**:
- `success-600`: #059669 (Passed assessments, positive actions)
- `warning-600`: #D97706 (Review needed, caution)
- `error-600`: #DC2626 (Failed checks, critical issues)
- `gray-500`: #6B7280 (Neutral, secondary info)

**Neutral Scale** (Tailwind default grays):
- White: #FFFFFF
- Gray-50 to Gray-900: Tailwind default scale

**Rationale**:
- Blue = trust, professionalism (finance/healthcare standard)
- High contrast for readability
- Semantic colors match compliance language (pass/fail/review)

### Background System

- `bg-white`: Primary surfaces (documents, cards)
- `bg-gray-50`: Secondary surfaces (page background)
- `bg-gray-100`: Tertiary surfaces (table rows, inputs)
- `bg-blue-50`: Highlighted sections (current assessment)

---

## Typography

### Font Families

**Headings & UI**: Inter (sans-serif)
- Professional, highly legible
- Excellent at all sizes
- Open source (Google Fonts)

**Body Text**: Inter (same for consistency)
- Reduces cognitive load
- Faster page loads (single font family)

**Monospace**: JetBrains Mono
- Code snippets, document IDs
- API documentation
- High legibility

**Rationale**: Single font family (Inter) simplifies system, loads faster, looks cohesive. Used by Stripe, GitHub, etc. - proven for B2B SaaS.

### Type Scale

```
text-xs: 12px (labels, metadata)
text-sm: 14px (body text, default UI)
text-base: 16px (emphasized body)
text-lg: 18px (section headers)
text-xl: 20px (card titles)
text-2xl: 24px (page titles)
text-3xl: 30px (hero headings - rare)
```

**Line Heights**:
- Headings: 1.2 (tight, impactful)
- Body: 1.5 (readable, standard)
- Dense data: 1.4 (tables, lists)

**Font Weights**:
- Regular (400): Body text
- Medium (500): Emphasized text
- Semibold (600): Buttons, labels
- Bold (700): Headings

---

## Spacing System

**Tailwind Default Scale** (4px base unit):
- `p-1`: 4px (tight spacing)
- `p-2`: 8px (compact spacing)
- `p-4`: 16px (default spacing)
- `p-6`: 24px (comfortable spacing)
- `p-8`: 32px (generous spacing)
- `p-12`: 48px (section spacing)

**Application**:
- Buttons: `px-4 py-2` (16px horizontal, 8px vertical)
- Cards: `p-6` (24px all around)
- Page margins: `px-8 py-6` (32px horizontal, 24px vertical)
- Section gaps: `gap-8` or `gap-12`

---

## Component Library (Journey-Mapped)

### Upload Zone (Journey Step 1)

**Design**:
```
┌─────────────────────────────────────┐
│  ⬆️                                 │
│  Drag PDF or click to upload       │
│  Max 50 MB • PDF, DOCX             │
└─────────────────────────────────────┘
```

**States**:
- Default: Dashed border (`border-dashed border-2 border-gray-300`)
- Hover: Blue border (`border-blue-500`)
- Dragging: Blue background (`bg-blue-50`)
- Uploading: Progress bar
- Success: Green checkmark, filename
- Error: Red border, error message

**Interaction**:
- Large click target (full area)
- Clear file type/size limits
- Immediate feedback on drop

### Framework Selector (Journey Step 2)

**Design**: Checkbox list with smart defaults

```
☑ SOC 2 Type II (recommended)
☑ GDPR (recommended)
☐ HIPAA
☐ PCI-DSS
☐ ISO 27001
```

**Features**:
- Pre-selected recommendations (based on document type)
- Expandable "Show all frameworks" (don't overwhelm)
- Search filter (for power users with many frameworks)

### Assessment Status (Journey Step 3)

**Design**: Progress indicator during processing

```
Assessing document...
[████████░░] 80%

Analyzing against SOC 2... ✓
Analyzing against GDPR... ⏳
Analyzing against HIPAA... ⏳

Estimated time: 25 seconds
```

**Features**:
- Real-time progress (polling every 2 seconds)
- Framework-level status (show which is processing)
- Time estimate (reduces anxiety)
- Cancellation option

### Results Display (Journey Step 4)

**Design**: Hierarchical findings list

```
┌─────────────────────────────────────────┐
│ SOC 2 Type II Assessment                │
│ ○ 3 Critical  ○ 5 Warning  ○ 12 Pass    │
├─────────────────────────────────────────┤
│ ⚠️ CRITICAL: Data encryption at rest   │
│ Section 4.2.1, Page 18                  │
│                                         │
│ "...data stored in plain text..."      │
│                                         │
│ Requirement: SOC 2 CC6.1                │
│ Recommendation: Implement AES-256...    │
│                                         │
│ [Mark as Resolved] [Add Note]           │
├─────────────────────────────────────────┤
│ ⚠️ WARNING: Access log retention...    │
│ ...                                     │
└─────────────────────────────────────────┘
```

**Features**:
- Color-coded severity (red/yellow/green)
- Expandable findings (default: show critical first)
- Document citations (section, page number)
- Direct quotes (evidence)
- Clear recommendations
- Action buttons (mark resolved, add notes)
- Filter by severity, framework, status

### Button Styles

**Primary Action** (main CTA):
```css
bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium
```

**Secondary Action**:
```css
bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 px-4 py-2 rounded-md font-medium
```

**Danger Action** (destructive):
```css
bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md font-medium
```

**Text Button** (low priority):
```css
text-blue-600 hover:text-blue-700 font-medium
```

### Cards

```css
bg-white border border-gray-200 rounded-lg p-6 shadow-sm
```

**Interactive Cards** (clickable):
```css
hover:shadow-md hover:border-blue-300 transition-all cursor-pointer
```

### Form Inputs

```css
border border-gray-300 rounded-md px-3 py-2 text-sm
focus:ring-2 focus:ring-blue-500 focus:border-blue-500
```

**Error State**:
```css
border-red-500 focus:ring-red-500 focus:border-red-500
```

---

## Interaction Patterns

### Loading States

**Skeleton Screens** (preferred over spinners):
- Show layout structure while loading
- Reduces perceived wait time
- Use for tables, cards, lists

**Spinners** (for indeterminate waits):
- Claude API processing (unknown duration)
- Button loading states (after click)

**Progress Bars** (for determinate waits):
- File uploads
- Multi-step processes

### Empty States

**First Time Use**:
```
📄 No assessments yet
Upload your first document to get started
[Upload Document]
```

**No Results**:
```
🔍 No findings in this category
All checks passed!
```

**Error State**:
```
⚠️ Assessment failed
We couldn't process this document.
[Try Again] [Contact Support]
```

### Feedback Mechanisms

**Success**: Toast notification (top-right, auto-dismiss 3s)
**Error**: Toast notification (top-right, manual dismiss)
**Info**: Inline banner (dismissible)
**Warning**: Inline banner with action (persistent until addressed)

---

## Accessibility Standards

**WCAG AA Compliance** (minimum):
- Color contrast: 4.5:1 for text, 3:1 for UI
- Keyboard navigation: All interactions keyboard-accessible
- Screen readers: Semantic HTML, ARIA labels
- Focus indicators: Visible focus states (ring-2 ring-blue-500)

**Additional Considerations**:
- No color-only information (use icons + color)
- Sufficient touch targets (min 44×44px)
- Clear error messages
- Skip navigation links

---

## Responsive Behavior

**Breakpoints** (Tailwind defaults):
- `sm`: 640px (mobile landscape)
- `md`: 768px (tablet)
- `lg`: 1024px (desktop)
- `xl`: 1280px (large desktop)

**Mobile-First Approach**:
- Default: Mobile layout (stack vertically)
- `md:`: Tablet layout (2-column grids)
- `lg:`: Desktop layout (sidebars, 3-column)

**Critical Journey Steps on Mobile**:
- Step 1 (Upload): Full-width, large touch target
- Step 2 (Frameworks): Scrollable list, large checkboxes
- Step 3 (Status): Full-width progress, clear updates
- Step 4 (Results): Stacked findings, expandable details

---

## Design Tokens (for Implementation)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          900: '#1E3A8A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

---

## Component-Journey Mapping

| Journey Step | Key Components | Design Priority |
|--------------|----------------|-----------------|
| 1. Upload | Upload zone, file list | Clarity, large targets |
| 2. Frameworks | Checkbox list, search | Smart defaults, fast selection |
| 3. Assessment | Progress indicator, status | Real-time feedback, time estimate |
| 4. Results | Findings cards, filters | Information density, scannability |
| 5. Export | Export button, preview | Professional output, shareability |

---

## Design System Documentation

**For Developers**:
- Storybook with all components
- Tailwind utility patterns documented
- Component props clearly defined
- Accessibility notes per component

**For Designers**:
- Figma library with all components
- Design tokens matched to Tailwind
- Interaction states documented
- Real content examples (not lorem ipsum)

---

**Next in Cascade**: Design system informs backlog (which components to build first, technical implementation tasks).
