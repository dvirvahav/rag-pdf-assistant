"""
Admin API routes for aggregating data from various services.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import common package
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from common.auth.dependencies import require_role

from app.services.audit_client import audit_client
from app.services.keycloak_client import keycloak_client
from app.services.service_monitor import service_monitor

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/health")
async def health_check():
    """Health check endpoint for admin service."""
    return {
        "status": "healthy",
        "service": "admin-service"
    }


@router.get("/audit/events")
async def get_audit_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get audit events from audit service.
    Requires admin role.
    """
    try:
        # Extract token from user claims
        token = current_user.get("claims", {}).get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")

        events = await audit_client.get_audit_events(
            token=token,
            skip=skip,
            limit=limit,
            event_type=event_type,
            service_name=service_name,
            from_date=from_date,
            to_date=to_date
        )
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit events: {str(e)}")


@router.get("/audit/events/{event_id}")
async def get_audit_event(
    event_id: int,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get a single audit event by ID.
    Requires admin role.
    """
    try:
        token = current_user.get("claims", {}).get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")

        event = await audit_client.get_audit_event_by_id(token=token, event_id=event_id)
        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit event: {str(e)}")


@router.get("/users")
async def get_users(
    max_users: int = Query(100, ge=1, le=1000),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get list of users from Keycloak.
    Requires admin role.
    """
    try:
        # For now, we'll use the current user's token
        # In production, you might want to use a service account
        token = current_user.get("claims", {}).get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")

        users = await keycloak_client.get_users(admin_token=token, max_users=max_users)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get user details by ID.
    Requires admin role.
    """
    try:
        token = current_user.get("claims", {}).get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")

        user = await keycloak_client.get_user_by_id(admin_token=token, user_id=user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")


@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get roles for a specific user.
    Requires admin role.
    """
    try:
        token = current_user.get("claims", {}).get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")

        roles = await keycloak_client.get_user_roles(admin_token=token, user_id=user_id)
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user roles: {str(e)}")


@router.get("/services/health")
async def get_services_health(
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get health status of all microservices.
    Requires admin role.
    """
    try:
        health_status = await service_monitor.check_all_services()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check services health: {str(e)}")


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """
    Get system overview for dashboard.
    Requires admin role.
    """
    try:
        system_overview = await service_monitor.get_system_overview()
        return system_overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard overview: {str(e)}")
