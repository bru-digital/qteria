"""
Health check endpoint for monitoring and load balancers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check_detailed(db: Session = Depends(get_db)):
    """
    Detailed health check with database connectivity test.

    Returns:
        dict: Comprehensive health status including database connection
    """
    health_status = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "unknown",
    }

    # Test database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = f"disconnected: {str(e)}"

    return health_status
