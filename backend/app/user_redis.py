"""
User Profile API with Upstash Redis (Simplified)
Fast deployment without PostgreSQL migrations
"""

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import jwt

from services.user_redis import UserRedis
from app.config import JWT_SECRET_KEY

router = APIRouter(prefix="/api/user", tags=["user-redis"])

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


# ==================== PYDANTIC MODELS ====================

class QuickRegisterRequest(BaseModel):
    """Quick user registration"""
    email: EmailStr
    password: str
    preferred_language: str = 'en'
    country_code: Optional[str] = None


class LoginRequest(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class LanguageUpdateRequest(BaseModel):
    """Language update"""
    email: EmailStr
    language: str


# ==================== HELPER FUNCTIONS ====================

def create_token(email: str) -> str:
    """Create JWT token"""
    from datetime import timedelta
    
    expiration = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    
    payload = {
        'email': email,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return email"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get('email')
    except:
        return None


# ==================== API ENDPOINTS ====================

@router.post("/quick-register")
async def quick_register(request: QuickRegisterRequest):
    """
    Quick user registration (no email verification required)
    
    - **email**: Valid email address
    - **password**: Password (min 8 chars)
    - **preferred_language**: UI language (en, de, fr, es, it, ru)
    - **country_code**: ISO country code (optional)
    
    Returns:
    - JWT token (7 days)
    - User profile
    """
    
    # Register user
    user = UserRedis.register(
        email=request.email,
        password=request.password,
        preferred_language=request.preferred_language,
        country_code=request.country_code
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create token
    token = create_token(request.email)
    
    return {
        "success": True,
        "token": token,
        "user": user,
        "message": f"Welcome! Your 7-day free trial has started."
    }


@router.post("/quick-login")
async def quick_login(request: LoginRequest):
    """
    User login
    
    - **email**: User email
    - **password**: User password
    
    Returns:
    - JWT token (7 days)
    - User profile with language preference
    """
    
    user = UserRedis.login(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_token(request.email)
    
    return {
        "success": True,
        "token": token,
        "user": user,
        "message": "Login successful. Welcome back!"
    }


@router.get("/profile/{email}")
async def get_profile(email: str):
    """
    Get user profile by email
    
    - **email**: User email
    
    Returns user profile with language preference
    """
    
    user = UserRedis.get_profile(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": user
    }


@router.patch("/language")
async def update_language(
    request: LanguageUpdateRequest,
    req: Request
):
    """
    Update user's preferred language
    
    - **email**: User email
    - **language**: New language (en, de, fr, es, it, ru)
    
    Updates language preference and syncs across devices
    """
    
    device_type = 'desktop'
    user_agent = req.headers.get('user-agent', '')
    if 'mobile' in user_agent.lower():
        device_type = 'mobile'
    elif 'tablet' in user_agent.lower():
        device_type = 'tablet'
    
    success = UserRedis.update_language(
        email=request.email,
        language=request.language,
        device_type=device_type
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found or invalid language")
    
    return {
        "success": True,
        "preferred_language": request.language,
        "message": f"Language updated to {request.language}"
    }


@router.get("/analytics/language-distribution")
async def get_language_distribution():
    """
    Get language distribution across all users
    
    Returns analytics data for monitoring
    """
    
    distribution = UserRedis.get_language_distribution()
    total_users = sum(distribution.values())
    
    return {
        "total_users": total_users,
        "distribution": distribution,
        "percentages": {
            lang: round(count / total_users * 100, 2) if total_users > 0 else 0
            for lang, count in distribution.items()
        }
    }


@router.get("/analytics/all-users")
async def get_all_users():
    """Get all registered user emails (for admin)"""
    
    emails = UserRedis.get_all_users()
    
    return {
        "total": len(emails),
        "users": emails[:100]  # Limit to first 100
    }

