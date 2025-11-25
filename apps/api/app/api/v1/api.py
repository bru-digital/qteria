"""
API v1 router aggregating all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, organizations, workflows

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(organizations.router, tags=["Organizations"])
api_router.include_router(workflows.router, tags=["Workflows"])
