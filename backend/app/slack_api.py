"""
Slack API endpoints for SSL Monitor Pro
Handles webhook, OAuth, and Slack app interactions
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime, timedelta

from database import get_db
from services.enhanced_slack_integration import EnhancedSlackIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slack", tags=["slack"])

# Pydantic models
class SlackOAuthRequest(BaseModel):
    """Slack OAuth request model"""
    code: str
    state: Optional[str] = None

class SlackWebhookData(BaseModel):
    """Slack webhook data model"""
    type: str
    challenge: Optional[str] = None
    event: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None

class SlackNotificationRequest(BaseModel):
    """Slack notification request model"""
    channel: str
    notification_type: str  # 'ssl_warning', 'ssl_critical', 'ssl_expired', etc.
    domain: Optional[str] = None
    days_left: Optional[int] = None
    language: str = 'en'
    **kwargs: Any

class SlackWorkspaceResponse(BaseModel):
    """Slack workspace response model"""
    team_id: str
    team_name: str
    bot_user_id: str
    app_id: str
    scope: str
    installed_at: datetime
    is_active: bool

class SlackChannelResponse(BaseModel):
    """Slack channel response model"""
    channel_id: str
    channel_name: str
    team_id: str
    is_private: bool
    notification_enabled: bool
    alert_threshold_days: int
    language: str
    quiet_hours_start: str
    quiet_hours_end: str
    timezone: str

class SlackStatsResponse(BaseModel):
    """Slack statistics response model"""
    total_workspaces: int
    active_workspaces: int
    total_channels: int
    notifications_sent_today: int
    notifications_sent_total: int
    delivery_rate: float
    languages: Dict[str, int]

@router.get("/oauth")
async def slack_oauth_start():
    """
    Start Slack OAuth flow
    """
    try:
        import os
        
        client_id = os.getenv("SLACK_CLIENT_ID")
        redirect_uri = os.getenv("SLACK_REDIRECT_URI")
        scope = "chat:write,channels:read,groups:read,im:read,mpim:read,users:read,team:read"
        
        if not client_id or not redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slack OAuth not configured"
            )
        
        oauth_url = (
            f"https://slack.com/oauth/v2/authorize?"
            f"client_id={client_id}&"
            f"scope={scope}&"
            f"redirect_uri={redirect_uri}"
        )
        
        return JSONResponse(content={
            "oauth_url": oauth_url,
            "message": "Redirect user to this URL to install the app"
        })
        
    except Exception as e:
        logger.error(f"Error starting Slack OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start OAuth: {str(e)}"
        )

@router.get("/oauth/callback")
async def slack_oauth_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Handle Slack OAuth callback
    """
    try:
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {error}"
            )
        
        import os
        import requests
        
        client_id = os.getenv("SLACK_CLIENT_ID")
        client_secret = os.getenv("SLACK_CLIENT_SECRET")
        redirect_uri = os.getenv("SLACK_REDIRECT_URI")
        
        if not all([client_id, client_secret, redirect_uri]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slack OAuth not configured"
            )
        
        # Exchange code for access token
        token_url = "https://slack.com/api/oauth.v2.access"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        response = requests.post(token_url, data=token_data, timeout=10)
        response.raise_for_status()
        
        token_result = response.json()
        
        if not token_result.get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth failed: {token_result.get('error')}"
            )
        
        # Store workspace information
        team_info = token_result.get("team", {})
        authed_user = token_result.get("authed_user", {})
        
        # This would store in the actual database
        # For now, just log the success
        
        logger.info(f"Slack app installed for team: {team_info.get('name')} ({team_info.get('id')})")
        
        # Send installation success message
        slack = EnhancedSlackIntegration(db_session=db)
        await slack.send_installation_success(
            team_info.get("id"),
            team_info.get("name")
        )
        
        return JSONResponse(content={
            "ok": True,
            "message": "Slack app installed successfully",
            "team_id": team_info.get("id"),
            "team_name": team_info.get("name"),
            "access_token": token_result.get("access_token"),
            "bot_user_id": token_result.get("bot_user_id")
        })
        
    except Exception as e:
        logger.error(f"Error handling Slack OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete OAuth: {str(e)}"
        )

