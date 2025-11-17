# User Journey: AI-Driven Document Pre-Assessment for TIC Industry

## Primary User Personas

### Project Handler (Daily User)
**Role**: Document coordinator at TIC (Testing, Inspection, Certification) notified bodies

**Context**:
- Collects documents from clients for certification assessments
- Runs 15-20 pre-assessments per day
- Currently outsources basic validation to India team ($100K/year, 1-2 day turnaround)
- Performance tracked by "clarification rounds" - fewer is better

**Current Pain Points**:
- **Speed**: 1-2 day wait for basic pre-check results blocks pipeline
- **Quality anxiety**: When errors slip through pre-check, creates embarrassing back-and-forth with Certification Person
- **No visibility**: Can't see validation happening, just waits for India team email
- **Cost**: $100K/year for 2-3 people in India doing basic checks

**Current Workaround**:
Email documents to India team → wait 1-2 days → receive results → fix issues → forward to Certification Person (often with additional clarifications needed)

**Success Criteria**:
- Pre-assessment results in <10 minutes instead of 1-2 days
- Evidence-based validation (shows WHERE in document issue exists)
- Zero false negatives (AI catches what India team would catch)
- Minimal false positives (AI doesn't flag issues that aren't real)
- Clean handoff to Certification Person with fewer clarification rounds

**Willingness to Pay**:
$30K/year per notified body (70% cost reduction + massive time savings)

**ROI Justification**:
- Direct savings: $100K → $30K = $70K/year
- Time savings: 1-2 days → 10 minutes = ~400x faster
- Indirect value: Fewer clarification rounds, faster certification pipeline
- **Value Ratio: ~3:1 in direct cost savings alone, 10x+ including time value**

---

### Process Manager (Power User)
**Role**: Quality gate owner who defines validation criteria

**Context**:
- Sets up validation workflows for different product types
- Starts with basic criteria, experiments and refines over time
- Responsible for ensuring AI validates relevant criteria without false positives

**Pain Points**:
- Current India team requires weeks to train on new criteria
- Hard to experiment and iterate on validation rules
- No visibility into which criteria actually improve quality vs create noise

**Success Criteria**:
- Create new validation workflow in <1 hour
- Easy to add/remove/refine criteria based on AI performance
- Can see which criteria catch real issues vs false positives

---

## Primary Job-to-Be-Done

**"When I** collect documents from clients and need to validate them against basic certification criteria, **I want to** run an AI pre-assessment that provides evidence-based pass/fail results in minutes, **so I can** fix issues immediately and forward clean documents to the Certification Person without embarrassing back-and-forth."

---

## Core User Flow (Happy Path)

### Step 1: Process Manager Creates Validation Workflow
**User Action**:
- Logs in, clicks "Create New Workflow"
- Names workflow (e.g., "Medical Device - Class II")
- Defines document buckets:
  - Bucket 1: "Technical Documentation" (required)
  - Bucket 2: "Test Reports" (required)
  - Bucket 3: "Risk Assessment" (optional)
- Adds criteria:
  - Criteria 1: "All documents must be signed" → applies to all buckets
  - Criteria 2: "Test report must include pass/fail summary" → applies to Bucket 2 only
  - Criteria 3: "Risk matrix must be complete" → applies to Bucket 3 only
- Saves workflow

**System Response**:
- Workflow saved, shareable link generated
- Shows preview: "3 document buckets (2 required, 1 optional), 3 validation criteria"

**User Emotion**: Confident - "This was fast and clear"

**Value Delivered**: Workflow ready to use in <30 minutes

**Potential Friction**:
- If criteria definition is unclear, AI won't validate correctly
- Mitigation: Simple text input + optional example document

**Metrics**: Time to create first workflow, criteria count per workflow

---

### Step 2: Project Handler Receives Workflow & Uploads Documents
**User Action**:
- Opens shared workflow link or selects from "My Workflows"
- Sees document buckets with clear labels (required vs optional)
- Drags/drops documents into each bucket:
  - Technical Documentation: uploads 3 PDFs
  - Test Reports: uploads 1 PDF
  - Risk Assessment: skips (optional)
- Clicks "Start Assessment"

**System Response**:
- Documents uploaded (progress indicator)
- "Assessment started - results in ~5-10 minutes"
- Email notification when complete

**User Emotion**: Relief - "Finally, no more waiting 2 days"

**Value Delivered**: Fast upload experience, clear expectations

**Potential Friction**:
- Large files slow upload
- Mitigation: Show progress, support common formats (PDF, DOCX)

**Metrics**: Documents uploaded per assessment, upload time, file sizes

---

### Step 3: AI Validates & Returns Evidence-Based Results ⭐ **AHA MOMENT**
**User Action**:
- Receives notification: "Assessment complete"
- Opens results page
- Sees criteria results with color coding:
  - ✅ GREEN: "Criteria 1: Signatures present - PASS"
  - ❌ RED: "Criteria 2: Test summary missing - FAIL → [Link: test-report.pdf, page 8]"
  - ✅ GREEN: "Criteria 3: Risk matrix complete - PASS"
- Clicks link to see exact location of issue in document
- Downloads summary report

**System Response**:
- Shows pass/fail per criteria with evidence (page number, section reference)
- Provides link directly to document location where issue exists
- Overall status: "2/3 criteria passed - review 1 issue before forwarding"

**User Emotion**: 🎯 **"IT ACTUALLY WORKS"** - AI found the exact issue with evidence

**Value Delivered**:
- **Functional**: 10 minutes instead of 1-2 days, exact location of issues
- **Emotional**: Confidence to fix issues before Certification Person sees them
- **Economic**: Avoids clarification rounds, speeds up pipeline

