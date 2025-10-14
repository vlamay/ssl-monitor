"""
User authentication endpoints
"""
from datetime import datetime, timezone, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_tokens, verify_token
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserLogin, User as UserSchema, Token, 
    PasswordChange, PasswordReset, PasswordResetConfirm
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    from datetime import timedelta
    trial_ends_at = datetime.now(timezone.utc) + timedelta(days=settings.FREE_TRIAL_DAYS)
    
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        trial_ends_at=trial_ends_at
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"New user registered: {user.email}")
    
    return user


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login user and return tokens"""
    
    # Find user
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Create tokens
    tokens = create_tokens(str(user.id))
    
    logger.info(f"User logged in: {user.email}")
    
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token"""
    
    try:
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        tokens = create_tokens(str(user.id))
        
        return tokens
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update current user information"""
    
    # Update allowed fields
    if "full_name" in user_update:
        current_user.full_name = user_update["full_name"]
    if "timezone" in user_update:
        current_user.timezone = user_update["timezone"]
    if "notification_preferences" in user_update:
        current_user.notification_preferences = user_update["notification_preferences"]
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Change user password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Logout user (client should discard tokens)"""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete user account"""
    
    # Soft delete - deactivate user
    current_user.is_active = False
    await db.commit()
    
    logger.info(f"Account deleted for user: {current_user.email}")
    
    return {"message": "Account deleted successfully"}
