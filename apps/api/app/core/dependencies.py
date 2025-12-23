"""
FastAPI dependencies for database sessions, authentication, and multi-tenancy.

This module provides:
- Database session dependency with automatic cleanup
- Redis client dependency for rate limiting and caching
- Organization-scoped database queries for multi-tenant isolation
- Type aliases for common dependency patterns

Exports:
- get_db: Database session dependency
- get_redis: Redis client dependency
- initialize_redis_client: Initialize Redis connection at startup
- DbSession: Type alias for database session dependency (Annotated[Session, Depends(get_db)])
- RedisClient: Type alias for Redis client dependency
"""

from __future__ import annotations

import logging
import sys
from typing import Annotated, TYPE_CHECKING
from collections.abc import Generator

from fastapi import Depends, Request
from redis import Redis, ConnectionError as RedisConnectionError, RedisError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.base import SessionLocal

if TYPE_CHECKING:
    from app.core.auth import AuthenticatedUser

logger = logging.getLogger(__name__)

# Global Redis client instance (connection pooling)
_redis_client: Redis | None = None


def initialize_redis_client() -> None:
    """
    Initialize global Redis client at application startup.

    Called from FastAPI startup event to establish Redis connection once,
    eliminating lock contention on every request (previously used double-check
    locking pattern which created bottleneck under high concurrency).

    Benefits of startup initialization:
    - No lock contention on request path (was bottleneck at 100+ req/s)
    - Fail-fast: Redis connection issues discovered at startup, not first request
    - Simpler code: No thread-safety concerns in get_redis()

    Graceful degradation: If Redis unavailable, sets _redis_client to None
    to allow application to start (rate limiting disabled, logged as warning).

    Note:
        This function is NOT thread-safe (doesn't need to be - called once at startup).
        Called from app.main:app.on_event("startup") before any requests are handled.
    """
    global _redis_client

    settings = get_settings()
    redis_url = settings.REDIS_URL
    if not redis_url:
        logger.warning(
            "REDIS_URL not configured - Redis features disabled (rate limiting will not be enforced)"
        )
        # Keep _redis_client as None for graceful degradation
        return

    # Redis URL is configured, attempt connection
    try:
        _redis_client = Redis.from_url(
            redis_url,
            decode_responses=True,  # Return strings instead of bytes
            socket_timeout=5,  # 5 second timeout for operations
            socket_connect_timeout=2,  # 2 second timeout for connection
            max_connections=settings.REDIS_MAX_CONNECTIONS,  # Connection pool size
            socket_keepalive=settings.REDIS_SOCKET_KEEPALIVE,  # Enable TCP keepalive
            socket_keepalive_options=settings.REDIS_SOCKET_KEEPALIVE_OPTIONS,  # Platform-specific keepalive options
            health_check_interval=30,  # Auto-reconnect on connection loss (seconds)
        )

        # Test connection
        if _redis_client is not None:
            _redis_client.ping()
        logger.info("Redis connection established successfully", extra={"redis_url": redis_url})

    except RedisConnectionError as e:
        # Detect test environment: check settings.ENVIRONMENT or pytest in sys.modules
        # This prevents ERROR-level Redis logs from polluting test output
        is_test = settings.ENVIRONMENT == "test" or "pytest" in sys.modules

        if is_test:
            # Test mode: log at DEBUG level (Redis is optional for tests)
            logger.debug(
                "Redis unavailable in test environment - rate limiting disabled",
                extra={"error": str(e), "redis_url": settings.REDIS_URL},
            )
        else:
            # Production/development: log at ERROR level (Redis should be available)
            logger.error(
                "Failed to connect to Redis - Redis features disabled",
                extra={"error": str(e), "redis_url": settings.REDIS_URL},
                exc_info=True,
            )
        # Keep _redis_client as None for graceful degradation
        _redis_client = None
    except Exception as e:
        # Detect test environment for unexpected errors too
        is_test = settings.ENVIRONMENT == "test" or "pytest" in sys.modules

        if is_test:
            # Test mode: log at DEBUG level
            logger.debug(
                "Unexpected error initializing Redis client in test environment",
                extra={"error": str(e)},
            )
        else:
            # Production/development: log at ERROR level
            logger.error(
                "Unexpected error initializing Redis client",
                extra={"error": str(e)},
                exc_info=True,
            )
        # Keep _redis_client as None for graceful degradation
        _redis_client = None


