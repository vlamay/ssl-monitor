"""
Calendly integration models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class CalendlyEventType(str, enum.Enum):
    """Calendly event types"""
    DEMO = "demo"
    ONBOARDING = "onboarding"
    SUPPORT = "support"


class CalendlyEventStatus(str, enum.Enum):
    """Calendly event status"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"
    NO_SHOW = "no_show"


class CalendlyEvent(Base):
    """Calendly event model"""
    __tablename__ = "calendly_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Calendly data
    calendly_event_id = Column(String(255), unique=True, nullable=False)
    calendly_invitee_id = Column(String(255), nullable=True)
    calendly_uri = Column(String(500), nullable=True)
    
    # Event details
    event_type = Column(Enum(CalendlyEventType), nullable=False)
    status = Column(Enum(CalendlyEventStatus), default=CalendlyEventStatus.SCHEDULED, nullable=False)
    
    # Scheduling
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Event info
    event_name = Column(String(255), nullable=True)
    event_description = Column(Text, nullable=True)
    
    # Attendee info
    attendee_name = Column(String(255), nullable=True)
    attendee_email = Column(String(255), nullable=True)
    attendee_phone = Column(String(50), nullable=True)
    
    # Custom questions (JSON)
    questions_and_answers = Column(Text, nullable=True)
    
    # Meeting details
    meeting_url = Column(String(500), nullable=True)
    meeting_password = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="calendly_events")
    
    def __repr__(self):
        return f"<CalendlyEvent(id={self.id}, user_id={self.user_id}, type={self.event_type}, status={self.status})>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate event duration in minutes"""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        return self.start_time > now and self.status == CalendlyEventStatus.SCHEDULED
