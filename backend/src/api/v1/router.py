"""
Main API router that includes all sub-routers for version 1 of the API.
"""

from fastapi import APIRouter

from api.admin import router as admin_router

# Import routers
from api.auth import router as auth_router
from api.chat import router as chat_router
from api.documents import router as documents_router
from api.themes_simple import router as themes_router

# Create main API router
api_router = APIRouter()


# Health check endpoints (simple versions)
@api_router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    from services.health import health_service

    return await health_service.check_liveness()


@api_router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    from services.health import health_service

    return await health_service.check_readiness()


# Placeholder endpoints - we'll create the full implementations
@api_router.get("/status")
async def status():
    """API status endpoint."""
    from config.settings import settings

    return {
        "api_version": "v1",
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
    }


# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(themes_router, prefix="/themes", tags=["Themes"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
