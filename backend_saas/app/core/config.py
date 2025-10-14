"""
Configuration settings for SSL Monitor Pro SaaS
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "SSL Monitor Pro"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = Field(..., description="Redis URL for caching and Celery")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default_factory=lambda: Settings().REDIS_URL)
    CELERY_RESULT_BACKEND: str = Field(default_factory=lambda: Settings().REDIS_URL)
    
    # Stripe
    STRIPE_PUBLISHABLE_KEY: str = Field(..., description="Stripe publishable key")
    STRIPE_SECRET_KEY: str = Field(..., description="Stripe secret key")
    STRIPE_WEBHOOK_SECRET: str = Field(..., description="Stripe webhook secret")
    STRIPE_PRICE_MONTHLY: str = Field(..., description="Stripe monthly price ID")
    STRIPE_PRICE_YEARLY: str = Field(..., description="Stripe yearly price ID")
    
    # Calendly
    CALENDLY_ACCESS_TOKEN: str = Field(
        default="eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzYwNDc5MzMyLCJqdGkiOiIyYzk5ODY3Yi01NmJlLTQ4ZjEtODdhNS0xMDQ1ZGQ4NzlkYjYiLCJ1c2VyX3V1aWQiOiI0OTliYTY4OC0yMzBlLTQxNzUtYWZkMS00MDk5NTIwNTYwODAifQ.BoGSD4VXK1oZEPy3ayVLZ3pGp5diiIJgiPETedEOyWLENPu1rX8Q3T3oy9mxoxLZFwVm9BX6s5jJ4eOjZ4idbA", 
        description="Calendly access token"
    )
    CALENDLY_ORGANIZATION_URI: str = Field(..., description="Calendly organization URI")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token")
    TELEGRAM_CHAT_ID: Optional[str] = Field(None, description="Default Telegram chat ID")
    
    # WhatsApp Business
    WHATSAPP_PHONE: str = Field(default="+420721579603", description="WhatsApp Business phone number")
    WHATSAPP_BUSINESS_NAME: str = Field(default="SSL Monitor Pro", description="WhatsApp Business name")
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # Frontend
    FRONTEND_URL: str = "https://ssl-monitor.pages.dev"
    ALLOWED_ORIGINS: List[str] = [
        "https://ssl-monitor.pages.dev",
        "https://sslmonitor.pro",
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    
    # SSL Monitoring
    SSL_CHECK_INTERVAL: int = 3600  # 1 hour
    SSL_EXPIRY_ALERTS: List[int] = [30, 7, 3, 1]  # days before expiry
    
    # Free Trial
    FREE_TRIAL_DAYS: int = 7
    FREE_TRIAL_MONITORS_LIMIT: int = 5
    
    # Plans
    PLANS: dict = {
        "free": {"monitors": 5, "checks_per_day": 24, "price": 0},
        "pro": {"monitors": 50, "checks_per_day": 1440, "price": 29},
        "enterprise": {"monitors": 500, "checks_per_day": 1440, "price": 99}
    }
    
    # Monitoring
    HEALTH_CHECK_INTERVAL: int = 300  # 5 minutes
    MAX_CONCURRENT_CHECKS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