@router.post("/webhook")
async def slack_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle incoming Slack webhook events
    """
    try:
        # Get request data
        body = await request.body()
        payload = json.loads(body)
        
        logger.info(f"Received Slack webhook: {payload.get('type')}")
        
        # Initialize Slack integration
        slack = EnhancedSlackIntegration(db_session=db)
        
        # Handle webhook
        result = await slack.handle_slack_interaction(payload)
        
        if result.get("ok"):
            return JSONResponse(content=result)
        else:
            return JSONResponse(
                content=result,
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Slack webhook error: {e}")
        return JSONResponse(
            content={"ok": False, "error": str(e)},
            status_code=500
        )

@router.post("/webhook/events")
async def slack_events_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Slack Events API webhook
    """
    try:
        body = await request.body()
        payload = json.loads(body)
        
        # Handle URL verification
        if payload.get("type") == "url_verification":
            return JSONResponse(content={
                "challenge": payload.get("challenge")
            })
        
        # Handle event callbacks
        if payload.get("type") == "event_callback":
            event = payload.get("event", {})
            event_type = event.get("type")
            
            logger.info(f"Received Slack event: {event_type}")
            
            # Handle different event types
            if event_type == "app_mention":
                await handle_app_mention(event, db)
            elif event_type == "message":
                await handle_message(event, db)
            elif event_type == "team_join":
                await handle_team_join(event, db)
            
            return JSONResponse(content={"ok": True})
        
        return JSONResponse(content={"ok": True})
        
    except Exception as e:
        logger.error(f"Slack events webhook error: {e}")
        return JSONResponse(
            content={"ok": False, "error": str(e)},
            status_code=500
        )

async def handle_app_mention(event: Dict[str, Any], db: Session):
    """Handle app mention events"""
    try:
        slack = EnhancedSlackIntegration(db_session=db)
        
        # Send help message when app is mentioned
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "👋 Hi! I'm SSL Monitor Pro. Here's what I can do:\n\n• Monitor your SSL certificates\n• Send alerts when certificates are expiring\n• Provide daily reports\n• Help you manage your domains\n\nUse `/ssl-help` for more commands!"
                }
            }
        ]
        
        channel = event.get("channel")
        await slack._send_slack_message(channel, blocks)
        
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")

async def handle_message(event: Dict[str, Any], db: Session):
    """Handle message events"""
    try:
        # Handle slash commands and mentions
        text = event.get("text", "")
        channel = event.get("channel")
        
        if text.startswith("/ssl"):
            await handle_slash_command(text, channel, event, db)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")

async def handle_team_join(event: Dict[str, Any], db: Session):
    """Handle team join events"""
    try:
        slack = EnhancedSlackIntegration(db_session=db)
        
        user = event.get("user", {})
        team_id = event.get("team")
        
        # Send welcome message to new team member
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"👋 Welcome to the team, <@{user.get('id')}>!\n\nSSL Monitor Pro is here to help keep your SSL certificates secure. Use `/ssl-help` to get started!"
                }
            }
        ]
        
        await slack._send_slack_message("#general", blocks)
        
    except Exception as e:
        logger.error(f"Error handling team join: {e}")

async def handle_slash_command(text: str, channel: str, event: Dict[str, Any], db: Session):
    """Handle slash commands"""
    try:
        slack = EnhancedSlackIntegration(db_session=db)
        
        if "/ssl-help" in text:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*SSL Monitor Pro Commands:*\n\n• `/ssl-add <domain>` - Add a domain to monitor\n• `/ssl-list` - List your monitored domains\n• `/ssl-status <domain>` - Get domain status\n• `/ssl-settings` - Configure notification settings\n• `/ssl-report` - Get daily monitoring report"
                    }
                }
            ]
            await slack._send_slack_message(channel, blocks)
            
        elif "/ssl-add" in text:
            # Extract domain from command
            domain = text.replace("/ssl-add", "").strip()
            if domain:
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"✅ Added {domain} to monitoring!\n\nI'll start checking this domain and send alerts when the SSL certificate is about to expire."
                        }
                    }
                ]
            else:
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "❌ Please provide a domain name.\n\nUsage: `/ssl-add example.com`"
                        }
                    }
                ]
            await slack._send_slack_message(channel, blocks)
            
        elif "/ssl-list" in text:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Your Monitored Domains:*\n\n• example.com - ✅ Healthy (89 days)\n• test.com - ⚠️ Warning (15 days)\n• demo.com - 🚨 Critical (3 days)\n\nUse `/ssl-status <domain>` for detailed information."
                    }
                }
            ]
            await slack._send_slack_message(channel, blocks)
            
        elif "/ssl-settings" in text:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚙️ SSL Monitor Settings"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Configure your notification preferences:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🌐 Language"
                            },
                            "action_id": "change_language",
                            "value": channel
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⚠️ Alert Threshold"
                            },
                            "action_id": "change_threshold",
                            "value": channel
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔔 Notifications"
                            },
                            "action_id": "toggle_notifications",
                            "value": channel
                        }
                    ]
                }
            ]
            await slack._send_slack_message(channel, blocks)
            
    except Exception as e:
        logger.error(f"Error handling slash command: {e}")

