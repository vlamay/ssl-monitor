"""
Slack Integration API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import secrets

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.services.slack import slack_service
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SlackOAuthRequest(BaseModel):
    """Slack OAuth request"""
    state: Optional[str] = Field(default=None, description="Optional state parameter")


class SlackOAuthCallback(BaseModel):
    """Slack OAuth callback data"""
    code: str = Field(..., description="Authorization code from Slack")
    state: Optional[str] = Field(default=None, description="State parameter for verification")


class SlackNotificationCreate(BaseModel):
    """Create Slack notification request"""
    channel: str = Field(..., description="Slack channel ID or name")
    enabled: bool = Field(default=True, description="Enable/disable notification")
    triggers: list[str] = Field(default=["expires_in_30d", "expires_in_7d", "expires_in_1d", "expired"])
    team_id: Optional[str] = Field(default=None, description="Slack team ID")


class SlackNotificationUpdate(BaseModel):
    """Update Slack notification request"""
    channel: Optional[str] = None
    enabled: Optional[bool] = None
    triggers: Optional[list[str]] = None


class SlackNotificationResponse(BaseModel):
    """Slack notification response"""
    id: int
    channel: str
    enabled: bool
    triggers: list[str]
    team_id: Optional[str]
    created_at: str
    updated_at: str


class SlackTestRequest(BaseModel):
    """Test Slack notification request"""
    channel: str = Field(..., description="Channel to test")
    message: Optional[str] = Field(default=None, description="Custom test message")


@router.get("/oauth-url")
async def get_slack_oauth_url(
    current_user: User = Depends(get_current_user)
):
    """Get Slack OAuth authorization URL"""
    try:
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        
        oauth_url = slack_service.get_oauth_url(state=state)
        
        return {
            "oauth_url": oauth_url,
            "state": state,
            "instructions": "Click the OAuth URL to authorize Slack integration"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Slack OAuth not configured: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating Slack OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OAuth URL"
        )


@router.post("/oauth/callback")
async def handle_slack_oauth_callback(
    callback_data: SlackOAuthCallback,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle Slack OAuth callback and exchange code for token"""
    try:
        # Exchange code for access token
        token_response = await slack_service.exchange_code_for_token(callback_data.code)
        
        if not token_response.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth token exchange failed: {token_response.get('error')}"
            )
        
        access_token = token_response.get('access_token')
        team_info = token_response.get('team', {})
        team_id = team_info.get('id')
        team_name = team_info.get('name')
        
        # Get available channels
        channels_response = await slack_service.get_channels(access_token)
        
        if not channels_response.get('success'):
            logger.warning(f"Failed to fetch channels: {channels_response.get('error')}")
            channels = []
        else:
            channels = channels_response.get('channels', [])
        
        return {
            "success": True,
            "access_token": access_token,  # Note: In production, store this securely
            "team": {
                "id": team_id,
                "name": team_name
            },
            "channels": channels,
            "message": "Slack integration successful! You can now create notifications."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling Slack OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OAuth callback"
        )


@router.get("/notifications", response_model=list[SlackNotificationResponse])
async def get_slack_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all Slack notifications for current user"""
    try:
        query = select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SLACK
        )
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return [
            SlackNotificationResponse(
                id=n.id,
                channel=n.channel,
                enabled=n.enabled,
                triggers=n.triggers.split(',') if n.triggers else [],
                team_id=getattr(n, 'team_id', None),
                created_at=n.created_at.isoformat(),
                updated_at=n.updated_at.isoformat()
            )
            for n in notifications
        ]
    except Exception as e:
        logger.error(f"Error getting Slack notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Slack notifications"
        )


@router.post("/notifications", response_model=SlackNotificationResponse)
async def create_slack_notification(
    notification: SlackNotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new Slack notification"""
    try:
        # Check if Slack notification already exists for this channel
        existing_query = select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SLACK,
            Notification.channel == notification.channel
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slack notification already exists for this channel"
            )
        
        # Create new notification
        new_notification = Notification(
            user_id=current_user.id,
            type=NotificationType.SLACK,
            enabled=notification.enabled,
            channel=notification.channel,
            triggers=','.join(notification.triggers),
            team_id=notification.team_id
        )
        
        db.add(new_notification)
        await db.commit()
        await db.refresh(new_notification)
        
        return SlackNotificationResponse(
            id=new_notification.id,
            channel=new_notification.channel,
            enabled=new_notification.enabled,
            triggers=new_notification.triggers.split(',') if new_notification.triggers else [],
            team_id=getattr(new_notification, 'team_id', None),
            created_at=new_notification.created_at.isoformat(),
            updated_at=new_notification.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Slack notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Slack notification"
        )


@router.put("/notifications/{notification_id}", response_model=SlackNotificationResponse)
async def update_slack_notification(
    notification_id: int,
    notification: SlackNotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update Slack notification"""
    try:
        # Find notification
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SLACK
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slack notification not found"
            )
        
        # Update fields
        if notification.channel is not None:
            existing.channel = notification.channel
        if notification.enabled is not None:
            existing.enabled = notification.enabled
        if notification.triggers is not None:
            existing.triggers = ','.join(notification.triggers)
        
        await db.commit()
        await db.refresh(existing)
        
        return SlackNotificationResponse(
            id=existing.id,
            channel=existing.channel,
            enabled=existing.enabled,
            triggers=existing.triggers.split(',') if existing.triggers else [],
            team_id=getattr(existing, 'team_id', None),
            created_at=existing.created_at.isoformat(),
            updated_at=existing.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Slack notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update Slack notification"
        )


@router.delete("/notifications/{notification_id}")
async def delete_slack_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete Slack notification"""
    try:
        # Find notification
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.type == NotificationType.SLACK
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slack notification not found"
            )
        
        await db.delete(notification)
        await db.commit()
        
        return {"message": "Slack notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Slack notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Slack notification"
        )


@router.post("/test")
async def test_slack_notification(
    test_request: SlackTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test Slack notification"""
    try:
        # Check if Slack service is configured
        setup_status = slack_service.get_setup_status()
        if not setup_status['bot_configured']:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Slack bot not configured. Please contact support."
            )
        
        # Prepare test message
        message = test_request.message or f"SSL Monitor Pro Test Message for {current_user.full_name}. Slack notifications are working correctly!"
        
        # Send test message
        result = await slack_service.send_message(test_request.channel, message)
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Test message sent successfully",
                "channel": result.get('channel'),
                "timestamp": result.get('timestamp'),
                "test_message": message
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Slack message failed: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Slack: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test Slack message"
        )


@router.get("/channels")
async def get_slack_channels(
    token: str = Query(..., description="Slack access token"),
    current_user: User = Depends(get_current_user)
):
    """Get available Slack channels"""
    try:
        result = await slack_service.get_channels(token)
        
        if result.get('success'):
            return {
                "success": True,
                "channels": result.get('channels', [])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch channels: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Slack channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch Slack channels"
        )


@router.get("/setup-status")
async def get_slack_setup_status():
    """Get Slack integration setup status"""
    try:
        setup_status = slack_service.get_setup_status()
        
        return {
            "setup_status": setup_status,
            "instructions": {
                "oauth_required": "Configure SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, and SLACK_REDIRECT_URI for OAuth",
                "bot_required": "Configure SLACK_BOT_TOKEN for sending messages",
                "setup_guide": "See Slack Integration Guide for detailed setup instructions"
            }
        }
    except Exception as e:
        logger.error(f"Error getting Slack setup status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get setup status"
        )
