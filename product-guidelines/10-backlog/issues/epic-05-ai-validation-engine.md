# [EPIC-05] AI Validation Engine

**Type**: Epic
**Journey Step**: Step 3 - AI Validates & Returns Evidence-Based Results ⭐ **AHA MOMENT**
**Priority**: P0 (MVP Critical - Core Value Delivery)

---

## Epic Overview

This is the **most critical epic** - the core AI engine that validates documents against criteria and returns evidence-based pass/fail results in <10 minutes. This is **Journey Step 3 - the aha moment** where users see: "Criteria 2: Test summary missing - FAIL → [Link: test-report.pdf, page 8]".

**User Value**: Project Handlers get accurate, evidence-based validation in <10 minutes (vs. 1-2 days with India team), with exact page/section references proving AI found the issue.

---

## Success Criteria

- [ ] Assessment completes in <10 minutes (P95)
- [ ] AI validates each criteria against relevant documents
- [ ] Results include pass/fail + confidence (high/medium/low)
- [ ] Evidence includes page number + section reference
- [ ] AI accuracy >95% (false positive <5%, false negative <1%)
- [ ] Background job processing with retries
- [ ] User notified when assessment complete

---

## Stories in This Epic

### STORY-020: PDF Parsing with PyPDF2 [P0, 3 days]

Implement PDF text extraction using PyPDF2/pdfplumber, detect page boundaries, and identify sections (headings, numbering). Store parsed text in PostgreSQL for caching.

**RICE**: R:100 × I:3 × C:90% ÷ E:3 = **90**

### STORY-021: Claude AI Integration [P0, 5 days]

Integrate Claude 3.5 Sonnet API for document validation. Design prompts to return structured JSON with pass/fail, confidence, evidence_page, evidence_section, reasoning. Handle API errors and timeouts.

**RICE**: R:100 × I:3 × C:80% ÷ E:5 = **48** (High complexity, but critical)

### STORY-022: Evidence Extraction (Page/Section Links) [P0, 4 days]

Parse Claude AI response to extract evidence location (page number, section name) and validate against parsed PDF structure. Store evidence metadata in assessment_results table.

**RICE**: R:100 × I:3 × C:85% ÷ E:4 = **64**

### STORY-023: Background Job Queue (Celery + Redis) [P0, 3 days]

Set up Celery worker with Redis queue (Upstash) for async AI validation. Implement retry logic (3 attempts), timeout handling (15 min max), and job status tracking.

**RICE**: R:100 × I:3 × C:90% ÷ E:3 = **90**

### STORY-024: Confidence Scoring [P1, 2 days]

Classify AI responses into confidence levels (green/yellow/red) based on uncertainty markers in Claude's reasoning. Yellow = "AI unsure, manual review recommended".

**RICE**: R:80 × I:2 × C:80% ÷ E:2 = **64**

### STORY-025: Parallel Document Processing [P1, 2 days]

Process multiple documents in assessment concurrently (not sequential) to reduce validation time from 10 min → 5 min.

**RICE**: R:80 × I:2 × C:70% ÷ E:2 = **56**

### STORY-026: AI Response Caching [P1, 1 day]

Cache parsed PDF text in PostgreSQL. If same document uploaded again, skip parsing (save 10-20 seconds).

**RICE**: R:60 × I:1 × C:80% ÷ E:1 = **48**

---

## Total Estimated Effort

**20 person-days** (4 weeks for solo founder)

**Breakdown**:

- Backend: 15 days (PDF parsing, AI integration, evidence extraction, background jobs)
- Testing: 5 days (unit + integration + performance - 95% coverage required)

**Note**: This is the longest epic because it's the most complex and critical. AI validation accuracy is non-negotiable.

---

## Dependencies

**Blocks**:

- EPIC-06: Results Display (needs assessment results to show)
- EPIC-07: Re-assessment (needs working AI engine to re-run)

**Blocked By**:

- STORY-015: Document upload (needs documents to process)
- STORY-016: Start assessment (triggers AI validation)

---

## Technical Approach

**Tech Stack**:

- PDF Parsing: PyPDF2 + pdfplumber (Python)
- AI: Claude 3.5 Sonnet (Anthropic API with zero-retention)
- Background Jobs: Celery + Redis (Upstash)
- Caching: PostgreSQL (store parsed PDF text)

**AI Validation Flow**:

1. Celery worker receives assessment job
2. Fetch workflow (buckets + criteria) from PostgreSQL
3. Download documents from Vercel Blob
4. **Parse PDFs** (STORY-020):
   - Extract full text per page
   - Detect section boundaries (headings, numbering)
   - Store in memory + cache in PostgreSQL
