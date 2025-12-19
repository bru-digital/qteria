"""
Tests for conftest.py fixtures.

Verifies that autouse fixtures work correctly and don't interfere with unit tests.
"""

import pytest


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
