"""
Tests for conftest.py fixtures and validation logic.

Verifies that autouse fixtures work correctly, don't interfere with unit tests,
and that DATABASE_URL validation logic works as expected.
"""

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
def test_validate_accepts_qteria_test(monkeypatch):
    """Test that database name 'qteria_test' is accepted without raising pytest.exit()."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/qteria_test")
    monkeypatch.setenv("CI", "")
    # Should not raise pytest.exit()
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_suffix_test_underscore(monkeypatch):
    """Test that database names ending with '_test' (e.g., 'myapp_test') are accepted."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/myapp_test")
    monkeypatch.setenv("CI", "")
    # Should not raise pytest.exit()
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_suffix_test_hyphen(monkeypatch):
    """Test that database names ending with '-test' (e.g., 'myapp-test') are accepted."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/myapp-test")
    monkeypatch.setenv("CI", "")
    # Should not raise pytest.exit()
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_accepts_qteria_test_uppercase(monkeypatch):
    """Test case-insensitive matching (e.g., 'QTERIA_TEST', 'Qteria-Test')."""
    test_urls = [
        "postgresql://user:pass@host/QTERIA_TEST",
        "postgresql://user:pass@host/Qteria-Test",
        "postgresql://user:pass@host/MyApp_TEST",
    ]

    for test_url in test_urls:
        monkeypatch.setenv("DATABASE_URL", test_url)
        monkeypatch.setenv("CI", "")
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
@pytest.mark.skip(
    reason="Test triggers pytest.exit() which interferes with cleanup - see issue #242"
)
def test_validate_rejects_neondb(monkeypatch):
    """Test that production database name 'neondb' triggers pytest.exit() with appropriate error."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/neondb")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    # Verify error message mentions production database
    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_postgres(monkeypatch):
    """Test that production database name 'postgres' triggers pytest.exit()."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/postgres")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_production(monkeypatch):
    """Test that database name 'production' triggers pytest.exit()."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/production")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_validate_rejects_missing_database_url(monkeypatch):
    """Test that missing DATABASE_URL environment variable triggers pytest.exit() with helpful error."""
    # Remove DATABASE_URL from environment
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    error_message = str(exc_info.value)
    assert "DATABASE_URL environment variable is not set" in error_message
    assert ".env.test" in error_message  # Should mention the fix


@pytest.mark.unit
def test_validate_rejects_malformed_url_no_database(monkeypatch):
    """Test that malformed URL (missing database name) triggers pytest.exit()."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "malformed" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_rejects_malformed_url_invalid_format(monkeypatch):
    """Test that completely invalid URL format triggers pytest.exit()."""
    monkeypatch.setenv("DATABASE_URL", "not-a-valid-url")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "malformed" in str(exc_info.value).lower()


@pytest.mark.unit
def test_validate_ci_environment_with_test_database(monkeypatch):
    """Test that CI environment (CI=true) with test database pattern is accepted and prints confirmation."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@neon.tech/qteria-test")
    monkeypatch.setenv("CI", "true")
    # Should not raise pytest.exit() and should print confirmation
    _validate_test_database_url()


@pytest.mark.unit
def test_validate_ci_environment_still_rejects_production(monkeypatch):
    """Test that CI environment does NOT bypass production database protection."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/production")
    monkeypatch.setenv("CI", "true")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    assert "PRODUCTION database" in str(exc_info.value)


@pytest.mark.unit
def test_password_masking_in_production_error(monkeypatch):
    """Test that passwords are masked (****) in error messages when production database is detected."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secretpass123@host/production")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    error_message = str(exc_info.value)
    # Password should be masked
    assert "secretpass123" not in error_message
    assert "****" in error_message


@pytest.mark.unit
def test_password_masking_in_malformed_error(monkeypatch):
    """Test that passwords are masked in error messages for malformed URLs."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:supersecret@host/")
    monkeypatch.setenv("CI", "")
    with pytest.raises(SystemExit) as exc_info:
        _validate_test_database_url()

    error_message = str(exc_info.value)
    # Password should be masked
    assert "supersecret" not in error_message
    assert "****" in error_message


@pytest.mark.unit
def test_accepts_postgres_protocol(monkeypatch):
    """Test that both 'postgresql://' and 'postgres://' protocols are accepted."""
    test_urls = [
        "postgresql://user:pass@host/qteria_test",
        "postgres://user:pass@host/qteria_test",
    ]

    for test_url in test_urls:
        monkeypatch.setenv("DATABASE_URL", test_url)
        monkeypatch.setenv("CI", "")
        # Should not raise pytest.exit()
        _validate_test_database_url()


@pytest.mark.unit
def test_accepts_url_with_query_params(monkeypatch):
    """Test that URLs with query parameters (e.g., ?sslmode=require) are parsed correctly."""
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://user:pass@host/qteria_test?sslmode=require&connect_timeout=10"
    )
    monkeypatch.setenv("CI", "")
    # Should not raise pytest.exit()
    _validate_test_database_url()
