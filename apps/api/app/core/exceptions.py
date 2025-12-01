"""Standardized error response handling for API contract compliance.

This module provides utilities for creating consistent error responses
that match the documented API contract in CLAUDE.md.

All errors must use the format:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "details": {...},  # optional
        "request_id": "req_abc123"
    }
}
"""

from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, Request


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[dict[str, Any]] = None,
    request: Optional[Request] = None,
    headers: Optional[dict[str, str]] = None,
) -> HTTPException:
    """Create standardized error response matching API contract.

    Args:
        status_code: HTTP status code (400, 401, 403, 404, etc.)
        error_code: Machine-readable error code (e.g., "INVALID_TOKEN")
        message: Human-readable error message
        details: Optional additional error context
        request: Optional Request object for extracting request_id
        headers: Optional HTTP headers to include in the response

    Returns:
        HTTPException with standardized error format

    Example:
        >>> raise create_error_response(
        ...     status_code=404,
        ...     error_code="RESOURCE_NOT_FOUND",
        ...     message="Workflow not found",
        ...     details={"workflow_id": "abc123"}
        ... )
    """
    # Extract request_id from request state, or generate new UUID
    request_id = (
        getattr(request.state, "request_id", None) if request else None
    ) or str(uuid4())

    error_body: dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
            "request_id": request_id,
        }
    }

    if details:
        error_body["error"]["details"] = details

    return HTTPException(status_code=status_code, detail=error_body, headers=headers)
