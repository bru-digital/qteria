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
- DbSession: Type alias for database session dependency (Annotated[Session, Depends(get_db)])
- RedisClient: Type alias for Redis client dependency
"""
import logging
import threading
from typing import Annotated, Generator, Optional

from fastapi import Depends
from redis import Redis, ConnectionError as RedisConnectionError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import SessionLocal

logger = logging.getLogger(__name__)

# Global Redis client instance (connection pooling)
_redis_client: Optional[Redis] = None
_redis_client_lock = threading.Lock()


def get_redis() -> Generator[Redis, None, None]:
    """
    Dependency function for FastAPI to get Redis client connections.

    Provides Redis client for rate limiting, caching, and background job queuing.
    Implements graceful degradation - if Redis is unavailable, yields None to allow
    endpoints to continue functioning (fail-open for availability over strict enforcement).

    Thread-safe initialization using lock to prevent race conditions during startup
    when multiple concurrent requests arrive before Redis client is initialized.

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
        Graceful degradation: Returns None if Redis unavailable (logged as warning).
    """
    global _redis_client

    # Initialize Redis client on first use (lazy loading with thread safety)
    if _redis_client is None:
        with _redis_client_lock:
            # Double-check pattern: verify client is still None after acquiring lock
            # (another thread might have initialized it while we were waiting)
            if _redis_client is None:
                try:
                    redis_url = settings.REDIS_URL
                    if not redis_url:
                        logger.warning(
                            "REDIS_URL not configured - Redis features disabled (rate limiting will not be enforced)"
                        )
                        # Don't set _redis_client, allow retry on next request
                        yield None
                        return

                    _redis_client = Redis.from_url(
                        redis_url,
                        decode_responses=True,  # Return strings instead of bytes
                        socket_timeout=5,       # 5 second timeout for operations
                        socket_connect_timeout=2,  # 2 second timeout for connection
                        max_connections=10,     # Connection pool size (10-20 for typical API)
                        health_check_interval=30,  # Auto-reconnect on connection loss (seconds)
                    )

                    # Test connection
                    _redis_client.ping()
                    logger.info("Redis connection established successfully", extra={"redis_url": redis_url})

                except RedisConnectionError as e:
                    logger.error(
                        "Failed to connect to Redis - Redis features disabled",
                        extra={"error": str(e), "redis_url": settings.REDIS_URL},
                        exc_info=True,
                    )
                    # Don't set _redis_client to None, keep it uninitialized
                    # This allows retry on next request
                    yield None
                    return
                except Exception as e:
                    logger.error(
                        "Unexpected error initializing Redis client",
                        extra={"error": str(e)},
                        exc_info=True,
                    )
                    # Don't set _redis_client to None, keep it uninitialized
                    # This allows retry on next request
                    yield None
                    return

    # Yield existing Redis client with connection verification
    try:
        if _redis_client:
            # Test connection before yielding to detect stale connections
            _redis_client.ping()
        yield _redis_client
    except RedisConnectionError:
        logger.warning(
            "Redis connection lost during request - returning None for graceful degradation"
        )
        # Reset to None to trigger reconnection attempt on next request
        _redis_client = None
        yield None


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
    request: "Request" = None,
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
    from fastapi import HTTPException, Request, status
    from app.core.auth import AuthenticatedUser
    from app.services.audit import AuditService

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

    # Redis key for rate limiting (per user, per hour)
    rate_limit_key = f"rate_limit:upload:{current_user.id}:{hour_bucket}"

    try:
        # DESIGN RATIONALE: Increment-first approach prevents TOCTOU race conditions
        # Instead of check-then-increment (vulnerable to race conditions where multiple
        # concurrent requests could all see count=99 and proceed), we increment first
        # atomically, then check. If exceeded, we rollback the increment.

        # Increment counter atomically FIRST (prevents race conditions)
        # Use Redis pipeline to ensure atomicity of INCRBY + EXPIRE
        pipe = redis.pipeline()
        pipe.incrby(rate_limit_key, file_count)
        pipe.expire(rate_limit_key, 3600)  # 1 hour TTL (prevent memory leak)
        result = pipe.execute()

        # Get the new count from pipeline result (first command result)
        new_count = result[0]

        # Check if this upload exceeded limit (AFTER increment)
        if new_count > settings.UPLOAD_RATE_LIMIT_PER_HOUR:
            # Rollback the increment since we're rejecting this upload
            redis.decrby(rate_limit_key, file_count)
            # Ensure TTL exists after rollback (edge case: key expired between INCRBY and DECRBY)
            redis.expire(rate_limit_key, 3600)

            # Calculate seconds until rate limit resets (next hour)
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            retry_after_seconds = int((next_hour - now).total_seconds())

            # Current count before this upload attempt
            current_count = new_count - file_count

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
            reset_time = next_hour
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
    except Exception as e:
        # Redis error - log and allow upload (graceful degradation)
        logger.error(
            "Failed to check upload rate limit - allowing upload",
            extra={
                "user_id": str(current_user.id),
                "file_count": file_count,
                "error": str(e),
            },
            exc_info=True,
        )
        # Fail open: Allow upload if rate limiting fails
        return 0


# Type alias for database dependency
DbSession = Annotated[Session, Depends(get_db)]

# Type alias for Redis dependency
RedisClient = Annotated[Optional[Redis], Depends(get_redis)]