**Potential Friction**:
- False positives (AI flags non-issues) → destroys trust
- False negatives (AI misses issues) → embarrassment when Certification Person finds them
- Mitigation: Clear confidence levels, ability to provide feedback

**Metrics**:
- Assessment completion time
- Pass/fail ratio per criteria
- False positive/negative rate (feedback loop)

---

### Step 4: Project Handler Fixes Issues & Re-Runs Assessment
**User Action**:
- Opens flagged document (test-report.pdf, page 8)
- Sees missing summary section
- Contacts client: "Please add test summary on page 8"
- Receives updated document
- Replaces document in Bucket 2
- Clicks "Re-Run Assessment"

**System Response**:
- Re-runs validation in ~5 minutes
- Shows updated results: "3/3 criteria passed - All clear!"

**User Emotion**: Satisfaction - "Fixed it before Certification Person even saw it"

**Value Delivered**: Iterative validation, avoids back-and-forth later

**Potential Friction**:
- Having to re-upload all documents vs just the updated one
- Mitigation: Allow replacing individual documents

**Metrics**: Re-assessment rate, time to fix issues, clarification rounds avoided

---

### Step 5: Project Handler Forwards Clean Documents
**User Action**:
- Exports validation report (PDF)
- Uploads documents + report to internal project management tool
- Forwards to Certification Person with note: "Pre-check complete, all criteria passed"

**System Response**:
- Validation report includes:
  - All criteria checked
  - Pass/fail status with evidence
  - Timestamp, workflow version

**User Emotion**: Relief - "No clarifications needed this time"

**Value Delivered**: Confidence in handoff quality, fewer clarification rounds

**Potential Friction**: Manual copy between systems
- Mitigation: Export feature, potential API integration in future

**Metrics**: Documents forwarded, clarification rounds per assessment

---

## Value Definition

### Functional Value (Quantified)
- **Time saved**: 1-2 days → 10 minutes = ~400x faster per assessment
- **Cost saved**: $100K/year → $30K/year = $70K direct savings per notified body
- **Quality improved**: Fewer clarification rounds (measurable via internal tracking)
- **Scale**: 15-20 assessments/day × ~250 working days = 5,000 assessments/year processed faster

### Emotional Value
- **Confidence**: Project Handlers fix issues BEFORE Certification Person sees them
- **Control**: Can iterate immediately instead of waiting for India team
- **Pride**: Tracked performance improves (fewer clarification rounds)
- **Relief**: No more 2-day waits blocking the pipeline

### Economic Value
**Per Notified Body:**
- Direct cost savings: $70K/year
- Time value (15-20 assessments/day × 1.5 days saved × ~$500 opportunity cost): ~$1.8M/year in pipeline acceleration
- Certification Person time saved (fewer clarifications): TBD based on actual usage

**For SaaS Provider:**
- At $30K/year per customer × 10 notified bodies = $300K ARR
- At 20 customers = $600K ARR
- At 50 customers = $1.5M ARR
- Marginal cost per customer: AI inference tokens (~$1-5K/year)

**Value Ratio**:
- User pays $30K, saves $70K direct + time value → **10:1+ value ratio**

---

## Journey Metrics

### Awareness → Consideration
- TIC companies aware of AI pre-assessment alternatives
- Demo showcases: Workflow creation → Assessment results in <15 minutes
- KPI: Demo-to-trial conversion

### Consideration → Activation
- Sign up for trial account
- Create first validation workflow
- Run first assessment with sample documents
- KPI: Trial signup → First assessment completed (Target: <24 hours)

### Activation → Adoption
- Run 10+ assessments in first month
- Create 2+ validation workflows
- Process Manager refines criteria based on AI performance
- KPI: Weekly active users, assessments per week

### Adoption → Retention
- Consistently run assessments (daily usage for Project Handlers)
- Measurable reduction in clarification rounds
- Process Manager adds new workflows for different product types
- KPI: Monthly retention, NPS, clarification round reduction

### Success Indicators
- **Leading**: Assessment completion time <10 min, criteria pass rate, false positive/negative feedback
- **Lagging**: Clarification rounds reduced, Certification Person time saved, contract renewals

---

## Critical Success Factors for MVP

### Must Have (Core Value):
1. **Workflow creation**: Document buckets + criteria definition in <1 hour
2. **Document upload**: Drag-drop PDFs into buckets
3. **AI validation**: Binary pass/fail per criteria in <10 minutes
4. **Evidence-based results**: Link to exact location in document (page/section)
5. **Re-run capability**: Fix and re-validate quickly

### Should Have (Trust & Usability):
1. **Confidence levels**: Green (pass) / Red (fail) / Yellow (unclear)
2. **Feedback mechanism**: User can flag false positives/negatives
3. **Export report**: PDF summary of validation results
4. **Workflow sharing**: Link to share workflow with team

### Could Have (Future):
1. **Templates**: Pre-built workflows for common certification types
2. **Analytics**: Which criteria catch most issues, false positive rates
3. **Annotations**: Project Handler can add notes to flagged criteria
4. **API integration**: Connect to existing project management tools
5. **Multi-language**: Support for non-English documents

---

## Next Steps

With this user journey defined, the next sessions will determine:
- **Tech Stack** (Session 3): Optimized for fast PDF processing, AI inference, minimal deployment friction
- **Architecture** (Session 4): How to structure workflow engine, document processing pipeline, AI validation
- **Database Schema** (Session 7): How to store workflows, criteria, assessment results
- **API Contracts** (Session 8): Endpoints for workflow CRUD, assessment execution, results retrieval

The journey is clear: **Fast, evidence-based AI validation that saves time and embarrassment.**
