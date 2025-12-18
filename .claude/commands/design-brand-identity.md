---
description: POST-CASCADE - Design comprehensive brand identity (logo, visual system, guidelines)
---

# Design Brand Identity (Post-Core Extension)

You are helping the user design a comprehensive visual brand identity including logo concepts, brand marks, visual assets, and usage guidelines. This identity expresses the brand strategy through visual design.

## When to Use This

**Run AFTER `/create-brand-strategy`** (Session 5) when you have:

- ✅ User journey defined (`product-guidelines/00-user-journey.md`)
- ✅ Brand strategy established (`product-guidelines/05-brand-strategy.md`)
- ✅ Design system created (`product-guidelines/06-design-system.md`) - recommended but optional
- ✅ Brand name chosen (from `product-guidelines/brand-naming.md` or already decided) - optional but helpful

Your visual identity should express the brand personality and values defined in your brand strategy, not be created in a vacuum.

**Skip this** if:

- You already have an established logo and visual identity
- You're building an internal tool without branding needs
- You plan to hire a professional designer (though this can serve as a creative brief)

## Cascade Inputs

This command READS previous outputs to create journey-grounded visual identity:

1. **Read the user journey**:

   ```bash
   Read product-guidelines/00-user-journey.md
   ```

   - Who is the target audience? (influences aesthetic)
   - What problem domain? (industry conventions vs. disruption)
   - What emotions should the brand evoke?

2. **Read the brand strategy**:

   ```bash
   Read product-guidelines/05-brand-strategy.md
   ```

   - Brand personality (professional/playful, serious/friendly, etc.)
   - Brand values (what guides design decisions)
   - Visual direction (color preferences, mood, aesthetic)
   - Brand differentiation (how to stand apart visually)

3. **Read the design system** (if exists):

   ```bash
   Read product-guidelines/06-design-system.md
   ```

   - Color palette (brand colors to incorporate)
   - Typography (font choices for logo/brand materials)
   - Design philosophy (visual principles)

4. **Read the brand name** (if exists):

   ```bash
   Read product-guidelines/brand-naming.md
   ```

   - Chosen name to incorporate into logo
   - Name meaning and associations

Your visual identity expresses [brand personality] to [journey audience] through design.

## Your Task

Create a comprehensive brand identity system including logo concepts, visual assets, and usage guidelines.

### Steps to Execute

1. **FIRST: Read cascade inputs** (see "Cascade Inputs" section above):

   ```bash
   Read product-guidelines/00-user-journey.md
   Read product-guidelines/05-brand-strategy.md
   Read product-guidelines/06-design-system.md  # If exists
   Read product-guidelines/brand-naming.md   # If exists
   ```

2. **Read the template structure**:

   ```bash
   Read templates/17-brand-identity-template.md
   ```

3. **Analyze brand personality for visual expression**:

   From brand strategy, identify:
   - **Personality traits**: Professional? Playful? Trustworthy? Innovative?
   - **Core values**: What must the visual identity communicate?
   - **Target audience**: Who needs to connect with this brand?
   - **Differentiation**: How to stand apart visually in the market?

4. **Logo Design Decision Tree**:

   **Logo Type Selection**:

   ```
   What best expresses the brand personality?

   ├─ Wordmark (text-only logo)
   │  ├─ ✅ Choose if: Name is distinctive, brand values clarity/directness
   │  ├─ ✅ Choose if: B2B/professional context, trust is key
   │  └─ Examples: Google, FedEx, Coca-Cola
   │
   ├─ Lettermark (initials/acronym)
   │  ├─ ✅ Choose if: Long name needs abbreviation
   │  ├─ ✅ Choose if: International audience (minimize language barriers)
   │  └─ Examples: IBM, HP, NASA
   │
   ├─ Icon + Wordmark (combination mark)
   │  ├─ ✅ Choose if: Want visual + text recognition
   │  ├─ ✅ Choose if: Need versatility (icon alone or with text)
   │  └─ Examples: Adidas, Burger King, Lacoste
   │
   ├─ Abstract Symbol
   │  ├─ ✅ Choose if: Creating new meaning/category
   │  ├─ ✅ Choose if: Global brand with ambition for iconic status
   │  └─ Examples: Nike, Pepsi, Airbnb
   │
   └─ Pictorial Mark (literal icon)
      ├─ ✅ Choose if: Industry/category needs instant recognition
      ├─ ✅ Choose if: Icon reinforces brand story
      └─ Examples: Apple, Twitter, Target
   ```

   **Decision criteria**:
   - **Trustworthy + Professional** → Wordmark with solid, classic typography
   - **Playful + Creative** → Icon + wordmark with custom illustration
   - **Technical + Efficient** → Lettermark or geometric abstract symbol
   - **Innovative + Disruptive** → Abstract symbol or unexpected pictorial mark

