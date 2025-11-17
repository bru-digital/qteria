# User Journey: Compliance Document Assessment Platform

> **Context**: This is a completed example from the Stack-Driven cascade. Your journey will be different!

---

## Primary User Persona

### Compliance Officer Clara

**Role**: Mid-level compliance officer at regulated financial services firm
**Context**: Reviews 20-50 regulatory documents monthly
**Pain Points**:
1. Spends 2-4 hours reading each document to identify relevant sections
2. Must cross-reference against 15+ different regulatory frameworks
3. Under pressure to approve documents quickly to avoid business delays
4. Risks missing critical non-compliance issues

**Current Workarounds**:
- Manual reading with ctrl+F searching
- Spreadsheet tracking of requirements
- Email chains with legal team for clarifications

**Success Looks Like**:
- Assess document compliance in <10 minutes instead of hours
- Confidence in identifying 95%+ of relevant issues
- Clear audit trail for regulatory inspection

**Willingness to Pay**: $200-500/month per user (time savings justify 10x+ ROI)

---

## Primary Job-to-Be-Done

When I receive a complex regulatory document,
I want to instantly understand its compliance status against relevant frameworks,
so I can approve it confidently or request specific changes without manual review.

---

## Core User Flow (Happy Path)

### Step 1: Upload Document
- **User Action**: Drags PDF document into upload zone
- **System Response**: Instantly uploads to S3, extracts text, identifies document type
- **User Feels**: Confident (system recognizes document type)
- **Value Delivered**: Document processed in <5 seconds
- **Potential Friction**: Large files (100+ pages), scanned PDFs with poor OCR
- **Success Metric**: 95% of uploads succeed on first try

### Step 2: Select Frameworks
- **User Action**: Checks relevant compliance frameworks (SOC2, GDPR, PCI-DSS, etc.)
- **System Response**: Shows recommended frameworks based on document type
- **User Feels**: Guided (system suggests right frameworks)
- **Value Delivered**: Saves mental overhead of remembering which frameworks apply
- **Potential Friction**: Too many frameworks to choose from
- **Success Metric**: 80% accept default recommendations

### Step 3: AI Assessment (THE AHA MOMENT)
- **User Action**: Clicks "Assess Compliance"
- **System Response**: Claude analyzes document in 30-60 seconds, returns structured findings
- **User Feels**: Amazed (hours of work done in seconds)
- **Value Delivered**: **CORE VALUE - instant compliance analysis**
- **Potential Friction**: Waiting for results, unclear progress
- **Success Metric**: 90% of assessments complete in <2 minutes

### Step 4: Review Results
- **User Action**: Reviews flagged issues, sees citations to specific document sections
- **System Response**: Shows findings by framework, severity levels, suggested remediation
- **User Feels**: Empowered (can make informed decision)
- **Value Delivered**: Actionable insights with evidence
- **Potential Friction**: Too many findings (information overload)
- **Success Metric**: Users mark 70%+ of findings as "helpful"

### Step 5: Export & Share
- **User Action**: Generates PDF report, shares link with stakeholders
- **System Response**: Creates professional compliance report, shareable URL
- **User Feels**: Professional (can show their work)
- **Value Delivered**: Audit trail + stakeholder communication
- **Potential Friction**: Report format not meeting organizational needs
- **Success Metric**: 60% of assessments result in exported report

**Time to Value**: <3 minutes from upload to actionable insights

---

## Friction Points & Solutions

| Journey Step | Friction Point | User Impact | Priority | Solution Design |
|--------------|----------------|-------------|----------|-----------------|
| Upload | Large scanned PDFs fail | Drop-off | High | OCR processing + file size handling |
| Assessment | 60-second wait feels long | Anxiety | High | Progress indicator + estimated time |
| Results | Too many low-priority findings | Overwhelm | Medium | Severity filtering + smart defaults |
| Integration | Can't fit into existing workflow | Abandonment | High | API access for power users |

---

## Value Definition

### Functional Value
- **Save time**: 2-4 hours → 3 minutes per document (40-80x faster)
- **Save money**: $150/hour (loaded cost) × 3 hours saved = $450 per document
- **Reduce risk**: Catch compliance issues before regulatory review
- **Enable capability**: Assess against multiple frameworks simultaneously

### Emotional Value
- Confident (not anxious about missing issues)
- In control (not drowning in paperwork)
- Professional (can explain findings clearly)

### Economic Value
- Direct time savings: $450 per document × 30 docs/month = $13,500/month
- Risk reduction: Avoiding one compliance failure (avg fine $50K+) justifies years of subscription
- **Value Ratio**: User saves $13,500/month, pays $200/month = 67:1 value ratio

---

## Journey Metrics

### Awareness → Consideration
- Metric: Website visit to trial signup rate
- Target: 8%

### Consideration → Activation
- Metric: Signup to first completed assessment
- Target: 60% within 10 minutes

### Activation → Adoption
- Metric: Weekly assessments per active user
- Target: 8 assessments/week

### Adoption → Retention
- Metric: 30-day retention rate
- Target: 75%

### Retention → Advocacy
- Metric: NPS score, referral rate
- Target: NPS > 50, 15% referral rate

---

## Connection to Tech Stack (see ../stack/04-tech-stack.md)

Journey requirements that drove tech decisions:

- **Step 1 (Upload)**: Large file handling → S3 + presigned URLs
- **Step 2 (Frameworks)**: Smart recommendations → PostgreSQL + user history analysis
- **Step 3 (Assessment)**: AI reasoning → Claude Sonnet API + FastAPI async
- **Step 4 (Results)**: Shareable reports → Next.js SSR for SEO + public links
- **Step 5 (Export)**: PDF generation → Python ecosystem (ReportLab/WeasyPrint)

---

**Next in Cascade**: This journey informed our mission (foundation/01-mission.md), tech stack decisions (stack/04-tech-stack.md), and every subsequent strategic choice.
