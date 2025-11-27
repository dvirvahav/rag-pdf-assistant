from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.audit_event import AuditEventResponse, AuditEventCreate
from app.services.postgres_service import (
    get_all_audit_events,
    get_audit_events_by_type,
    get_audit_events_by_service,
    get_audit_event_by_id,
    create_audit_event
)

router = APIRouter(prefix="/audit", tags=["Audit Events"])


@router.get("/health")
def health_check():
    """
    Health check endpoint for the audit service.
    """
    return {"status": "healthy", "service": "audit-service"}


@router.get("/events", response_model=List[AuditEventResponse])
def list_audit_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    service_name: Optional[str] = Query(None, description="Filter by service name")
):
    """
    Retrieve audit events with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **event_type**: Optional filter by event type
    - **service_name**: Optional filter by service name
    """
    if event_type:
        events = get_audit_events_by_type(event_type, skip, limit)
    elif service_name:
        events = get_audit_events_by_service(service_name, skip, limit)
    else:
        events = get_all_audit_events(skip, limit)
    
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