5. **Interview the user** with journey-informed questions:

   **Visual Direction**:
   - "Your brand personality is [traits from brand strategy]. Should your logo be minimalist/complex, geometric/organic, modern/classic?"

   **Color Strategy**:
   - "Your brand values [values]. What emotions should the colors evoke? Should we follow industry conventions (trust = blue in finance) or disrupt them?"

   **Typography Direction**:
   - "Should the logo typography be serif (traditional, trustworthy) or sans-serif (modern, clean)? Custom or standard font?"

   **Symbolism** (if using icon):
   - "What visual metaphors connect to [journey value]? What should the icon communicate at a glance?"

   **Differentiation**:
   - "I've analyzed your competitors from the product strategy. They use [common patterns]. Should we follow conventions for category recognition, or differentiate boldly?"

6. **Generate 3-5 logo concepts**:

   For each concept, provide:
   - **Visual description**: Detailed description of the logo design
   - **Rationale**: How it expresses brand personality and journey value
   - **Logo type**: Wordmark, lettermark, combination, etc.
   - **Color application**: How brand colors are used
   - **Typography**: Font choice and why it fits
   - **Versatility**: How it scales (favicon, billboard, mobile app icon)
   - **Differentiation**: How it stands apart from competitors

   **Concept diversity**: Generate different approaches:
   - Concept A: Conservative/safe (industry-appropriate)
   - Concept B: Balanced (brand personality + recognition)
   - Concept C: Bold/distinctive (maximum differentiation)
   - Concepts D-E: Variations exploring different visual metaphors

7. **What We DIDN'T Choose (And Why)**:

   Document design decisions:

   **Logo Type Not Chosen**:
   - "Didn't choose abstract symbol because brand is new and needs name recognition"
   - "Avoided pictorial marks because [journey value] is abstract, not a physical thing"
   - "Decided against lettermark because full name is short and memorable"

   **Visual Style Not Chosen**:
   - "Avoided gradients and complexity because brand values clarity and simplicity"
   - "Didn't use illustration style because B2B audience expects professionalism"
   - "Decided against vintage aesthetic because innovation is core to brand"

   **Color Decisions**:
   - "Avoided blue (despite industry norm) because brand differentiates through [personality]"
   - "Didn't use bright colors because audience is [demographic] in [industry] expecting [tone]"
   - "Chose [color] over [color] because it better expresses [brand value from strategy]"

8. **Create comprehensive brand identity system**:

   **Primary Logo**:
   - Full color version
   - Single color version
   - Reversed (light on dark)
   - Minimum size specifications

   **Logo Variations**:
   - Horizontal layout
   - Stacked/vertical layout
   - Icon only (for app icons, favicons)
   - Simplified version (for small sizes)

   **Color Palette Application**:
   - Primary brand color(s) and usage
   - Secondary colors for variety
   - Accent colors for CTAs/highlights
   - Neutral colors for backgrounds/text
   - Color codes: HEX, RGB, CMYK (print), Pantone (if needed)

   **Typography System**:
   - Primary brand font (logo, headlines)
   - Secondary font (body copy)
   - Font weights and when to use
   - Typographic hierarchy

   **Visual Elements**:
   - Patterns or textures (if applicable)
   - Iconography style
   - Photography/illustration style
   - Graphic elements (shapes, lines, etc.)

   **Usage Guidelines**:
   - Logo clearspace (minimum space around logo)
   - Incorrect logo usage (don't stretch, don't change colors, etc.)
   - Backgrounds: approved colors/images for logo placement
   - Accessibility: color contrast requirements
   - File formats: SVG (web), PNG (transparency), JPG, PDF (print)

9. **Brand Applications** (examples of identity in use):

   Show how the identity appears across touchpoints:
   - **Digital**: Website header, mobile app icon, social media avatars
   - **Marketing**: Business cards, presentations, email signatures
   - **Product**: App UI, dashboard, loading screens
   - **Collateral**: Pitch decks, one-pagers, reports

   For each application, describe:
   - How the logo is used
   - Which color palette elements appear
   - How it reinforces brand personality

10. **Journey-Brand Alignment Check**:

    Validate that visual identity serves the user journey:
    - Does the logo communicate [journey value] visually?
    - Does the aesthetic fit [target audience] expectations?
    - Does the personality expressed match [brand strategy]?
    - Can users recognize and remember this identity?
    - Does it differentiate from competitors solving [journey problem]?

11. **Write the output**:
    ```bash
    Write product-guidelines/17-brand-identity.md
    ```

## Output Location

`product-guidelines/17-brand-identity.md`

This will be read by:

- `/create-content-guidelines` - Uses identity for visual content standards
- Design and marketing teams - Implementation reference
- External vendors - Design brief for assets
- Future branding decisions - Source of truth for visual identity

## Template Structure

The output follows this structure:

- **Brand Identity Overview** (purpose, brand personality expressed)
- **Logo Concepts** (3-5 concepts with rationale)
- **Recommended Logo** (primary choice and why)
- **Logo System** (variations, sizes, formats)
- **Color Palette Application** (brand colors in use)
- **Typography System** (fonts and usage)
- **Visual Elements** (patterns, iconography, photography style)
- **Usage Guidelines** (do's and don'ts)
- **Brand Applications** (examples across touchpoints)
- **What We DIDN'T Choose** (alternatives and reasoning)

