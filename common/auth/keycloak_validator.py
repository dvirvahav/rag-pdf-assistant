"""
Keycloak JWT token validator for microservices.
Validates tokens using Keycloak's public keys (JWKS).
"""
import logging
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)


class KeycloakValidator:
    """
    Validates JWT tokens issued by Keycloak.
    Fetches public keys from Keycloak's JWKS endpoint and caches them.
    """

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        verify_audience: bool = True
    ):
        """
        Initialize the Keycloak validator.

        Args:
            keycloak_url: Base URL of Keycloak (e.g., http://keycloak:8080)
            realm: Keycloak realm name
            client_id: Expected audience (client ID)
            verify_audience: Whether to verify the audience claim
        """
        self.keycloak_url = keycloak_url.rstrip('/')
        self.realm = realm
        self.client_id = client_id
        self.verify_audience = verify_audience
        self.jwks_uri = f"{self.keycloak_url}/realms/{realm}/protocol/openid-connect/certs"
        self.issuer = f"{self.keycloak_url}/realms/{realm}"

    @lru_cache(maxsize=1)
    def _get_jwks(self) -> Dict[str, Any]:
        """
        Fetch JWKS (JSON Web Key Set) from Keycloak.
        Cached to avoid repeated requests.

        Returns:
            JWKS dictionary
        """
        try:
            response = requests.get(self.jwks_uri, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS from {self.jwks_uri}: {e}")
            raise ValueError(f"Unable to fetch Keycloak public keys: {e}")

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token and return its claims.

        Args:
            token: JWT token string (without 'Bearer ' prefix)

        Returns:
            Dictionary of token claims if valid, None if invalid

        Raises:
            ValueError: If token validation fails
        """
        try:
            # Get JWKS for signature verification
            jwks = self._get_jwks()

            # Decode and validate token
            claims = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=self.client_id if self.verify_audience else None,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_aud": self.verify_audience,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iss": True,
                    "verify_sub": True,
                    "verify_jti": True,
                    "verify_at_hash": False,
                    "require_aud": self.verify_audience,
                    "require_iat": True,
                    "require_exp": True,
                    "require_nbf": False,
                    "require_iss": True,
                    "require_sub": True,
                    "require_jti": False,
                }
            )

            logger.info(f"Token validated successfully for user: {claims.get('preferred_username', 'unknown')}")
            return claims

        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise ValueError("Token has expired")
        except JWTClaimsError as e:
            logger.warning(f"Token claims validation failed: {e}")
            raise ValueError(f"Invalid token claims: {e}")
        except JWTError as e:
            logger.warning(f"Token validation failed: {e}")
            raise ValueError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            raise ValueError(f"Token validation error: {e}")

    def get_user_info(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user information from token claims.

        Args:
            claims: Token claims dictionary

        Returns:
            Dictionary with user information
        """
        return {
            "user_id": claims.get("sub"),
            "username": claims.get("preferred_username"),
            "email": claims.get("email"),
            "email_verified": claims.get("email_verified", False),
            "name": claims.get("name"),
            "given_name": claims.get("given_name"),
            "family_name": claims.get("family_name"),
            "roles": claims.get("realm_access", {}).get("roles", []),
        }

    def has_role(self, claims: Dict[str, Any], role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            claims: Token claims dictionary
            role: Role name to check

        Returns:
            True if user has the role, False otherwise
        """
        roles = claims.get("realm_access", {}).get("roles", [])
        return role in roles

    def clear_cache(self):
        """Clear the JWKS cache. Useful when keys are rotated."""
        self._get_jwks.cache_clear()
        logger.info("JWKS cache cleared")
