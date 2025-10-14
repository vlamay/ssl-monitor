"""
SSL Monitor Pro - Notification Management API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Pydantic models
class NotificationSettings(BaseModel):
    email_enabled: bool = True
    telegram_enabled: bool = False
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Email notification triggers
    email_expiring_30_days: bool = True
    email_expiring_7_days: bool = True
    email_expiring_3_days: bool = True
    email_expiring_1_day: bool = True
    email_expired: bool = True
    email_check_failed: bool = True
    email_weekly_report: bool = True

class NotificationTestRequest(BaseModel):
    notification_type: str  # 'expiring_soon', 'expired', 'check_failed', 'weekly_report'
    recipient_email: EmailStr
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
    test_domain: str = "example.com"
    test_days_left: int = 7

# In-memory storage (replace with database in production)
notification_settings_db = {}
notification_history_db = []

@router.get("/settings/{user_email}")
async def get_notification_settings(user_email: str):
    """Get notification settings for a user"""
    settings = notification_settings_db.get(user_email, {
        "email_enabled": True,
        "telegram_enabled": False,
        "webhook_enabled": False,
        "webhook_url": None,
        "telegram_chat_id": None,
        "email_expiring_30_days": True,
        "email_expiring_7_days": True,
        "email_expiring_3_days": True,
        "email_expiring_1_day": True,
        "email_expired": True,
        "email_check_failed": True,
        "email_weekly_report": True
    })
    
    return {
        "success": True,
        "settings": settings
    }

@router.put("/settings/{user_email}")
async def update_notification_settings(
    user_email: str, 
    settings: NotificationSettings
):
    """Update notification settings for a user"""
    notification_settings_db[user_email] = settings.dict()
    
    logger.info(f"Updated notification settings for {user_email}")
    
    return {
        "success": True,
        "message": "Notification settings updated successfully",
        "settings": settings.dict()
    }

@router.post("/test")
async def test_notification(request: NotificationTestRequest):
    """Send a test notification to verify settings"""
    try:
        # Prepare test data
        recipient_data = {
            "email": request.recipient_email,
            "name": "Test User",
            "telegram_chat_id": request.telegram_chat_id
        }
        
        domain_info = {
            "name": request.test_domain,
            "days_left": request.test_days_left,
            "expiry_date": (datetime.now() + timedelta(days=request.test_days_left)).strftime("%Y-%m-%d"),
            "status": "expiring_soon"
        }
        
        notification_settings = {
            "email_enabled": True,
            "telegram_enabled": bool(request.telegram_chat_id),
            "webhook_enabled": bool(request.webhook_url),
            "webhook_url": request.webhook_url
        }
        
        # Send test notification
        results = await notification_service.send_notification(
            notification_type=request.notification_type,
            recipient_data=recipient_data,
            domain_info=domain_info,
            notification_settings=notification_settings
        )
        
        # Log the test
        notification_history_db.append({
            "id": len(notification_history_db) + 1,
            "notification_type": f"test_{request.notification_type}",
            "domain_name": request.test_domain,
            "recipient_email": request.recipient_email,
            "sent_at": datetime.now(),
            "channels": results,
            "status": "success" if any(results.values()) else "failed"
        })
        
        return {
            "success": True,
            "message": "Test notification sent",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Test notification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test notification failed: {str(e)}"
        )

@router.get("/history/{user_email}")
async def get_notification_history(user_email: str, limit: int = 50):
    """Get notification history for a user"""
    user_history = [
        notification for notification in notification_history_db
        if notification["recipient_email"] == user_email
    ]
    
    # Sort by sent_at descending and limit
    user_history.sort(key=lambda x: x["sent_at"], reverse=True)
    user_history = user_history[:limit]
    
    return {
        "success": True,
        "history": user_history,
        "total": len(user_history)
    }

@router.get("/templates")
async def get_notification_templates():
    """Get available notification templates"""
    templates = {
        "expiring_soon": {
            "name": "Certificate Expiring Soon",
            "description": "Sent when SSL certificate expires in 30, 7, 3, or 1 days",
            "channels": ["email", "telegram", "webhook"],
            "triggers": ["30_days", "7_days", "3_days", "1_day"]
        },
        "expired": {
            "name": "Certificate Expired",
            "description": "Sent when SSL certificate has expired",
            "channels": ["email", "telegram", "webhook"],
            "triggers": ["expired"]
        },
        "check_failed": {
            "name": "SSL Check Failed",
            "description": "Sent when SSL certificate check fails",
            "channels": ["email", "telegram", "webhook"],
            "triggers": ["check_failed"]
        },
        "weekly_report": {
            "name": "Weekly Report",
            "description": "Weekly summary of all monitored domains",
            "channels": ["email"],
            "triggers": ["weekly"]
        }
    }
    
    return {
        "success": True,
        "templates": templates
    }

@router.get("/channels")
async def get_available_channels():
    """Get available notification channels"""
    channels = {
        "email": {
            "name": "Email",
            "description": "Send notifications via email",
            "enabled": True,
            "icon": "📧",
            "setup_required": False
        },
        "telegram": {
            "name": "Telegram",
            "description": "Send notifications via Telegram bot",
            "enabled": True,
            "icon": "📱",
            "setup_required": True,
            "setup_instructions": "Add @CloudereMonitorBot and send /start command"
        },
        "webhook": {
            "name": "Webhook",
            "description": "Send notifications to custom webhook URL (Slack, Discord, etc.)",
            "enabled": True,
            "icon": "🔗",
            "setup_required": True,
            "setup_instructions": "Provide webhook URL for your service"
        }
    }
    
    return {
        "success": True,
        "channels": channels
    }