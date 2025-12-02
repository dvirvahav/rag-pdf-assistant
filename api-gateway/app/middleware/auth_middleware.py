"""
Authentication Middleware - Validates Keycloak JWT tokens
"""
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class KeycloakValidator:
    """Validates JWT tokens from Keycloak"""

    def __init__(self):
        self.public_key: Optional[str] = None
        self.realm_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"

    async def get_public_key(self) -> str:
        """Fetch Keycloak public key for JWT verification"""
        if self.public_key:
            return self.public_key

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.realm_url}")
                response.raise_for_status()
                realm_info = response.json()
                self.public_key = f"-----BEGIN PUBLIC KEY-----\n{realm_info['public_key']}\n-----END PUBLIC KEY-----"
                return self.public_key
        except Exception as e:
            logger.error(f"Failed to fetch Keycloak public key: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

    async def validate_token(self, token: str) -> dict:
        """Validate JWT token and return decoded payload"""
        try:
            public_key = await self.get_public_key()

            # Decode and verify token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.KEYCLOAK_CLIENT_ID,
                options={"verify_aud": False}  # Keycloak tokens may not have aud claim
            )

            return payload

        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token validation failed"
            )


# Global validator instance
keycloak_validator = KeycloakValidator()


async def verify_token(request: Request) -> Optional[dict]:
    """
    Middleware function to verify JWT token from request headers.
    Returns decoded token payload or None if no token provided.
    """
    # Get authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    # Extract token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]

    # Validate token
    payload = await keycloak_validator.validate_token(token)

    return payload


def require_auth(payload: Optional[dict] = None) -> dict:
    """
    Dependency to require authentication.
    Raises 401 if no valid token is provided.
    """
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def require_role(required_role: str):
    """
    Dependency factory to require specific role.
    Usage: Depends(require_role("admin"))
    """
    def role_checker(payload: dict) -> dict:
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract roles from token
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )

        return payload

    return role_checker
