"""
Main FastAPI application entry point.
Configures the app with middleware, routers, and startup/shutdown events.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add the backend directories to Python path
backend_root = Path(__file__).parent.parent  # backend/
src_dir = Path(__file__).parent  # backend/src/
sys.path.insert(0, str(backend_root))  # For config module
sys.path.insert(0, str(src_dir))  # For src modules

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from api.v1.router import api_router
from api.websocket import router as websocket_router
from config.settings import settings
from core.cache import close_cache, init_cache
from core.database import close_db, init_db
from core.exceptions import setup_exception_handlers
from core.logging import setup_logging
from services.health import health_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting GenAI Chatbot Backend...")

    # Setup logging
    setup_logging()

    # Initialize database
    await init_db()

    # Initialize cache
    await init_cache()

    # Initialize health service
    await health_service.initialize()

    # Initialize default themes
    try:
        from startup.theme_init import startup_initialization
        await startup_initialization()
    except Exception as e:
        logger.error(f"Theme initialization failed: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down GenAI Chatbot Backend...")

    # Close connections
    await close_cache()
    await close_db()

    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        docs_url=settings.docs_url if settings.is_development else None,
        redoc_url=settings.redoc_url if settings.is_development else None,
        openapi_url=settings.openapi_url if settings.is_development else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **settings.cors_config,
    )

    # Add trusted host middleware for production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure as needed
        )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(websocket_router, prefix="/api/v1", tags=["WebSocket"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return await health_service.check_health()

    # Metrics endpoint
    if settings.enable_metrics:

        @app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            return JSONResponse(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "GenAI Chatbot Backend API",
            "version": settings.app_version,
            "docs_url": f"{settings.docs_url}" if settings.is_development else None,
        }

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
        reload_dirs=settings.reload_dirs if settings.is_development else None,
        reload_includes=settings.reload_extensions if settings.is_development else None,
    )
