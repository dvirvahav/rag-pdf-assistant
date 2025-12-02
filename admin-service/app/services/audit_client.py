"""
Client for communicating with the Audit Service.
"""
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.config import settings


class AuditClient:
    """
    Client to interact with the Audit Service API.
    """

    def __init__(self):
        self.base_url = settings.AUDIT_SERVICE_URL
        self.timeout = 30.0

    async def get_audit_events(
        self,
        token: str,
        skip: int = 0,
        limit: int = 100,
        event_type: Optional[str] = None,
        service_name: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch audit events from the audit service.

        Args:
            token: JWT token for authentication
            skip: Number of records to skip
            limit: Maximum number of records to return
            event_type: Optional filter by event type
            service_name: Optional filter by service name
            from_date: Optional filter from date
            to_date: Optional filter to date

        Returns:
            List of audit events
        """
        params = {
            "skip": skip,
            "limit": limit
        }

        if event_type:
            params["event_type"] = event_type
        if service_name:
            params["service_name"] = service_name
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/audit/events",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def get_audit_event_by_id(self, token: str, event_id: int) -> Dict[str, Any]:
        """
        Fetch a single audit event by ID.

        Args:
            token: JWT token for authentication
            event_id: ID of the audit event

        Returns:
            Audit event details
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/audit/events/{event_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of audit service.

        Returns:
            Health status
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/audit/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "audit-service",
                "error": str(e)
            }


# Singleton instance
audit_client = AuditClient()
