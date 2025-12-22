"""
Root conftest.py for pytest configuration.

This file loads .env.test before running any tests and validates that
DATABASE_URL points to a test database (not production).
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
import pytest


def _validate_test_database_url():
    """
    Validate that DATABASE_URL points to a test database, not production.

    Accepted patterns:
    - Database name contains 'qteria_test'
    - Database name ends with '_test'
    - CI environment (CI=true) with test database name

    Raises pytest.exit() if validation fails (fail-fast safety check).
    """
    database_url = os.getenv("DATABASE_URL")

    # Check 1: DATABASE_URL must be set
    if not database_url:
        pytest.exit(
            "❌ CRITICAL: DATABASE_URL environment variable is not set.\n"
            "\n"
            "Fix: Create .env.test file with:\n"
            "  DATABASE_URL=postgresql://user:pass@host/qteria_test\n"
            "\n"
            "If you don't have a test database yet:\n"
            "  1. Create 'qteria_test' database in Neon dashboard\n"
            "  2. Copy DATABASE_URL from Neon and update .env.test\n",
            returncode=1,
        )

    # Mask password in DATABASE_URL for error messages (security)
    masked_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", database_url)

    # Extract database name from URL (supports postgresql:// and postgres://)
    # Format: postgresql://user:pass@host:port/database_name?params
    match = re.search(r"/([^/?]+)(?:\?|$)", database_url)
    if not match:
        pytest.exit(
            f"❌ CRITICAL: DATABASE_URL is malformed!\n"
            f"\n"
            f"Current DATABASE_URL: {masked_url}\n"
            f"\n"
            f"Expected format: postgresql://user:pass@host/database_name\n"
            f"\n"
            f"Fix: Update .env.test with valid PostgreSQL URL:\n"
            f"  DATABASE_URL=postgresql://user:pass@host/qteria_test\n",
            returncode=1,
        )
    database_name = match.group(1)

    # Check 2: Is this a CI environment with test database?
    # CI exception requires both CI=true AND test database name pattern
    is_ci = os.getenv("CI", "").lower() in ("true", "1", "yes")
    is_ci_test = is_ci and (
        "qteria-test" in database_name.lower()
        or "qteria_test" in database_name.lower()
        or database_name.lower().endswith("-test")
        or database_name.lower().endswith("_test")
    )
    if is_ci_test:
        print(f"✅ CI environment detected with test database: {database_name}")
        return

    # Check 3: Does database name match test patterns?
    is_test_database = (
        "qteria-test" in database_name.lower()
        or "qteria_test" in database_name.lower()
        or database_name.lower().endswith("-test")
        or database_name.lower().endswith("_test")
    )

    if not is_test_database:
        pytest.exit(
            f"❌ CRITICAL: DATABASE_URL points to PRODUCTION database!\n"
            f"\n"
            f"Current DATABASE_URL: {masked_url}\n"
            f"Database name: {database_name}\n"
            f"\n"
            f"Accepted patterns:\n"
            f"  - Database name contains 'qteria-test' or 'qteria_test'\n"
            f"  - Database name ends with '-test' or '_test'\n"
            f"  - CI environment (CI=true) with test database name\n"
            f"\n"
            f"Fix: Update .env.test to point to test database:\n"
            f"  DATABASE_URL=postgresql://user:pass@host/qteria-test\n"
            f"\n"
            f"NEVER run tests against production database!\n",
            returncode=1,
        )

    print(f"✅ Test database validated: {database_name}")


def pytest_configure(config):
    """
    Load .env.test before running tests and validate DATABASE_URL.

    This ensures tests use the test database (qteria_test),
    not the development or production database.

    Fail-fast if DATABASE_URL points to production (safety check).
    """
    # Load .env.test if it exists (don't override existing env vars from CI)
    env_test_path = Path(__file__).parent / ".env.test"
    if env_test_path.exists():
        load_dotenv(env_test_path, override=False)
        print(f"✅ Loaded test environment from {env_test_path}")
    else:
        print(f"⚠️  Warning: {env_test_path} not found. Using default .env")

    # Validate DATABASE_URL points to test database (fail-fast safety check)
    _validate_test_database_url()
