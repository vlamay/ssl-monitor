"""
SSL Monitor model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class MonitorStatus(str, enum.Enum):
    """Monitor status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class SSLCertStatus(str, enum.Enum):
    """SSL certificate status"""
    VALID = "valid"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class Monitor(Base):
    """SSL Monitor model"""
    __tablename__ = "monitors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Domain info
    domain = Column(String(255), nullable=False, index=True)
    port = Column(Integer, default=443, nullable=False)
    
    # Status
    status = Column(Enum(MonitorStatus), default=MonitorStatus.ACTIVE, nullable=False)
    ssl_status = Column(Enum(SSLCertStatus), default=SSLCertStatus.UNKNOWN, nullable=False)
    
    # SSL Certificate data
    issuer = Column(String(500), nullable=True)
    subject = Column(String(500), nullable=True)
    serial_number = Column(String(100), nullable=True)
    fingerprint = Column(String(255), nullable=True)
    
    # Dates
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_successful_check = Column(DateTime(timezone=True), nullable=True)
    
    # Monitoring settings
    check_interval = Column(Integer, default=3600, nullable=False)  # seconds
    alert_before_days = Column(Integer, default=30, nullable=False)  # days before expiry
    enabled_notifications = Column(Text, nullable=True)  # JSON array of notification types
    
    # Error handling
    last_error = Column(Text, nullable=True)
    consecutive_errors = Column(Integer, default=0, nullable=False)
    max_consecutive_errors = Column(Integer, default=3, nullable=False)
    
    # Performance metrics
    response_time_ms = Column(Float, nullable=True)
    uptime_percentage = Column(Float, default=100.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="monitors")
    check_results = relationship("MonitorCheckResult", back_populates="monitor")
    
    def __repr__(self):
        return f"<Monitor(id={self.id}, domain={self.domain}, status={self.status})>"
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until SSL certificate expiry"""
        if not self.valid_until:
            return None
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        delta = self.valid_until - now
        return delta.days
    
    @property
    def is_expiring_soon(self) -> bool:
        """Check if SSL certificate is expiring soon"""
        days_left = self.days_until_expiry
        if days_left is None:
            return False
        return days_left <= self.alert_before_days
    
    @property
    def is_expired(self) -> bool:
        """Check if SSL certificate is expired"""
        days_left = self.days_until_expiry
        return days_left is not None and days_left < 0
    
    @property
    def should_check(self) -> bool:
        """Check if monitor should be checked now"""
        if not self.last_checked_at:
            return True
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        next_check = self.last_checked_at + timedelta(seconds=self.check_interval)
        return now >= next_check
