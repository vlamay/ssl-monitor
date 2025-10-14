"""
User Management with Upstash Redis
Simple, fast, serverless user profiles
"""

import json
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from services.redis_client import redis_client


class UserRedis:
    """User management via Upstash Redis"""
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def register(
        email: str,
        password: str,
        preferred_language: str = 'en',
        country_code: Optional[str] = None
    ) -> Optional[Dict]:
        """Register new user"""
        
        # Check if user exists
        user_key = f"user:{email}"
        if redis_client.exists(user_key):
            return None  # User already exists
        
        # Validate language
        if preferred_language not in ['en', 'de', 'fr', 'es', 'it', 'ru']:
            preferred_language = 'en'
        
        # Hash password
        password_hash = UserRedis._hash_password(password)
        
        # Calculate trial end date (7 days)
        trial_ends_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        # Create user data
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'preferred_language': preferred_language,
            'signup_language': preferred_language,
            'country_code': country_code or '',
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'is_active': 'true',
            'email_verified': 'false',
            'plan': 'trial',
            'trial_ends_at': trial_ends_at,
            'monitors': '[]',  # JSON array of monitored domains
            'settings': json.dumps({
                'notifications': True,
                'alert_threshold': 30
            })
        }
        
        # Save to Redis
        success = redis_client.hset(user_key, user_data)
        
        if success:
            # Add to email index
            redis_client.hset('users:index', {email: email})
            
            # Log registration
            print(f"✅ User registered: {email} ({preferred_language})")
            
            return {
                'email': email,
                'preferred_language': preferred_language,
                'trial_ends_at': trial_ends_at,
                'is_active': True
            }
        
        return None
    
    @staticmethod
    def login(email: str, password: str) -> Optional[Dict]:
        """Login user"""
        
        user_key = f"user:{email}"
        user_data = redis_client.hgetall(user_key)
        
        if not user_data or 'email' not in user_data:
            return None  # User not found
        
        # Verify password
        if not UserRedis._verify_password(password, user_data['password_hash']):
            return None  # Invalid password
        
        # Update last login
        redis_client.hset(user_key, {
            'last_login': datetime.utcnow().isoformat()
        })
        
        # Return user profile (without password)
        return {
            'email': user_data['email'],
            'preferred_language': user_data.get('preferred_language', 'en'),
            'country_code': user_data.get('country_code', ''),
            'created_at': user_data.get('created_at'),
            'last_login': datetime.utcnow().isoformat(),
            'is_active': user_data.get('is_active', 'true') == 'true',
            'plan': user_data.get('plan', 'trial'),
            'trial_ends_at': user_data.get('trial_ends_at')
        }
    
    @staticmethod
    def get_profile(email: str) -> Optional[Dict]:
        """Get user profile"""
        
        user_key = f"user:{email}"
        user_data = redis_client.hgetall(user_key)
        
        if not user_data or 'email' not in user_data:
            return None
        
        return {
            'email': user_data['email'],
            'preferred_language': user_data.get('preferred_language', 'en'),
            'signup_language': user_data.get('signup_language', 'en'),
            'country_code': user_data.get('country_code', ''),
            'created_at': user_data.get('created_at'),
            'last_login': user_data.get('last_login'),
            'is_active': user_data.get('is_active', 'true') == 'true',
            'plan': user_data.get('plan', 'trial'),
            'trial_ends_at': user_data.get('trial_ends_at'),
            'monitors': json.loads(user_data.get('monitors', '[]'))
        }
    
    @staticmethod
    def update_language(email: str, language: str, device_type: str = 'unknown') -> bool:
        """Update user's preferred language"""
        
        if language not in ['en', 'de', 'fr', 'es', 'it', 'ru']:
            return False
        
        user_key = f"user:{email}"
        
        if not redis_client.exists(user_key):
            return False
        
        # Update language
        success = redis_client.hset(user_key, {
            'preferred_language': language
        })
        
        if success:
            # Log language change
            log_key = f"lang_log:{email}:{datetime.utcnow().timestamp()}"
            redis_client.hset(log_key, {
                'email': email,
                'new_language': language,
                'device_type': device_type,
                'changed_at': datetime.utcnow().isoformat()
            })
            redis_client.expire(log_key, 86400 * 30)  # Keep logs for 30 days
            
            print(f"✅ Language updated: {email} → {language}")
        
        return success
    
    @staticmethod
    def get_all_users() -> list:
        """Get all user emails (for analytics)"""
        users_index = redis_client.hgetall('users:index')
        return list(users_index.keys()) if users_index else []
    
    @staticmethod
    def get_language_distribution() -> Dict[str, int]:
        """Get distribution of languages among users"""
        distribution = {}
        
        all_emails = UserRedis.get_all_users()
        
        for email in all_emails:
            user = UserRedis.get_profile(email)
            if user:
                lang = user.get('preferred_language', 'en')
                distribution[lang] = distribution.get(lang, 0) + 1
        
        return distribution

