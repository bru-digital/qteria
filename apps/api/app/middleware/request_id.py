"""Request ID middleware for distributed tracing and audit logging.

This middleware handles X-Request-ID header propagation:
- Accepts client-provided request IDs from X-Request-ID header
- Generates UUID if no client ID provided
- Stores request_id in request.state for use in error handlers and logging
- Returns request_id in response header for client-side tracking

This enables:
- End-to-end request tracing across frontend/backend
- Better debugging (clients can reference specific request IDs)
- SOC2/ISO 27001 compliance (complete audit trail)
- Correlation of logs across distributed systems

Usage in endpoints:
    request.state.request_id  # Access current request ID

Usage in client:
    fetch('/api/workflows', {
        headers: { 'X-Request-ID': 'client-generated-uuid' }
    })
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request ID propagation via X-Request-ID header.

    This middleware:
    1. Extracts X-Request-ID from incoming request header (if present)
    2. Generates new UUID if no header provided
    3. Stores request_id in request.state for access throughout request lifecycle
    4. Returns X-Request-ID in response header for client tracking

    The request_id is used by:
    - create_error_response() for audit trail
    - Structured logging for request correlation
    - Audit service for SOC2/ISO 27001 compliance
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process incoming request and add request ID.

        Args:
            request: Incoming FastAPI request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response with X-Request-ID header added
        """
        # Accept client-provided ID or generate new one
        # Client IDs enable frontend-to-backend request tracking
        request_id = request.headers.get("X-Request-ID")

        if not request_id:
            # Generate server-side UUID if client didn't provide one
            request_id = f"req_{uuid.uuid4()}"

        # Store in request state for access in endpoints and error handlers
        # This is the canonical location checked by create_error_response()
        request.state.request_id = request_id

        # Process request through remaining middleware/endpoint
        response = await call_next(request)

        # Return request_id in response header for client-side logging/debugging
        # Standard header name used by AWS, GCP, Stripe, etc.
        response.headers["X-Request-ID"] = request_id

        return response