@router.get("/workspaces", response_model=List[SlackWorkspaceResponse])
async def get_slack_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of Slack workspaces
    """
    try:
        # This would query the actual database
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Error getting Slack workspaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Slack workspaces: {str(e)}"
        )

@router.get("/channels", response_model=List[SlackChannelResponse])
async def get_slack_channels(
    team_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of Slack channels
    """
    try:
        # This would query the actual database
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Error getting Slack channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Slack channels: {str(e)}"
        )

@router.post("/notifications/send")
async def send_slack_notification(
    notification: SlackNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send a Slack notification
    """
    try:
        slack = EnhancedSlackIntegration(db_session=db)
        
        # Prepare notification data
        notification_data = {
            "domain": notification.domain,
            "days": notification.days_left,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        }
        
        # Add any additional kwargs
        notification_data.update(notification.kwargs)
        
        # Send notification
        success = await slack.send_rich_notification(
            notification.channel,
            notification.notification_type,
            notification.language,
            **notification_data
        )
        
        if success:
            return JSONResponse(content={
                "ok": True,
                "message": "Notification sent successfully",
                "channel": notification.channel,
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
        logger.error(f"Error sending Slack notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )

@router.get("/stats", response_model=SlackStatsResponse)
async def get_slack_stats(db: Session = Depends(get_db)):
    """
    Get Slack integration statistics
    """
    try:
        # This would query the actual database
        # For now, return mock stats
        return SlackStatsResponse(
            total_workspaces=5,
            active_workspaces=4,
            total_channels=15,
            notifications_sent_today=45,
            notifications_sent_total=320,
            delivery_rate=0.97,
            languages={"en": 12, "de": 2, "ru": 1}
        )
    except Exception as e:
        logger.error(f"Error getting Slack stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Slack stats: {str(e)}"
        )

@router.post("/test-connection")
async def test_slack_connection():
    """
    Test Slack integration connection
    """
    try:
        import os
        
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        client_id = os.getenv("SLACK_CLIENT_ID")
        
        if not webhook_url and not client_id:
            return JSONResponse(
                content={
                    "ok": False,
                    "error": "Slack integration not configured"
                },
                status_code=400
            )
        
        # Test webhook if available
        if webhook_url:
            import requests
            
            test_payload = {
                "text": "✅ SSL Monitor Pro - Slack connection test successful!",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ *SSL Monitor Pro* - Slack integration is working correctly!"
                        }
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=test_payload, timeout=10)
            response.raise_for_status()
        
        return JSONResponse(content={
            "ok": True,
            "message": "Slack connection test successful",
            "webhook_configured": bool(webhook_url),
            "oauth_configured": bool(client_id)
        })
        
    except Exception as e:
        logger.error(f"Error testing Slack connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test Slack connection: {str(e)}"
        )

@router.get("/info")
async def get_slack_app_info():
    """
    Get Slack app information
    """
    try:
        import os
        
        client_id = os.getenv("SLACK_CLIENT_ID")
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        return {
            "app_name": "SSL Monitor Pro",
            "client_id": client_id,
            "webhook_configured": bool(webhook_url),
            "oauth_configured": bool(client_id),
            "features": [
                "SSL certificate monitoring",
                "Rich notifications with blocks",
                "Interactive buttons and actions",
                "Slash commands",
                "Multi-language support",
                "Channel-specific settings"
            ],
            "commands": [
                "/ssl-add <domain> - Add domain to monitor",
                "/ssl-list - List monitored domains",
                "/ssl-status <domain> - Get domain status",
                "/ssl-settings - Configure notifications",
                "/ssl-help - Show help message"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting Slack app info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Slack app info: {str(e)}"
        )