5. **For each criteria** (STORY-021):
   - Build Claude prompt:

     ```
     Validate this document against the criteria:
     Criteria: "Test report must include pass/fail summary"
     Applies to: Test Reports bucket

     Document text: [extracted text from test-report.pdf]

     Return JSON:
     {
       "pass": true/false,
       "confidence": "high"/"medium"/"low",
       "evidence_page": 8,
       "evidence_section": "3.2 Test Results",
       "reasoning": "Test report page 8 section 3.2 contains pass/fail summary with clear results table."
     }
     ```

   - Call Claude API (POST https://api.anthropic.com/v1/messages)
   - Parse JSON response

6. **Extract evidence** (STORY-022):
   - Validate evidence_page exists in PDF
   - Validate evidence_section matches detected sections
   - Store in assessment_results table
7. **Update assessment status**: "completed"
8. **Send notification** (email or in-app)

**Confidence Scoring** (STORY-024):

- **High (green)**: Claude says "definitely", "clear evidence", "explicit statement"
- **Medium (yellow)**: Claude says "likely", "appears to", "suggests"
- **Low (red)**: Claude says "unclear", "possibly", "not certain"

**Performance Optimization** (STORY-025):

- Process all documents in parallel (not sequential)
- Batch criteria checks in single Claude prompt (reduce API calls 10 → 1)

**Reference**: `product-guidelines/02-tech-stack.md` (Claude), `product-guidelines/04-architecture.md` (Step 3 flow)

---

## Success Metrics

**Performance** (Critical):

- Assessment completion time P95: <10 minutes (target)
- PDF parsing time (10MB): <5 seconds
- Claude API response time P95: <30 seconds per criteria

**Accuracy** (Critical):

- False positive rate: <5% (AI flags non-issue)
- False negative rate: <1% (AI misses real issue)
- User trust score: >95% (users trust AI results)

**Reliability**:

- Background job success rate: >98% (retry logic handles failures)
- Assessment completion rate: >95% (not abandoned mid-process)

---

## Definition of Done

- [ ] PDF parsing extracts text and sections accurately
- [ ] Claude API integration returns structured JSON
- [ ] Evidence extraction validates page/section references
- [ ] Background jobs process assessments reliably
- [ ] Confidence scoring classifies responses (green/yellow/red)
- [ ] Parallel processing reduces time <10 min
- [ ] Caching skips re-parsing same documents
- [ ] Error handling: retries, timeouts, clear failure messages
- [ ] Performance benchmarks met (<10 min P95)
- [ ] AI accuracy tested with real documents (>95%)
- [ ] Code coverage >95% (critical business logic)
- [ ] Code reviewed and merged to main

---

## Risks & Mitigations

**Risk**: Claude API accuracy <95% (false positives/negatives)

- **Mitigation**: Extensive prompt engineering, test with real TÜV SÜD documents, feedback loop for improvement

**Risk**: PDF parsing fails (section detection unreliable)

- **Mitigation**: Use multiple libraries (PyPDF2 + pdfplumber), fallback to page-only if sections unclear

**Risk**: Background jobs timeout (>15 min processing)

- **Mitigation**: Parallel processing, batch criteria checks, timeout handling with retry

**Risk**: Claude API downtime (assessments fail)

- **Mitigation**: Retry logic (3 attempts), clear error messages, queue jobs for later retry

---

## Testing Requirements

**Unit Tests** (95% coverage required):

- [ ] PDF text extraction (various formats)
- [ ] Section detection algorithm
- [ ] Claude prompt building
- [ ] Evidence extraction logic
- [ ] Confidence scoring classification

**Integration Tests** (90% coverage required):

- [ ] End-to-end: PDF → Claude API → Evidence → Results
- [ ] Celery job execution and retry logic
- [ ] Error handling (Claude timeout, invalid PDF, malformed JSON)
- [ ] Caching (same document skips re-parsing)
- [ ] Parallel processing (multiple docs processed concurrently)

**Performance Tests** (benchmarks):

- [ ] PDF parsing (10MB): <5 seconds
- [ ] Claude API call: <30 seconds
- [ ] Complete assessment (3 docs, 5 criteria): <10 minutes P95
- [ ] Parallel processing 2x faster than sequential

**Accuracy Tests** (real documents):

- [ ] Test with 20 real TÜV SÜD documents
- [ ] Measure false positive/negative rates
- [ ] Target: >95% accuracy

---

## Next Epic

After completing this epic, proceed to **EPIC-06: Results & Evidence Display** to show AI validation results beautifully with clickable evidence links.
