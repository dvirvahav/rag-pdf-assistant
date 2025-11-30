from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime
from app.config import DATABASE_URL
from app.models.audit_event import Base, AuditEvent, AuditEventCreate

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Get a database session.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def create_audit_event(event_data: AuditEventCreate) -> AuditEvent:
    """
    Create a new audit event in the database.

    Args:
        event_data: The audit event data to insert.

    Returns:
        The created audit event with ID and timestamp.
    """
    db = SessionLocal()
    try:
        db_event = AuditEvent(
            event_type=event_data.event_type,
            service_name=event_data.service_name,
            payload=event_data.payload
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    finally:
        db.close()


def get_all_audit_events(skip: int = 0, limit: int = 100) -> List[AuditEvent]:
    """
    Retrieve all audit events from the database.

    Args:
        skip: Number of records to skip (pagination).
        limit: Maximum number of records to return.

    Returns:
        List of audit events.
    """
    db = SessionLocal()
    try:
        return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
    finally:
        db.close()


def get_audit_event_by_id(event_id: int) -> Optional[AuditEvent]:
    """
    Retrieve a single audit event by ID.

    Args:
        event_id: The ID of the audit event.

    Returns:
        The audit event if found, None otherwise.
    """
    db = SessionLocal()
    try:
        return db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
    finally:
        db.close()


def get_events_filtered(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    service_name: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[AuditEvent]:
    """
    Retrieve audit events with dynamic filtering support.

    Supports combined filtering by multiple criteria:
    - event_type: Filter by specific event type
    - service_name: Filter by service name
    - from_date: Filter events created on or after this datetime
    - to_date: Filter events created on or before this datetime

    Args:
        skip: Number of records to skip (pagination).
        limit: Maximum number of records to return.
        event_type: Optional event type filter.
        service_name: Optional service name filter.
        from_date: Optional start date filter (inclusive).
        to_date: Optional end date filter (inclusive).

    Returns:
        List of audit events matching all provided filters.
    """
    db = SessionLocal()
    try:
        # Start with base query
        query = db.query(AuditEvent)

        # Apply filters conditionally
        if event_type is not None:
            query = query.filter(AuditEvent.event_type == event_type)

        if service_name is not None:
            query = query.filter(AuditEvent.service_name == service_name)

        if from_date is not None:
            query = query.filter(AuditEvent.created_at >= from_date)

        if to_date is not None:
            query = query.filter(AuditEvent.created_at <= to_date)

        # Order by created_at descending and apply pagination
        return query.order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
    finally:
        db.close()
