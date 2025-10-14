"""
User Profile Model with i18n Support
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.sql import func
from datetime import datetime

from database import Base

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'de', 'fr', 'es', 'it', 'ru']


class UserProfile(Base):
    """User profile with i18n preferences and analytics"""
    
    __tablename__ = 'user_profiles'
    
    # Primary key (SERIAL instead of UUID for Render compatibility)
    id = Column(Integer, primary_key=True, server_default=func.nextval('user_profiles_id_seq'))
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # i18n Preferences
    preferred_language = Column(
        String(5), 
        nullable=False, 
        default='en',
        index=True
    )
    signup_language = Column(String(5), nullable=False, default='en')
    
    # Analytics
    device_languages = Column(JSONB, default=list)
    timezone = Column(String(50))
    country_code = Column(String(2), index=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    last_login = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Subscription reference
    subscription_id = Column(Integer, nullable=True)
    
    # GDPR compliance
    data_processing_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            f"preferred_language IN {tuple(SUPPORTED_LANGUAGES)}", 
            name='check_preferred_language'
        ),
        CheckConstraint(
            f"signup_language IN {tuple(SUPPORTED_LANGUAGES)}", 
            name='check_signup_language'
        ),
    )
    
    def __repr__(self):
        return f"<UserProfile {self.email} ({self.preferred_language})>"
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': str(self.id),
            'email': self.email,
            'preferred_language': self.preferred_language,
            'signup_language': self.signup_language,
            'timezone': self.timezone,
            'country_code': self.country_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
        }
        
        if include_sensitive:
            data['device_languages'] = self.device_languages
            data['subscription_id'] = self.subscription_id
            data['data_processing_consent'] = self.data_processing_consent
            data['marketing_consent'] = self.marketing_consent
        
        return data


class LanguageChangeLog(Base):
    """Audit log for language preference changes"""
    
    __tablename__ = 'language_change_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    old_language = Column(String(5))
    new_language = Column(String(5), nullable=False)
    device_type = Column(String(50))
    user_agent = Column(String)
    ip_address = Column(INET)
    changed_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True
    )
    
    __table_args__ = (
        CheckConstraint(
            f"new_language IN {tuple(SUPPORTED_LANGUAGES)}", 
            name='check_new_language'
        ),
    )
    
    def __repr__(self):
        return f"<LanguageChange {self.old_language}→{self.new_language} at {self.changed_at}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': str(self.user_id),
            'old_language': self.old_language,
            'new_language': self.new_language,
            'device_type': self.device_type,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
        }
