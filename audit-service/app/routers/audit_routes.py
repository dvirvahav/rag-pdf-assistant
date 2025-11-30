from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import common package
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from common.event_types import EventType

from app.models.audit_event import AuditEventResponse, AuditEventCreate
from app.services.postgres_service import (
    get_all_audit_events,
    get_audit_event_by_id,
    create_audit_event,
    get_events_filtered
)

router = APIRouter(prefix="/audit", tags=["Audit Events"])


@router.get("/health")
def health_check():
    try:
        # Quick DB check (tests connection only)
        get_all_audit_events(skip=0, limit=1)
        return {"status": "healthy", "service": "audit-service", "db": "ok"}
    except Exception:
        return {"status": "unhealthy", "service": "audit-service", "db": "down"}



@router.get("/events", response_model=List[AuditEventResponse])
def list_audit_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    from_date: Optional[datetime] = Query(None, description="Filter events from this date (inclusive)"),
    to_date: Optional[datetime] = Query(None, description="Filter events until this date (inclusive)")
):
    """
    Retrieve audit events with optional filtering.

    Supports combined filtering by multiple criteria:
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **event_type**: Optional filter by event type
    - **service_name**: Optional filter by service name
    - **from_date**: Optional filter for events created on or after this datetime
    - **to_date**: Optional filter for events created on or before this datetime
    """
    events = get_events_filtered(
        skip=skip,
        limit=limit,
        event_type=event_type.value if event_type else None,
        service_name=service_name,
        from_date=from_date,
        to_date=to_date
    )

    return events


@router.get("/events/{event_id}", response_model=AuditEventResponse)
def get_audit_event(event_id: int):
    """
    Retrieve a single audit event by ID.

    - **event_id**: The ID of the audit event to retrieve
    """
    event = get_audit_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Audit event with ID {event_id} not found")
    return event


@router.post("/events", response_model=AuditEventResponse, status_code=201)
def create_audit_event_endpoint(event_data: AuditEventCreate):
    """
    Create a new audit event directly via REST API.
    This is an alternative to publishing via RabbitMQ.

    - **event_type**: Type of the audit event (e.g., FILE_UPLOADED, EMBEDDING_COMPLETED)
    - **service_name**: Name of the service that generated the event
    - **payload**: Optional JSON payload with additional event data
    """
    created_event = create_audit_event(event_data)
    return created_event
