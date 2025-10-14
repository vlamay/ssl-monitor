"""
Subscription model for Stripe integration
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class BillingInterval(str, enum.Enum):
    """Billing intervals"""
    MONTH = "month"
    YEAR = "year"


class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stripe data
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_price_id = Column(String(255), nullable=False)
    stripe_customer_id = Column(String(255), nullable=False)
    
    # Plan details
    plan = Column(String(50), nullable=False)  # free, pro, enterprise
    status = Column(Enum(SubscriptionStatus), nullable=False)
    price = Column(Float, nullable=False)  # Monthly price in USD
    currency = Column(String(3), default="USD", nullable=False)
    billing_interval = Column(Enum(BillingInterval), nullable=False)
    
    # Billing dates
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    @property
    def is_trialing(self) -> bool:
        """Check if subscription is in trial"""
        return self.status == SubscriptionStatus.TRIALING
