"""
Tests for conftest.py fixtures and validation logic.

Verifies that autouse fixtures work correctly, don't interfere with unit tests,
and that DATABASE_URL validation logic works as expected.
"""

import os
from unittest.mock import patch
import pytest
from conftest import _validate_test_database_url


def test_autouse_blob_mock_available(_auto_mock_vercel_blob):
    """Verify autouse blob storage mock is available in integration tests."""
    assert _auto_mock_vercel_blob is not None, "Autouse mock should be available"
    assert "put" in _auto_mock_vercel_blob, "Mock should have 'put' function"
    assert "delete" in _auto_mock_vercel_blob, "Mock should have 'delete' function"
    assert _auto_mock_vercel_blob["put"].call_count == 0, "Mock should not be called yet"
    assert _auto_mock_vercel_blob["delete"].call_count == 0, "Mock should not be called yet"


@pytest.mark.unit
def test_autouse_blob_mock_skipped_for_unit_tests(_auto_mock_vercel_blob):
    """Verify autouse blob storage mock is skipped for unit tests."""
    assert _auto_mock_vercel_blob is None, "Autouse mock should be None for @pytest.mark.unit tests"


# ============================================================================
# DATABASE_URL Validation Tests
# ============================================================================


@pytest.mark.unit
def test_validate_accepts_qteria_test():
    """Test that database name 'qteria_test' is accepted without raising pytest.exit()."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@host/qteria_test", "CI": ""},
        clear=False,
    ):
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_suffix_test_underscore():
    """Test that database names ending with '_test' (e.g., 'myapp_test') are accepted."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@host/myapp_test", "CI": ""},
        clear=False,
    ):
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_suffix_test_hyphen():
    """Test that database names ending with '-test' (e.g., 'myapp-test') are accepted."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@host/myapp-test", "CI": ""},
        clear=False,
    ):
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_qteria_test_uppercase():
    """Test case-insensitive matching (e.g., 'QTERIA_TEST', 'Qteria-Test')."""
    test_urls = [
        "postgresql://user:pass@host/QTERIA_TEST",
        "postgresql://user:pass@host/Qteria-Test",
        "postgresql://user:pass@host/MyApp_TEST",
    ]

    for test_url in test_urls:
        with patch.dict(os.environ, {"DATABASE_URL": test_url, "CI": ""}, clear=False):
            # Should not raise pytest.exit()
            _validate_test_database_url()


@pytest.mark.unit
@pytest.mark.skip(reason="Test causes environment contamination in CI - tracked in issue #215")
def test_validate_rejects_neondb():
    """Test that production database name 'neondb' triggers pytest.exit() with appropriate error."""
    with patch.dict(
        os.environ, {"DATABASE_URL": "postgresql://user:pass@host/neondb", "CI": ""}, clear=False
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        # Verify error message mentions production database
        assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_postgres():
    """Test that production database name 'postgres' triggers pytest.exit()."""
    with patch.dict(
        os.environ, {"DATABASE_URL": "postgresql://user:pass@host/postgres", "CI": ""}, clear=False
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_production():
    """Test that database name 'production' triggers pytest.exit()."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@host/production", "CI": ""},
        clear=False,
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_missing_database_url():
    """Test that missing DATABASE_URL environment variable triggers pytest.exit() with helpful error."""
    # Clear DATABASE_URL from environment
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        error_message = str(exc_info.value)
        assert "DATABASE_URL environment variable is not set" in error_message
        assert ".env.test" in error_message  # Should mention the fix


@pytest.mark.unit
def test_validate_rejects_malformed_url_no_database():
    """Test that malformed URL (missing database name) triggers pytest.exit()."""
    with patch.dict(
        os.environ, {"DATABASE_URL": "postgresql://user:pass@host/", "CI": ""}, clear=False
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        assert "malformed" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_rejects_malformed_url_invalid_format():
    """Test that completely invalid URL format triggers pytest.exit()."""
    with patch.dict(os.environ, {"DATABASE_URL": "not-a-valid-url", "CI": ""}, clear=False):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        assert "malformed" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_ci_environment_with_test_database():
    """Test that CI environment (CI=true) with test database pattern is accepted and prints confirmation."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@neon.tech/qteria-test", "CI": "true"},
        clear=False,
    ):
        # Should not raise pytest.exit() and should print confirmation
        _validate_test_database_url()


@pytest.mark.unit
def test_validate_ci_environment_still_rejects_production():
    """Test that CI environment does NOT bypass production database protection."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@host/production", "CI": "true"},
        clear=False,
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_password_masking_in_production_error():
    """Test that passwords are masked (****) in error messages when production database is detected."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:secretpass123@host/production", "CI": ""},
        clear=False,
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        error_message = str(exc_info.value)
        # Password should be masked
        assert "secretpass123" not in error_message
        assert "****" in error_message


@pytest.mark.unit
def test_password_masking_in_malformed_error():
    """Test that passwords are masked in error messages for malformed URLs."""
    with patch.dict(
        os.environ, {"DATABASE_URL": "postgresql://user:supersecret@host/", "CI": ""}, clear=False
    ):
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        error_message = str(exc_info.value)
        # Password should be masked
        assert "supersecret" not in error_message
        assert "****" in error_message


@pytest.mark.unit
def test_accepts_postgres_protocol():
    """Test that both 'postgresql://' and 'postgres://' protocols are accepted."""
    test_urls = [
        "postgresql://user:pass@host/qteria_test",
        "postgres://user:pass@host/qteria_test",
    ]

    for test_url in test_urls:
        with patch.dict(os.environ, {"DATABASE_URL": test_url, "CI": ""}, clear=False):
            # Should not raise pytest.exit()
            _validate_test_database_url()


@pytest.mark.unit
def test_accepts_url_with_query_params():
    """Test that URLs with query parameters (e.g., ?sslmode=require) are parsed correctly."""
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql://user:pass@host/qteria_test?sslmode=require&connect_timeout=10",
            "CI": "",
        },
        clear=False,
    ):
        # Should not raise pytest.exit()
        _validate_test_database_url()