## Key Principles

1. **Express brand personality** - Every design choice traces to brand strategy
2. **Serve the journey** - Visual identity should appeal to target audience
3. **Be versatile** - Logo must work at all sizes and contexts
4. **Be memorable** - Distinctive enough to stand out and be recalled
5. **Be timeless** - Avoid trends that will date quickly
6. **Be scalable** - Must work as favicon (16px) and billboard (huge)

## Example Prompt Flow

```
You: I've read your brand strategy and user journey. Your brand personality is [traits], your audience is [description], and you deliver [journey value].

Let me design a visual identity that expresses this. First, should your logo be a wordmark (text only), combination mark (icon + text), or symbol?

Your brand values [value] and your audience is [audience type]. Let me explain the trade-offs...

User: [Chooses direction]

You: Perfect. Now, your brand strategy says the visual direction is [from strategy]. Should we follow industry conventions (like blue for trust in fintech) or differentiate boldly?

User: [Explains preference]

You: Excellent. Let me generate 3-5 logo concepts that express [brand personality] for [journey audience]. Each concept will take a different approach - conservative, balanced, and bold.

[Generate concepts with detailed descriptions and rationale]

You: Here are 5 concepts:
1. [Concept A] - Conservative wordmark, expresses [value], safe industry fit
2. [Concept B] - Combination mark, balances recognition + personality
3. [Concept C] - Bold abstract symbol, maximum differentiation
4. [Concept D] - [Alternative exploration]
5. [Concept E] - [Alternative exploration]

Which direction resonates? We can refine any of these.

User: [Provides feedback]

You: Great! I'll develop [chosen concept] into a complete brand identity system with color applications, typography, usage guidelines, and examples across touchpoints.

[Create comprehensive identity system]

You: I've created your complete brand identity system in product-guidelines/17-brand-identity.md:

✅ Logo system (primary + variations)
✅ Color palette application
✅ Typography standards
✅ Visual elements and patterns
✅ Usage guidelines (do's and don'ts)
✅ Brand applications (digital, marketing, product)
✅ Alternatives we didn't choose (and why)

Every design decision traces back to your brand strategy: [key connections]

File created: product-guidelines/17-brand-identity.md

This visual identity expresses [brand personality] and will help [journey audience] recognize and trust your brand.
```

## After This Session

**Recommended next**:

- `/create-content-guidelines` (Session extends) - Uses brand identity for content standards
- `/define-messaging` (if not done) - Messaging framework with identity in mind
- Designer handoff - Use this as creative brief for professional design

**Optional**:

- Work with designer to create actual logo files (SVG, PNG, etc.)
- Create brand guidelines presentation/PDF
- Design additional brand assets (patterns, illustrations, etc.)

## What We DIDN'T Choose (And Why)

**Approach 1: AI-Generated Logo Images**

- **Why not**: Claude Code focuses on strategy and description, not pixel-perfect design execution
- **When to reconsider**: If AI image generation is integrated and user requests visual mockups
- **Instead**: Provide detailed descriptions that serve as design briefs

**Approach 2: Require Professional Designer First**

- **Why not**: Not all products need expensive design work upfront; strategic thinking comes first
- **When to reconsider**: For consumer brands where visual identity is core differentiator
- **Instead**: Create comprehensive design brief that CAN be handed to designer or executed by team

**Approach 3: Focus Only on Logo, Skip Full Identity System**

- **Why not**: Logo alone isn't enough - need colors, typography, usage guidelines
- **When to reconsider**: Never - comprehensive identity prevents inconsistent brand application
- **Instead**: Full identity system ensures brand consistency across all touchpoints

**Approach 4: Generate Generic "Modern Tech" Aesthetic**

- **Why not**: Visual identity must be grounded in specific brand strategy and journey
- **When to reconsider**: Never - generic branding doesn't differentiate or serve journey
- **Instead**: Every design choice traces to brand personality, audience, and journey value

## Validation Checklist

- [ ] Logo concepts express brand personality from Session 5?
- [ ] Visual identity serves target audience from user journey?
- [ ] Color palette aligns with brand strategy visual direction?
- [ ] Typography choices support brand personality?
- [ ] Logo works at all sizes (favicon to billboard)?
- [ ] Usage guidelines prevent incorrect application?
- [ ] Brand applications show identity across touchpoints?
- [ ] "What We DIDN'T Choose" documents alternatives?
- [ ] Every design decision traces to brand strategy or journey?

## Reference

- Template: `/templates/brand-identity-template.md`
- Example: `/examples/compliance-saas/branding/` (if available)
- Related: `product-guidelines/05-brand-strategy.md` (conceptual foundation)
- Related: `product-guidelines/06-design-system.md` (UI implementation)
- Related: `product-guidelines/brand-naming.md` (name to incorporate)

---

**Now, create a visual brand identity that expresses your journey value!**
