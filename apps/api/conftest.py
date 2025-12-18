"""
Root conftest.py for pytest configuration.

This file loads .env.test before running any tests.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def pytest_configure(config):
    """
    Load .env.test before running tests.

    This ensures tests use the test database (qteria-test),
    not the development database.
    """
    # Load .env.test if it exists
    env_test_path = Path(__file__).parent / ".env.test"
    if env_test_path.exists():
        load_dotenv(env_test_path, override=True)
        print(f"✅ Loaded test environment from {env_test_path}")
    else:
        print(f"⚠️  Warning: {env_test_path} not found. Using default .env")
