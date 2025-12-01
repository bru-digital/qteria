"""
FastAPI main application entry point.
"""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.middleware.multi_tenant import MultiTenantMiddleware
from app.middleware.request_id import RequestIDMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
async def validate_server_timezone():
    """
    Validate that server is running in UTC timezone.

    Rate limiting hour buckets use UTC time calculation via datetime.now(timezone.utc),
    which is timezone-aware and works correctly regardless of system timezone.
    However, running in UTC is recommended for consistency and to avoid confusion.

    This validation logs a warning if the server is not running in UTC, but does NOT
    fail in production because the code uses timezone-aware datetimes that work correctly
    regardless of system timezone.
    """
    # Check if local timezone is UTC
    now = datetime.now()
    local_tz = now.astimezone().tzinfo

    # Compare timezone offset with UTC
    # UTC offset should be 0 (no offset from UTC)
    utc_offset = now.astimezone().utcoffset()

    # If utc_offset != 0, the server is NOT running in UTC
    # Log warning but don't fail - code uses datetime.now(timezone.utc) which is already correct
    if utc_offset is None or utc_offset.total_seconds() != 0:
        logger.warning(
            f"Server is not running in UTC timezone (current: {local_tz}, offset: {utc_offset}). "
            f"While the code uses UTC-aware datetimes, running in UTC is recommended. "
            f"Set TZ=UTC environment variable if preferred."
        )
    else:
        logger.info(
            "Server timezone validation passed",
            extra={"timezone": str(local_tz), "utc_offset": utc_offset}
        )


@app.on_event("shutdown")
async def close_redis():
    """
    Close Redis connection on application shutdown.

    Prevents potential memory leaks by properly closing the global Redis client
    connection pool when the application shuts down.

    Note: Low impact in production (processes are recycled), but good practice
    for clean shutdown and local development environments.
    """
    from app.core.dependencies import _redis_client

    if _redis_client:
        try:
            _redis_client.close()
            logger.info("Redis connection closed successfully")
        except Exception as e:
            logger.error(
                "Error closing Redis connection",
                extra={"error": str(e)},
                exc_info=True
            )


# Request ID middleware
# Sets request.state.request_id from X-Request-ID header or generates UUID
# Must run BEFORE other middleware to ensure request_id is available for error handling
# Client can provide: fetch('/api', { headers: { 'X-Request-ID': 'uuid' } })
app.add_middleware(RequestIDMiddleware)

# Multi-tenant isolation middleware
# Ensures organization context is properly reset after each request
# to prevent context leakage between requests (safety net for contextvars)
# NOTE: Added BEFORE CORS so it executes AFTER CORS validation (middleware runs in reverse)
app.add_middleware(MultiTenantMiddleware)

# Configure CORS
# Runs first on request path to validate origins before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1": settings.API_V1_PREFIX,
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Custom HTTPException handler to unwrap detail field
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Custom HTTPException handler to unwrap the detail field.

    FastAPI automatically wraps HTTPException.detail in {"detail": ...},
    but our create_error_response already creates {"error": {...}} format.
    This handler unwraps the detail field to return {"error": {...}} directly.

    DOUBLE-WRAPPING PREVENTION:
    Without this handler, errors would be double-wrapped:
    - create_error_response() creates: {"error": {"code": "...", "message": "..."}}
    - FastAPI wraps it again: {"detail": {"error": {"code": "...", "message": "..."}}}

    This handler prevents double-wrapping by:
    1. Checking if exc.detail is a dict (from create_error_response)
    2. If yes, returning it directly as {"error": {...}} (unwrapped)
    3. If no (plain string from direct HTTPException), wrapping it in {"error": {...}}

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse: Error response in standardized format
    """
    # If detail is already a dict (from create_error_response), return it directly
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # Otherwise, create standardized error format
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "request_id": getattr(request.state, "request_id", str(uuid4())),
            }
        },
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse: Error response with request_id for audit trail
    """
    # Extract request_id from request state (set by RequestIDMiddleware)
    # Fall back to generating a new UUID if not present
    request_id = getattr(request.state, "request_id", str(uuid4()))

    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred. Please try again later.",
                "request_id": request_id,
                "details": str(exc) if settings.ENVIRONMENT == "development" else None,
            }
        },
    )


# Include API v1 router
from app.api.v1.api import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
    )
