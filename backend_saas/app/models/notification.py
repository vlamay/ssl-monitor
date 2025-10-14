"""
Notification models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification types"""
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    SLACK = "slack"


class NotificationTrigger(str, enum.Enum):
    """Notification triggers"""
    EXPIRES_IN_30D = "expires_in_30d"
    EXPIRES_IN_7D = "expires_in_7d"
    EXPIRES_IN_3D = "expires_in_3d"
    EXPIRES_IN_1D = "expires_in_1d"
    EXPIRED = "expired"
    WEEKLY_REPORT = "weekly_report"
    MONITOR_DOWN = "monitor_down"
    MONITOR_UP = "monitor_up"


class Notification(Base):
    """Notification settings model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=True)  # None for global settings
    
    # Notification configuration
    type = Column(Enum(NotificationType), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Channel-specific settings
    email_address = Column(String(255), nullable=True)
    telegram_chat_id = Column(String(100), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    webhook_headers = Column(Text, nullable=True)  # JSON string
    whatsapp_phone = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)  # For SMS notifications
    channel = Column(String(100), nullable=True)  # For Slack channel
    team_id = Column(String(100), nullable=True)  # For Slack team ID
    
    # Triggers
    triggers = Column(Text, nullable=False)  # JSON array of NotificationTrigger
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    monitor = relationship("Monitor")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, enabled={self.enabled})>"


class NotificationLog(Base):
    """Notification log model"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=True)
    
    # Notification details
    type = Column(Enum(NotificationType), nullable=False)
    trigger = Column(Enum(NotificationTrigger), nullable=False)
    
    # Content
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    
    # Delivery
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivery_status = Column(String(50), default="sent", nullable=False)  # sent, failed, pending
    error_message = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON string with additional data
    
    # Relationships
    notification = relationship("Notification")
    monitor = relationship("Monitor")
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, type={self.type}, status={self.delivery_status})>"
