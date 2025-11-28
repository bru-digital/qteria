"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
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
    from uuid import uuid4

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
