"""
Service health monitoring client.
"""
import httpx
from typing import Dict, Any, List
from app.config import settings


class ServiceMonitor:
    """
    Monitor health of all microservices.
    """

    def __init__(self):
        self.services = {
            "audit-service": f"{settings.AUDIT_SERVICE_URL}/audit/health",
            "file-service": f"{settings.FILE_SERVICE_URL}/health",
            "embedding-service": f"{settings.EMBEDDING_SERVICE_URL}/health",
            "rag-service": f"{settings.RAG_SERVICE_URL}/health",
        }
        self.timeout = 5.0

    async def check_service_health(self, service_name: str, health_url: str) -> Dict[str, Any]:
        """
        Check health of a single service.

        Args:
            service_name: Name of the service
            health_url: Health check URL

        Returns:
            Health status
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(health_url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "service": service_name,
                        "status": data.get("status", "healthy"),
                        "url": health_url,
                        "details": data
                    }
                else:
                    return {
                        "service": service_name,
                        "status": "unhealthy",
                        "url": health_url,
                        "error": f"HTTP {response.status_code}"
                    }
        except httpx.TimeoutException:
            return {
                "service": service_name,
                "status": "timeout",
                "url": health_url,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "url": health_url,
                "error": str(e)
            }

    async def check_all_services(self) -> List[Dict[str, Any]]:
        """
        Check health of all registered services.

        Returns:
            List of health statuses for all services
        """
        results = []
        for service_name, health_url in self.services.items():
            result = await self.check_service_health(service_name, health_url)
            results.append(result)
        return results

    async def get_system_overview(self) -> Dict[str, Any]:
        """
        Get overall system health overview.

        Returns:
            System overview with health statistics
        """
        services_health = await self.check_all_services()

        healthy_count = sum(1 for s in services_health if s["status"] == "healthy")
        total_count = len(services_health)

        return {
            "total_services": total_count,
            "healthy_services": healthy_count,
            "unhealthy_services": total_count - healthy_count,
            "overall_status": "healthy" if healthy_count == total_count else "degraded",
            "services": services_health
        }


# Singleton instance
service_monitor = ServiceMonitor()
