from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
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


def get_audit_events_by_type(event_type: str, skip: int = 0, limit: int = 100) -> List[AuditEvent]:
    """
    Retrieve audit events filtered by event type.
    
    Args:
        event_type: The type of events to filter by.
        skip: Number of records to skip (pagination).
        limit: Maximum number of records to return.
        
    Returns:
        List of audit events matching the event type.
    """
    db = SessionLocal()
    try:
        return db.query(AuditEvent).filter(AuditEvent.event_type == event_type).order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
    finally:
        db.close()


def get_audit_events_by_service(service_name: str, skip: int = 0, limit: int = 100) -> List[AuditEvent]:
    """
    Retrieve audit events filtered by service name.
    
    Args:
        service_name: The name of the service to filter by.
        skip: Number of records to skip (pagination).
        limit: Maximum number of records to return.
        
    Returns:
        List of audit events from the specified service.
    """
    db = SessionLocal()
    try:
        return db.query(AuditEvent).filter(AuditEvent.service_name == service_name).order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
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
