"""
Tests for conftest.py fixtures and validation logic.

Verifies that autouse fixtures work correctly, don't interfere with unit tests,
and that DATABASE_URL validation logic works as expected.
"""

import os
import pytest
from conftest import _validate_test_database_url


@pytest.fixture
def database_url_patch():
    """
    Fixture that safely patches DATABASE_URL and guarantees restoration.

    This fixture ensures the original DATABASE_URL is restored in the teardown phase,
    even if the test fails or raises an exception.

    Usage in tests:
        def test_something(database_url_patch):
            database_url_patch("postgresql://user:pass@host/test_db")
            # Test code here
    """
    original_url = os.environ.get("DATABASE_URL")
    original_ci = os.environ.get("CI")

    def _patch(url, ci_value=""):
        """Set DATABASE_URL and CI environment variables."""
        os.environ["DATABASE_URL"] = url
        os.environ["CI"] = ci_value

    yield _patch

    # Teardown: restore original values
    if original_url is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = original_url

    if original_ci is None:
        os.environ.pop("CI", None)
    else:
        os.environ["CI"] = original_ci


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
def test_validate_accepts_qteria_test(database_url_patch):
    """Test that database name 'qteria_test' is accepted without raising pytest.exit()."""
    database_url_patch("postgresql://user:pass@host/qteria_test")
    # Should not raise pytest.exit()
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_suffix_test_underscore(database_url_patch):
    """Test that database names ending with '_test' (e.g., 'myapp_test') are accepted."""
    database_url_patch("postgresql://user:pass@host/myapp_test")
    # Should not raise pytest.exit()
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_suffix_test_hyphen(database_url_patch):
    """Test that database names ending with '-test' (e.g., 'myapp-test') are accepted."""
    database_url_patch("postgresql://user:pass@host/myapp-test")
    # Should not raise pytest.exit()
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_qteria_test_uppercase(database_url_patch):
    """Test case-insensitive matching (e.g., 'QTERIA_TEST', 'Qteria-Test')."""
    test_urls = [
        "postgresql://user:pass@host/QTERIA_TEST",
        "postgresql://user:pass@host/Qteria-Test",
        "postgresql://user:pass@host/MyApp_TEST",
    ]

    for test_url in test_urls:
        database_url_patch(test_url)
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
@pytest.mark.skip(reason="Test causes environment contamination in CI - tracked in issue #215")
def test_validate_rejects_neondb(database_url_patch):
    """Test that production database name 'neondb' triggers pytest.exit() with appropriate error."""
    database_url_patch("postgresql://user:pass@host/neondb")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    # Verify error message mentions production database
    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_postgres(database_url_patch):
    """Test that production database name 'postgres' triggers pytest.exit()."""
    database_url_patch("postgresql://user:pass@host/postgres")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_production(database_url_patch):
    """Test that database name 'production' triggers pytest.exit()."""
    database_url_patch("postgresql://user:pass@host/production")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_missing_database_url():
    """Test that missing DATABASE_URL environment variable triggers pytest.exit() with helpful error."""
    # Store original DATABASE_URL to restore later
    original_url = os.environ.get("DATABASE_URL")
    try:
        # Clear DATABASE_URL from environment
        os.environ.pop("DATABASE_URL", None)
        with pytest.raises(SystemExit) as exc_info:
            _validate_test_database_url()

        error_message = str(exc_info.value)
        assert "DATABASE_URL environment variable is not set" in error_message
        assert ".env.test" in error_message  # Should mention the fix
    finally:
        # Restore original DATABASE_URL
        if original_url is not None:
            os.environ["DATABASE_URL"] = original_url


@pytest.mark.unit
def test_validate_rejects_malformed_url_no_database(database_url_patch):
    """Test that malformed URL (missing database name) triggers pytest.exit()."""
    database_url_patch("postgresql://user:pass@host/")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "malformed" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_rejects_malformed_url_invalid_format(database_url_patch):
    """Test that completely invalid URL format triggers pytest.exit()."""
    database_url_patch("not-a-valid-url")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "malformed" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_ci_environment_with_test_database(database_url_patch):
    """Test that CI environment (CI=true) with test database pattern is accepted and prints confirmation."""
    database_url_patch("postgresql://user:pass@neon.tech/qteria-test", ci_value="true")
    # Should not raise pytest.exit() and should print confirmation
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_ci_environment_still_rejects_production(database_url_patch):
    """Test that CI environment does NOT bypass production database protection."""
    database_url_patch("postgresql://user:pass@host/production", ci_value="true")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_password_masking_in_production_error(database_url_patch):
    """Test that passwords are masked (****) in error messages when production database is detected."""
    database_url_patch("postgresql://user:secretpass123@host/production")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    error_message = str(exc_info.value)
    # Password should be masked
    assert "secretpass123" not in error_message
    assert "****" in error_message


@pytest.mark.unit
def test_password_masking_in_malformed_error(database_url_patch):
    """Test that passwords are masked in error messages for malformed URLs."""
    database_url_patch("postgresql://user:supersecret@host/")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    error_message = str(exc_info.value)
    # Password should be masked
    assert "supersecret" not in error_message
    assert "****" in error_message


@pytest.mark.unit
def test_accepts_postgres_protocol(database_url_patch):
    """Test that both 'postgresql://' and 'postgres://' protocols are accepted."""
    test_urls = [
        "postgresql://user:pass@host/qteria_test",
        "postgres://user:pass@host/qteria_test",
    ]

    for test_url in test_urls:
        database_url_patch(test_url)
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
def test_accepts_url_with_query_params(database_url_patch):
    """Test that URLs with query parameters (e.g., ?sslmode=require) are parsed correctly."""
    database_url_patch("postgresql://user:pass@host/qteria_test?sslmode=require&connect_timeout=10")
    # Should not raise pytest.exit()
    _validate_test_database_url()
