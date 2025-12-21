#!/usr/bin/env python3
"""
Seed data script for Qteria development environment.

Creates realistic sample data for testing and development:
- 1 System organization (for security audit logs - SOC2/ISO 27001 compliance)
- 1 organization (TÜV SÜD Demo)
- 2 users (Process Manager and Project Handler)
- 2 workflows based on real certification standards
  - Machinery Directive 2006/42/EC
  - Medical Device Regulation (EU) 2017/745

Usage:
    python scripts/seed_data.py              # Seed data (idempotent)
    python scripts/seed_data.py --reset      # Reset and reseed
"""
import argparse
import os
import sys
import time
from uuid import UUID

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.exc import IntegrityError
from app.models import (
    SessionLocal,
    Organization,
    User,
    Workflow,
    Bucket,
    Criteria,
    Assessment,
    AssessmentDocument,
    AssessmentResult,
    AuditLog,
)


# Fixed UUIDs for consistent seed data across environments
SYSTEM_ORG_ID = UUID("00000000-0000-0000-0000-000000000000")  # System org for audit logs
ORG_ID = UUID("00000000-0000-0000-0000-000000000001")
USER_PM_ID = UUID("00000000-0000-0000-0000-000000000002")
USER_PH_ID = UUID("00000000-0000-0000-0000-000000000003")
WORKFLOW_MACHINERY_ID = UUID("00000000-0000-0000-0000-000000000004")
WORKFLOW_MEDICAL_ID = UUID("00000000-0000-0000-0000-000000000005")


def check_environment():
    """
    Verify we're running in development environment.
    Refuse to reset production data.
    """
    python_env = os.getenv("PYTHON_ENV", "development")
    if python_env == "production":
        print("❌ ERROR: Cannot run seed script in production environment!")
        print("   Set PYTHON_ENV=development to run this script.")
        sys.exit(1)


def reset_database(session):
    """
    Drop all data from all tables in reverse dependency order.
    Deletes child records before parent records to avoid foreign key violations.
    """
    print("🗑️  Resetting database...")
    try:
        # Delete in reverse dependency order
        # 1. Delete assessment results (depends on assessments and criteria)
        session.query(AssessmentResult).delete()

        # 2. Delete assessment documents (depends on assessments and buckets)
        session.query(AssessmentDocument).delete()

        # 3. Delete assessments (depends on organization, workflow, user)
        session.query(Assessment).delete()

        # 4. Delete criteria (depends on workflow)
        session.query(Criteria).delete()

        # 5. Delete buckets (depends on workflow)
        session.query(Bucket).delete()

        # 6. Delete workflows (depends on organization and user)
        session.query(Workflow).delete()

        # 7. Delete audit logs (depends on organization)
        session.query(AuditLog).delete()

        # 8. Delete users (depends on organization)
        session.query(User).delete()

        # 9. Finally delete organizations (no dependencies)
        session.query(Organization).delete()

        session.commit()
        print("✅ Database reset complete")
    except Exception as e:
        session.rollback()
        print(f"❌ Error resetting database: {e}")
        raise


def check_data_exists(session):
    """
    Check if seed data already exists.
    Returns True if demo organization exists.
    """
    org = session.query(Organization).filter_by(id=ORG_ID).first()
    return org is not None


def seed_system_organization(session):
    """
    Create System organization for security audit logs.

    This organization is used for audit logging security events where
    a user's organization is unknown (e.g., failed OAuth login attempts
    for non-existent users).

    Required for SOC2/ISO 27001 compliance - ensures all security events
    are audited even when user context is unavailable.

    Returns the created System organization.
    """
    print("🔒 Creating System organization...")

    system_org = Organization(
        id=SYSTEM_ORG_ID,
        name="System",
        subscription_tier="internal",
        subscription_status="active",
    )

    session.add(system_org)
    session.flush()  # Flush to get the ID for audit logs

    print(f"   ✓ System Organization: {system_org.name} (for security audit logs)")
    return system_org


def seed_organization(session):
    """
    Create TÜV SÜD Demo organization.
    Returns the created organization.
    """
    print("📦 Creating organization...")

    org = Organization(
        id=ORG_ID,
        name="TÜV SÜD Demo",
        subscription_tier="professional",
        subscription_status="trial",
    )

    session.add(org)
    session.flush()  # Flush to get the ID for relationships

    print(f"   ✓ Organization: {org.name}")
    return org


def seed_users(session, org_id):
    """
    Create 2 users: Process Manager and Project Handler.
    Returns list of created users.
    """
    print("👥 Creating users...")

    users = [
        User(
            id=USER_PM_ID,
            organization_id=org_id,
            email="process.manager@tuvsud-demo.com",
            name="Process Manager Demo",
            role="process_manager",
        ),
        User(
            id=USER_PH_ID,
            organization_id=org_id,
            email="project.handler@tuvsud-demo.com",
            name="Project Handler Demo",
            role="project_handler",
        ),
    ]

    for user in users:
        session.add(user)
        print(f"   ✓ User: {user.name} ({user.role})")

    session.flush()
    return users


