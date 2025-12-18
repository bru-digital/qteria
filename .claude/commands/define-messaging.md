---
description: POST-CASCADE - Create brand messaging framework and voice guidelines
---

# Define Brand Messaging (Post-Core Extension)

You are helping the user create a comprehensive brand messaging framework that communicates the value they deliver through their user journey.

## When to Use This

**Run AFTER `/create-brand-strategy`** when you have:

- ✅ User journey defined (`product-guidelines/00-user-journey.md`)
- ✅ Mission statement (`product-guidelines/03-mission.md`)
- ✅ Brand strategy (`product-guidelines/05-brand-strategy.md`)
- ✅ Brand name chosen (from `product-guidelines/brand-naming.md` or already decided)

Your messaging should communicate [journey value] in [brand voice], not be created in isolation.

**Skip this** if:

- You're building an internal tool without marketing needs
- You prefer to develop voice organically through content creation
- You don't need formal messaging documentation

## Cascade Inputs

This command READS previous outputs to create journey-grounded messaging:

1. **Read the user journey**:

   ```bash
   Read product-guidelines/00-user-journey.md
   ```

   - Who is the target audience? (from journey)
   - What problem do they struggle with?
   - What transformation do they experience?
   - What's the value delivered?

2. **Read the mission**:

   ```bash
   Read product-guidelines/03-mission.md
   ```

   - This becomes your value proposition foundation

3. **Read the brand strategy**:

   ```bash
   Read product-guidelines/05-brand-strategy.md
   ```

   - Brand voice (how you sound)
   - Brand values (what guides communication)
   - Brand personality (tone characteristics)

4. **Read the brand name** (if available):
   ```bash
   Read product-guidelines/brand-naming.md  # If naming was done
   ```

   - Use chosen name in messaging

Your messaging communicates [journey value] to [journey audience] in [brand voice].

## Your Task

Create a brand messaging framework that expresses the journey value in your brand voice.

### Steps to Execute

1. **FIRST: Read cascade inputs** (see "Cascade Inputs" section above):

   ```bash
   Read product-guidelines/00-user-journey.md
   Read product-guidelines/03-mission.md
   Read product-guidelines/05-brand-strategy.md
   Read product-guidelines/brand-naming.md  # If exists
   ```

2. **Read the template structure**:

   ```bash
   Read templates/16-brand-messaging-template.md
   ```

3. **Interview the user** with journey-informed questions:

   **Value Proposition (journey-based)**:
   - "Your mission is [mission]. How would you express this as a one-sentence value prop for [journey audience]?"

   **Elevator Pitch (journey-grounded)**:
   - "Let's create your elevator pitch. Start with: [Audience] struggles with [journey problem]. We help them [journey transformation] through [unique approach from brand strategy]."

   **Messaging Pillars (journey-connected)**:
   - "Your journey delivers value at [key moments]. What are the 3-5 core themes we should communicate about this value?"

   **Voice (brand-aligned)**:
   - "Your brand personality is [from brand strategy]. How should this show up in copy? Let's define specific do's and don'ts."

4. **Develop messaging framework** grounded in journey:
   - Value proposition = [Mission statement] for [journey audience]
   - Elevator pitch = [Journey problem] → [Journey solution] → [Journey value]
   - Messaging pillars = Key themes from [journey moments]
   - Voice guidelines = [Brand personality] applied to copy
   - EVERY element traces back to journey

5. **Create sample copy** that demonstrates journey value:
   - Homepage hero: Speaks to [journey problem], promises [journey value]
   - About us: Tells story of WHY you solve [journey problem]
   - Product description: Explains HOW you deliver [journey transformation]
   - All copy in [brand voice], addressing [journey audience]

6. **Write the output**:
   ```bash
   Write product-guidelines/16-brand-messaging.md
   ```

## Output Location

`product-guidelines/16-brand-messaging.md`

This will be read by:

- `/create-content-guidelines` - Uses messaging for detailed content style guide
- Marketing and content creation efforts
- Sales and customer support training

## Template Structure

The output follows this structure:

- Value Proposition (one-line promise)
- Target Audience (who we serve)
- Elevator Pitch (15-second, 30-second, 1-minute versions)
- Messaging Pillars (3-5 core themes)
- Voice Guidelines (how we sound)
- Tone Variations (adjusting for context)
- Sample Copy (real examples)
- Messaging Do's and Don'ts

## Key Principles

1. **Be specific** - "Fast and easy" is generic; "Deploy in 60 seconds" is specific
2. **Lead with benefit** - Customers care about outcomes, not features
3. **Be consistent** - Voice should be recognizable across channels
4. **Be authentic** - Don't fake a personality that doesn't match your values
5. **Test comprehension** - Can a stranger understand your value in 5 seconds?
6. **Show, don't tell** - Demonstrate voice through examples, not descriptions

## Example Prompt Flow

```
You: I've read your user journey, mission, brand strategy, and chosen name. Let me create messaging that expresses this journey value.

Your journey shows [audience] struggling with [problem] at [step]. You help them [transformation], and your brand personality is [traits].

Let's start with your value proposition. Your mission is "[mission]". How would you express this as one sentence for [audience]?

User: [Proposes value prop]

You: Great! That connects directly to the journey transformation. Now let's build your elevator pitch:

"[Audience] struggles with [journey problem]. [Brand name] helps them [journey transformation] through [unique approach from brand]. The result? [Journey value outcome]."

Does that feel right?

User: [Feedback]

[Continue developing messaging pillars, voice, sample copy...]

You: Perfect! Let me create sample copy that demonstrates this. Here's your homepage hero:

Headline: "[Speaks directly to journey problem]"
Subhead: "[Promises journey transformation in brand voice]"

Notice how it connects to [journey step] and speaks in [brand personality].

[Show more examples]

You: I've captured everything in product-guidelines/16-brand-messaging.md:
- Value proposition: "[specific one-liner tied to mission]"
- Elevator pitches (all grounded in journey)
- 4 messaging pillars (each connects to journey value)
- Voice guidelines (brand personality applied to copy)
- Sample copy for key scenarios (all journey-informed)

Every line traces back to your user journey. Try the homepage hero - does it speak to [journey audience]?
```

## After This Session

**Recommended next**:

- `/create-content-guidelines` - Detailed content style guide with journey-aligned messaging
- Apply messaging to website, product, and marketing materials

Your messaging framework expresses journey value in brand voice - grounded, not generic.

---

**Remember**: This is POST-CORE. Messaging communicates journey value, it doesn't precede it. Every message traces back to the user journey.
