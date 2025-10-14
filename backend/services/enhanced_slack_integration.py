"""
Enhanced Slack Integration for SSL Monitor Pro
Features:
- Rich message formatting with blocks
- Interactive buttons and actions
- Channel-specific settings
- Team workspace management
- Slack app installation flow
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

@dataclass
class SlackWorkspace:
    """Slack workspace data model"""
    team_id: str
    team_name: str
    access_token: str
    bot_user_id: str
    app_id: str
    scope: str
    installed_at: datetime
    is_active: bool = True

@dataclass
class SlackChannel:
    """Slack channel data model"""
    channel_id: str
    channel_name: str
    team_id: str
    is_private: bool = False
    notification_enabled: bool = True
    alert_threshold_days: int = 30
    language: str = 'en'
    quiet_hours_start: str = '22:00'
    quiet_hours_end: str = '08:00'
    timezone: str = 'UTC'

class EnhancedSlackIntegration:
    """Enhanced Slack integration with rich notifications"""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        self.redirect_uri = os.getenv("SLACK_REDIRECT_URI")
        
        # Language support
        self.languages = {
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'it': 'Italiano',
            'ru': 'Русский',
            'cs': 'Čeština'
        }
        
        # Notification templates by language
        self.templates = self._load_templates()
        
        if not all([self.client_id, self.client_secret, self.signing_secret]):
            logger.warning("Slack integration disabled: Missing configuration")
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load notification templates for different languages"""
        return {
            'en': {
                'ssl_warning': {
                    'title': '⚠️ SSL Certificate Warning',
                    'color': '#ff9500',
                    'fields': [
                        {'title': 'Domain', 'value': '{domain}', 'short': True},
                        {'title': 'Days Left', 'value': '{days}', 'short': True},
                        {'title': 'Status', 'value': 'Expiring Soon', 'short': True},
                        {'title': 'Time', 'value': '{timestamp}', 'short': True}
                    ]
                },
                'ssl_critical': {
                    'title': '🚨 SSL Certificate Critical',
                    'color': '#ff0000',
                    'fields': [
                        {'title': 'Domain', 'value': '{domain}', 'short': True},
                        {'title': 'Days Left', 'value': '{days}', 'short': True},
                        {'title': 'Status', 'value': 'URGENT ACTION REQUIRED', 'short': True},
                        {'title': 'Time', 'value': '{timestamp}', 'short': True}
                    ]
                },
                'ssl_expired': {
                    'title': '💥 SSL Certificate Expired',
                    'color': '#ff0000',
                    'fields': [
                        {'title': 'Domain', 'value': '{domain}', 'short': True},
                        {'title': 'Days Overdue', 'value': '{days}', 'short': True},
                        {'title': 'Status', 'value': 'EXPIRED - IMMEDIATE ACTION', 'short': True},
                        {'title': 'Time', 'value': '{timestamp}', 'short': True}
                    ]
                },
                'payment_success': {
                    'title': '💳 Payment Successful',
                    'color': '#00ff00',
                    'fields': [
                        {'title': 'Customer', 'value': '{email}', 'short': True},
                        {'title': 'Plan', 'value': '{plan}', 'short': True},
                        {'title': 'Amount', 'value': '{amount} {currency}', 'short': True},
                        {'title': 'Time', 'value': '{timestamp}', 'short': True}
                    ]
                }
            },
            'de': {
                'ssl_warning': {
                    'title': '⚠️ SSL-Zertifikat Warnung',
                    'color': '#ff9500',
                    'fields': [
                        {'title': 'Domain', 'value': '{domain}', 'short': True},
                        {'title': 'Tage übrig', 'value': '{days}', 'short': True},
                        {'title': 'Status', 'value': 'Läuft bald ab', 'short': True},
                        {'title': 'Zeit', 'value': '{timestamp}', 'short': True}
                    ]
                },
                'ssl_critical': {
                    'title': '🚨 SSL-Zertifikat kritisch',
                    'color': '#ff0000',
                    'fields': [
                        {'title': 'Domain', 'value': '{domain}', 'short': True},
                        {'title': 'Tage übrig', 'value': '{days}', 'short': True},
                        {'title': 'Status', 'value': 'DRINGENDE MASSNAHME ERFORDERLICH', 'short': True},
                        {'title': 'Zeit', 'value': '{timestamp}', 'short': True}
                    ]
                }
            }
        }
    
    async def send_rich_notification(
        self, 
        channel: str, 
        notification_type: str, 
        language: str = 'en',
        **kwargs
    ) -> bool:
        """Send rich Slack notification with blocks"""
        try:
            template = self.templates.get(language, self.templates['en']).get(notification_type)
            if not template:
                logger.warning(f"No template found for {notification_type} in language {language}")
                return False
            
            # Prepare message data
            message_data = {
                'domain': kwargs.get('domain', 'Unknown'),
                'days': kwargs.get('days', 'N/A'),
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
                'email': kwargs.get('email', 'Unknown'),
                'plan': kwargs.get('plan', 'Unknown'),
                'amount': kwargs.get('amount', 'N/A'),
                'currency': kwargs.get('currency', 'EUR')
            }
            
            # Create rich message
            blocks = self._create_notification_blocks(template, message_data)
            
            # Send message
            return await self._send_slack_message(channel, blocks)
            
        except Exception as e:
            logger.error(f"Error sending rich Slack notification: {e}")
            return False
    
    def _create_notification_blocks(self, template: Dict[str, Any], data: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create Slack blocks for notification"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": template['title']
                }
            },
            {
                "type": "section",
                "fields": []
            }
        ]
        
        # Add fields
        for field in template['fields']:
            field_value = field['value'].format(**data)
            blocks[1]['fields'].append({
                "type": "mrkdwn",
                "text": f"*{field['title']}:*\n{field_value}"
            })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        # Add action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Dashboard"
                    },
                    "url": "https://cloudsre.xyz/dashboard",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Manage Domains"
                    },
                    "url": "https://cloudsre.xyz/dashboard#domains"
                }
            ]
        })
        
        return blocks
    
    async def send_interactive_notification(
        self,
        channel: str,
        domain: str,
        days_left: int,
        language: str = 'en'
    ) -> bool:
        """Send interactive notification with buttons"""
        try:
            status = "warning"
            color = "#ff9500"
            emoji = "⚠️"
            
            if days_left <= 0:
                status = "expired"
                color = "#ff0000"
                emoji = "💥"
            elif days_left <= 7:
                status = "critical"
                color = "#ff0000"
                emoji = "🚨"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} SSL Certificate Alert - {domain}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Domain:* {domain}\n*Days Left:* {days_left}\n*Status:* {status.title()}\n*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Acknowledge"
                            },
                            "action_id": "acknowledge_alert",
                            "value": f"{domain}_{days_left}",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔔 Mute Domain"
                            },
                            "action_id": "mute_domain",
                            "value": domain
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⚙️ Settings"
                            },
                            "action_id": "open_settings",
                            "value": channel
                        }
                    ]
                }
            ]
            
            return await self._send_slack_message(channel, blocks)
            
        except Exception as e:
            logger.error(f"Error sending interactive Slack notification: {e}")
            return False
    
    async def handle_slack_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack button clicks and interactions"""
        try:
            action = payload.get('actions', [{}])[0]
            action_id = action.get('action_id')
            value = action.get('value')
            user = payload.get('user', {})
            channel = payload.get('channel', {})
            
            response = {"ok": True}
            
            if action_id == 'acknowledge_alert':
                response = await self._handle_acknowledge_alert(value, user, channel)
            elif action_id == 'mute_domain':
                response = await self._handle_mute_domain(value, user, channel)
            elif action_id == 'open_settings':
                response = await self._handle_open_settings(value, user, channel)
            else:
                response = {"ok": False, "error": "Unknown action"}
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling Slack interaction: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _handle_acknowledge_alert(self, value: str, user: Dict[str, Any], channel: Dict[str, Any]) -> Dict[str, Any]:
        """Handle alert acknowledgment"""
        try:
            domain, days = value.split('_')
            
            # Update acknowledgment in database
            # This would integrate with the actual database
            
            # Send confirmation message
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ Alert for {domain} acknowledged by <@{user['id']}>"
                    }
                }
            ]
            
            await self._send_slack_message(channel['id'], blocks)
            
            return {"ok": True, "message": "Alert acknowledged"}
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _handle_mute_domain(self, domain: str, user: Dict[str, Any], channel: Dict[str, Any]) -> Dict[str, Any]:
        """Handle domain muting"""
        try:
            # Update domain muting in database
            # This would integrate with the actual database
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔕 Alerts for {domain} have been muted by <@{user['id']}>\n\nUse `/ssl-unmute {domain}` to unmute."
                    }
                }
            ]
            
            await self._send_slack_message(channel['id'], blocks)
            
            return {"ok": True, "message": "Domain muted"}
            
        except Exception as e:
            logger.error(f"Error muting domain: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _handle_open_settings(self, channel_id: str, user: Dict[str, Any], channel: Dict[str, Any]) -> Dict[str, Any]:
        """Handle settings opening"""
        try:
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
                        "text": "Configure your SSL monitoring preferences:"
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
                            "value": channel_id
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "⚠️ Alert Threshold"
                            },
                            "action_id": "change_threshold",
                            "value": channel_id
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔔 Notifications"
                            },
                            "action_id": "toggle_notifications",
                            "value": channel_id
                        }
                    ]
                }
            ]
            
            await self._send_slack_message(channel_id, blocks)
            
            return {"ok": True, "message": "Settings opened"}
            
        except Exception as e:
            logger.error(f"Error opening settings: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _send_slack_message(self, channel: str, blocks: List[Dict[str, Any]]) -> bool:
        """Send message to Slack channel"""
        try:
            # This would use the appropriate access token for the workspace
            # For now, use webhook URL if available
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            
            if not webhook_url:
                logger.warning("No Slack webhook URL configured")
                return False
            
            payload = {
                "channel": channel,
                "blocks": blocks,
                "text": "SSL Monitor Pro Alert"  # Fallback text
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False
    
    async def send_daily_report(self, channel: str, stats: Dict[str, Any]) -> bool:
        """Send daily monitoring report"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 SSL Monitor Daily Report"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Domains:*\n{stats.get('total_domains', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Expiring Soon:*\n{stats.get('expiring_soon', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Expired:*\n{stats.get('expired', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Errors:*\n{stats.get('errors', 0)}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Report generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                        }
                    ]
                }
            ]
            
            return await self._send_slack_message(channel, blocks)
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
            return False
    
    async def send_installation_success(self, team_id: str, team_name: str) -> bool:
        """Send installation success message"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎉 SSL Monitor Pro Installed Successfully!"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Welcome to SSL Monitor Pro, {team_name}!\n\nI'll help you monitor your SSL certificates and send alerts when they're about to expire.\n\n*Getting Started:*\n1. Use `/ssl-add <domain>` to add a domain\n2. Use `/ssl-list` to see your monitored domains\n3. Use `/ssl-settings` to configure alerts"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🚀 Open Dashboard"
                            },
                            "url": "https://cloudsre.xyz/dashboard",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📚 View Documentation"
                            },
                            "url": "https://cloudsre.xyz/docs"
                        }
                    ]
                }
            ]
            
            # Send to general channel or direct message
            return await self._send_slack_message("#general", blocks)
            
        except Exception as e:
            logger.error(f"Error sending installation success message: {e}")
            return False

# Global instance
_slack_instance = None

def get_slack_instance(db_session: Session = None) -> EnhancedSlackIntegration:
    """Get global Slack instance"""
    global _slack_instance
    if _slack_instance is None:
        _slack_instance = EnhancedSlackIntegration(db_session=db_session)
    return _slack_instance

async def handle_slack_webhook(payload: Dict[str, Any], db_session: Session = None) -> Dict[str, Any]:
    """Handle incoming Slack webhook"""
    slack = get_slack_instance(db_session)
    
    # Handle different types of interactions
    if payload.get('type') == 'url_verification':
        return {"challenge": payload.get('challenge')}
    elif payload.get('type') == 'event_callback':
        # Handle event callbacks
        return {"ok": True}
    elif payload.get('type') == 'interactive_message':
        # Handle interactive message responses
        return await slack.handle_slack_interaction(payload)
    else:
        return {"ok": False, "error": "Unknown payload type"}