def create_machinery_workflow(session, org_id, pm_user_id):
    """
    Create Machinery Directive 2006/42/EC workflow.
    Returns the created workflow.
    """
    workflow = Workflow(
        id=WORKFLOW_MACHINERY_ID,
        organization_id=org_id,
        created_by=pm_user_id,
        name="Machinery Directive 2006/42/EC",
        description="Validation workflow for machinery certification under EU Directive 2006/42/EC",
        is_active=True,
    )
    session.add(workflow)
    session.flush()

    # Bucket 1: Technical Documentation
    bucket_tech = Bucket(
        workflow_id=workflow.id,
        name="Technical Documentation",
        required=True,
        order_index=1,
    )
    session.add(bucket_tech)
    session.flush()

    # Criteria for Technical Documentation
    criteria_tech = [
        Criteria(
            workflow_id=workflow.id,
            name="Risk Assessment Present",
            description="Technical documentation must include a comprehensive risk assessment identifying all hazards and implemented protective measures.",
            applies_to_bucket_ids=[bucket_tech.id],
            example_text="Look for sections titled 'Risk Assessment', 'Hazard Analysis', or 'Safety Analysis' with systematic identification of mechanical, electrical, and operational hazards.",
        ),
        Criteria(
            workflow_id=workflow.id,
            name="Assembly Instructions Included",
            description="Clear assembly, installation, and commissioning instructions must be provided for safe machinery setup.",
            applies_to_bucket_ids=[bucket_tech.id],
            example_text="Documentation should include step-by-step assembly procedures, installation requirements, and commissioning checklists.",
        ),
        Criteria(
            workflow_id=workflow.id,
            name="Maintenance Procedures Documented",
            description="Maintenance procedures and schedules must be clearly documented to ensure continued safe operation.",
            applies_to_bucket_ids=[bucket_tech.id],
            example_text="Look for maintenance schedules, procedures for routine checks, and spare parts lists.",
        ),
    ]

    for criteria in criteria_tech:
        session.add(criteria)

    # Bucket 2: EC Declaration of Conformity
    bucket_ec = Bucket(
        workflow_id=workflow.id,
        name="EC Declaration of Conformity",
        required=True,
        order_index=2,
    )
    session.add(bucket_ec)
    session.flush()

    # Criteria for EC Declaration
    criteria_ec = [
        Criteria(
            workflow_id=workflow.id,
            name="Manufacturer Details Correct",
            description="Declaration must include complete and accurate manufacturer identification (name, address, authorized representative).",
            applies_to_bucket_ids=[bucket_ec.id],
            example_text="Verify manufacturer's legal name, full address, and authorized representative details are present and correct.",
        ),
        Criteria(
            workflow_id=workflow.id,
            name="Directive References Accurate",
            description="All applicable EU directives must be correctly referenced with full directive numbers.",
            applies_to_bucket_ids=[bucket_ec.id],
            example_text="Declaration must cite Machinery Directive 2006/42/EC and any other applicable directives (e.g., EMC, Low Voltage).",
        ),
        Criteria(
            workflow_id=workflow.id,
            name="Harmonized Standards Listed",
            description="All harmonized standards applied must be listed with correct designation and date.",
            applies_to_bucket_ids=[bucket_ec.id],
            example_text="Look for EN ISO 12100 (Safety of machinery), EN 60204-1 (Electrical equipment), and other relevant EN standards.",
        ),
    ]

    for criteria in criteria_ec:
        session.add(criteria)

    session.flush()
    print(f"   ✓ Workflow: {workflow.name}")
    print(f"     - 2 buckets, 6 criteria")

    return workflow


