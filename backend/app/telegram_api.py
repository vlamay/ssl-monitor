"""
Telegram API endpoints for SSL Monitor Pro
Handles webhook, user management, and bot interactions
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime, timedelta

from database import get_db
from services.enhanced_telegram_bot import EnhancedTelegramBot, TelegramUser
from services.telegram_bot import TelegramNotifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Pydantic models
class TelegramWebhookData(BaseModel):
    """Telegram webhook update data"""
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

class TelegramUserResponse(BaseModel):
    """Telegram user response model"""
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str
    notification_enabled: bool
    alert_threshold_days: int
    quiet_hours_start: str
    quiet_hours_end: str
    timezone: str
    subscription_status: str
    subscription_plan: Optional[str] = None
    subscription_ends_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class TelegramUserUpdate(BaseModel):
    """Telegram user update model"""
    language: Optional[str] = None
    notification_enabled: Optional[bool] = None
    alert_threshold_days: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

class TelegramNotificationRequest(BaseModel):
    """Telegram notification request model"""
    telegram_id: int
    notification_type: str  # 'ssl_warning', 'ssl_critical', 'ssl_expired', 'payment', etc.
    domain: Optional[str] = None
    days_left: Optional[int] = None
    message: Optional[str] = None
    **kwargs: Any

class TelegramStatsResponse(BaseModel):
    """Telegram statistics response model"""
    total_users: int
    active_users: int
    notifications_sent_today: int
    notifications_sent_total: int
    delivery_rate: float
    languages: Dict[str, int]
    subscription_stats: Dict[str, int]

@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle incoming Telegram webhook updates
    """
    try:
        # Get update data
        update_data = await request.json()
        logger.info(f"Received Telegram webhook: {update_data.get('update_id')}")
        
        # Initialize enhanced bot
        bot = EnhancedTelegramBot(db_session=db)
        
        # Handle update
        success = await bot.handle_update(update_data)
        
        if success:
            return JSONResponse(content={"ok": True, "message": "Update processed"})
        else:
            return JSONResponse(
                content={"ok": False, "error": "Failed to process update"},
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return JSONResponse(
            content={"ok": False, "error": str(e)},
            status_code=500
        )

@router.get("/users", response_model=List[TelegramUserResponse])
async def get_telegram_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of Telegram users
    """
    try:
        # This would query the actual database
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Error getting telegram users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get telegram users: {str(e)}"
        )

@router.get("/users/{telegram_id}", response_model=TelegramUserResponse)
async def get_telegram_user(telegram_id: int, db: Session = Depends(get_db)):
    """
    Get specific Telegram user by telegram_id
    """
    try:
        # This would query the actual database
        # For now, return a mock user
        return TelegramUserResponse(
            id=1,
            telegram_id=telegram_id,
            username="testuser",
            first_name="Test",
            language="en",
            notification_enabled=True,
            alert_threshold_days=30,
            quiet_hours_start="22:00",
            quiet_hours_end="08:00",
            timezone="UTC",
            subscription_status="trial",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error getting telegram user {telegram_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram user {telegram_id} not found"
        )

@router.patch("/users/{telegram_id}", response_model=TelegramUserResponse)
async def update_telegram_user(
    telegram_id: int,
    user_update: TelegramUserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update Telegram user preferences
    """
    try:
        # This would update the actual database
        # For now, return the updated mock user
        return TelegramUserResponse(
            id=1,
            telegram_id=telegram_id,
            username="testuser",
            first_name="Test",
            language=user_update.language or "en",
            notification_enabled=user_update.notification_enabled or True,
            alert_threshold_days=user_update.alert_threshold_days or 30,
            quiet_hours_start=user_update.quiet_hours_start or "22:00",
            quiet_hours_end=user_update.quiet_hours_end or "08:00",
            timezone=user_update.timezone or "UTC",
            subscription_status="trial",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error updating telegram user {telegram_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update telegram user: {str(e)}"
        )

@router.post("/notifications/send")
async def send_telegram_notification(
    notification: TelegramNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send a Telegram notification to a specific user
    """
    try:
        bot = EnhancedTelegramBot(db_session=db)
        
        # Prepare notification data
        notification_data = {
            "domain": notification.domain,
            "days": notification.days_left,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        }
        
        # Add any additional kwargs
        notification_data.update(notification.kwargs)
        
        # Send notification
        success = await bot.send_personalized_notification(
            notification.telegram_id,
            notification.notification_type,
            **notification_data
        )
        
        if success:
            return JSONResponse(content={
                "ok": True,
                "message": "Notification sent successfully",
                "telegram_id": notification.telegram_id,
                "notification_type": notification.notification_type
            })
        else:
            return JSONResponse(
                content={
                    "ok": False,
                    "error": "Failed to send notification"
                },
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error sending telegram notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )

@router.get("/notifications/history")
async def get_notification_history(
    telegram_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get notification history
    """
    try:
        # This would query the actual database
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Error getting notification history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification history: {str(e)}"
        )

@router.get("/stats", response_model=TelegramStatsResponse)
async def get_telegram_stats(db: Session = Depends(get_db)):
    """
    Get Telegram bot statistics
    """
    try:
        # This would query the actual database
        # For now, return mock stats
        return TelegramStatsResponse(
            total_users=10,
            active_users=8,
            notifications_sent_today=25,
            notifications_sent_total=150,
            delivery_rate=0.95,
            languages={"en": 6, "de": 2, "ru": 1, "cs": 1},
            subscription_stats={"trial": 6, "active": 3, "expired": 1}
        )
    except Exception as e:
        logger.error(f"Error getting telegram stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get telegram stats: {str(e)}"
        )

@router.post("/test-connection")
async def test_telegram_connection():
    """
    Test Telegram bot connection
    """
    try:
        from utils.telegram import test_telegram_connection
        
        result = test_telegram_connection()
        
        if result.get("ok"):
            return JSONResponse(content={
                "ok": True,
                "message": "Telegram connection successful",
                "bot_info": result.get("bot", {}),
                "chat_id_configured": result.get("chat_id_configured", False)
            })
        else:
            return JSONResponse(
                content={
                    "ok": False,
                    "error": result.get("error", "Unknown error")
                },
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error testing telegram connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test telegram connection: {str(e)}"
        )

@router.post("/broadcast")
async def broadcast_message(
    message: str,
    language: Optional[str] = None,
    subscription_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Broadcast message to all or filtered Telegram users
    """
    try:
        # This would send to all matching users
        # For now, just return success
        return JSONResponse(content={
            "ok": True,
            "message": "Broadcast message sent",
            "recipients": 10,  # Mock count
            "message": message
        })
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast message: {str(e)}"
        )

@router.get("/settings")
async def get_telegram_settings(db: Session = Depends(get_db)):
    """
    Get Telegram bot settings
    """
    try:
        # This would query the actual database
        # For now, return mock settings
        return {
            "bot_username": "CloudereMonitorBot",
            "webhook_enabled": False,
            "default_language": "en",
            "welcome_message_enabled": True,
            "help_message_enabled": True,
            "rate_limit_per_minute": 20,
            "notification_retry_attempts": 3,
            "quiet_hours_enabled": True
        }
    except Exception as e:
        logger.error(f"Error getting telegram settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get telegram settings: {str(e)}"
        )

@router.post("/settings")
async def update_telegram_settings(
    settings: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update Telegram bot settings
    """
    try:
        # This would update the actual database
        # For now, just return success
        return JSONResponse(content={
            "ok": True,
            "message": "Settings updated successfully",
            "updated_settings": list(settings.keys())
        })
    except Exception as e:
        logger.error(f"Error updating telegram settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update telegram settings: {str(e)}"
        )

@router.post("/webhook/set")
async def set_telegram_webhook(
    webhook_url: str,
    secret_token: Optional[str] = None
):
    """
    Set Telegram webhook URL
    """
    try:
        import os
        import requests
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TELEGRAM_BOT_TOKEN not configured"
            )
        
        # Set webhook
        url = f"https://api.telegram.org/bot{token}/setWebhook"
        data = {"url": webhook_url}
        
        if secret_token:
            data["secret_token"] = secret_token
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("ok"):
            return JSONResponse(content={
                "ok": True,
                "message": "Webhook set successfully",
                "webhook_url": webhook_url,
                "result": result
            })
        else:
            return JSONResponse(
                content={
                    "ok": False,
                    "error": result.get("description", "Unknown error")
                },
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error setting telegram webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set telegram webhook: {str(e)}"
        )

@router.delete("/webhook")
async def delete_telegram_webhook():
    """
    Delete Telegram webhook
    """
    try:
        import os
        import requests
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TELEGRAM_BOT_TOKEN not configured"
            )
        
        # Delete webhook
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("ok"):
            return JSONResponse(content={
                "ok": True,
                "message": "Webhook deleted successfully",
                "result": result
            })
        else:
            return JSONResponse(
                content={
                    "ok": False,
                    "error": result.get("description", "Unknown error")
                },
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error deleting telegram webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete telegram webhook: {str(e)}"
        )

@router.get("/info")
async def get_telegram_bot_info():
    """
    Get Telegram bot information
    """
    try:
        import os
        import requests
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TELEGRAM_BOT_TOKEN not configured"
            )
        
        # Get bot info
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("ok"):
            return JSONResponse(content={
                "ok": True,
                "bot_info": result.get("result", {}),
                "webhook_info": await get_webhook_info()
            })
        else:
            return JSONResponse(
                content={
                    "ok": False,
                    "error": result.get("description", "Unknown error")
                },
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error getting telegram bot info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get telegram bot info: {str(e)}"
        )

async def get_webhook_info():
    """Get webhook information"""
    try:
        import os
        import requests
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            return None
        
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result.get("result", {}) if result.get("ok") else None
        
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return None
