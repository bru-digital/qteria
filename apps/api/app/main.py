"""
FastAPI main application entry point.
"""

from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown logic.

    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    decorators with modern lifespan pattern (FastAPI 0.109+).

    Startup (before yield):
    - Log server timezone for debugging
    - Initialize Redis connection pool

    Shutdown (after yield):
    - Close Redis connection pool cleanly
    """
    # Startup
    # Log server timezone for debugging and monitoring
    try:
        import time

        # Check if we're in UTC timezone (no offset and no DST info)
        # time.timezone: offset from UTC in seconds (0 for UTC)
        # time.daylight: indicates if DST is in effect (0 means no DST)
        is_utc = time.timezone == 0 and not time.daylight

        if not is_utc:
            logger.info(
                "Server timezone is not UTC, but rate limiting uses UTC-aware datetimes (no issue)",
                extra={"timezone_offset_seconds": time.timezone},
            )
        else:
            logger.info("Server timezone: UTC")
    except Exception as e:
        # Non-critical: timezone detection failed (e.g., in some container environments)
        logger.debug(
            "Could not determine server timezone - not critical",
            extra={"error": str(e)},
        )

    # Initialize Redis client
    from app.core.dependencies import initialize_redis_client

    initialize_redis_client()

    yield

    # Shutdown
    # Close Redis connection pool
    from app.core.dependencies import _redis_client

    if _redis_client:
        try:
            # close() is sufficient for synchronous Redis client (waits for in-flight operations)
            # For async Redis client (redis.asyncio.Redis), would use: await _redis_client.aclose()
            _redis_client.close()
            logger.info("Redis connection pool closed successfully")
        except Exception as e:
            logger.error(
                "Error closing Redis connection pool", extra={"error": str(e)}, exc_info=True
            )


# Create FastAPI app with lifespan context manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
        dict: Service health status with ISO 8601 timestamp
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={"request_id": request_id})
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
