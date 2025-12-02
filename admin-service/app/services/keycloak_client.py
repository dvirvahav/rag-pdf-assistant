"""
Client for communicating with Keycloak Admin API.
"""
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings


class KeycloakClient:
    """
    Client to interact with Keycloak Admin API.
    """

    def __init__(self):
        self.base_url = settings.KEYCLOAK_URL
        self.realm = settings.KEYCLOAK_REALM
        self.timeout = 30.0

    async def get_admin_token(self, username: str, password: str) -> str:
        """
        Get admin access token from Keycloak.

        Args:
            username: Admin username
            password: Admin password

        Returns:
            Access token
        """
        token_url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token"

        data = {
            "grant_type": "password",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "username": username,
            "password": password
        }

        if settings.KEYCLOAK_CLIENT_SECRET:
            data["client_secret"] = settings.KEYCLOAK_CLIENT_SECRET

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()["access_token"]

    async def get_users(self, admin_token: str, max_users: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of users from Keycloak.

        Args:
            admin_token: Admin access token
            max_users: Maximum number of users to return

        Returns:
            List of users
        """
        users_url = f"{self.base_url}/admin/realms/{self.realm}/users"

        headers = {
            "Authorization": f"Bearer {admin_token}"
        }

        params = {
            "max": max_users
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(users_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_user_by_id(self, admin_token: str, user_id: str) -> Dict[str, Any]:
        """
        Get user details by ID.

        Args:
            admin_token: Admin access token
            user_id: User ID

        Returns:
            User details
        """
        user_url = f"{self.base_url}/admin/realms/{self.realm}/users/{user_id}"

        headers = {
            "Authorization": f"Bearer {admin_token}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(user_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_user_roles(self, admin_token: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get roles assigned to a user.

        Args:
            admin_token: Admin access token
            user_id: User ID

        Returns:
            List of roles
        """
        roles_url = f"{self.base_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm"

        headers = {
            "Authorization": f"Bearer {admin_token}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(roles_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of Keycloak service.

        Returns:
            Health status
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "service": "keycloak"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "service": "keycloak",
                        "error": f"Status code: {response.status_code}"
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "keycloak",
                "error": str(e)
            }


# Singleton instance
keycloak_client = KeycloakClient()
