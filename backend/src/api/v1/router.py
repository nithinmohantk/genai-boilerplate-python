"""
Main API router that includes all sub-routers for version 1 of the API.
"""

from fastapi import APIRouter

# Import routers (we'll create these next)
# from api.v1.endpoints import chat, documents, health, admin

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
        "status": "operational"
    }

# TODO: Include other routers when created
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
# api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
