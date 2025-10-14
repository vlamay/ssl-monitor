"""
Subscription schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.subscription import SubscriptionStatus, BillingInterval


class SubscriptionBase(BaseModel):
    """Base subscription schema"""
    plan: str
    status: SubscriptionStatus
    price: float
    currency: str = "USD"
    billing_interval: BillingInterval


class SubscriptionCreate(SubscriptionBase):
    """Subscription creation schema"""
    user_id: int
    stripe_subscription_id: str
    stripe_price_id: str
    stripe_customer_id: str
    current_period_start: datetime
    current_period_end: datetime


class SubscriptionUpdate(BaseModel):
    """Subscription update schema"""
    status: Optional[SubscriptionStatus] = None
    price: Optional[float] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    canceled_at: Optional[datetime] = None


class SubscriptionInDB(SubscriptionBase):
    """Subscription in database schema"""
    id: int
    user_id: int
    stripe_subscription_id: str
    stripe_price_id: str
    stripe_customer_id: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Subscription(SubscriptionInDB):
    """Subscription response schema"""
    is_active: bool
    is_trialing: bool


class SubscriptionPlan(BaseModel):
    """Subscription plan schema"""
    id: str
    name: str
    price: float
    currency: str
    interval: str
    features: List[str]
    monitors_limit: int
    checks_per_day_limit: int


class CreateCheckoutSession(BaseModel):
    """Create checkout session schema"""
    price_id: str
    success_url: str
    cancel_url: str


class CheckoutSession(BaseModel):
    """Checkout session response schema"""
    session_id: str
    url: str


class BillingPortal(BaseModel):
    """Billing portal schema"""
    url: str


class UsageStats(BaseModel):
    """Usage statistics schema"""
    monitors_used: int
    monitors_limit: int
    checks_this_month: int
    checks_limit: int
    usage_percentage: float
