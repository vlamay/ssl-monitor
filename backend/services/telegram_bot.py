import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram bot for sending SSL monitoring alerts"""
    
    def __init__(self, token: str = None, chat_id: str = None):
        """
        Initialize Telegram notifier
        
        Args:
            token: Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID (or set TELEGRAM_CHAT_ID env var)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        self.enabled = bool(self.token and self.chat_id)
        
        if not self.enabled:
            logger.warning("Telegram notifications disabled: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message via Telegram
        
        Args:
            message: Message text to send
            parse_mode: Parse mode (HTML, Markdown, or None)
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Telegram disabled, would have sent: {message}")
            return False
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    def send_alert(self, domain: str, expires_in: int, status: str = "warning"):
        """
        Send SSL certificate alert
        
        Args:
            domain: Domain name
            expires_in: Days until expiration
            status: Alert status (warning, critical, error)
        """
        emoji_map = {
            "warning": "⚠️",
            "critical": "🚨",
            "error": "❌",
            "info": "ℹ️"
        }
        
        emoji = emoji_map.get(status, "⚠️")
        
        if expires_in <= 0:
            message = f"{emoji} <b>SSL Certificate EXPIRED</b>\n\n"
            message += f"🌐 Domain: <code>{domain}</code>\n"
            message += f"📅 Expired: {abs(expires_in)} days ago"
        else:
            message = f"{emoji} <b>SSL Certificate Expiring Soon</b>\n\n"
            message += f"🌐 Domain: <code>{domain}</code>\n"
            message += f"📅 Expires in: <b>{expires_in} days</b>"
        
        return self.send_message(message)
    
    def send_report(self, total_domains: int, expiring: int, expired: int, errors: int):
        """
        Send daily monitoring report
        
        Args:
            total_domains: Total number of monitored domains
            expiring: Number of domains expiring soon
            expired: Number of expired domains
            errors: Number of domains with errors
        """
        message = "📊 <b>SSL Monitor Daily Report</b>\n\n"
        message += f"🌐 Total Domains: {total_domains}\n"
        message += f"⚠️ Expiring Soon: {expiring}\n"
        message += f"🚨 Expired: {expired}\n"
        message += f"❌ Errors: {errors}\n"
        
        return self.send_message(message)

# Global notifier instance
_notifier = TelegramNotifier()

def send_telegram_alert(message: str) -> bool:
    """
    Convenience function to send Telegram alert
    
    Args:
        message: Message to send
    
    Returns:
        True if sent successfully, False otherwise
    """
    return _notifier.send_message(message)

def configure_telegram(token: str, chat_id: str):
    """
    Configure Telegram notifier
    
    Args:
        token: Telegram bot token
        chat_id: Telegram chat ID
    """
    global _notifier
    _notifier = TelegramNotifier(token, chat_id)

# Example usage:
# from services.telegram_bot import send_telegram_alert
# send_telegram_alert("🚨 SSL Certificate for example.com expires in 15 days!")

