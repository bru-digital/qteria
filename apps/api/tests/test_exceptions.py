"""Unit tests for standardized error response handling."""

from fastapi import Request
from unittest.mock import MagicMock, Mock
from uuid import UUID

from app.core.exceptions import create_error_response


def test_create_error_response_basic():
    """Test basic error response without details or request."""
    error = create_error_response(
        status_code=400,
        error_code="VALIDATION_ERROR",
        message="Invalid input",
    )

    assert error.status_code == 400
    assert error.detail["error"]["code"] == "VALIDATION_ERROR"
    assert error.detail["error"]["message"] == "Invalid input"
    assert "request_id" in error.detail["error"]
    # Validate request_id is a valid UUID
    UUID(error.detail["error"]["request_id"])


def test_create_error_response_with_details():
    """Test error response with additional details."""
    error = create_error_response(
        status_code=404,
        error_code="RESOURCE_NOT_FOUND",
        message="Workflow not found",
        details={"workflow_id": "abc123"},
    )

    assert error.detail["error"]["details"] == {"workflow_id": "abc123"}


def test_create_error_response_with_request_state():
    """Test error response uses request_id from request state."""

    # Create a simple state object with instance attribute
    class State:
        def __init__(self):
            self.request_id = "req_test_123"

    # Use Mock instead of MagicMock to avoid spec restrictions
    mock_request = Mock()
    mock_request.state = State()

    error = create_error_response(
        status_code=401,
        error_code="INVALID_TOKEN",
        message="Token expired",
        request=mock_request,
    )

    assert error.detail["error"]["request_id"] == "req_test_123"


def test_create_error_response_generates_uuid_when_no_request():
    """Test error response generates UUID when request_id not in state."""
    mock_request = MagicMock(spec=Request)
    # Simulate no request_id in state by raising AttributeError
    type(mock_request.state).request_id = property(
        lambda self: (_ for _ in ()).throw(AttributeError)
    )

    error = create_error_response(
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="Unexpected error",
        request=mock_request,
    )

    # Should generate a valid UUID
    UUID(error.detail["error"]["request_id"])


def test_error_response_structure_matches_contract():
    """Test error response matches documented API contract format."""
    error = create_error_response(
        status_code=422,
        error_code="INSUFFICIENT_CREDITS",
        message="Not enough credits",
        details={"balance": 0, "required": 100},
    )

    # Verify exact structure from CLAUDE.md
    assert "error" in error.detail
    assert "code" in error.detail["error"]
    assert "message" in error.detail["error"]
    assert "request_id" in error.detail["error"]
    assert "details" in error.detail["error"]

    # Should NOT have 'detail' wrapper (old format)
    assert "detail" not in error.detail.get("error", {})


def test_create_error_response_without_details():
    """Test error response without optional details field."""
    error = create_error_response(
        status_code=403,
        error_code="INSUFFICIENT_PERMISSIONS",
        message="Access denied",
    )

    # details field should not be present when not provided
    assert "details" not in error.detail["error"]


def test_create_error_response_all_standard_error_codes():
    """Test error response with all documented error codes from CLAUDE.md."""
    error_codes = [
        ("VALIDATION_ERROR", 400),
        ("INVALID_TOKEN", 401),
        ("INSUFFICIENT_PERMISSIONS", 403),
        ("RESOURCE_NOT_FOUND", 404),
        ("INSUFFICIENT_CREDITS", 422),
        ("RATE_LIMIT_EXCEEDED", 429),
    ]

    for code, status_code in error_codes:
        error = create_error_response(
            status_code=status_code,
            error_code=code,
            message=f"Test {code}",
        )

        assert error.status_code == status_code
        assert error.detail["error"]["code"] == code
        assert "request_id" in error.detail["error"]


def test_create_error_response_allows_custom_headers():
    """Test that HTTPException can have custom headers added after creation."""
    error = create_error_response(
        status_code=401,
        error_code="INVALID_TOKEN",
        message="Could not validate credentials",
    )

    # Headers can be added after creation (pattern used in auth.py)
    error.headers = {"WWW-Authenticate": "Bearer"}

    assert error.status_code == 401
    assert error.headers == {"WWW-Authenticate": "Bearer"}
    # Verify error body format is still correct
    assert error.detail["error"]["code"] == "INVALID_TOKEN"


def test_create_error_response_complex_details():
    """Test error response with complex nested details."""
    error = create_error_response(
        status_code=413,
        error_code="FILE_TOO_LARGE",
        message="File exceeds maximum size",
        details={
            "file_size_bytes": 52428800,
            "max_size_bytes": 52428800,
            "file_name": "test.pdf",
        },
    )

    assert error.detail["error"]["details"]["file_size_bytes"] == 52428800
    assert error.detail["error"]["details"]["max_size_bytes"] == 52428800
    assert error.detail["error"]["details"]["file_name"] == "test.pdf"


def test_create_error_response_uuid_uniqueness():
    """Test that generated request_ids are unique."""
    error1 = create_error_response(
        status_code=400,
        error_code="ERROR_1",
        message="First error",
    )

    error2 = create_error_response(
        status_code=400,
        error_code="ERROR_2",
        message="Second error",
    )

    request_id_1 = error1.detail["error"]["request_id"]
    request_id_2 = error2.detail["error"]["request_id"]

    # Request IDs should be different
    assert request_id_1 != request_id_2
    # Both should be valid UUIDs
    UUID(request_id_1)
    UUID(request_id_2)
