"""
User model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"


class PlanType(str, enum.Enum):
    """Subscription plans"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Subscription
    plan = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Profile
    timezone = Column(String(50), default="UTC", nullable=False)
    notification_preferences = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    monitors = relationship("Monitor", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    calendly_events = relationship("CalendlyEvent", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, plan={self.plan})>"
    
    @property
    def is_trial_active(self) -> bool:
        """Check if user is in trial period"""
        if not self.trial_ends_at:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.trial_ends_at
    
    @property
    def monitors_limit(self) -> int:
        """Get monitors limit based on plan"""
        from app.core.config import settings
        return settings.PLANS.get(self.plan.value, {}).get("monitors", 5)
    
    @property
    def checks_per_day_limit(self) -> int:
        """Get checks per day limit based on plan"""
        from app.core.config import settings
        return settings.PLANS.get(self.plan.value, {}).get("checks_per_day", 24)
