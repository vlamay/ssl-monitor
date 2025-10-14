"""
Notification tasks
"""
import json
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from celery import current_task
from app.tasks.celery_app import celery_app
from app.core.database import async_session_maker
from app.core.config import settings
from app.models.notification import Notification, NotificationLog, NotificationType, NotificationTrigger
from app.models.monitor import Monitor
from app.models.user import User
from sqlalchemy import select
import logging

# Import notification services
from app.services.whatsapp import whatsapp_service
from app.services.telegram import telegram_service
from app.services.sms import sms_service
from app.services.slack import slack_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_notification(self, notification_id: int, trigger: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a notification
    
    Args:
        notification_id: ID of the notification configuration
        trigger: Notification trigger type
        data: Data for the notification
        
    Returns:
        Dict with send result
    """
    try:
        logger.info(f"Sending notification {notification_id} with trigger {trigger}")
        
        async with async_session_maker() as session:
            # Get notification configuration
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if not notification:
                logger.error(f"Notification {notification_id} not found")
                return {"error": "Notification not found"}
            
            if not notification.enabled:
                logger.info(f"Notification {notification_id} is disabled")
                return {"skipped": "Notification disabled"}
            
            # Get monitor and user info
            monitor = None
            if notification.monitor_id:
                monitor_result = await session.execute(
                    select(Monitor).where(Monitor.id == notification.monitor_id)
                )
                monitor = monitor_result.scalar_one_or_none()
            
            user_result = await session.execute(
                select(User).where(User.id == notification.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {notification.user_id} not found")
                return {"error": "User not found"}
            
            # Send notification based on type
            if notification.type == NotificationType.EMAIL:
                result = await _send_email_notification(notification, user, monitor, trigger, data)
            elif notification.type == NotificationType.TELEGRAM:
                result = await _send_telegram_notification(notification, user, monitor, trigger, data)
            elif notification.type == NotificationType.WEBHOOK:
                result = await _send_webhook_notification(notification, user, monitor, trigger, data)
            elif notification.type == NotificationType.WHATSAPP:
                result = await _send_whatsapp_notification(notification, user, monitor, trigger, data)
            elif notification.type == NotificationType.SMS:
                result = await _send_sms_notification(notification, user, monitor, trigger, data)
            elif notification.type == NotificationType.SLACK:
                result = await _send_slack_notification(notification, user, monitor, trigger, data)
            else:
                logger.error(f"Unknown notification type: {notification.type}")
                return {"error": "Unknown notification type"}
            
            # Log notification
            notification_log = NotificationLog(
                notification_id=notification_id,
                monitor_id=notification.monitor_id,
                type=notification.type,
                trigger=NotificationTrigger(trigger),
                subject=result.get("subject"),
                message=result.get("message"),
                delivery_status=result.get("status", "sent"),
                error_message=result.get("error"),
                metadata=json.dumps(data)
            )
            
            session.add(notification_log)
            await session.commit()
            
            logger.info(f"Notification {notification_id} sent successfully")
            return result
            
    except Exception as exc:
        logger.error(f"Failed to send notification {notification_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying notification {notification_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {"error": str(exc)}


@celery_app.task
def trigger_notifications(monitor_id: int, trigger: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger notifications for a monitor event
    
    Args:
        monitor_id: ID of the monitor
        trigger: Event trigger
        data: Event data
        
    Returns:
        Dict with trigger results
    """
    try:
        logger.info(f"Triggering notifications for monitor {monitor_id} with trigger {trigger}")
        
        async with async_session_maker() as session:
            # Get all enabled notifications for this monitor and user
            result = await session.execute(
                select(Notification).where(
                    (Notification.monitor_id == monitor_id) | (Notification.monitor_id.is_(None)),
                    Notification.enabled == True
                )
            )
            notifications = result.scalars().all()
            
            # Filter notifications by trigger
            triggered_notifications = []
            for notification in notifications:
                try:
                    triggers = json.loads(notification.triggers) if notification.triggers else []
                    if trigger in triggers:
                        triggered_notifications.append(notification)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid triggers JSON for notification {notification.id}")
                    continue
            
            # Send notifications
            results = []
            for notification in triggered_notifications:
                try:
                    task_result = send_notification.delay(notification.id, trigger, data)
                    results.append({
                        "notification_id": notification.id,
                        "type": notification.type,
                        "task_id": task_result.id,
                        "status": "queued"
                    })
                except Exception as e:
                    results.append({
                        "notification_id": notification.id,
                        "type": notification.type,
                        "error": str(e),
                        "status": "failed"
                    })
            
            logger.info(f"Triggered {len(results)} notifications for monitor {monitor_id}")
            return {
                "monitor_id": monitor_id,
                "trigger": trigger,
                "total_notifications": len(results),
                "queued": len([r for r in results if r.get("status") == "queued"]),
                "failed": len([r for r in results if r.get("status") == "failed"]),
                "results": results
            }
            
    except Exception as exc:
        logger.error(f"Failed to trigger notifications for monitor {monitor_id}: {exc}")
        return {"error": str(exc)}


async def _send_email_notification(
    notification: Notification,
    user: User,
    monitor: Optional[Monitor],
    trigger: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send email notification"""
    try:
        # TODO: Implement email sending with fastapi-mail
        # For now, just log the notification
        subject = f"SSL Monitor Alert - {trigger}"
        message = f"SSL certificate alert for {monitor.domain if monitor else 'your domains'}"
        
        logger.info(f"Email notification would be sent to {notification.email_address}")
        
        return {
            "status": "sent",
            "subject": subject,
            "message": message
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


async def _send_telegram_notification(
    notification: Notification,
    user: User,
    monitor: Optional[Monitor],
    trigger: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send Telegram notification"""
    try:
        if not settings.TELEGRAM_BOT_TOKEN:
            return {"status": "failed", "error": "Telegram bot token not configured"}
        
        chat_id = notification.telegram_chat_id or settings.TELEGRAM_CHAT_ID
        if not chat_id:
            return {"status": "failed", "error": "Telegram chat ID not configured"}
        
        # Format message
        emoji_map = {
            "expires_in_30d": "⚠️",
            "expires_in_7d": "🟡",
            "expires_in_3d": "🟠",
            "expires_in_1d": "🔴",
            "expired": "🚨",
            "ssl_check_success": "✅",
            "ssl_check_error": "❌",
            "monitor_down": "🔴",
            "monitor_up": "🟢",
            "weekly_report": "📊"
        }
        
        emoji = emoji_map.get(trigger, "🔔")
        message = f"{emoji} *SSL Monitor Alert*\n\n"
        
        if monitor:
            message += f"Domain: `{monitor.domain}`\n"
            message += f"Status: {monitor.ssl_status.value}\n"
            if monitor.days_until_expiry is not None:
                message += f"Expires in: {monitor.days_until_expiry} days\n"
        
        message += f"Trigger: {trigger}\n"
        message += f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        # Send message
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "sent",
                    "message": message
                }
            else:
                return {
                    "status": "failed",
                    "error": f"Telegram API error: {response.text}"
                }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


async def _send_webhook_notification(
    notification: Notification,
    user: User,
    monitor: Optional[Monitor],
    trigger: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send webhook notification"""
    try:
        if not notification.webhook_url:
            return {"status": "failed", "error": "Webhook URL not configured"}
        
        # Prepare payload
        payload = {
            "trigger": trigger,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user.id,
            "user_email": user.email,
            "data": data
        }
        
        if monitor:
            payload["monitor"] = {
                "id": monitor.id,
                "domain": monitor.domain,
                "status": monitor.ssl_status.value,
                "days_until_expiry": monitor.days_until_expiry
            }
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if notification.webhook_headers:
            try:
                custom_headers = json.loads(notification.webhook_headers)
                headers.update(custom_headers)
            except json.JSONDecodeError:
                logger.warning(f"Invalid webhook headers JSON for notification {notification.id}")
        
        # Send webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                notification.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                return {
                    "status": "sent",
                    "message": f"Webhook sent to {notification.webhook_url}",
                    "response_status": response.status_code
                }
            else:
                return {
                    "status": "failed",
                    "error": f"Webhook failed with status {response.status_code}: {response.text}"
                }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


async def _send_whatsapp_notification(
    notification: Notification,
    user: User,
    monitor: Optional[Monitor],
    trigger: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send WhatsApp notification"""
    try:
        from app.services.whatsapp import whatsapp_service
        
        phone_number = notification.whatsapp_phone
        if not phone_number:
            return {"status": "failed", "error": "WhatsApp phone number not configured"}
        
        # Format message based on trigger
        if trigger.startswith("expires_"):
            days_until_expiry = data.get("days_until_expiry", 0)
            message = whatsapp_service.get_ssl_alert_message(
                monitor.domain if monitor else "your domain",
                days_until_expiry
            )
        elif trigger == "welcome":
            message = whatsapp_service.get_welcome_message(user.full_name)
        elif trigger == "support":
            message = whatsapp_service.get_support_message(data.get("issue_type"))
        elif trigger == "demo_request":
            message = whatsapp_service.get_demo_request_message(data.get("company"))
        else:
            # Generic message
            message = f"🔔 *SSL Monitor Pro Alert*\n\nTrigger: {trigger}\nTime: {data.get('timestamp', 'now')}"
            if monitor:
                message += f"\nDomain: {monitor.domain}"
        
        # Send notification (currently returns URL for manual sending)
        result = await whatsapp_service.send_notification(phone_number, message, trigger)
        
        return {
            "status": "sent",
            "message": message,
            "whatsapp_url": result.get("whatsapp_url"),
            "phone_number": phone_number
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def send_bulk_notifications(notification_ids: List[int], trigger: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send multiple notifications
    
    Args:
        notification_ids: List of notification IDs
        trigger: Notification trigger
        data: Notification data
        
    Returns:
        Dict with bulk send results
    """
    results = []
    
    for notification_id in notification_ids:
        try:
            task_result = send_notification.delay(notification_id, trigger, data)
            results.append({
                "notification_id": notification_id,
                "task_id": task_result.id,
                "status": "queued"
            })
        except Exception as e:
            results.append({
                "notification_id": notification_id,
                "error": str(e),
                "status": "failed"
            })
    
    return {
        "trigger": trigger,
        "total_notifications": len(notification_ids),
        "queued": len([r for r in results if r.get("status") == "queued"]),
        "failed": len([r for r in results if r.get("status") == "failed"]),
        "results": results
    }


async def _send_sms_notification(
    notification: Notification,
    user: User,
    monitor: Optional[Monitor],
    trigger: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send SMS notification"""
    try:
        phone_number = notification.phone_number  # Assuming we add this field
        if not phone_number:
            return {"status": "failed", "error": "SMS phone number not configured"}
        
        # Format message based on trigger
        if trigger.startswith("expires_"):
            days_until_expiry = data.get("days_until_expiry", 0)
            domain = monitor.domain if monitor else "your domain"
            message = f"SSL Alert: {domain} expires in {days_until_expiry} days. Renew now!"
        elif trigger == "expired":
            domain = monitor.domain if monitor else "your domain"
            message = f"URGENT: SSL certificate for {domain} has EXPIRED! Immediate action required."
        elif trigger == "welcome":
            message = f"Welcome to SSL Monitor Pro, {user.full_name}! Your SSL monitoring is now active."
        elif trigger == "support":
            message = f"SSL Monitor Pro Support: We received your {data.get('issue_type', 'support')} request. We'll contact you soon."
        elif trigger == "demo_request":
            message = f"Demo request for {data.get('company', 'your company')} confirmed. We'll schedule a call soon."
        else:
            # Generic message
            message = f"SSL Monitor Pro Alert: {trigger} - {data.get('timestamp', 'now')}"
            if monitor:
                message += f" for {monitor.domain}"
        
        # Send SMS
        result = await sms_service.send_sms(phone_number, message)
        
        return {
            "status": "sent" if result.get("success") else "failed",
            "message": message,
            "phone_number": phone_number,
            "provider": result.get("provider"),
            "message_id": result.get("message_id"),
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


async def _send_slack_notification(
    notification: Notification,
    user: User,
    monitor: Optional[Monitor],
    trigger: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send Slack notification"""
    try:
        channel = notification.channel
        if not channel:
            return {"status": "failed", "error": "Slack channel not configured"}
        
        # Format message based on trigger
        if trigger.startswith("expires_"):
            days_until_expiry = data.get("days_until_expiry", 0)
            domain = monitor.domain if monitor else "your domain"
            alert_type = "expires_soon"
        elif trigger == "expired":
            domain = monitor.domain if monitor else "your domain"
            alert_type = "expired"
        elif trigger == "welcome":
            domain = "your SSL monitoring"
            alert_type = "welcome"
        elif trigger == "support":
            domain = "support request"
            alert_type = "support"
        elif trigger == "demo_request":
            domain = "demo request"
            alert_type = "demo_request"
        else:
            domain = monitor.domain if monitor else "your domain"
            alert_type = "generic"
        
        # Send Slack message
        result = await slack_service.send_ssl_alert(
            channel=channel,
            domain=domain,
            alert_type=alert_type,
            days_remaining=data.get("days_until_expiry")
        )
        
        return {
            "status": "sent" if result.get("success") else "failed",
            "channel": channel,
            "domain": domain,
            "alert_type": alert_type,
            "timestamp": result.get("timestamp"),
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
