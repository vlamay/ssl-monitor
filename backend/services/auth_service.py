"""
Authentication Service with JWT
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user_profile import UserProfile
from app.config import SECRET_KEY, JWT_SECRET_KEY

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


class AuthService:
    """Authentication service for user profiles"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Create JWT access token"""
        expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        payload = {
            'user_id': user_id,  # Integer ID
            'email': email,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_access_token(token: str) -> dict:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        preferred_language: str = 'en',
        country_code: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> UserProfile:
        """Register new user"""
        
        # Check if user already exists
        existing_user = db.query(UserProfile).filter(
            UserProfile.email == email
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate language
        if preferred_language not in ['en', 'de', 'fr', 'es', 'it', 'ru']:
            preferred_language = 'en'
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create user profile
        user = UserProfile(
            email=email,
            password_hash=password_hash,
            preferred_language=preferred_language,
            signup_language=preferred_language,
            country_code=country_code,
            timezone=timezone,
            data_processing_consent=True,  # Required for GDPR
            device_languages=[{
                'language': preferred_language,
                'device': 'registration',
                'timestamp': datetime.utcnow().isoformat()
            }]
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def login_user(
        db: Session,
        email: str,
        password: str
    ) -> tuple[UserProfile, str]:
        """Login user and return profile + token"""
        
        # Find user
        user = db.query(UserProfile).filter(
            UserProfile.email == email
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create token
        token = AuthService.create_access_token(user.id, user.email)
        
        return user, token
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> UserProfile:
        """Get current user from token"""
        
        # Decode token
        payload = AuthService.decode_access_token(token)
        user_id = payload.get('user_id')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Find user
        user = db.query(UserProfile).filter(
            UserProfile.id == user_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        return user
