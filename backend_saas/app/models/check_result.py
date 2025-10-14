"""
Monitor check result model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class MonitorCheckResult(Base):
    """SSL check result model"""
    __tablename__ = "monitor_check_results"
    
    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)
    
    # Check details
    check_type = Column(String(50), default="ssl_cert", nullable=False)  # ssl_cert, port_check, etc.
    success = Column(Boolean, nullable=False)
    
    # SSL Certificate info
    issuer = Column(String(500), nullable=True)
    subject = Column(String(500), nullable=True)
    serial_number = Column(String(100), nullable=True)
    fingerprint = Column(String(255), nullable=True)
    
    # Dates
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Performance metrics
    response_time_ms = Column(Float, nullable=True)
    connection_time_ms = Column(Float, nullable=True)
    handshake_time_ms = Column(Float, nullable=True)
    
    # Error details
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional data
    certificate_chain_length = Column(Integer, nullable=True)
    cipher_suite = Column(String(100), nullable=True)
    protocol_version = Column(String(20), nullable=True)
    
    # Raw data (JSON)
    raw_data = Column(JSON, nullable=True)
    
    # Timestamp
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    monitor = relationship("Monitor", back_populates="check_results")
    
    def __repr__(self):
        return f"<MonitorCheckResult(id={self.id}, monitor_id={self.monitor_id}, success={self.success})>"
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until SSL certificate expiry"""
        if not self.valid_until:
            return None
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        delta = self.valid_until - now
        return delta.days
