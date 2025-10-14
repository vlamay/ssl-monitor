"""
User Profile API Router with i18n Support
"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from database import get_db
from models.user_profile import UserProfile, LanguageChangeLog, SUPPORTED_LANGUAGES
from services.auth_service import AuthService

router = APIRouter(prefix="/api/user", tags=["user-profile"])


# ==================== PYDANTIC MODELS ====================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    preferred_language: str = Field(default='en', pattern='^(en|de|fr|es|it|ru)$')
    country_code: Optional[str] = Field(None, max_length=2)
    timezone: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class LanguageUpdateRequest(BaseModel):
    """Language preference update request"""
    language: str = Field(..., pattern='^(en|de|fr|es|it|ru)$')
    device_type: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response"""
    token: str
    user: dict
    message: str


class ProfileResponse(BaseModel):
    """User profile response"""
    user: dict


class LanguageResponse(BaseModel):
    """Language update response"""
    success: bool
    preferred_language: str
    message: str


# ==================== HELPER FUNCTIONS ====================

def get_current_user_from_header(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> UserProfile:
    """Extract and validate user from Authorization header"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    # Extract token (format: "Bearer <token>")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    # Get user from token
    return AuthService.get_current_user(db, token)


def log_language_change(
    db: Session,
    user_id: str,
    old_language: str,
    new_language: str,
    request: Request,
    device_type: Optional[str] = None
):
    """Log language preference change"""
    
    log_entry = LanguageChangeLog(
        user_id=user_id,
        old_language=old_language,
        new_language=new_language,
        device_type=device_type or 'unknown',
        user_agent=request.headers.get('user-agent'),
        ip_address=request.client.host if request.client else None
    )
    
    db.add(log_entry)
    db.commit()


# ==================== AUTH ENDPOINTS ====================

@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Register new user with i18n preferences
    
    - **email**: User email (unique)
    - **password**: Password (min 8 characters)
    - **preferred_language**: UI language (en, de, fr, es, it, ru)
    - **country_code**: ISO country code (optional)
    - **timezone**: User timezone (optional)
    """
    
    try:
        # Register user
        user = AuthService.register_user(
            db=db,
            email=request.email,
            password=request.password,
            preferred_language=request.preferred_language,
            country_code=request.country_code,
            timezone=request.timezone
        )
        
        # Create token
        token = AuthService.create_access_token(user.id, user.email)
        
        # Log initial language
        log_language_change(
            db=db,
            user_id=str(user.id),
            old_language=None,
            new_language=request.preferred_language,
            request=req,
            device_type='registration'
        )
        
        return AuthResponse(
            token=token,
            user=user.to_dict(),
            message=f"Registration successful. Welcome!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT token + profile
    
    - **email**: User email
    - **password**: User password
    
    Returns:
    - JWT token (expires in 7 days)
    - User profile with preferred_language
    """
    
    try:
        # Login user
        user, token = AuthService.login_user(
            db=db,
            email=request.email,
            password=request.password
        )
        
        return AuthResponse(
            token=token,
            user=user.to_dict(),
            message=f"Login successful. Welcome back!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


# ==================== PROFILE ENDPOINTS ====================

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: UserProfile = Depends(get_current_user_from_header)
):
    """
    Get current user profile
    
    Requires: Authorization header with Bearer token
    """
    
    return ProfileResponse(user=current_user.to_dict(include_sensitive=True))


@router.patch("/language", response_model=LanguageResponse)
async def update_language(
    request: LanguageUpdateRequest,
    req: Request,
    current_user: UserProfile = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Update user's preferred language
    
    - **language**: New language (en, de, fr, es, it, ru)
    - **device_type**: Device type (optional, for analytics)
    
    Requires: Authorization header with Bearer token
    """
    
    old_language = current_user.preferred_language
    new_language = request.language
    
    # Update language
    current_user.preferred_language = new_language
    
    # Update device_languages array
    if not current_user.device_languages:
        current_user.device_languages = []
    
    current_user.device_languages.append({
        'language': new_language,
        'device': request.device_type or 'unknown',
        'timestamp': datetime.utcnow().isoformat()
    })
    
    db.commit()
    
    # Log change
    log_language_change(
        db=db,
        user_id=str(current_user.id),
        old_language=old_language,
        new_language=new_language,
        request=req,
        device_type=request.device_type
    )
    
    return LanguageResponse(
        success=True,
        preferred_language=new_language,
        message=f"Language updated to {new_language}"
    )


@router.get("/preferences")
async def get_preferences(
    current_user: UserProfile = Depends(get_current_user_from_header)
):
    """
    Get all user preferences (extended profile data)
    
    Requires: Authorization header with Bearer token
    """
    
    return {
        "preferences": {
            "language": current_user.preferred_language,
            "timezone": current_user.timezone,
            "country_code": current_user.country_code,
            "email_verified": current_user.email_verified,
            "marketing_consent": current_user.marketing_consent
        },
        "analytics": {
            "signup_language": current_user.signup_language,
            "device_languages": current_user.device_languages,
            "created_at": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None
        }
    }


# ==================== GDPR ENDPOINTS ====================

@router.delete("/profile")
async def delete_profile(
    current_user: UserProfile = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Delete user profile (GDPR compliance)
    
    Requires: Authorization header with Bearer token
    
    ⚠️ This action is irreversible!
    """
    
    # Soft delete (set inactive)
    current_user.is_active = False
    current_user.email = f"deleted_{current_user.id}@deleted.local"
    db.commit()
    
    return {
        "success": True,
        "message": "Profile deleted successfully"
    }


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics/language-history")
async def get_language_history(
    current_user: UserProfile = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get user's language change history
    
    Requires: Authorization header with Bearer token
    """
    
    history = db.query(LanguageChangeLog).filter(
        LanguageChangeLog.user_id == current_user.id
    ).order_by(LanguageChangeLog.changed_at.desc()).limit(50).all()
    
    return {
        "history": [log.to_dict() for log in history],
        "current_language": current_user.preferred_language
    }
