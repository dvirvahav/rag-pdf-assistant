"""
Proxy Routes - Routes requests to backend microservices
"""
import logging
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
import httpx

from app.config import settings
from app.middleware.auth_middleware import verify_token, require_auth

logger = logging.getLogger(__name__)
router = APIRouter()


async def proxy_request(
    request: Request,
    target_url: str,
    token_payload: Optional[dict] = None
):
    """
    Generic proxy function to forward requests to backend services.
    Adds user context headers from validated token.
    """
    # Prepare headers
    headers = dict(request.headers)

    # Remove host header to avoid conflicts
    headers.pop("host", None)

    # Add user context headers if authenticated
    if token_payload:
        headers["X-User-Id"] = token_payload.get("sub", "")
        headers["X-User-Email"] = token_payload.get("email", "")
        headers["X-User-Name"] = token_payload.get("preferred_username", "")

        # Add roles as comma-separated string
        realm_access = token_payload.get("realm_access", {})
        roles = realm_access.get("roles", [])
        headers["X-User-Roles"] = ",".join(roles)

    # Add correlation ID if available
    if hasattr(request.state, "correlation_id"):
        headers["X-Correlation-ID"] = request.state.correlation_id

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward the request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=request.query_params
            )

            # Return response
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

    except httpx.TimeoutException:
        logger.error(f"Timeout calling {target_url}")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.RequestError as e:
        logger.error(f"Error calling {target_url}: {e}")
        raise HTTPException(status_code=502, detail="Bad gateway")
    except Exception as e:
        logger.error(f"Unexpected error proxying request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# FILE SERVICE ROUTES
# ============================================================================

@router.post("/api/files/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Upload PDF file - proxies to file-service"""
    # Require authentication
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        # Prepare multipart form data
        files = {"file": (file.filename, await file.read(), file.content_type)}

        # Prepare headers with user context
        headers = {
            "X-User-Id": token_payload.get("sub", ""),
            "X-User-Email": token_payload.get("email", ""),
        }

        if hasattr(request.state, "correlation_id"):
            headers["X-Correlation-ID"] = request.state.correlation_id

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.FILE_SERVICE_URL}/files/upload",
                files=files,
                headers=headers
            )

            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Upload timeout")
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/api/files/jobs/{job_id}/status")
async def get_job_status(
    request: Request,
    job_id: str,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Get job status - proxies to file-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    target_url = f"{settings.FILE_SERVICE_URL}/files/jobs/{job_id}/status"
    return await proxy_request(request, target_url, token_payload)


@router.get("/api/files/")
async def list_files(
    request: Request,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """List files - proxies to file-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    target_url = f"{settings.FILE_SERVICE_URL}/files/"
    return await proxy_request(request, target_url, token_payload)


@router.delete("/api/files/{filename}")
async def delete_file(
    request: Request,
    filename: str,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Delete file - proxies to file-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    target_url = f"{settings.FILE_SERVICE_URL}/files/{filename}"
    return await proxy_request(request, target_url, token_payload)


# ============================================================================
# RAG SERVICE ROUTES
# ============================================================================

@router.post("/api/rag/ask")
async def ask_question(
    request: Request,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Ask question - proxies to rag-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    target_url = f"{settings.RAG_SERVICE_URL}/rag/ask"
    return await proxy_request(request, target_url, token_payload)


# ============================================================================
# ADMIN SERVICE ROUTES
# ============================================================================

@router.get("/api/admin/health")
async def admin_health(
    request: Request,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Admin health check - proxies to admin-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check for admin role
    realm_access = token_payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    target_url = f"{settings.ADMIN_SERVICE_URL}/api/health"
    return await proxy_request(request, target_url, token_payload)


@router.get("/api/admin/services/status")
async def admin_services_status(
    request: Request,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Get all services status - proxies to admin-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check for admin role
    realm_access = token_payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    target_url = f"{settings.ADMIN_SERVICE_URL}/api/services/status"
    return await proxy_request(request, target_url, token_payload)


@router.post("/api/admin/audit/search")
async def admin_audit_search(
    request: Request,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Search audit logs - proxies to admin-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check for admin role
    realm_access = token_payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    target_url = f"{settings.ADMIN_SERVICE_URL}/api/audit/search"
    return await proxy_request(request, target_url, token_payload)


# ============================================================================
# AUDIT SERVICE ROUTES (Direct access for internal monitoring)
# ============================================================================

@router.get("/api/audit/events")
async def get_audit_events(
    request: Request,
    token_payload: Optional[dict] = Depends(verify_token)
):
    """Get audit events - proxies to audit-service"""
    if not token_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    target_url = f"{settings.AUDIT_SERVICE_URL}/audit/events"
    return await proxy_request(request, target_url, token_payload)
