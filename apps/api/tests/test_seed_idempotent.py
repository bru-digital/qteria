"""
Test idempotent database seeding (closes #255).

This test verifies that seed_test_data() can be run multiple times without
causing duplicate key errors, ensuring pytest can run successfully even when
the test database already contains seeded data.
"""

from sqlalchemy.orm import Session
from app.models.models import Organization, User
from scripts.seed_test_data import seed_test_data
from tests.conftest import (
    TEST_ORG_A_ID,
    TEST_ORG_B_ID,
    TEST_USER_A_ID,
    TEST_USER_A_PM_ID,
    TEST_USER_A_PH_ID,
    TEST_USER_B_ID,
    TEST_USER_B_PM_ID,
    TEST_USER_B_PH_ID,
)


def test_seed_idempotent_empty_database(db_session: Session):
    """
    Test seeding works on empty database.

    Acceptance criteria:
    - All 2 organizations are created
    - All 6 users are created
    """
    # Clear all test data first (within savepoint, will rollback after test)
    db_session.query(User).delete()
    db_session.query(Organization).delete()
    db_session.commit()

    # Run seeding
    seed_test_data()

    # Verify organizations
    orgs = db_session.query(Organization).all()
    assert len(orgs) == 2
    org_ids = {str(org.id) for org in orgs}
    assert TEST_ORG_A_ID in org_ids
    assert TEST_ORG_B_ID in org_ids

    # Verify users
    users = db_session.query(User).all()
    assert len(users) == 6
    user_ids = {str(user.id) for user in users}
    assert TEST_USER_A_ID in user_ids
    assert TEST_USER_A_PM_ID in user_ids
    assert TEST_USER_A_PH_ID in user_ids
    assert TEST_USER_B_ID in user_ids
    assert TEST_USER_B_PM_ID in user_ids
    assert TEST_USER_B_PH_ID in user_ids


def test_seed_idempotent_partial_data(db_session: Session):
    """
    Test seeding works when only some data exists (e.g., only org_a).

    This is the bug scenario from #255 - if org_b exists but org_a doesn't,
    the old code would skip seeding and leave org_a missing.

    Acceptance criteria:
    - No duplicate key errors
    - Missing organization is created
    - Missing users are created
    - Existing data is preserved
    """
    from uuid import UUID

    # Clear all test data
    db_session.query(User).delete()
    db_session.query(Organization).delete()
    db_session.commit()

    # Create only Org B (simulate partial failure scenario)
    org_b = Organization(
        id=UUID(TEST_ORG_B_ID),
        name="Test Organization B",
        subscription_tier="trial",
        subscription_status="trial",
    )
    db_session.add(org_b)
    db_session.commit()

    # Run seeding - should NOT error, should create org_a
    seed_test_data()

    # Verify both organizations exist
    orgs = db_session.query(Organization).all()
    assert len(orgs) == 2
    org_ids = {str(org.id) for org in orgs}
    assert TEST_ORG_A_ID in org_ids
    assert TEST_ORG_B_ID in org_ids

    # Verify all users exist
    users = db_session.query(User).all()
    assert len(users) == 6


def test_seed_idempotent_full_data(db_session: Session):
    """
    Test seeding works when all data already exists.

    Acceptance criteria:
    - No duplicate key errors
    - No errors at all
    - Data count stays the same (no duplicates)
    """
    # Ensure data exists (pytest_sessionstart should have seeded it)
    orgs_before = db_session.query(Organization).count()
    users_before = db_session.query(User).count()

    # This should be at least 2 orgs and 6 users from session seeding
    assert orgs_before >= 2
    assert users_before >= 6

    # Run seeding again - should be no-op
    seed_test_data()

    # Verify counts didn't increase
    orgs_after = db_session.query(Organization).count()
    users_after = db_session.query(User).count()

    # Count should stay the same (ON CONFLICT DO NOTHING prevents duplicates)
    assert orgs_after == orgs_before
    assert users_after == users_before


def test_seed_idempotent_multiple_runs(db_session: Session):
    """
    Test seeding can be run multiple times in succession.

    This simulates the pytest_sessionstart hook being called multiple times
    (e.g., in pytest watch mode or when re-running failed tests).

    Acceptance criteria:
    - Three consecutive runs complete without error
    - Data count stays constant after first run
    """
    # Clear all test data
    db_session.query(User).delete()
    db_session.query(Organization).delete()
    db_session.commit()

    # First run - should create data
    seed_test_data()
    orgs_after_first = db_session.query(Organization).count()
    users_after_first = db_session.query(User).count()
    assert orgs_after_first == 2
    assert users_after_first == 6

    # Second run - should be no-op
    seed_test_data()
    orgs_after_second = db_session.query(Organization).count()
    users_after_second = db_session.query(User).count()
    assert orgs_after_second == 2
    assert users_after_second == 6

    # Third run - should still be no-op
    seed_test_data()
    orgs_after_third = db_session.query(Organization).count()
    users_after_third = db_session.query(User).count()
    assert orgs_after_third == 2
    assert users_after_third == 6
