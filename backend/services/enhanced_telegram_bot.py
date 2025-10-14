"""
Enhanced Telegram Bot for SSL Monitor Pro
Features:
- Interactive commands and keyboards
- User preference management
- Personalized notifications
- Multi-language support
- Subscription management
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

@dataclass
class TelegramUser:
    """Telegram user data model"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = 'en'
    notification_enabled: bool = True
    alert_threshold_days: int = 30
    quiet_hours_start: str = '22:00'
    quiet_hours_end: str = '08:00'
    timezone: str = 'UTC'
    subscription_status: str = 'trial'  # trial, active, expired, cancelled
    created_at: datetime = None
    updated_at: datetime = None

class EnhancedTelegramBot:
    """Enhanced Telegram bot with interactive features"""
    
    def __init__(self, token: str = None, db_session: Session = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        self.db = db_session
        self.enabled = bool(self.token)
        
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
        
        if not self.enabled:
            logger.warning("Enhanced Telegram bot disabled: TELEGRAM_BOT_TOKEN not set")
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load notification templates for different languages"""
        return {
            'en': {
                'welcome': "🎉 Welcome to SSL Monitor Pro!\n\nI'll help you monitor your SSL certificates and send alerts when they're about to expire.\n\nUse /help to see all available commands.",
                'ssl_warning': "⚠️ <b>SSL Certificate Warning</b>\n\n🌐 Domain: <code>{domain}</code>\n📅 Expires in: <b>{days} days</b>\n🕐 Time: {timestamp}\n\n<a href='https://cloudsre.xyz/dashboard'>View Dashboard</a>",
                'ssl_critical': "🚨 <b>SSL Certificate Critical</b>\n\n🌐 Domain: <code>{domain}</code>\n📅 Expires in: <b>{days} days</b>\n🕐 Time: {timestamp}\n\n⚠️ Action required immediately!",
                'ssl_expired': "💥 <b>SSL Certificate Expired</b>\n\n🌐 Domain: <code>{domain}</code>\n📅 Expired: <b>{days} days ago</b>\n🕐 Time: {timestamp}\n\n🚨 URGENT: Certificate needs renewal!",
                'payment_success': "💳 <b>Payment Successful</b>\n\n👤 Customer: {email}\n📦 Plan: {plan}\n💰 Amount: {amount} {currency}\n🕐 Time: {timestamp}\n\n✅ Subscription activated!",
                'trial_ending': "⏰ <b>Trial Ending Soon</b>\n\n👤 User: {email}\n📅 Days left: <b>{days}</b>\n🕐 Time: {timestamp}\n\n💡 Upgrade to continue monitoring!",
                'settings_menu': "⚙️ <b>Settings</b>\n\nSelect an option:",
                'language_changed': "🌐 Language changed to {language}",
                'notifications_enabled': "🔔 Notifications enabled",
                'notifications_disabled': "🔕 Notifications disabled"
            },
            'de': {
                'welcome': "🎉 Willkommen bei SSL Monitor Pro!\n\nIch helfe Ihnen dabei, Ihre SSL-Zertifikate zu überwachen und sende Warnungen, wenn sie bald ablaufen.\n\nVerwenden Sie /help, um alle verfügbaren Befehle zu sehen.",
                'ssl_warning': "⚠️ <b>SSL-Zertifikat Warnung</b>\n\n🌐 Domain: <code>{domain}</code>\n📅 Läuft ab in: <b>{days} Tagen</b>\n🕐 Zeit: {timestamp}",
                'ssl_critical': "🚨 <b>SSL-Zertifikat kritisch</b>\n\n🌐 Domain: <code>{domain}</code>\n📅 Läuft ab in: <b>{days} Tagen</b>\n🕐 Zeit: {timestamp}\n\n⚠️ Sofortige Maßnahme erforderlich!",
                'ssl_expired': "💥 <b>SSL-Zertifikat abgelaufen</b>\n\n🌐 Domain: <code>{domain}</code>\n📅 Abgelaufen: <b>vor {days} Tagen</b>\n🕐 Zeit: {timestamp}\n\n🚨 DRINGEND: Zertifikat muss erneuert werden!",
                'payment_success': "💳 <b>Zahlung erfolgreich</b>\n\n👤 Kunde: {email}\n📦 Plan: {plan}\n💰 Betrag: {amount} {currency}\n🕐 Zeit: {timestamp}\n\n✅ Abonnement aktiviert!",
                'trial_ending': "⏰ <b>Testversion läuft bald ab</b>\n\n👤 Benutzer: {email}\n📅 Tage übrig: <b>{days}</b>\n🕐 Zeit: {timestamp}\n\n💡 Upgrade für fortgesetzte Überwachung!",
                'settings_menu': "⚙️ <b>Einstellungen</b>\n\nWählen Sie eine Option:",
                'language_changed': "🌐 Sprache geändert zu {language}",
                'notifications_enabled': "🔔 Benachrichtigungen aktiviert",
                'notifications_disabled': "🔕 Benachrichtigungen deaktiviert"
            },
            'ru': {
                'welcome': "🎉 Добро пожаловать в SSL Monitor Pro!\n\nЯ помогу вам отслеживать ваши SSL-сертификаты и отправлять уведомления, когда они скоро истекают.\n\nИспользуйте /help, чтобы увидеть все доступные команды.",
                'ssl_warning': "⚠️ <b>Предупреждение SSL-сертификата</b>\n\n🌐 Домен: <code>{domain}</code>\n📅 Истекает через: <b>{days} дней</b>\n🕐 Время: {timestamp}",
                'ssl_critical': "🚨 <b>SSL-сертификат критический</b>\n\n🌐 Домен: <code>{domain}</code>\n📅 Истекает через: <b>{days} дней</b>\n🕐 Время: {timestamp}\n\n⚠️ Требуются немедленные действия!",
                'ssl_expired': "💥 <b>SSL-сертификат истек</b>\n\n🌐 Домен: <code>{domain}</code>\n📅 Истек: <b>{days} дней назад</b>\n🕐 Время: {timestamp}\n\n🚨 СРОЧНО: Сертификат нужно обновить!",
                'payment_success': "💳 <b>Платеж успешен</b>\n\n👤 Клиент: {email}\n📦 План: {plan}\n💰 Сумма: {amount} {currency}\n🕐 Время: {timestamp}\n\n✅ Подписка активирована!",
                'trial_ending': "⏰ <b>Пробный период скоро закончится</b>\n\n👤 Пользователь: {email}\n📅 Осталось дней: <b>{days}</b>\n🕐 Время: {timestamp}\n\n💡 Обновитесь для продолжения мониторинга!",
                'settings_menu': "⚙️ <b>Настройки</b>\n\nВыберите опцию:",
                'language_changed': "🌐 Язык изменен на {language}",
                'notifications_enabled': "🔔 Уведомления включены",
                'notifications_disabled': "🔕 Уведомления отключены"
            }
        }
    
    async def handle_update(self, update: Dict[str, Any]) -> bool:
        """Handle incoming Telegram update"""
        try:
            if 'message' in update:
                await self._handle_message(update['message'])
            elif 'callback_query' in update:
                await self._handle_callback_query(update['callback_query'])
            
            return True
        except Exception as e:
            logger.error(f"Error handling update: {e}")
            return False
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        
        # Register or update user
        await self._register_user(message['from'])
        
        # Handle commands
        if text.startswith('/'):
            command = text.split()[0].lower()
            
            if command == '/start':
                await self._handle_start_command(chat_id, user_id)
            elif command == '/help':
                await self._handle_help_command(chat_id, user_id)
            elif command == '/status':
                await self._handle_status_command(chat_id, user_id)
            elif command == '/settings':
                await self._handle_settings_command(chat_id, user_id)
            elif command == '/domains':
                await self._handle_domains_command(chat_id, user_id)
            elif command == '/language':
                await self._handle_language_command(chat_id, user_id)
            else:
                await self._send_message(chat_id, "Unknown command. Use /help to see available commands.")
        else:
            # Handle regular messages
            await self._send_message(chat_id, "I understand! Use /help to see what I can do.")
    
    async def _handle_callback_query(self, callback_query: Dict[str, Any]):
        """Handle callback query from inline keyboards"""
        chat_id = callback_query['message']['chat']['id']
        user_id = callback_query['from']['id']
        data = callback_query['data']
        
        # Answer callback query
        await self._answer_callback_query(callback_query['id'])
        
        # Handle different callback data
        if data.startswith('lang_'):
            language = data.split('_')[1]
            await self._change_language(chat_id, user_id, language)
        elif data == 'settings_notifications':
            await self._toggle_notifications(chat_id, user_id)
        elif data == 'settings_threshold':
            await self._show_threshold_menu(chat_id, user_id)
        elif data.startswith('threshold_'):
            days = int(data.split('_')[1])
            await self._change_threshold(chat_id, user_id, days)
        elif data == 'settings_back':
            await self._handle_settings_command(chat_id, user_id)
    
    async def _handle_start_command(self, chat_id: int, user_id: int):
        """Handle /start command"""
        user = await self._get_user(user_id)
        language = user.language if user else 'en'
        
        welcome_text = self.templates.get(language, self.templates['en'])['welcome']
        keyboard = self._create_start_keyboard(language)
        
        await self._send_message(chat_id, welcome_text, reply_markup=keyboard)
    
    async def _handle_help_command(self, chat_id: int, user_id: int):
        """Handle /help command"""
        user = await self._get_user(user_id)
        language = user.language if user else 'en'
        
        help_text = self._get_help_text(language)
        await self._send_message(chat_id, help_text)
    
    async def _handle_status_command(self, chat_id: int, user_id: int):
        """Handle /status command"""
        user = await self._get_user(user_id)
        if not user:
            await self._send_message(chat_id, "User not found. Please use /start first.")
            return
        
        status_text = f"""
📊 <b>Your Status</b>

👤 User: {user.first_name or user.username or 'Unknown'}
🌐 Language: {self.languages.get(user.language, user.language)}
🔔 Notifications: {'Enabled' if user.notification_enabled else 'Disabled'}
⚠️ Alert Threshold: {user.alert_threshold_days} days
📅 Subscription: {user.subscription_status.title()}
🕐 Quiet Hours: {user.quiet_hours_start} - {user.quiet_hours_end}
🌍 Timezone: {user.timezone}
"""
        await self._send_message(chat_id, status_text)
    
    async def _handle_settings_command(self, chat_id: int, user_id: int):
        """Handle /settings command"""
        user = await self._get_user(user_id)
        if not user:
            await self._send_message(chat_id, "User not found. Please use /start first.")
            return
        
        language = user.language
        settings_text = self.templates.get(language, self.templates['en'])['settings_menu']
        keyboard = self._create_settings_keyboard(language)
        
        await self._send_message(chat_id, settings_text, reply_markup=keyboard)
    
    async def _handle_domains_command(self, chat_id: int, user_id: int):
        """Handle /domains command"""
        # This would integrate with the domain management system
        domains_text = """
🌐 <b>Your Monitored Domains</b>

1. example.com - ✅ Healthy (89 days)
2. test.com - ⚠️ Warning (15 days)
3. demo.com - 🚨 Critical (3 days)

Use the dashboard to manage domains:
<a href="https://cloudsre.xyz/dashboard">Open Dashboard</a>
"""
        await self._send_message(chat_id, domains_text)
    
    async def _handle_language_command(self, chat_id: int, user_id: int):
        """Handle /language command"""
        keyboard = self._create_language_keyboard()
        await self._send_message(chat_id, "🌐 Select your language:", reply_markup=keyboard)
    
    async def _change_language(self, chat_id: int, user_id: int, language: str):
        """Change user language"""
        if language not in self.languages:
            await self._send_message(chat_id, "Invalid language selection.")
            return
        
        # Update user language in database
        await self._update_user_language(user_id, language)
        
        language_name = self.languages[language]
        message = self.templates.get(language, self.templates['en'])['language_changed'].format(language=language_name)
        await self._send_message(chat_id, message)
    
    async def _toggle_notifications(self, chat_id: int, user_id: int):
        """Toggle user notifications"""
        user = await self._get_user(user_id)
        if not user:
            return
        
        new_status = not user.notification_enabled
        await self._update_user_notifications(user_id, new_status)
        
        language = user.language
        if new_status:
            message = self.templates.get(language, self.templates['en'])['notifications_enabled']
        else:
            message = self.templates.get(language, self.templates['en'])['notifications_disabled']
        
        await self._send_message(chat_id, message)
    
    async def _show_threshold_menu(self, chat_id: int, user_id: int):
        """Show alert threshold selection menu"""
        keyboard = self._create_threshold_keyboard()
        await self._send_message(chat_id, "⚠️ Select alert threshold (days before expiry):", reply_markup=keyboard)
    
    async def _change_threshold(self, chat_id: int, user_id: int, days: int):
        """Change alert threshold"""
        await self._update_user_threshold(user_id, days)
        await self._send_message(chat_id, f"✅ Alert threshold set to {days} days")
    
    def _create_start_keyboard(self, language: str) -> Dict[str, Any]:
        """Create start command keyboard"""
        return {
            "inline_keyboard": [
                [
                    {"text": "⚙️ Settings", "callback_data": "settings"},
                    {"text": "📊 Status", "callback_data": "status"}
                ],
                [
                    {"text": "🌐 Domains", "callback_data": "domains"},
                    {"text": "❓ Help", "callback_data": "help"}
                ]
            ]
        }
    
    def _create_settings_keyboard(self, language: str) -> Dict[str, Any]:
        """Create settings keyboard"""
        return {
            "inline_keyboard": [
                [
                    {"text": "🌐 Language", "callback_data": "language"},
                    {"text": "🔔 Notifications", "callback_data": "settings_notifications"}
                ],
                [
                    {"text": "⚠️ Alert Threshold", "callback_data": "settings_threshold"},
                    {"text": "🕐 Quiet Hours", "callback_data": "quiet_hours"}
                ],
                [
                    {"text": "📊 Subscription", "callback_data": "subscription"},
                    {"text": "🔙 Back", "callback_data": "settings_back"}
                ]
            ]
        }
    
    def _create_language_keyboard(self) -> Dict[str, Any]:
        """Create language selection keyboard"""
        buttons = []
        for code, name in self.languages.items():
            buttons.append([{"text": f"🌐 {name}", "callback_data": f"lang_{code}"}])
        
        return {"inline_keyboard": buttons}
    
    def _create_threshold_keyboard(self) -> Dict[str, Any]:
        """Create threshold selection keyboard"""
        return {
            "inline_keyboard": [
                [
                    {"text": "7 days", "callback_data": "threshold_7"},
                    {"text": "14 days", "callback_data": "threshold_14"}
                ],
                [
                    {"text": "30 days", "callback_data": "threshold_30"},
                    {"text": "60 days", "callback_data": "threshold_60"}
                ]
            ]
        }
    
    def _get_help_text(self, language: str) -> str:
        """Get help text for language"""
        if language == 'en':
            return """
🤖 <b>SSL Monitor Pro Bot Commands</b>

/start - Start the bot and see welcome message
/help - Show this help message
/status - Show your current status and settings
/settings - Open settings menu
/domains - Show your monitored domains
/language - Change language

<b>Features:</b>
🔔 SSL certificate expiration alerts
⚙️ Customizable notification preferences
🌐 Multi-language support
📊 Real-time monitoring status
💳 Subscription management

<b>Dashboard:</b>
<a href="https://cloudsre.xyz/dashboard">Open Dashboard</a>
"""
        elif language == 'de':
            return """
🤖 <b>SSL Monitor Pro Bot Befehle</b>

/start - Bot starten und Willkommensnachricht anzeigen
/help - Diese Hilfenachricht anzeigen
/status - Aktuellen Status und Einstellungen anzeigen
/settings - Einstellungsmenü öffnen
/domains - Überwachte Domains anzeigen
/language - Sprache ändern

<b>Funktionen:</b>
🔔 SSL-Zertifikat-Ablaufwarnungen
⚙️ Anpassbare Benachrichtigungseinstellungen
🌐 Mehrsprachige Unterstützung
📊 Echtzeit-Monitoring-Status
💳 Abonnementverwaltung
"""
        else:
            return self._get_help_text('en')  # Fallback to English
    
    async def send_personalized_notification(self, user_id: int, notification_type: str, **kwargs) -> bool:
        """Send personalized notification to user"""
        user = await self._get_user(user_id)
        if not user or not user.notification_enabled:
            return False
        
        # Check quiet hours
        if self._is_quiet_time(user):
            return False  # Skip notification during quiet hours
        
        language = user.language
        template = self.templates.get(language, self.templates['en']).get(notification_type)
        
        if not template:
            logger.warning(f"No template found for {notification_type} in language {language}")
            return False
        
        message = template.format(**kwargs)
        return await self._send_message(user.telegram_id, message)
    
    def _is_quiet_time(self, user: TelegramUser) -> bool:
        """Check if current time is within user's quiet hours"""
        # This would implement timezone-aware quiet hours checking
        # For now, return False (no quiet hours)
        return False
    
    async def _send_message(self, chat_id: int, text: str, reply_markup: Dict[str, Any] = None) -> bool:
        """Send message to Telegram chat"""
        if not self.enabled:
            logger.debug(f"Telegram disabled, would have sent to {chat_id}: {text}")
            return False
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def _answer_callback_query(self, callback_query_id: str):
        """Answer callback query"""
        if not self.enabled:
            return
        
        url = f"{self.base_url}/answerCallbackQuery"
        data = {"callback_query_id": callback_query_id}
        
        try:
            requests.post(url, data=data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to answer callback query: {e}")
    
    # Database operations (would integrate with actual database)
    async def _register_user(self, user_data: Dict[str, Any]):
        """Register or update user in database"""
        # This would integrate with the actual database
        pass
    
    async def _get_user(self, user_id: int) -> Optional[TelegramUser]:
        """Get user from database"""
        # This would integrate with the actual database
        # For now, return a mock user
        return TelegramUser(
            telegram_id=user_id,
            username="testuser",
            first_name="Test",
            language="en",
            notification_enabled=True,
            alert_threshold_days=30,
            subscription_status="trial"
        )
    
    async def _update_user_language(self, user_id: int, language: str):
        """Update user language in database"""
        pass
    
    async def _update_user_notifications(self, user_id: int, enabled: bool):
        """Update user notification preferences"""
        pass
    
    async def _update_user_threshold(self, user_id: int, days: int):
        """Update user alert threshold"""
        pass

# Global bot instance
_bot_instance = None

def get_bot_instance(db_session: Session = None) -> EnhancedTelegramBot:
    """Get global bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = EnhancedTelegramBot(db_session=db_session)
    return _bot_instance

async def handle_telegram_webhook(update_data: Dict[str, Any], db_session: Session = None) -> bool:
    """Handle incoming webhook from Telegram"""
    bot = get_bot_instance(db_session)
    return await bot.handle_update(update_data)
