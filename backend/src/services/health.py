"""
Health check service for monitoring application and dependency status.
"""

import time
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from config.settings import settings
from core.cache import check_cache_health
from core.database import check_database_health


class HealthService:
    """Service for health checks and monitoring."""

    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.health_checks: dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize health service."""
        logger.info("Health service initialized")

    async def check_health(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        start_time = time.time()

        # Basic application info
        uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(uptime_seconds, 2),
            "version": settings.app_version,
            "environment": settings.environment,
            "checks": {},
        }

        # Check individual components
        checks = await self._run_health_checks()
        health_status["checks"] = checks

        # Determine overall status
        failed_checks = [
            name for name, status in checks.items() if not status["healthy"]
        ]
        if failed_checks:
            health_status["status"] = "unhealthy"
            health_status["failed_checks"] = failed_checks

        # Add timing
        health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

        return health_status

    async def _run_health_checks(self) -> dict[str, dict[str, Any]]:
        """Run all health checks."""
        checks = {}

        # Database health check
        checks["database"] = await self._check_database()

        # Cache health check
        checks["cache"] = await self._check_cache()

        # Add more health checks as needed

        return checks

    async def _check_database(self) -> dict[str, Any]:
        """Check database health."""
        start_time = time.time()

        try:
            is_healthy = await check_database_health()
            response_time = round((time.time() - start_time) * 1000, 2)

            return {
                "healthy": is_healthy,
                "response_time_ms": response_time,
                "message": "Database connection successful"
                if is_healthy
                else "Database connection failed",
            }
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Database health check failed: {e}")

            return {
                "healthy": False,
                "response_time_ms": response_time,
                "message": f"Database health check error: {str(e)}",
                "error": str(e),
            }

    async def _check_cache(self) -> dict[str, Any]:
        """Check cache health."""
        start_time = time.time()

        try:
            is_healthy = await check_cache_health()
            response_time = round((time.time() - start_time) * 1000, 2)

            return {
                "healthy": is_healthy,
                "response_time_ms": response_time,
                "message": "Cache connection successful"
                if is_healthy
                else "Cache connection failed",
            }
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Cache health check failed: {e}")

            return {
                "healthy": False,
                "response_time_ms": response_time,
                "message": f"Cache health check error: {str(e)}",
                "error": str(e),
            }

    async def check_readiness(self) -> dict[str, Any]:
        """Check if application is ready to serve requests."""
        checks = await self._run_health_checks()

        # Application is ready if all critical services are healthy
        critical_services = ["database", "cache"]
        ready = all(
            checks.get(service, {}).get("healthy", False)
            for service in critical_services
        )

        return {
            "ready": ready,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {k: v for k, v in checks.items() if k in critical_services},
        }

    async def check_liveness(self) -> dict[str, Any]:
        """Check if application is alive (basic health check)."""
        return {
            "alive": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(
                (datetime.now(timezone.utc) - self.start_time).total_seconds(), 2
            ),
        }


# Global health service instance
health_service = HealthService()
