import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Загружаем .env файл
load_dotenv()

def get_database_url():
    """
    Получает DATABASE_URL из environment и очищает от лишних кавычек
    """
    url = os.getenv("DATABASE_URL", "")
    
    # Убираем лишние кавычки если есть
    url = url.strip('"').strip("'")
    
    # Для Render: если URL начинается с postgres://, меняем на postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # Если URL пустой, используем дефолтный
    if not url:
        url = "postgresql://sslmonitor_user@localhost:5433/sslmonitor"
    
    return url

def get_redis_url():
    """
    Получает REDIS_URL из environment
    """
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return url.strip('"').strip("'")

class Settings:
    # Database
    DATABASE_URL = get_database_url()
    
    # Redis
    REDIS_URL = get_redis_url()
    
    # Flask/FastAPI
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    
    # JWT Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-jwt-secret-change-in-production-min-32-chars"))
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days
    
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    
    # URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

settings = Settings()

# Для удобства экспортируем
DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL
SECRET_KEY = settings.SECRET_KEY
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


