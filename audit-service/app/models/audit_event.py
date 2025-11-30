from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import common package
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from common.event_types import EventType

Base = declarative_base()


class AuditEvent(Base):
    """
    SQLAlchemy model for audit events stored in PostgreSQL.
    """
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False)
    service_name = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AuditEventCreate(BaseModel):
    """
    Pydantic model for creating audit events (input validation).
    """
    event_type: EventType
    service_name: str
    payload: Optional[Any] = None


class AuditEventResponse(BaseModel):
    """
    Pydantic model for audit event responses.
    """
    id: int
    event_type: EventType
    service_name: str
    payload: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True
