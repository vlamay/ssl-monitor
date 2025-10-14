"""
Slack Integration Service
Supports OAuth 2.0 authentication and team notifications
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SlackService:
    """Slack integration service for team notifications"""
    
    def __init__(self):
        self.client_id = getattr(settings, 'SLACK_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'SLACK_CLIENT_SECRET', None)
        self.redirect_uri = getattr(settings, 'SLACK_REDIRECT_URI', None)
        self.bot_token = getattr(settings, 'SLACK_BOT_TOKEN', None)
        
        # Slack API endpoints
        self.oauth_url = "https://slack.com/oauth/v2/authorize"
        self.token_url = "https://slack.com/api/oauth.v2.access"
        self.chat_url = "https://slack.com/api/chat.postMessage"
        self.channels_url = "https://slack.com/api/conversations.list"
        self.user_info_url = "https://slack.com/api/users.info"
    
    def get_oauth_url(self, state: str = None) -> str:
        """
        Generate Slack OAuth 2.0 authorization URL
        
        Args:
            state: Optional state parameter for security
        
        Returns:
            OAuth authorization URL
        """
        if not self.client_id or not self.redirect_uri:
            raise ValueError("Slack OAuth not configured. Set SLACK_CLIENT_ID and SLACK_REDIRECT_URI")
        
        params = {
            'client_id': self.client_id,
            'scope': 'chat:write,channels:read,groups:read,im:read,mpim:read',
            'redirect_uri': self.redirect_uri,
            'response_type': 'code'
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.oauth_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
        
        Returns:
            Token response with access token and team info
        """
        if not self.client_secret:
            raise ValueError("Slack client secret not configured")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        return {
                            'success': True,
                            'access_token': result.get('access_token'),
                            'team': result.get('team'),
                            'authed_user': result.get('authed_user'),
                            'scope': result.get('scope')
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error')
                        }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
                    
        except Exception as e:
            logger.error(f"Slack token exchange failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_message(
        self, 
        channel: str, 
        message: str, 
        token: str = None,
        blocks: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send message to Slack channel
        
        Args:
            channel: Channel ID or name (e.g., '#general', 'C1234567890')
            message: Message text
            token: Bot token (optional, uses default if not provided)
            blocks: Rich message blocks (optional)
        
        Returns:
            Send result with success status and details
        """
        token = token or self.bot_token
        if not token:
            return {
                'success': False,
                'error': 'No Slack token available'
            }
        
        payload = {
            'channel': channel,
            'text': message,
            'token': token
        }
        
        if blocks:
            payload['blocks'] = blocks
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.chat_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        return {
                            'success': True,
                            'channel': result.get('channel'),
                            'timestamp': result.get('ts'),
                            'message': result.get('message')
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error')
                        }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
                    
        except Exception as e:
            logger.error(f"Slack message send failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_channels(self, token: str = None) -> Dict[str, Any]:
        """
        Get list of available channels
        
        Args:
            token: Bot token (optional, uses default if not provided)
        
        Returns:
            List of channels with details
        """
        token = token or self.bot_token
        if not token:
            return {
                'success': False,
                'error': 'No Slack token available'
            }
        
        params = {
            'token': token,
            'types': 'public_channel,private_channel'
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.channels_url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        channels = []
                        for channel in result.get('channels', []):
                            channels.append({
                                'id': channel.get('id'),
                                'name': channel.get('name'),
                                'is_private': channel.get('is_private', False),
                                'is_member': channel.get('is_member', False)
                            })
                        
                        return {
                            'success': True,
                            'channels': channels
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error')
                        }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
                    
        except Exception as e:
            logger.error(f"Slack channels fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_info(self, user_id: str, token: str = None) -> Dict[str, Any]:
        """
        Get user information
        
        Args:
            user_id: Slack user ID
            token: Bot token (optional, uses default if not provided)
        
        Returns:
            User information
        """
        token = token or self.bot_token
        if not token:
            return {
                'success': False,
                'error': 'No Slack token available'
            }
        
        params = {
            'token': token,
            'user': user_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.user_info_url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        user = result.get('user', {})
                        return {
                            'success': True,
                            'user': {
                                'id': user.get('id'),
                                'name': user.get('name'),
                                'real_name': user.get('real_name'),
                                'email': user.get('profile', {}).get('email'),
                                'avatar': user.get('profile', {}).get('image_72')
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error')
                        }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
                    
        except Exception as e:
            logger.error(f"Slack user info fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_ssl_alert(
        self, 
        channel: str, 
        domain: str, 
        alert_type: str,
        days_remaining: Optional[int] = None,
        token: str = None
    ) -> Dict[str, Any]:
        """
        Send SSL-specific alert to Slack
        
        Args:
            channel: Slack channel
            domain: Domain name
            alert_type: Type of alert (expires_soon, expired, renewed)
            days_remaining: Days until expiration (for expires_soon)
            token: Bot token (optional)
        """
        messages = {
            'expires_soon': f"🔒 *SSL Alert*: {domain} expires in {days_remaining} days. Time to renew!",
            'expired': f"🚨 *URGENT*: SSL certificate for {domain} has EXPIRED! Immediate action required.",
            'renewed': f"✅ *SSL Update*: Certificate for {domain} has been renewed successfully.",
            'renewal_failed': f"❌ *SSL Error*: Failed to renew certificate for {domain}. Manual intervention needed."
        }
        
        message = messages.get(alert_type, f"SSL Alert for {domain}")
        
        # Create rich message blocks for better formatting
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Domain: {domain} | SSL Monitor Pro"
                    }
                ]
            }
        ]
        
        return await self.send_message(channel, message, token, blocks)
    
    def get_setup_status(self) -> Dict[str, Any]:
        """Get Slack integration setup status"""
        return {
            'oauth_configured': bool(self.client_id and self.client_secret and self.redirect_uri),
            'bot_configured': bool(self.bot_token),
            'client_id': bool(self.client_id),
            'client_secret': bool(self.client_secret),
            'redirect_uri': bool(self.redirect_uri),
            'bot_token': bool(self.bot_token)
        }


# Global Slack service instance
slack_service = SlackService()
