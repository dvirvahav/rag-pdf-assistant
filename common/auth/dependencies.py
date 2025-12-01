"""
FastAPI dependencies for authentication.
Provides reusable dependencies for protecting routes with JWT validation.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from common.auth.keycloak_validator import KeycloakValidator

# Security scheme for Bearer token
security = HTTPBearer()

# Initialize Keycloak validator (singleton pattern)
_validator: Optional[KeycloakValidator] = None


def get_keycloak_validator() -> KeycloakValidator:
    """
    Get or create Keycloak validator instance.
    Configuration is read from environment variables.
    """
    global _validator
    if _validator is None:
        keycloak_url = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
        realm = os.getenv("KEYCLOAK_REALM", "rag-assistant")
        client_id = os.getenv("KEYCLOAK_CLIENT_ID", "rag-backend")

        _validator = KeycloakValidator(
            keycloak_url=keycloak_url,
            realm=realm,
            client_id=client_id,
            verify_audience=True
        )
    return _validator


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    validator: KeycloakValidator = Depends(get_keycloak_validator)
) -> Dict[str, Any]:
    """
    Validate JWT token and return user information.

    This dependency can be used to protect routes that require authentication.

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"message": f"Hello {user['username']}"}

    Args:
        credentials: HTTP Bearer token from Authorization header
        validator: Keycloak validator instance

    Returns:
        Dictionary containing user information from token claims

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        # Extract token from credentials
        token = credentials.credentials

        # Validate token and get claims
        claims = validator.validate_token(token)

        # Extract user information
        user_info = validator.get_user_info(claims)

        # Add full claims for advanced use cases
        user_info["claims"] = claims

        return user_info

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    validator: KeycloakValidator = Depends(get_keycloak_validator)
) -> Optional[Dict[str, Any]]:
    """
    Validate JWT token if provided, return None if not provided.

    This dependency can be used for routes that work with or without authentication.

    Usage:
        @app.get("/optional-auth")
        async def optional_route(user: Optional[dict] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user['username']}"}
            return {"message": "Hello anonymous"}

    Args:
        credentials: Optional HTTP Bearer token from Authorization header
        validator: Keycloak validator instance

    Returns:
        Dictionary containing user information if token is valid, None otherwise
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        claims = validator.validate_token(token)
        user_info = validator.get_user_info(claims)
        user_info["claims"] = claims
        return user_info
    except Exception:
        return None


def require_role(required_role: str):
    """
    Create a dependency that requires a specific role.

    Usage:
        @app.get("/admin")
        async def admin_route(user: dict = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}

    Args:
        required_role: Role name that user must have

    Returns:
        Dependency function that validates role
    """
    async def role_checker(
        user: Dict[str, Any] = Depends(get_current_user),
        validator: KeycloakValidator = Depends(get_keycloak_validator)
    ) -> Dict[str, Any]:
        claims = user.get("claims", {})
        if not validator.has_role(claims, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user

    return role_checker
