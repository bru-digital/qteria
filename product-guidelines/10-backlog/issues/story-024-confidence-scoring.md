# [STORY-024] Confidence Scoring

**Type**: Story
**Epic**: EPIC-05 (AI Validation Engine)
**Journey Step**: Step 3 - Show AI Confidence Levels
**Priority**: P1 (Important for Trust)
**RICE Score**: 64 (R:80 × I:2 × C:80% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When AI is uncertain about findings, users need confidence indicators (green/yellow/red), so they know which results need manual verification.

**Value Delivered**: Transparent confidence scoring that builds trust by showing when AI is uncertain.

**Success Metric**: Confidence accuracy >90% (yellow results actually need review).

---

## Acceptance Criteria

- [ ] Parses Claude reasoning text for uncertainty markers
- [ ] Classifies confidence: high (green), medium (yellow), low (red)
- [ ] High: "definitely", "clear evidence", "explicit"
- [ ] Medium: "likely", "appears to", "suggests"
- [ ] Low: "unclear", "possibly", "not certain"
- [ ] Displays confidence in results UI
- [ ] Yellow confidence triggers "manual review recommended" flag

---

## Technical Approach

```python
def classify_confidence(reasoning: str, confidence_level: str) -> str:
    HIGH_MARKERS = ["definitely", "clear", "explicit", "unambiguous"]
    LOW_MARKERS = ["unclear", "possibly", "uncertain", "may be"]

    reasoning_lower = reasoning.lower()

    if confidence_level == "low" or any(m in reasoning_lower for m in LOW_MARKERS):
        return "low"  # Red
    elif any(m in reasoning_lower for m in HIGH_MARKERS):
        return "high"  # Green
    else:
        return "medium"  # Yellow
```

---

## Dependencies

- **Blocked By**: STORY-021 (Claude AI) - need reasoning text
- **Blocks**: STORY-027 (Results Display) - UI shows confidence

---

## Estimation

**Effort**: 2 person-days

---

## Definition of Done

- [ ] Confidence classification working
- [ ] Displayed in results UI (colors)
- [ ] Tests pass (classification accuracy)
- [ ] Code reviewed and merged

---

## Notes

- P1 priority - important for trust but not MVP blocker
- After completing, proceed to STORY-025 (Parallel Processing)
