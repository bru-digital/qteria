# [STORY-003] Seed Data for Development

**Type**: Story
**Epic**: EPIC-01 (Database & Infrastructure)
**Journey Step**: Foundation
**Priority**: P0 (Enables Testing)
**RICE Score**: 100 (R:50 × I:1 × C:100% ÷ E:0.5)

---

## User Value

**Job-to-Be-Done**: When developers start building features, they need realistic sample data in the database, so they can test workflows and APIs without manually creating test data each time.

**Value Delivered**: Enables rapid development and testing with pre-populated sample data matching production structure.

**Success Metric**: Seed data script creates complete test environment in <5 seconds.

---

## Acceptance Criteria

- [ ] Seed data script creates 1 sample organization ("TÜV SÜD Demo")
- [ ] Creates 2 sample users with different roles (Process Manager, Project Handler)
- [ ] Creates 2 sample workflows with realistic buckets and criteria
- [ ] All relationships properly linked (org → users → workflows → buckets → criteria)
- [ ] Seed data uses realistic values (e.g., actual criteria text from certification standards)
- [ ] Script is idempotent (can run multiple times without errors)
- [ ] Script has clear flag (--reset) to drop all data and reseed
- [ ] Seed data documented with description of what's created
- [ ] Script runs in <5 seconds

---

## Technical Approach

**Tech Stack Components Used**:

- Backend: Python script using SQLAlchemy
- Database: PostgreSQL 15+

**Implementation Notes**:

- Create `scripts/seed_data.py` script
- Use SQLAlchemy ORM for inserting data
- Check if data exists before inserting (idempotent)
- Use UUIDs for IDs (consistent across environments)

**Sample Data Structure**:

```python
# Organization
organization = {
    "id": "org_tuv_sud_demo_uuid",
    "name": "TÜV SÜD Demo",
    "subscription_tier": "professional",
    "subscription_status": "trial"
}

# Users
users = [
    {
        "id": "user_pm_uuid",
        "organization_id": "org_tuv_sud_demo_uuid",
        "email": "process.manager@tuvsud-demo.com",
        "name": "Process Manager Demo",
        "role": "process_manager"
    },
    {
        "id": "user_ph_uuid",
        "organization_id": "org_tuv_sud_demo_uuid",
        "email": "project.handler@tuvsud-demo.com",
        "name": "Project Handler Demo",
        "role": "project_handler"
    }
]

# Workflows
workflows = [
    {
        "id": "workflow_machinery_uuid",
        "organization_id": "org_tuv_sud_demo_uuid",
        "name": "Machinery Directive 2006/42/EC",
        "created_by": "user_pm_uuid",
        "buckets": [
            {
                "name": "Technical Documentation",
                "criteria": [
                    "Risk assessment present",
                    "Assembly instructions included"
                ]
            },
            {
                "name": "EC Declaration of Conformity",
                "criteria": [
                    "Manufacturer details correct",
                    "Directive references accurate"
                ]
            }
        ]
    },
    {
        "id": "workflow_medical_device_uuid",
        "organization_id": "org_tuv_sud_demo_uuid",
        "name": "Medical Device Regulation (EU) 2017/745",
        "created_by": "user_pm_uuid",
        "buckets": [
            {
                "name": "Clinical Evaluation Report",
                "criteria": [
                    "Clinical data summarized",
                    "Benefit-risk analysis included"
                ]
            }
        ]
    }
]
```

**Script Usage**:

```bash
# Seed data (idempotent)
python scripts/seed_data.py

# Reset database and reseed
python scripts/seed_data.py --reset

# Seed specific environment
python scripts/seed_data.py --env staging
```

---

## Dependencies

- **Blocked By**:
  - STORY-001 (Database Schema) - need tables to exist
  - STORY-002 (Migrations) - need schema applied before seeding
- **Blocks**: Feature development - developers need sample data to test against

---

## Estimation

**Effort**: 0.5 person-days (4 hours)

**Breakdown**:

- Script setup: 0.1 days (file structure, imports)
- Sample data creation: 0.2 days (realistic workflows, criteria text)
- Idempotency logic: 0.1 days (check if data exists)
- Testing: 0.1 days (run script, verify data)

---

## Definition of Done

- [ ] `scripts/seed_data.py` script created
- [ ] Script creates 1 organization, 2 users, 2 workflows
- [ ] All relationships properly linked (foreign keys valid)
- [ ] Script runs without errors on empty database
- [ ] Script runs without errors on database with existing seed data (idempotent)
- [ ] `--reset` flag drops all data and reseeds
- [ ] Script completes in <5 seconds
- [ ] Seed data documented in README (what's created, how to run)
- [ ] Sample workflows use realistic certification criteria
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Functional Tests**:

- [ ] Run script on empty database → verify 1 org, 2 users, 2 workflows created
- [ ] Run script again → no errors, no duplicate data
- [ ] Run with `--reset` → old data deleted, new data inserted
- [ ] Verify foreign key relationships (users.organization_id links to organizations.id)
- [ ] Verify workflows have buckets and criteria properly nested

**Performance Tests**:

- [ ] Script completes in <5 seconds
- [ ] Insert 2 workflows with 5 buckets each, 10 criteria per bucket → <5 seconds

---

## Risks & Mitigations

**Risk**: Seed data conflicts with production data (same UUIDs)

- **Mitigation**: Use clearly marked demo UUIDs with prefix (e.g., `demo_org_uuid`), never use in production

**Risk**: Script fails mid-execution, leaves partial data

- **Mitigation**: Wrap inserts in transaction, rollback on error

**Risk**: Seed data becomes stale as schema evolves

- **Mitigation**: Update seed data script whenever schema changes (link to migrations)

---

## Notes

- Use realistic certification criteria from actual standards (e.g., Machinery Directive 2006/42/EC)
- Seed data should demonstrate the full user journey (Process Manager creates workflow → Project Handler uses workflow)
- Keep seed data small (2 workflows, not 100) to avoid slow startup
- After completing this story, proceed to STORY-004 (FastAPI Infrastructure)
- Consider adding more seed data scenarios in the future (e.g., completed assessments with results)
