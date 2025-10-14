"""
User schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, PlanType


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[str] = None


class UserInDB(UserBase):
    """User in database schema"""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    plan: PlanType
    trial_ends_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    timezone: str
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """User response schema"""
    monitors_limit: int
    checks_per_day_limit: int
    is_trial_active: bool


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str


class PasswordReset(BaseModel):
    """Password reset schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str