def create_medical_device_workflow(session, org_id, pm_user_id):
    """
    Create Medical Device Regulation (EU) 2017/745 workflow.
    Returns the created workflow.
    """
    workflow = Workflow(
        id=WORKFLOW_MEDICAL_ID,
        organization_id=org_id,
        created_by=pm_user_id,
        name="Medical Device Regulation (EU) 2017/745",
        description="Validation workflow for medical device certification under EU MDR 2017/745",
        is_active=True,
    )
    session.add(workflow)
    session.flush()

    # Bucket 1: Clinical Evaluation Report
    bucket_clinical = Bucket(
        workflow_id=workflow.id,
        name="Clinical Evaluation Report",
        required=True,
        order_index=1,
    )
    session.add(bucket_clinical)
    session.flush()

    # Criteria for Clinical Evaluation
    criteria_clinical = [
        Criteria(
            workflow_id=workflow.id,
            name="Clinical Data Summarized",
            description="Clinical Evaluation Report must include comprehensive summary of all relevant clinical data for the device.",
            applies_to_bucket_ids=[bucket_clinical.id],
            example_text="Look for systematic literature review, clinical investigations, post-market surveillance data, and equivalent device analysis.",
        ),
        Criteria(
            workflow_id=workflow.id,
            name="Benefit-Risk Analysis Included",
            description="Report must contain detailed benefit-risk analysis demonstrating clinical benefits outweigh residual risks.",
            applies_to_bucket_ids=[bucket_clinical.id],
            example_text="Verify presence of quantitative and qualitative benefit-risk assessment considering intended use, patient population, and risk mitigation measures.",
        ),
        Criteria(
            workflow_id=workflow.id,
            name="Clinical Evidence Adequate",
            description="Clinical evidence must be sufficient to demonstrate conformity with safety and performance requirements.",
            applies_to_bucket_ids=[bucket_clinical.id],
            example_text="Assess if clinical data is current, relevant to intended use, and covers the full lifecycle of the device.",
        ),
    ]

    for criteria in criteria_clinical:
        session.add(criteria)

    # Bucket 2: Technical Documentation
    bucket_tech = Bucket(
        workflow_id=workflow.id,
        name="Technical Documentation",
        required=True,
        order_index=2,
    )
    session.add(bucket_tech)
    session.flush()

    # Criteria for Technical Documentation
    criteria_tech = [
        Criteria(
            workflow_id=workflow.id,
            name="Design and Manufacturing Information Complete",
            description="Technical file must contain complete design specifications, manufacturing information, and verification/validation documentation.",
            applies_to_bucket_ids=[bucket_tech.id],
            example_text="Look for design drawings, materials specifications, manufacturing process descriptions, and design verification test reports.",
        ),
    ]

    for criteria in criteria_tech:
        session.add(criteria)

    session.flush()
    print(f"   ✓ Workflow: {workflow.name}")
    print(f"     - 2 buckets, 4 criteria")

    return workflow


def seed_workflows(session, org_id, pm_user_id):
    """
    Create 2 sample workflows with buckets and criteria.
    """
    print("📋 Creating workflows...")

    workflows = [
        create_machinery_workflow(session, org_id, pm_user_id),
        create_medical_device_workflow(session, org_id, pm_user_id),
    ]

    return workflows


def main():
    """
    Main entry point for seed data script.
    """
    parser = argparse.ArgumentParser(description="Seed Qteria development database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (delete all data) before seeding",
    )
    args = parser.parse_args()

    # Check environment safety
    check_environment()

    print("\n🌱 Qteria Seed Data Script")
    print("=" * 50)

    # Track execution time
    start_time = time.time()

    # Create database session
    session = SessionLocal()

    try:
        # Reset database if requested
        if args.reset:
            reset_database(session)

        # Check if data already exists
        if check_data_exists(session):
            if not args.reset:
                print("\n✅ Seed data already exists (idempotent check passed)")
                print("   Run with --reset flag to drop and reseed data")
                return

        # Seed data in transaction
        print("\n🚀 Seeding database...")

        # Create System organization (for security audit logs)
        system_org = seed_system_organization(session)

        # Create organization
        org = seed_organization(session)

        # Create users
        users = seed_users(session, org.id)
        pm_user = users[0]  # Process Manager

        # Create workflows with buckets and criteria
        workflows = seed_workflows(session, org.id, pm_user.id)

        # Commit transaction
        session.commit()

        # Calculate execution time
        elapsed_time = time.time() - start_time

        # Success summary
        print("\n" + "=" * 50)
        print("✅ Seed data created successfully!")
        print(f"⏱️  Execution time: {elapsed_time:.2f}s")
        print("\n📊 Summary:")
        print(f"   • System organization: {system_org.name} (for security audit logs)")
        print(f"   • 1 organization: {org.name}")
        print(f"   • 2 users: Process Manager, Project Handler")
        print(f"   • 2 workflows:")
        print(f"     - {workflows[0].name} (2 buckets, 6 criteria)")
        print(f"     - {workflows[1].name} (2 buckets, 4 criteria)")
        print("\n🔑 Login credentials:")
        print(f"   Process Manager: process.manager@tuvsud-demo.com")
        print(f"   Project Handler: project.handler@tuvsud-demo.com")
        print("=" * 50 + "\n")

    except IntegrityError as e:
        session.rollback()
        print(f"\n❌ Database integrity error: {e}")
        print("   This usually means seed data already exists.")
        print("   Run with --reset flag to drop and reseed data.")
        sys.exit(1)

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error seeding database: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        session.close()


if __name__ == "__main__":
    main()
