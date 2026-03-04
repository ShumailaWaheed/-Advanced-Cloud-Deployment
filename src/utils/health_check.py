"""Health check utilities for the todo chatbot application."""

import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime
import logging
from .database import check_db_health
from ..config.db_config import DatabaseConfig


class HealthChecker:
    """Health checker for the application services."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()

    async def check_database(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            result = await check_db_health()
            return {
                "name": "database",
                "status": result["status"],
                "details": result.get("checks", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                "name": "database",
                "status": "unhealthy",
                "details": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_dependencies(self) -> List[Dict[str, Any]]:
        """Check all dependencies."""
        checks = []

        # Check database
        db_check = await self.check_database()
        checks.append(db_check)

        return checks

    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health status."""
        checks = await self.check_dependencies()

        # Overall status is healthy if all checks pass
        overall_status = "healthy" if all(check["status"] == "healthy" for check in checks) else "unhealthy"

        uptime_seconds = int(time.time() - self.start_time)

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": f"{uptime_seconds}s",
            "checks": checks
        }

    async def get_readiness_status(self) -> Dict[str, Any]:
        """Get readiness status for Kubernetes readiness probe."""
        # For readiness, we typically check if the service is ready to serve traffic
        # This might include checking if all dependencies are available

        checks = await self.check_dependencies()

        # Service is ready if database is healthy
        ready = all(check["status"] == "healthy" for check in checks)

        return {
            "ready": ready,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }

    async def get_liveness_status(self) -> Dict[str, Any]:
        """Get liveness status for Kubernetes liveness probe."""
        # For liveness, we check if the service itself is alive
        # Usually just checks that the service is responding

        uptime_seconds = int(time.time() - self.start_time)

        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": f"{uptime_seconds}s"
        }


# Global health checker instance
health_checker = HealthChecker()


async def get_health_status() -> Dict[str, Any]:
    """Get overall health status."""
    return await health_checker.get_overall_health()


async def get_readiness_status() -> Dict[str, Any]:
    """Get readiness status."""
    return await health_checker.get_readiness_status()


async def get_liveness_status() -> Dict[str, Any]:
    """Get liveness status."""
    return await health_checker.get_liveness_status()