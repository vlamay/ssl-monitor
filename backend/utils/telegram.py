"""
Telegram notification service for SSL Monitor Pro
Sends alerts to admin via @CloudereMonitorBot
"""
import os
import requests
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_telegram_alert(
    message: str,
    parse_mode: str = 'HTML',
    disable_notification: bool = False,
    retry_count: int = 3
) -> bool:
    """
    Send alert message to Telegram
    
    Args:
        message: Message text (supports HTML formatting)
        parse_mode: Message format ('HTML' or 'Markdown')
        disable_notification: Silent notification
        retry_count: Number of retry attempts
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured. Skipping notification.")
        return False
    
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_notification": disable_notification
    }
    
    for attempt in range(retry_count):
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent successfully (attempt {attempt + 1})")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram alert failed (attempt {attempt + 1}/{retry_count}): {str(e)}")
            
            if attempt == retry_count - 1:
                logger.error(f"Failed to send Telegram alert after {retry_count} attempts")
                return False
    
    return False


def send_ssl_expiring_alert(domain: str, days_left: int) -> bool:
    """
    Send alert for SSL certificate expiring soon
    
    Args:
        domain: Domain name
        days_left: Days until expiration
        
    Returns:
        bool: Success status
    """
    if days_left <= 0:
        emoji = "🚨"
        urgency = "EXPIRED"
    elif days_left <= 7:
        emoji = "⚠️"
        urgency = "CRITICAL"
    elif days_left <= 14:
        emoji = "⏰"
        urgency = "WARNING"
    else:
        emoji = "ℹ️"
        urgency = "NOTICE"
    
    message = f"""
{emoji} <b>SSL Certificate {urgency}</b>

<b>Domain:</b> {domain}
<b>Days Left:</b> {days_left}
<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

<a href="https://cloudsre.xyz/dashboard">View Dashboard</a>
"""
    
    return send_telegram_alert(message.strip())


def send_payment_success_alert(email: str, plan: str, amount: float, currency: str = "EUR") -> bool:
    """
    Send alert for successful payment
    
    Args:
        email: Customer email
        plan: Subscription plan name
        amount: Payment amount
        currency: Currency code
        
    Returns:
        bool: Success status
    """
    message = f"""
💳 <b>Payment Successful</b>

<b>Customer:</b> {email}
<b>Plan:</b> {plan}
<b>Amount:</b> {amount} {currency}
<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

✅ Subscription activated
"""
    
    return send_telegram_alert(message.strip())


def send_payment_failed_alert(email: str, plan: str, reason: str = "Unknown") -> bool:
    """
    Send alert for failed payment
    
    Args:
        email: Customer email
        plan: Subscription plan name
        reason: Failure reason
        
    Returns:
        bool: Success status
    """
    message = f"""
❌ <b>Payment Failed</b>

<b>Customer:</b> {email}
<b>Plan:</b> {plan}
<b>Reason:</b> {reason}
<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

⚠️ Action required
"""
    
    return send_telegram_alert(message.strip())


def send_new_user_alert(email: str, trial_ends_at: str) -> bool:
    """
    Send alert for new user registration
    
    Args:
        email: User email
        trial_ends_at: Trial end date
        
    Returns:
        bool: Success status
    """
    message = f"""
🆕 <b>New User Registered</b>

<b>Email:</b> {email}
<b>Trial Ends:</b> {trial_ends_at}
<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

🎉 Welcome to SSL Monitor Pro!
"""
    
    return send_telegram_alert(message.strip())


def send_trial_ending_alert(email: str, days_left: int) -> bool:
    """
    Send alert for trial ending soon
    
    Args:
        email: User email
        days_left: Days until trial ends
        
    Returns:
        bool: Success status
    """
    message = f"""
⏰ <b>Trial Ending Soon</b>

<b>User:</b> {email}
<b>Days Left:</b> {days_left}
<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

💡 Encourage upgrade to paid plan
"""
    
    return send_telegram_alert(message.strip())


def send_system_error_alert(error: str, context: str = "") -> bool:
    """
    Send alert for system errors
    
    Args:
        error: Error message
        context: Additional context
        
    Returns:
        bool: Success status
    """
    message = f"""
🔥 <b>System Error</b>

<b>Error:</b> {error}
<b>Context:</b> {context}
<b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

⚠️ Immediate attention required
"""
    
    return send_telegram_alert(message.strip())


def test_telegram_connection() -> dict:
    """
    Test Telegram bot connection
    
    Returns:
        dict: Status and bot info
    """
    if not TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not configured"}
    
    try:
        # Get bot info
        response = requests.get(f"{TELEGRAM_API_URL}/getMe", timeout=10)
        response.raise_for_status()
        bot_info = response.json()
        
        # Try sending test message
        if TELEGRAM_CHAT_ID:
            test_msg = "✅ SSL Monitor Pro - Telegram connection test successful!"
            send_telegram_alert(test_msg)
        
        return {
            "ok": True,
            "bot": bot_info.get('result', {}),
            "chat_id_configured": bool(TELEGRAM_CHAT_ID)
        }
        
    except Exception as e:
        logger.error(f"Telegram connection test failed: {str(e)}")
        return {"ok": False, "error": str(e)}

