"""
SSL Monitor Pro - Advanced Notification Service
Supports Email, Telegram, Slack, Discord, and Webhooks
"""

import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import json
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # Email settings
        self.smtp_server = os.getenv('MAIL_SERVER', 'smtp-relay.brevo.com')
        self.smtp_port = int(os.getenv('MAIL_PORT', '587'))
        self.smtp_username = os.getenv('MAIL_USERNAME')
        self.smtp_password = os.getenv('MAIL_PASSWORD')
        self.mail_from = os.getenv('MAIL_FROM', 'no-reply@cloudsre.xyz')
        
        # Telegram settings
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Webhook settings
        self.webhook_urls = {}  # Will be populated from user settings

    async def send_notification(self, 
                              notification_type: str,
                              recipient_data: Dict[str, Any],
                              domain_info: Dict[str, Any],
                              notification_settings: Dict[str, Any]) -> Dict[str, bool]:
        """
        Send notification through all enabled channels
        
        Args:
            notification_type: 'expiring_soon', 'expired', 'check_failed', 'weekly_report'
            recipient_data: User email, telegram_chat_id, etc.
            domain_info: Domain name, days_left, expiry_date, etc.
            notification_settings: User's notification preferences
        """
        results = {
            'email': False,
            'telegram': False,
            'webhook': False
        }
        
        try:
            # Email notification
            if notification_settings.get('email_enabled', True):
                results['email'] = await self.send_email_notification(
                    notification_type, recipient_data, domain_info
                )
            
            # Telegram notification
            if (notification_settings.get('telegram_enabled', False) and 
                recipient_data.get('telegram_chat_id')):
                results['telegram'] = await self.send_telegram_notification(
                    notification_type, recipient_data, domain_info
                )
            
            # Webhook notification
            if (notification_settings.get('webhook_enabled', False) and 
                notification_settings.get('webhook_url')):
                results['webhook'] = await self.send_webhook_notification(
                    notification_type, recipient_data, domain_info,
                    notification_settings['webhook_url']
                )
                
        except Exception as e:
            logger.error(f"Notification sending failed: {str(e)}")
            
        return results

    async def send_email_notification(self, 
                                    notification_type: str,
                                    recipient_data: Dict[str, Any],
                                    domain_info: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            # Get email template
            template = self.get_email_template(notification_type)
            subject = self.get_email_subject(notification_type, domain_info)
            body = template.render(
                domain_name=domain_info.get('name'),
                days_left=domain_info.get('days_left', 0),
                expiry_date=domain_info.get('expiry_date'),
                user_name=recipient_data.get('name', 'User'),
                dashboard_url='https://cloudsre.xyz/dashboard'
            )
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.mail_from
            msg['To'] = recipient_data['email']
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.mail_from, recipient_data['email'], text)
            server.quit()
            
            logger.info(f"Email sent to {recipient_data['email']} for {domain_info.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False

    async def send_telegram_notification(self,
                                       notification_type: str,
                                       recipient_data: Dict[str, Any],
                                       domain_info: Dict[str, Any]) -> bool:
        """Send Telegram notification"""
        try:
            message = self.format_telegram_message(notification_type, domain_info)
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': recipient_data.get('telegram_chat_id', self.telegram_chat_id),
                'text': message,
                'parse_mode': 'HTML',
                'reply_markup': self.get_telegram_keyboard(notification_type, domain_info)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(f"Telegram message sent for {domain_info.get('name')}")
                        return True
                    else:
                        logger.error(f"Telegram API error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Telegram sending failed: {str(e)}")
            return False

    async def send_webhook_notification(self,
                                      notification_type: str,
                                      recipient_data: Dict[str, Any],
                                      domain_info: Dict[str, Any],
                                      webhook_url: str) -> bool:
        """Send webhook notification"""
        try:
            payload = {
                'type': notification_type,
                'timestamp': datetime.utcnow().isoformat(),
                'domain': {
                    'name': domain_info.get('name'),
                    'days_left': domain_info.get('days_left', 0),
                    'expiry_date': domain_info.get('expiry_date'),
                    'status': domain_info.get('status', 'unknown')
                },
                'user': {
                    'email': recipient_data.get('email'),
                    'name': recipient_data.get('name', 'User')
                },
                'dashboard_url': 'https://cloudsre.xyz/dashboard'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status in [200, 201, 204]:
                        logger.info(f"Webhook sent to {webhook_url} for {domain_info.get('name')}")
                        return True
                    else:
                        logger.error(f"Webhook error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Webhook sending failed: {str(e)}")
            return False

    def get_email_template(self, notification_type: str) -> Template:
        """Get email template for notification type"""
        templates = {
            'expiring_soon': Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                    .alert { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .button { display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
                    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔔 SSL Certificate Alert</h1>
                        <p>Hello {{ user_name }},</p>
                    </div>
                    
                    <div class="alert">
                        <h2>⚠️ Certificate Expiring Soon</h2>
                        <p><strong>Domain:</strong> {{ domain_name }}</p>
                        <p><strong>Days until expiry:</strong> {{ days_left }} days</p>
                        <p><strong>Expiry date:</strong> {{ expiry_date }}</p>
                    </div>
                    
                    <p>Your SSL certificate for <strong>{{ domain_name }}</strong> will expire in {{ days_left }} days.</p>
                    
                    <p><strong>Recommended actions:</strong></p>
                    <ul>
                        <li>Renew your SSL certificate immediately</li>
                        <li>Update your domain's SSL certificate</li>
                        <li>Test your website after renewal</li>
                    </ul>
                    
                    <a href="{{ dashboard_url }}" class="button">View Dashboard</a>
                    
                    <div class="footer">
                        <p>This is an automated message from SSL Monitor Pro.</p>
                        <p>If you no longer wish to receive these notifications, you can update your preferences in the dashboard.</p>
                    </div>
                </div>
            </body>
            </html>
            """)
        }
        
        return templates.get(notification_type, templates['expiring_soon'])

    def get_email_subject(self, notification_type: str, domain_info: Dict[str, Any]) -> str:
        """Get email subject for notification type"""
        domain_name = domain_info.get('name', 'Unknown')
        days_left = domain_info.get('days_left', 0)
        
        subjects = {
            'expiring_soon': f"⚠️ SSL Certificate Expiring: {domain_name} ({days_left} days left)",
            'expired': f"🚨 URGENT: SSL Certificate Expired - {domain_name}",
            'check_failed': f"❌ SSL Check Failed: {domain_name}",
            'weekly_report': "📊 Your Weekly SSL Monitoring Report"
        }
        
        return subjects.get(notification_type, f"SSL Alert: {domain_name}")

    def format_telegram_message(self, notification_type: str, domain_info: Dict[str, Any]) -> str:
        """Format message for Telegram"""
        domain_name = domain_info.get('name', 'Unknown')
        days_left = domain_info.get('days_left', 0)
        
        messages = {
            'expiring_soon': f"""
🔔 <b>SSL Certificate Alert</b>

⚠️ <b>Certificate Expiring Soon</b>
🌐 Domain: <code>{domain_name}</code>
⏰ Days left: <b>{days_left}</b>
📅 Expiry: {domain_info.get('expiry_date', 'Unknown')}

<i>Please renew your SSL certificate to avoid service disruption.</i>
            """
        }
        
        return messages.get(notification_type, f"SSL Alert: {domain_name}")

    def get_telegram_keyboard(self, notification_type: str, domain_info: Dict[str, Any]) -> Dict:
        """Get inline keyboard for Telegram"""
        keyboard = {
            'inline_keyboard': [
                [
                    {
                        'text': '🔍 View Dashboard',
                        'url': 'https://cloudsre.xyz/dashboard'
                    }
                ]
            ]
        }
        
        return keyboard

# Global instance
notification_service = NotificationService()