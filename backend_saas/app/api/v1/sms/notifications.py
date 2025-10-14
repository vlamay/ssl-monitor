"""
SMS Notification API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.services.sms import sms_service
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SMSNotificationCreate(BaseModel):
    """Create SMS notification request"""
    phone_number: str = Field(..., description="Phone number in international format")
    enabled: bool = Field(default=True, description="Enable/disable notification")
    triggers: List[str] = Field(default=["expires_in_30d", "expires_in_7d", "expires_in_1d", "expired"])
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        
        # Add + if missing
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        # Validate format
        if not re.match(r'^\+[1-9]\d{9,14}$', cleaned):
            raise ValueError('Invalid phone number format. Use international format like +420123456789')
        
        return cleaned


class SMSNotificationUpdate(BaseModel):
    """Update SMS notification request"""
    phone_number: Optional[str] = None
    enabled: Optional[bool] = None
    triggers: Optional[List[str]] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
            
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        
        # Add + if missing
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        # Validate format
        if not re.match(r'^\+[1-9]\d{9,14}$', cleaned):
            raise ValueError('Invalid phone number format. Use international format like +420123456789')
        
        return cleaned


class SMSNotificationResponse(BaseModel):
    """SMS notification response"""
    id: int
    phone_number: str
    enabled: bool
    triggers: List[str]
    created_at: str
    updated_at: str


class SMSTestRequest(BaseModel):
    """Test SMS request"""
    phone_number: str = Field(..., description="Phone number to test")
    message: Optional[str] = Field(default=None, description="Custom message")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        
        # Add + if missing
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        # Validate format
        if not re.match(r'^\+[1-9]\d{9,14}$', cleaned):
            raise ValueError('Invalid phone number format. Use international format like +420123456789')
        
        return cleaned


@router.get("/", response_model=List[SMSNotificationResponse])
async def get_sms_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all SMS notifications for current user"""
    try:
        query = select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SMS
        )
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return [
            SMSNotificationResponse(
                id=n.id,
                phone_number=n.phone_number,
                enabled=n.enabled,
                triggers=n.triggers.split(',') if n.triggers else [],
                created_at=n.created_at.isoformat(),
                updated_at=n.updated_at.isoformat()
            )
            for n in notifications
        ]
    except Exception as e:
        logger.error(f"Error getting SMS notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve SMS notifications"
        )


@router.post("/", response_model=SMSNotificationResponse)
async def create_sms_notification(
    notification: SMSNotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new SMS notification"""
    try:
        # Check if SMS notifications are already configured for this user
        existing_query = select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SMS,
            Notification.phone_number == notification.phone_number
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SMS notification already exists for this phone number"
            )
        
        # Create new notification
        new_notification = Notification(
            user_id=current_user.id,
            type=NotificationType.SMS,
            enabled=notification.enabled,
            phone_number=notification.phone_number,
            triggers=','.join(notification.triggers)
        )
        
        db.add(new_notification)
        await db.commit()
        await db.refresh(new_notification)
        
        return SMSNotificationResponse(
            id=new_notification.id,
            phone_number=new_notification.phone_number,
            enabled=new_notification.enabled,
            triggers=new_notification.triggers.split(',') if new_notification.triggers else [],
            created_at=new_notification.created_at.isoformat(),
            updated_at=new_notification.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating SMS notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SMS notification"
        )


@router.put("/{notification_id}", response_model=SMSNotificationResponse)
async def update_sms_notification(
    notification_id: int,
    notification: SMSNotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update SMS notification"""
    try:
        # Find notification
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SMS
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS notification not found"
            )
        
        # Update fields
        if notification.phone_number is not None:
            existing.phone_number = notification.phone_number
        if notification.enabled is not None:
            existing.enabled = notification.enabled
        if notification.triggers is not None:
            existing.triggers = ','.join(notification.triggers)
        
        await db.commit()
        await db.refresh(existing)
        
        return SMSNotificationResponse(
            id=existing.id,
            phone_number=existing.phone_number,
            enabled=existing.enabled,
            triggers=existing.triggers.split(',') if existing.triggers else [],
            created_at=existing.created_at.isoformat(),
            updated_at=existing.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating SMS notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update SMS notification"
        )


@router.delete("/{notification_id}")
async def delete_sms_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete SMS notification"""
    try:
        # Find notification
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SMS
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS notification not found"
            )
        
        await db.delete(notification)
        await db.commit()
        
        return {"message": "SMS notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting SMS notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete SMS notification"
        )


@router.post("/test")
async def test_sms_notification(
    test_request: SMSTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test SMS notification"""
    try:
        # Check if SMS service is configured
        provider_info = sms_service.get_provider_info()
        if provider_info['active_provider'] == 'none':
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="SMS service not configured. Please contact support."
            )
        
        # Prepare test message
        message = test_request.message or f"SSL Monitor Pro Test Message for {current_user.full_name}. SMS notifications are working correctly!"
        
        # Send test SMS
        result = await sms_service.send_sms(test_request.phone_number, message)
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Test SMS sent successfully",
                "provider": result.get('provider'),
                "message_id": result.get('message_id'),
                "phone_number": test_request.phone_number
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SMS sending failed: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing SMS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test SMS"
        )


@router.get("/providers")
async def get_sms_providers():
    """Get available SMS providers and configuration status"""
    try:
        provider_info = sms_service.get_provider_info()
        return {
            "active_provider": provider_info['active_provider'],
            "available_providers": provider_info['available_providers'],
            "total_providers": provider_info['total_providers'],
            "setup_instructions": {
                "twilio": "Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER",
                "sms_ru": "Configure SMS_RU_API_ID for EU-based SMS service"
            }
        }
    except Exception as e:
        logger.error(f"Error getting SMS providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get SMS provider information"
        )
