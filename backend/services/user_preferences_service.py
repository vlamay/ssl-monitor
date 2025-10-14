"""
User Preferences Service for SSL Monitor Pro
Manages user preferences, notification settings, and personalization
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

logger = logging.getLogger(__name__)

@dataclass
class UserPreferences:
    """User preferences data model"""
    user_id: str
    email: str
    language: str = 'en'
    timezone: str = 'UTC'
    theme: str = 'light'  # light, dark, auto
    notifications_enabled: bool = True
    email_notifications: bool = True
    telegram_notifications: bool = False
    slack_notifications: bool = False
    alert_threshold_days: int = 30
    quiet_hours_enabled: bool = True
    quiet_hours_start: str = '22:00'
    quiet_hours_end: str = '08:00'
    weekly_reports: bool = True
    monthly_reports: bool = True
    dashboard_refresh_interval: int = 30  # seconds
    default_domain_limit: int = 10
    auto_renewal_enabled: bool = False
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class NotificationPreferences:
    """Notification preferences for specific alert types"""
    user_id: str
    alert_type: str  # 'ssl_warning', 'ssl_critical', 'ssl_expired', 'system_error'
    email_enabled: bool = True
    telegram_enabled: bool = False
    slack_enabled: bool = False
    webhook_enabled: bool = False
    custom_message: Optional[str] = None
    frequency_limit: int = 1  # max notifications per hour

@dataclass
class DomainPreferences:
    """Domain-specific preferences"""
    user_id: str
    domain_id: int
    custom_alert_threshold: Optional[int] = None
    notification_enabled: bool = True
    priority: str = 'normal'  # low, normal, high, critical
    custom_message: Optional[str] = None

class UserPreferencesService:
    """Service for managing user preferences"""
    
    def __init__(self, db_session: Session = None, redis_client: redis.Redis = None):
        self.db = db_session
        self.redis = redis_client or self._get_redis_client()
        self.cache_ttl = 3600  # 1 hour
        
        # Default preferences
        self.default_preferences = {
            'language': 'en',
            'timezone': 'UTC',
            'theme': 'light',
            'notifications_enabled': True,
            'email_notifications': True,
            'telegram_notifications': False,
            'slack_notifications': False,
            'alert_threshold_days': 30,
            'quiet_hours_enabled': True,
            'quiet_hours_start': '22:00',
            'quiet_hours_end': '08:00',
            'weekly_reports': True,
            'monthly_reports': True,
            'dashboard_refresh_interval': 30,
            'default_domain_limit': 10,
            'auto_renewal_enabled': False
        }
        
        # Supported languages
        self.supported_languages = {
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'it': 'Italiano',
            'ru': 'Русский',
            'cs': 'Čeština'
        }
        
        # Supported timezones
        self.supported_timezones = [
            'UTC', 'Europe/Prague', 'Europe/Berlin', 'Europe/London',
            'America/New_York', 'America/Los_Angeles', 'Asia/Tokyo',
            'Asia/Shanghai', 'Australia/Sydney'
        ]
    
    def _get_redis_client(self) -> redis.Redis:
        """Get Redis client"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            return redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            return None
    
    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences"""
        try:
            # Try cache first
            cache_key = f"user_preferences:{user_id}"
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return UserPreferences(**data)
            
            # Query database
            if self.db:
                query = text("""
                    SELECT * FROM user_preferences 
                    WHERE user_id = :user_id
                """)
                result = self.db.execute(query, {"user_id": user_id}).fetchone()
                
                if result:
                    preferences = UserPreferences(
                        user_id=result.user_id,
                        email=result.email,
                        language=result.language,
                        timezone=result.timezone,
                        theme=result.theme,
                        notifications_enabled=result.notifications_enabled,
                        email_notifications=result.email_notifications,
                        telegram_notifications=result.telegram_notifications,
                        slack_notifications=result.slack_notifications,
                        alert_threshold_days=result.alert_threshold_days,
                        quiet_hours_enabled=result.quiet_hours_enabled,
                        quiet_hours_start=result.quiet_hours_start,
                        quiet_hours_end=result.quiet_hours_end,
                        weekly_reports=result.weekly_reports,
                        monthly_reports=result.monthly_reports,
                        dashboard_refresh_interval=result.dashboard_refresh_interval,
                        default_domain_limit=result.default_domain_limit,
                        auto_renewal_enabled=result.auto_renewal_enabled,
                        created_at=result.created_at,
                        updated_at=result.updated_at
                    )
                    
                    # Cache the result
                    if self.redis:
                        self.redis.setex(
                            cache_key, 
                            self.cache_ttl, 
                            json.dumps(asdict(preferences), default=str)
                        )
                    
                    return preferences
            
            # Return default preferences if not found
            return UserPreferences(
                user_id=user_id,
                email="",
                **self.default_preferences,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return UserPreferences(
                user_id=user_id,
                email="",
                **self.default_preferences,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        preferences_update: Dict[str, Any]
    ) -> UserPreferences:
        """Update user preferences"""
        try:
            # Get current preferences
            current = await self.get_user_preferences(user_id)
            
            # Update with new values
            updated_data = asdict(current)
            updated_data.update(preferences_update)
            updated_data['updated_at'] = datetime.utcnow()
            
            # Validate preferences
            validated_data = self._validate_preferences(updated_data)
            
            # Save to database
            if self.db:
                query = text("""
                    INSERT INTO user_preferences (
                        user_id, email, language, timezone, theme,
                        notifications_enabled, email_notifications, telegram_notifications,
                        slack_notifications, alert_threshold_days, quiet_hours_enabled,
                        quiet_hours_start, quiet_hours_end, weekly_reports, monthly_reports,
                        dashboard_refresh_interval, default_domain_limit, auto_renewal_enabled,
                        created_at, updated_at
                    ) VALUES (
                        :user_id, :email, :language, :timezone, :theme,
                        :notifications_enabled, :email_notifications, :telegram_notifications,
                        :slack_notifications, :alert_threshold_days, :quiet_hours_enabled,
                        :quiet_hours_start, :quiet_hours_end, :weekly_reports, :monthly_reports,
                        :dashboard_refresh_interval, :default_domain_limit, :auto_renewal_enabled,
                        :created_at, :updated_at
                    ) ON CONFLICT (user_id) DO UPDATE SET
                        language = EXCLUDED.language,
                        timezone = EXCLUDED.timezone,
                        theme = EXCLUDED.theme,
                        notifications_enabled = EXCLUDED.notifications_enabled,
                        email_notifications = EXCLUDED.email_notifications,
                        telegram_notifications = EXCLUDED.telegram_notifications,
                        slack_notifications = EXCLUDED.slack_notifications,
                        alert_threshold_days = EXCLUDED.alert_threshold_days,
                        quiet_hours_enabled = EXCLUDED.quiet_hours_enabled,
                        quiet_hours_start = EXCLUDED.quiet_hours_start,
                        quiet_hours_end = EXCLUDED.quiet_hours_end,
                        weekly_reports = EXCLUDED.weekly_reports,
                        monthly_reports = EXCLUDED.monthly_reports,
                        dashboard_refresh_interval = EXCLUDED.dashboard_refresh_interval,
                        default_domain_limit = EXCLUDED.default_domain_limit,
                        auto_renewal_enabled = EXCLUDED.auto_renewal_enabled,
                        updated_at = EXCLUDED.updated_at
                """)
                
                self.db.execute(query, validated_data)
                self.db.commit()
            
            # Clear cache
            if self.redis:
                cache_key = f"user_preferences:{user_id}"
                self.redis.delete(cache_key)
            
            return UserPreferences(**validated_data)
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            if self.db:
                self.db.rollback()
            raise
    
    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user preferences"""
        validated = {}
        
        # Validate language
        validated['language'] = preferences.get('language', 'en')
        if validated['language'] not in self.supported_languages:
            validated['language'] = 'en'
        
        # Validate timezone
        validated['timezone'] = preferences.get('timezone', 'UTC')
        if validated['timezone'] not in self.supported_timezones:
            validated['timezone'] = 'UTC'
        
        # Validate theme
        validated['theme'] = preferences.get('theme', 'light')
        if validated['theme'] not in ['light', 'dark', 'auto']:
            validated['theme'] = 'light'
        
        # Validate boolean preferences
        boolean_fields = [
            'notifications_enabled', 'email_notifications', 'telegram_notifications',
            'slack_notifications', 'quiet_hours_enabled', 'weekly_reports',
            'monthly_reports', 'auto_renewal_enabled'
        ]
        for field in boolean_fields:
            validated[field] = bool(preferences.get(field, True))
        
        # Validate numeric preferences
        validated['alert_threshold_days'] = max(1, min(365, int(preferences.get('alert_threshold_days', 30))))
        validated['dashboard_refresh_interval'] = max(10, min(300, int(preferences.get('dashboard_refresh_interval', 30))))
        validated['default_domain_limit'] = max(1, min(1000, int(preferences.get('default_domain_limit', 10))))
        
        # Validate time formats
        validated['quiet_hours_start'] = self._validate_time_format(preferences.get('quiet_hours_start', '22:00'))
        validated['quiet_hours_end'] = self._validate_time_format(preferences.get('quiet_hours_end', '08:00'))
        
        # Copy other fields
        for field in ['user_id', 'email', 'created_at', 'updated_at']:
            if field in preferences:
                validated[field] = preferences[field]
        
        return validated
    
    def _validate_time_format(self, time_str: str) -> str:
        """Validate time format (HH:MM)"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return time_str
        except ValueError:
            return '22:00'
    
    async def get_notification_preferences(self, user_id: str) -> List[NotificationPreferences]:
        """Get notification preferences for user"""
        try:
            cache_key = f"notification_preferences:{user_id}"
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return [NotificationPreferences(**item) for item in data]
            
            # Query database
            preferences = []
            if self.db:
                query = text("""
                    SELECT * FROM notification_preferences 
                    WHERE user_id = :user_id
                """)
                results = self.db.execute(query, {"user_id": user_id}).fetchall()
                
                for result in results:
                    preferences.append(NotificationPreferences(
                        user_id=result.user_id,
                        alert_type=result.alert_type,
                        email_enabled=result.email_enabled,
                        telegram_enabled=result.telegram_enabled,
                        slack_enabled=result.slack_enabled,
                        webhook_enabled=result.webhook_enabled,
                        custom_message=result.custom_message,
                        frequency_limit=result.frequency_limit
                    ))
            
            # Cache the result
            if self.redis:
                self.redis.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps([asdict(p) for p in preferences])
                )
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting notification preferences: {e}")
            return []
    
    async def update_notification_preferences(
        self, 
        user_id: str, 
        alert_type: str, 
        preferences: Dict[str, Any]
    ) -> NotificationPreferences:
        """Update notification preferences for specific alert type"""
        try:
            # Validate preferences
            validated = {
                'user_id': user_id,
                'alert_type': alert_type,
                'email_enabled': bool(preferences.get('email_enabled', True)),
                'telegram_enabled': bool(preferences.get('telegram_enabled', False)),
                'slack_enabled': bool(preferences.get('slack_enabled', False)),
                'webhook_enabled': bool(preferences.get('webhook_enabled', False)),
                'custom_message': preferences.get('custom_message'),
                'frequency_limit': max(1, min(10, int(preferences.get('frequency_limit', 1))))
            }
            
            # Save to database
            if self.db:
                query = text("""
                    INSERT INTO notification_preferences (
                        user_id, alert_type, email_enabled, telegram_enabled,
                        slack_enabled, webhook_enabled, custom_message, frequency_limit
                    ) VALUES (
                        :user_id, :alert_type, :email_enabled, :telegram_enabled,
                        :slack_enabled, :webhook_enabled, :custom_message, :frequency_limit
                    ) ON CONFLICT (user_id, alert_type) DO UPDATE SET
                        email_enabled = EXCLUDED.email_enabled,
                        telegram_enabled = EXCLUDED.telegram_enabled,
                        slack_enabled = EXCLUDED.slack_enabled,
                        webhook_enabled = EXCLUDED.webhook_enabled,
                        custom_message = EXCLUDED.custom_message,
                        frequency_limit = EXCLUDED.frequency_limit
                """)
                
                self.db.execute(query, validated)
                self.db.commit()
            
            # Clear cache
            if self.redis:
                cache_key = f"notification_preferences:{user_id}"
                self.redis.delete(cache_key)
            
            return NotificationPreferences(**validated)
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {e}")
            if self.db:
                self.db.rollback()
            raise
    
    async def get_domain_preferences(self, user_id: str, domain_id: int) -> Optional[DomainPreferences]:
        """Get domain-specific preferences"""
        try:
            cache_key = f"domain_preferences:{user_id}:{domain_id}"
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return DomainPreferences(**data)
            
            # Query database
            if self.db:
                query = text("""
                    SELECT * FROM domain_preferences 
                    WHERE user_id = :user_id AND domain_id = :domain_id
                """)
                result = self.db.execute(query, {
                    "user_id": user_id, 
                    "domain_id": domain_id
                }).fetchone()
                
                if result:
                    preferences = DomainPreferences(
                        user_id=result.user_id,
                        domain_id=result.domain_id,
                        custom_alert_threshold=result.custom_alert_threshold,
                        notification_enabled=result.notification_enabled,
                        priority=result.priority,
                        custom_message=result.custom_message
                    )
                    
                    # Cache the result
                    if self.redis:
                        self.redis.setex(
                            cache_key, 
                            self.cache_ttl, 
                            json.dumps(asdict(preferences))
                        )
                    
                    return preferences
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting domain preferences: {e}")
            return None
    
    async def update_domain_preferences(
        self, 
        user_id: str, 
        domain_id: int, 
        preferences: Dict[str, Any]
    ) -> DomainPreferences:
        """Update domain-specific preferences"""
        try:
            # Validate preferences
            validated = {
                'user_id': user_id,
                'domain_id': domain_id,
                'custom_alert_threshold': preferences.get('custom_alert_threshold'),
                'notification_enabled': bool(preferences.get('notification_enabled', True)),
                'priority': preferences.get('priority', 'normal'),
                'custom_message': preferences.get('custom_message')
            }
            
            # Validate priority
            if validated['priority'] not in ['low', 'normal', 'high', 'critical']:
                validated['priority'] = 'normal'
            
            # Validate alert threshold
            if validated['custom_alert_threshold']:
                validated['custom_alert_threshold'] = max(1, min(365, int(validated['custom_alert_threshold'])))
            
            # Save to database
            if self.db:
                query = text("""
                    INSERT INTO domain_preferences (
                        user_id, domain_id, custom_alert_threshold,
                        notification_enabled, priority, custom_message
                    ) VALUES (
                        :user_id, :domain_id, :custom_alert_threshold,
                        :notification_enabled, :priority, :custom_message
                    ) ON CONFLICT (user_id, domain_id) DO UPDATE SET
                        custom_alert_threshold = EXCLUDED.custom_alert_threshold,
                        notification_enabled = EXCLUDED.notification_enabled,
                        priority = EXCLUDED.priority,
                        custom_message = EXCLUDED.custom_message
                """)
                
                self.db.execute(query, validated)
                self.db.commit()
            
            # Clear cache
            if self.redis:
                cache_key = f"domain_preferences:{user_id}:{domain_id}"
                self.redis.delete(cache_key)
            
            return DomainPreferences(**validated)
            
        except Exception as e:
            logger.error(f"Error updating domain preferences: {e}")
            if self.db:
                self.db.rollback()
            raise
    
    async def should_send_notification(
        self, 
        user_id: str, 
        alert_type: str, 
        domain_id: Optional[int] = None
    ) -> bool:
        """Check if notification should be sent based on user preferences"""
        try:
            # Get user preferences
            user_prefs = await self.get_user_preferences(user_id)
            
            if not user_prefs.notifications_enabled:
                return False
            
            # Check quiet hours
            if user_prefs.quiet_hours_enabled and self._is_quiet_time(user_prefs):
                return False
            
            # Get notification preferences
            notification_prefs = await self.get_notification_preferences(user_id)
            alert_prefs = next((p for p in notification_prefs if p.alert_type == alert_type), None)
            
            if alert_prefs:
                # Check frequency limit
                if not self._check_frequency_limit(user_id, alert_type, alert_prefs.frequency_limit):
                    return False
            
            # Check domain-specific preferences
            if domain_id:
                domain_prefs = await self.get_domain_preferences(user_id, domain_id)
                if domain_prefs and not domain_prefs.notification_enabled:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking notification preferences: {e}")
            return True  # Default to sending notification
    
    def _is_quiet_time(self, preferences: UserPreferences) -> bool:
        """Check if current time is within quiet hours"""
        try:
            from datetime import datetime
            import pytz
            
            # Get current time in user's timezone
            user_tz = pytz.timezone(preferences.timezone)
            current_time = datetime.now(user_tz).time()
            
            # Parse quiet hours
            start_time = datetime.strptime(preferences.quiet_hours_start, '%H:%M').time()
            end_time = datetime.strptime(preferences.quiet_hours_end, '%H:%M').time()
            
            # Check if current time is within quiet hours
            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:  # Quiet hours span midnight
                return current_time >= start_time or current_time <= end_time
                
        except Exception as e:
            logger.error(f"Error checking quiet time: {e}")
            return False
    
    def _check_frequency_limit(self, user_id: str, alert_type: str, limit: int) -> bool:
        """Check if notification frequency limit is exceeded"""
        try:
            if not self.redis:
                return True  # No rate limiting without Redis
            
            # Create rate limit key
            current_hour = datetime.utcnow().strftime('%Y-%m-%d-%H')
            rate_key = f"notification_rate:{user_id}:{alert_type}:{current_hour}"
            
            # Get current count
            current_count = self.redis.get(rate_key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            # Check if limit exceeded
            if current_count >= limit:
                return False
            
            # Increment counter
            self.redis.incr(rate_key)
            self.redis.expire(rate_key, 3600)  # Expire in 1 hour
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking frequency limit: {e}")
            return True  # Default to allowing notification

# Global service instance
_preferences_service = None

def get_preferences_service(db_session: Session = None) -> UserPreferencesService:
    """Get global preferences service instance"""
    global _preferences_service
    if _preferences_service is None:
        _preferences_service = UserPreferencesService(db_session=db_session)
    return _preferences_service
