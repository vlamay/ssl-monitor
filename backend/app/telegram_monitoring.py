"""
Telegram Monitoring Bot for SSL Monitor Pro
Handles alerts, notifications, and monitoring communications
"""

import requests
import json
import logging
from datetime import datetime, timezone
import os
from typing import Dict, List, Optional
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class TelegramMonitoringBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _format_timestamp(self, dt=None):
        """Format timestamp for Telegram messages"""
        if dt is None:
            dt = datetime.now(timezone.utc)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    def _escape_markdown(self, text):
        """Escape special characters for Telegram markdown"""
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    def send_message(self, message: str, parse_mode: str = 'HTML', disable_notification: bool = False) -> bool:
        """Send message to Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot token or chat ID not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            logger.info("Telegram message sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_message_async(self, message: str, parse_mode: str = 'HTML', disable_notification: bool = False) -> bool:
        """Send message to Telegram asynchronously"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot token or chat ID not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(url, data=data, timeout=10) as response:
                response.raise_for_status()
                logger.info("Telegram message sent successfully (async)")
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message (async): {e}")
            return False
    
    def send_service_down_alert(self, service_name: str, error_message: str, severity: str = "HIGH") -> bool:
        """Send service down alert"""
        emoji = "🚨" if severity == "CRITICAL" else "⚠️"
        
        message = f"""
{emoji} <b>SERVICE DOWN ALERT</b>

<b>Service:</b> {self._escape_markdown(service_name)}
<b>Severity:</b> {severity}
<b>Time:</b> {self._format_timestamp()}
<b>Error:</b> {self._escape_markdown(error_message)}

<b>Action Required:</b> Please check the service immediately!
        """
        
        return self.send_message(message, disable_notification=(severity != "CRITICAL"))
    
    def send_service_recovery_alert(self, service_name: str, downtime_minutes: Optional[int] = None) -> bool:
        """Send service recovery alert"""
        downtime_text = f" (Downtime: {downtime_minutes} minutes)" if downtime_minutes else ""
        
        message = f"""
✅ <b>SERVICE RECOVERED</b>

<b>Service:</b> {self._escape_markdown(service_name)}
<b>Time:</b> {self._format_timestamp()}
<b>Status:</b> Back online{downtime_text}

Service is operational again.
        """
        
        return self.send_message(message)
    
    def send_deployment_alert(self, environment: str, status: str, commit_hash: Optional[str] = None, 
                            version: Optional[str] = None) -> bool:
        """Send deployment notification"""
        if status == 'success':
            emoji = "🚀"
            status_text = "✅ SUCCESS"
        else:
            emoji = "❌"
            status_text = "❌ FAILED"
        
        message = f"""
{emoji} <b>DEPLOYMENT {status.upper()}</b>

<b>Environment:</b> {environment}
<b>Status:</b> {status_text}
<b>Time:</b> {self._format_timestamp()}
        """
        
        if commit_hash:
            message += f"<b>Commit:</b> <code>{commit_hash[:8]}</code>\n"
        
        if version:
            message += f"<b>Version:</b> {version}\n"
        
        if status == 'success':
            message += "\nDeployment completed successfully!"
        else:
            message += "\nDeployment failed. Please check logs."
        
        return self.send_message(message, disable_notification=(status == 'success'))
    
    def send_ssl_certificate_alert(self, domain: str, days_remaining: int, status: str = "expiring") -> bool:
        """Send SSL certificate alert"""
        if status == "expiring":
            emoji = "⚠️"
            title = "SSL CERTIFICATE EXPIRING"
        elif status == "expired":
            emoji = "🚨"
            title = "SSL CERTIFICATE EXPIRED"
        else:
            emoji = "ℹ️"
            title = "SSL CERTIFICATE UPDATE"
        
        message = f"""
{emoji} <b>{title}</b>

<b>Domain:</b> {domain}
<b>Days Remaining:</b> {days_remaining}
<b>Time:</b> {self._format_timestamp()}

<b>Action Required:</b> Please renew the SSL certificate.
        """
        
        return self.send_message(message, disable_notification=(status != "expired"))
    
    def send_user_signup_alert(self, email: str, plan: str, source: str = "website") -> bool:
        """Send new user signup alert"""
        message = f"""
🎉 <b>NEW USER SIGNUP</b>

<b>Email:</b> {email}
<b>Plan:</b> {plan}
<b>Source:</b> {source}
<b>Time:</b> {self._format_timestamp()}

New user has signed up for SSL Monitor Pro!
        """
        
        return self.send_message(message)
    
    def send_payment_alert(self, email: str, amount: float, currency: str, plan: str, status: str) -> bool:
        """Send payment notification"""
        if status == "success":
            emoji = "💰"
            title = "PAYMENT SUCCESS"
        else:
            emoji = "💳"
            title = "PAYMENT FAILED"
        
        message = f"""
{emoji} <b>{title}</b>

<b>Email:</b> {email}
<b>Amount:</b> {amount} {currency}
<b>Plan:</b> {plan}
<b>Time:</b> {self._format_timestamp()}

Payment processed successfully!
        """
        
        return self.send_message(message)
    
    def send_system_alert(self, alert_type: str, message: str, severity: str = "INFO") -> bool:
        """Send generic system alert"""
        emoji_map = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "🔶",
            "LOW": "ℹ️",
            "INFO": "ℹ️"
        }
        
        emoji = emoji_map.get(severity, "ℹ️")
        
        formatted_message = f"""
{emoji} <b>SYSTEM ALERT - {alert_type}</b>

<b>Severity:</b> {severity}
<b>Time:</b> {self._format_timestamp()}

{message}
        """
        
        return self.send_message(formatted_message, disable_notification=(severity not in ["CRITICAL", "HIGH"]))
    
    def send_daily_summary(self, stats: Dict) -> bool:
        """Send daily summary report"""
        message = f"""
📊 <b>DAILY SUMMARY</b>

<b>Date:</b> {self._format_timestamp().split()[0]}

<b>SSL Checks:</b> {stats.get('ssl_checks', 0)}
<b>Domains Monitored:</b> {stats.get('domains_monitored', 0)}
<b>Alerts Sent:</b> {stats.get('alerts_sent', 0)}
<b>New Signups:</b> {stats.get('new_signups', 0)}
<b>Revenue:</b> {stats.get('revenue', 0)} {stats.get('currency', 'EUR')}

<b>System Status:</b> All systems operational ✅
        """
        
        return self.send_message(message)
    
    def send_uptime_alert(self, service_name: str, status: str, response_time: Optional[int] = None) -> bool:
        """Send uptime monitoring alert"""
        if status == "down":
            return self.send_service_down_alert(service_name, "Service is not responding", "CRITICAL")
        else:
            return self.send_service_recovery_alert(service_name)
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            bot_info = response.json()
            if bot_info.get('ok'):
                logger.info(f"Telegram bot connected: @{bot_info['result']['username']}")
                return True
            else:
                logger.error("Telegram bot connection failed")
                return False
        except Exception as e:
            logger.error(f"Failed to test Telegram connection: {e}")
            return False

# Global monitoring bot instance
monitoring_bot = TelegramMonitoringBot()

# Convenience functions for easy use
def send_alert(message: str, severity: str = "INFO") -> bool:
    """Send alert using global bot instance"""
    return monitoring_bot.send_system_alert("ALERT", message, severity)

def send_service_down(service_name: str, error_message: str) -> bool:
    """Send service down alert"""
    return monitoring_bot.send_service_down_alert(service_name, error_message)

def send_service_recovery(service_name: str) -> bool:
    """Send service recovery alert"""
    return monitoring_bot.send_service_recovery_alert(service_name)

def send_deployment_notification(environment: str, status: str, commit_hash: str = None) -> bool:
    """Send deployment notification"""
    return monitoring_bot.send_deployment_alert(environment, status, commit_hash)

def send_ssl_alert(domain: str, days_remaining: int, status: str = "expiring") -> bool:
    """Send SSL certificate alert"""
    return monitoring_bot.send_ssl_certificate_alert(domain, days_remaining, status)

def test_telegram_bot() -> bool:
    """Test Telegram bot connection"""
    return monitoring_bot.test_connection()
