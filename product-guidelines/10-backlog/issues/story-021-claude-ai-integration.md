# [STORY-021] Claude AI Integration

**Type**: Story
**Epic**: EPIC-05 (AI Validation Engine)
**Journey Step**: Step 3 - AI Validates Documents ⭐ **CORE VALUE**
**Priority**: P0 (MVP Critical - THE AHA MOMENT)
**RICE Score**: 48 (R:100 × I:3 × C:80% ÷ E:5)

---

## User Value

**Job-to-Be-Done**: When validating documents against criteria, the AI needs to analyze document text and return structured pass/fail results with evidence locations, so Project Handlers see "Test summary missing - FAIL → [page 8, section 3.2]".

**Value Delivered**: Core AI validation that delivers the product's primary value - evidence-based document validation 400x faster than manual review.

**Success Metric**: AI accuracy >95%, response time <30 seconds per criteria, validation completes in <10 minutes total.

---

## Acceptance Criteria

- [ ] Integrates Claude 3.5 Sonnet API (Anthropic)
- [ ] Validates each criteria against relevant documents
- [ ] Returns structured JSON: `{pass: bool, confidence: string, evidence_page: int, evidence_section: string, reasoning: string}`
- [ ] Handles API errors (timeout, rate limits, invalid response)
- [ ] Uses zero-retention API (data not stored by Anthropic)
- [ ] Prompt engineering optimized for accuracy
- [ ] Batches multiple criteria in single API call (performance optimization)
- [ ] Response time <30 seconds per criteria (P95)
- [ ] False positive rate <5%, false negative rate <1%

---

## Technical Approach

**Tech Stack Components**:
- AI: Claude 3.5 Sonnet via Anthropic API
- Prompt Engineering: Structured prompts with examples
- Error Handling: Retry logic, timeouts, fallbacks

**Claude Integration** (`app/services/claude_validator.py`):
```python
import anthropic
import os
import json
from typing import Dict

class ClaudeValidator:
    """Validate documents against criteria using Claude AI"""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    async def validate_criteria(
        self,
        criteria_name: str,
        criteria_description: str,
        document_text: List[Dict],  # From STORY-020
        document_name: str
    ) -> Dict:
        """
        Validate single criteria against document.

        Returns: {
            "pass": true/false,
            "confidence": "high"/"medium"/"low",
            "evidence_page": 8,
            "evidence_section": "3.2 Test Results",
            "reasoning": "Test report page 8..."
        }
        """
        # Build prompt with document context
        prompt = self._build_validation_prompt(
            criteria_name,
            criteria_description,
            document_text,
            document_name
        )

        # Call Claude API
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0,  # Deterministic for validation
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse JSON response
            result_text = response.content[0].text
            result = json.loads(result_text)

            return result

        except anthropic.APITimeoutError:
            raise ValidationError("Claude API timeout")
        except anthropic.RateLimitError:
            raise ValidationError("Claude API rate limit exceeded")
        except json.JSONDecodeError:
            raise ValidationError(f"Invalid JSON from Claude: {result_text}")

    def _build_validation_prompt(
        self,
        criteria_name: str,
        criteria_description: str,
        document_text: List[Dict],
        document_name: str
    ) -> str:
        """
        Build validation prompt with few-shot examples.
        """
        # Format document text with page/section markers
        formatted_doc = self._format_document(document_text)

        prompt = f"""You are a certification document validator for technical standards compliance (e.g., Machinery Directive, Medical Device Regulation).

Your task: Validate whether the document satisfies the given criteria.

**Criteria**: {criteria_name}
**Description**: {criteria_description}

**Document**: {document_name}
---
{formatted_doc}
---

**Instructions**:
1. Carefully read the document
2. Determine if the criteria is satisfied (PASS or FAIL)
3. Identify the EXACT location of evidence (page number + section name)
4. Assess your confidence (high/medium/low)
5. Provide clear reasoning

**Output Format** (JSON only, no markdown):
{{
  "pass": true or false,
  "confidence": "high" or "medium" or "low",
  "evidence_page": <page number where evidence found, or null if not found>,
  "evidence_section": "<section name where evidence found, or null>",
  "reasoning": "<explain what you found and where>"
}}

**Examples**:

Example 1 (PASS):
Criteria: "Test report must include pass/fail summary"
Document: [page 8, section 3.2 Test Results] "All tests passed. Summary: Test 1 PASS, Test 2 PASS..."
Output: {{"pass": true, "confidence": "high", "evidence_page": 8, "evidence_section": "3.2 Test Results", "reasoning": "Test report page 8 section 3.2 contains explicit pass/fail summary with clear results table."}}

Example 2 (FAIL):
Criteria: "Risk assessment must be present"
Document: [page 1-20] No mention of risk assessment or hazard analysis.
Output: {{"pass": false, "confidence": "high", "evidence_page": null, "evidence_section": null, "reasoning": "Searched entire document (20 pages). No risk assessment section found. Missing required element."}}

Example 3 (MEDIUM CONFIDENCE):
Criteria: "Manufacturer details must be correct"
Document: [page 2] "Manufactured by: ABC GmbH" but Directive requires full address.
Output: {{"pass": false, "confidence": "medium", "evidence_page": 2, "evidence_section": "1. Manufacturer", "reasoning": "Page 2 lists manufacturer name but missing required full address. Unclear if sufficient for compliance."}}

Now validate the criteria against the provided document."""

        return prompt

    def _format_document(self, document_text: List[Dict]) -> str:
        """Format parsed document for Claude"""
        formatted = []
        for page in document_text:
            header = f"[Page {page['page']}, Section: {page['section']}]"
            formatted.append(f"{header}\n{page['text']}\n")
        return "\n".join(formatted)
```

---

## Dependencies

- **Blocked By**: STORY-020 (PDF Parsing) - need parsed text
- **Blocks**: STORY-022 (Evidence Extraction) - validates evidence locations

---

## Estimation

**Effort**: 5 person-days

**Breakdown**:
- Claude API integration: 1 day
- Prompt engineering: 2 days (critical for accuracy)
- Error handling: 1 day
- Testing with real documents: 1 day

---

## Definition of Done

- [ ] Claude API integrated successfully
- [ ] Structured JSON responses validated
- [ ] Prompt optimized for >95% accuracy
- [ ] Error handling (timeouts, rate limits)
- [ ] Zero-retention API confirmed
- [ ] Response time <30 seconds
- [ ] Tested with 20 real documents
- [ ] False positive/negative rates measured
- [ ] Code reviewed and merged

---

## Testing Requirements

**Accuracy Tests** (20 real documents):
- [ ] 10 clear PASS cases → AI returns pass=true
- [ ] 10 clear FAIL cases → AI returns pass=false
- [ ] Measure false positives (<5%)
- [ ] Measure false negatives (<1%)

**Performance Tests**:
- [ ] Single criteria validation <30 seconds
- [ ] API timeout handling works

---

## Risks & Mitigations

**Risk**: AI accuracy <95%
- **Mitigation**: Extensive prompt engineering, few-shot examples, test with TÜV SÜD

**Risk**: Claude API downtime
- **Mitigation**: Retry logic, clear error messages

---

## Notes

- This is **THE CORE VALUE** story - AI validation is the product
- After completing, proceed to STORY-022 (Evidence Extraction)
