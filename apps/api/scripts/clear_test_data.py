#!/usr/bin/env python3
"""
Clear all data from qteria-test database.

This script removes all test data while preserving the schema.
Useful for resetting the test database to a clean state.

Usage:
    python scripts/clear_test_data.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from app.models.base import SessionLocal
from app.models import (
    AssessmentResult,
    AssessmentDocument,
    Assessment,
    Criteria,
    Bucket,
    Workflow,
    User,
    Organization,
    AuditLog,
)


def clear_test_data():
    """Clear all data from test database (preserves schema)."""
    load_dotenv(".env.test", override=True)

    db = SessionLocal()

    try:
        print("Clearing test data...")

        # Delete in order to respect foreign key constraints
        # (child tables first, parent tables last)

        counts = {}
        counts["assessment_results"] = db.query(AssessmentResult).delete()
        counts["assessment_documents"] = db.query(AssessmentDocument).delete()
        counts["assessments"] = db.query(Assessment).delete()
        counts["criteria"] = db.query(Criteria).delete()
        counts["buckets"] = db.query(Bucket).delete()
        counts["workflows"] = db.query(Workflow).delete()
        counts["audit_logs"] = db.query(AuditLog).delete()
        counts["users"] = db.query(User).delete()
        counts["organizations"] = db.query(Organization).delete()

        db.commit()

        print("\n✅ Test data cleared successfully!")
        print("\nDeleted records:")
        for table, count in counts.items():
            if count > 0:
                print(f"   - {table}: {count}")

        print("\nYou can now re-seed:")
        print("   python scripts/seed_test_data.py")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error clearing test data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Clearing Test Data from qteria-test Database")
    print("=" * 60)
    print()

    response = input("⚠️  This will DELETE ALL DATA from qteria-test. Continue? (yes/no): ")
    if response.lower() == "yes":
        clear_test_data()
    else:
        print("Cancelled.")