def get_redis() -> Generator[Redis | None, None, None]:
    """
    Dependency function for FastAPI to get Redis client connections.

    Provides Redis client for rate limiting, caching, and background job queuing.
    Implements graceful degradation - if Redis is unavailable, yields None to allow
    endpoints to continue functioning (fail-open for availability over strict enforcement).

    Redis client is initialized once at application startup (see initialize_redis_client),
    eliminating lock contention on every request for better performance under high load.

    Usage:
        @app.post("/items")
        def create_item(redis: Redis = Depends(get_redis)):
            if redis:
                redis.incr("item_count")
            return {"status": "created"}

    Yields:
        Redis: Redis client connection, or None if Redis unavailable

    Note:
        Connection is reused via connection pooling for performance.
        Graceful degradation: Returns None if Redis unavailable (logged at startup).
    """
    # Yield pre-initialized Redis client (no locking needed - initialized at startup)
    # Connection health checked by pool's health_check_interval
    # If connection fails during operation, graceful degradation in
    # check_upload_rate_limit() will catch and log the error
    yield _redis_client


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database sessions.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: SQLAlchemy database session

    Note:
        Session is automatically closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_upload_rate_limit(
    current_user: "AuthenticatedUser",  # Forward reference to avoid circular import
    redis: RedisClient,
    db: DbSession,
    file_count: int = 1,
    request: Request | None = None,
) -> int:
    """
    Check if user has exceeded upload rate limit (100 uploads per hour).

    Implements Redis-based rate limiting with graceful degradation:
    - If Redis unavailable: Log warning and allow upload (fail-open for availability)
    - If limit exceeded: Raise 429 HTTPException with proper headers
    - Batch uploads: Each file counts toward the limit (20 files = 20 uploads)

    Rate limit implementation:
    - Key pattern: rate_limit:upload:{user_id}:{hour_bucket}
    - Counter: Atomically incremented with Redis INCRBY (prevents race conditions)
    - TTL: 1 hour (3600 seconds) to ensure automatic cleanup
    - Hour bucket: Format YYYY-MM-DD-HH for hourly reset

    Args:
        current_user: Authenticated user from JWT
        redis: Redis client (can be None if Redis unavailable)
        db: Database session for audit logging
        file_count: Number of files being uploaded (default 1)
        request: FastAPI request for extracting request_id

    Returns:
        int: Updated upload count after incrementing (or 0 if Redis unavailable)

    Raises:
        HTTPException: 429 if rate limit exceeded with retry-after header

    Note:
        Graceful degradation: If Redis unavailable, allows upload (logged as warning)
        Uses increment-first approach to prevent TOCTOU race conditions
    """
    from datetime import datetime, timedelta, timezone
    from fastapi import HTTPException, status
    from app.services.audit import AuditService

    settings = get_settings()

    # Graceful degradation: If Redis unavailable, log warning and allow upload
    if redis is None:
        logger.warning(
            "Upload rate limit check skipped - Redis unavailable",
            extra={
                "user_id": str(current_user.id),
                "organization_id": str(current_user.organization_id),
                "file_count": file_count,
            },
        )
        return 0

    # Get current hour bucket (e.g., "2024-11-30-14" for 2PM on Nov 30, 2024)
    now = datetime.now(timezone.utc)
    hour_bucket = now.strftime("%Y-%m-%d-%H")

    # Calculate reset time (next hour boundary) for EXPIREAT
    # This ensures rate limit always resets at the next hour boundary,
    # regardless of when requests arrive (prevents TTL reset bugs with EXPIRE)
    reset_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    reset_timestamp = int(reset_time.timestamp())

    # Redis key for rate limiting (per user, per hour)
    rate_limit_key = f"rate_limit:upload:{current_user.id}:{hour_bucket}"

    try:
        # DESIGN RATIONALE: Increment-first approach prevents TOCTOU race conditions
        # Instead of check-then-increment (vulnerable to race conditions where multiple
        # concurrent requests could all see count=99 and proceed), we increment first
        # atomically, then check. If exceeded, we rollback the increment.

        # Increment counter atomically FIRST (prevents race conditions)
        # Use Redis pipeline to ensure atomicity of INCRBY + EXPIREAT
        pipe = redis.pipeline()
        pipe.incrby(rate_limit_key, file_count)
        pipe.expireat(
            rate_limit_key, reset_timestamp
        )  # Absolute timestamp (prevents TTL reset bugs)
        result = pipe.execute()

        # Get the new count from pipeline result (first command result)
        new_count = result[0]

        # Check if this upload exceeded limit (AFTER increment)
        if new_count > settings.UPLOAD_RATE_LIMIT_PER_HOUR:
            # Rollback the increment atomically using pipeline (prevents race conditions)
            # Without pipeline: concurrent requests could increment between DECRBY and EXPIREAT,
            # leading to incorrect counts or lost TTL
            rollback_pipe = redis.pipeline()
            rollback_pipe.decrby(rate_limit_key, file_count)
            rollback_pipe.expireat(
                rate_limit_key, reset_timestamp
            )  # EXPIREAT is idempotent - no NX needed
            rollback_pipe.get(rate_limit_key)  # Fetch actual count after rollback
            rollback_results = rollback_pipe.execute()

            # Get actual count after rollback (third command result)
            # More accurate than new_count - file_count due to potential concurrent requests
            # Fallback to new_count - file_count if key doesn't exist (e.g., expired between operations)
            # This preserves semantic meaning: user exceeded limit even if Redis key disappeared
            if rollback_results[2]:
                current_count = int(rollback_results[2])
            else:
                # Fallback: key expired between increment and rollback
                current_count = new_count - file_count
                logger.warning(
                    "Rate limit key expired between increment and rollback - using fallback count",
                    extra={
                        "user_id": str(current_user.id),
                        "organization_id": str(current_user.organization_id),
                        "fallback_count": current_count,
                        "new_count": new_count,
                        "file_count": file_count,
                        "hour_bucket": hour_bucket,
                    },
                )

            # Calculate seconds until rate limit resets (use pre-calculated reset_time)
            retry_after_seconds = int((reset_time - now).total_seconds())

            logger.warning(
                "Upload rate limit exceeded",
                extra={
                    "user_id": str(current_user.id),
                    "organization_id": str(current_user.organization_id),
                    "current_count": current_count,
                    "limit": settings.UPLOAD_RATE_LIMIT_PER_HOUR,
                    "retry_after_seconds": retry_after_seconds,
                },
            )

            # Audit log for security monitoring (potential abuse)
            AuditService.log_event(
                db=db,
                action="rate_limit.exceeded",
                organization_id=current_user.organization_id,
                user_id=current_user.id,
                resource_type="document",
                metadata={
                    "limit_type": "upload",
                    "current_count": current_count,
                    "limit": settings.UPLOAD_RATE_LIMIT_PER_HOUR,
                    "hour_bucket": hour_bucket,
                },
                request=request,
            )

            # Raise 429 with standardized error format and rate limit headers
            from app.core.exceptions import create_error_response

            # Prepare rate limit headers for 429 response
            # API contract compliance: product-guidelines/08-api-contracts.md:838-846
            #
            # NOTE: Minor race condition possible with concurrent requests.
            # Headers show count at time of THIS request's increment, but concurrent
            # requests may have incremented the counter since then. This is acceptable
            # as rate limit ENFORCEMENT (INCRBY) is atomic - only header values may
            # be briefly stale. The increment-first approach guarantees no request
            # bypasses the rate limit, even under concurrent load.
            rate_limit_headers = {
                "X-RateLimit-Limit": str(settings.UPLOAD_RATE_LIMIT_PER_HOUR),
                "X-RateLimit-Remaining": "0",  # No remaining capacity when limit exceeded
                "X-RateLimit-Reset": str(reset_timestamp),
                "Retry-After": str(retry_after_seconds),
            }

            raise create_error_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                error_code="RATE_LIMIT_EXCEEDED",
                message=f"Upload rate limit exceeded. Maximum {settings.UPLOAD_RATE_LIMIT_PER_HOUR} uploads per hour. Try again in {retry_after_seconds} seconds.",
                details={
                    "limit": settings.UPLOAD_RATE_LIMIT_PER_HOUR,
                    "current_count": current_count,
                    "retry_after_seconds": retry_after_seconds,
                    "reset_time": reset_time.isoformat() + "Z",
                },
                request=request,
                headers=rate_limit_headers,
            )

        logger.debug(
            "Upload rate limit check passed",
            extra={
                "user_id": str(current_user.id),
                "file_count": file_count,
                "new_count": new_count,
                "limit": settings.UPLOAD_RATE_LIMIT_PER_HOUR,
                "hour_bucket": hour_bucket,
            },
        )

        return new_count

    except HTTPException:
        # Re-raise HTTP exceptions (rate limit exceeded)
        raise
    except (RedisConnectionError, RedisError) as e:
        # Redis error - log and allow upload (graceful degradation)
        # Expected errors: connection failures, timeouts, pipeline errors
        logger.error(
            "Failed to check upload rate limit - allowing upload (graceful degradation)",
            extra={
                "user_id": str(current_user.id),
                "file_count": file_count,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        # Fail open: Allow upload if rate limiting fails
        return 0
    except (ValueError, TypeError, KeyError) as e:
        # Data validation errors - log and allow upload
        # Examples: invalid Redis response format, missing pipeline result
        logger.error(
            "Data validation error in rate limit check - allowing upload",
            extra={
                "user_id": str(current_user.id),
                "file_count": file_count,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        return 0
    except Exception as e:
        # Unexpected error - should be investigated
        # This catch-all ensures availability but logs at ERROR level for investigation
        # Fail open consistently across all environments for availability
        # (logging infrastructure should alert on ERROR-level logs for investigation)
        logger.error(
            "Unexpected error in rate limit check - allowing upload (requires investigation)",
            extra={
                "user_id": str(current_user.id),
                "file_count": file_count,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        # Always fail open for availability (consistent behavior across environments)
        return 0


# Type alias for database dependency
DbSession = Annotated[Session, Depends(get_db)]

# Type alias for Redis dependency
RedisClient = Annotated[Redis | None, Depends(get_redis)]
