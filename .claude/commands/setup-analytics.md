---
description: POST-CASCADE - Create detailed analytics implementation plan
---

# Setup Analytics (Post-Cascade Optional)

You are helping the user create a comprehensive analytics implementation plan including event tracking, funnels, dashboards, and tooling. This expands on the metrics defined in Session 3.

## When to Use This

**Run AFTER Session 3** (`/generate-strategy`) if:

- You've defined North Star and success metrics
- You're ready to implement analytics tracking
- You need detailed event taxonomy and tracking plan

**Difference from Session 3**:

- **Session 3**: Defines WHAT to measure (North Star, input metrics, health metrics) - the strategy
- **This command**: Defines HOW to measure (events, properties, funnels, dashboards, tools) - the implementation
- **Both complement**: Session 3 is "what success looks like", this is "how to track it"

**Skip this** if:

- You're pre-launch and don't need analytics yet
- You have a data team that handles this
- You prefer to add analytics incrementally

## Your Task

Create a comprehensive analytics implementation plan using the prompt in `/prompts/analytics/metrics.md`.

### Steps to Execute

1. **Read the analytics prompt**:

   ```bash
   Read /prompts/analytics/metrics.md
   ```

2. **Read the template structure**:

   ```bash
   Read templates/20-analytics-plan-template.md
   ```

3. **Check for metrics from Session 3** (required):

   ```bash
   Read product-guidelines/03-metrics.md
   ```

   - North Star metric
   - Input metrics
   - Health metrics
   - Guardrail metrics

4. **Check for user journey** (recommended):

   ```bash
   Read product-guidelines/00-user-journey.md
   ```

   - Identify key moments to track

5. **Interview the user** following the analytics prompt:
   - **Current state**: What analytics do you have now? Gaps?
   - **Event taxonomy**: How will you name events? Naming convention?
   - **User identification**: Anonymous tracking? User IDs? Cross-device?
   - **Event tracking plan**: Which events? Which properties?
   - **Funnels**: What conversion paths to track?
   - **Cohorts**: How to segment users?
   - **Dashboards**: What views do different roles need?
   - **A/B testing**: What hypotheses to test?
   - **Tools**: What analytics stack? (Amplitude, Mixpanel, Segment, etc.)
   - **Privacy**: GDPR, CCPA compliance? Consent management?

6. **Develop analytics plan**:
   - Event taxonomy (naming conventions, structure)
   - Event tracking plan (30-50 events with properties)
   - User properties (demographics, firmographics, behavior)
   - Funnels (5-10 conversion paths)
   - Cohort definitions (10-15 segments)
   - Dashboard specs (exec, product, growth, eng)
   - AARRR metrics mapping (acquisition → retention → revenue)
   - A/B testing roadmap
   - Tool recommendations with setup guide
   - Privacy and compliance requirements
   - Implementation priorities (phase 1, 2, 3)

7. **Write the output**:
   ```bash
   Write product-guidelines/20-analytics-plan.md
   ```

## Output Location

`product-guidelines/20-analytics-plan.md`

This will be used by:

- Engineers implementing event tracking
- Product managers analyzing user behavior
- Growth teams optimizing conversion
- Executives monitoring North Star metric
- Data teams building dashboards

## Template Structure

The output follows this structure:

- Analytics Strategy (how this implements metrics from Session 3)
- Event Taxonomy (naming conventions, categories)
- Event Tracking Plan (detailed event spec table)
- User Properties (demographics, behavior, firmographics)
- Funnels and Conversion Paths
- Cohort Definitions
- Dashboard Specifications
- AARRR Metrics Mapping
- A/B Testing Roadmap
- Tool Recommendations
- Privacy and Compliance
- Implementation Roadmap (phased approach)

## Key Principles

1. **Start with metrics** - Every event should map to a metric from Session 3
2. **Be consistent** - Strict naming conventions prevent chaos
3. **Track generously** - Easier to ignore data than to add tracking retroactively
4. **Think in funnels** - User journeys are conversion paths
5. **Segment everything** - Cohort analysis reveals insights
6. **Build for self-service** - Dashboards should answer questions without SQL
7. **Privacy by design** - Compliance isn't optional

## Example Prompt Flow

```
You: Let's setup your analytics. First, let me check your metrics from Session 3...

[Read product-guidelines/03-metrics.md]

You: Perfect! Your North Star is [metric] and you have [X] input metrics. Now, what analytics do you currently have? Google Analytics? Custom events? Nothing?

User: [Describes current state]

You: Got it. Let's build a proper event tracking plan. First, naming convention. Do you prefer:
- `snake_case` (user_signed_up)
- `Proper Case` (User Signed Up)
- `Object Action` (User Signed Up)
- `Action Object` (Signed Up User)

User: [Chooses convention]

You: Perfect. Now let's map your user journey to events. Looking at your journey, the critical moments are [X, Y, Z]. Let's define events for each...

[Walk through journey]

You: Great. That's 15 core events. Now let's think about properties. For "User Signed Up", what context matters? Source? Plan? Team size?

User: [Describes properties]

You: Excellent. Now let's define your funnels. Your North Star is [metric], so the conversion path is: [step 1] → [step 2] → [step 3]. What are the 5 most important funnels to track?

User: [Lists funnels]

You: Perfect. What about cohorts? How do you segment users? By plan? By behavior? By acquisition source?

User: [Describes segments]

You: Great. Now dashboards. What do you need to see daily? Weekly? What does your CEO need to see? Your growth team?

User: [Describes dashboard needs]

You: And for tools - are you already using something? Amplitude? Mixpanel? Segment? Or starting from scratch?

User: [Describes tool preferences]

[Continue through A/B testing, privacy, implementation phases...]

You: Excellent! I've created your comprehensive analytics plan in product-guidelines/20-analytics-plan.md:
- Event taxonomy with strict naming conventions
- 42 events with detailed properties
- 12 user properties
- 7 conversion funnels
- 14 cohort definitions
- 4 dashboard specs (exec, product, growth, eng)
- AARRR metrics mapping
- A/B testing roadmap (8 experiments)
- Tool recommendation: [Segment + Amplitude] with setup guide
- Privacy compliance checklist
- 3-phase implementation plan

Phase 1 focuses on your North Star and core input metrics. Ready to start implementing?
```

## After This Session

**Use this document**:

- When writing tracking code
- When building dashboards
- When analyzing user behavior
- When planning experiments

**Implementation priority**:

1. **Phase 1**: North Star metric and core user journey (Week 1-2)
2. **Phase 2**: Input metrics and funnels (Week 3-4)
3. **Phase 3**: Advanced cohorts and experiments (Week 5+)

---

**Remember**: This is OPTIONAL but highly recommended. Good analytics = good decisions. Start with phase 1 and expand over time.
