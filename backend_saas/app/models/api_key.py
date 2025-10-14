"""
API Key model for managing API access
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import hashlib


class APIKey(Base):
    """API Key model for authentication"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # API Key details
    name = Column(String(100), nullable=False)  # User-friendly name
    key_hash = Column(String(64), nullable=False)  # SHA-256 hash of the key
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for identification
    
    # Permissions and limits
    is_active = Column(Boolean, default=True, nullable=False)
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    rate_limit_per_hour = Column(Integer, default=100, nullable=False)  # Requests per hour
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    total_requests = Column(Integer, default=0, nullable=False)
    requests_this_hour = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For temporary keys
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @staticmethod
    def generate_key() -> tuple[str, str]:
        """
        Generate a new API key
        
        Returns:
            Tuple of (full_key, key_hash, key_prefix)
        """
        # Generate a secure random key
        full_key = f"sk_{secrets.token_urlsafe(32)}"
        
        # Create hash for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        # Create prefix for identification
        key_prefix = full_key[:8]
        
        return full_key, key_hash, key_prefix
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def verify_key(self, key: str) -> bool:
        """Verify if the provided key matches this API key"""
        return self.key_hash == hashlib.sha256(key.encode()).hexdigest()
    
    def is_expired(self) -> bool:
        """Check if the API key is expired"""
        if not self.expires_at:
            return False
        return self.expires_at < func.now()
    
    def can_make_request(self) -> bool:
        """Check if the API key can make a request (rate limit)"""
        return self.is_active and not self.is_expired() and self.requests_this_hour < self.rate_limit_per_hour
    
    def increment_usage(self):
        """Increment the usage counters"""
        self.total_requests += 1
        self.requests_this_hour += 1
        self.last_used_at = func.now()


class APIUsage(Base):
    """API usage tracking for analytics"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request details
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    
    # Request metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    api_key = relationship("APIKey")
    user = relationship("User")


class APIPermission(Base):
    """API permissions definition"""
    __tablename__ = "api_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200), nullable=True)
    endpoints = Column(Text, nullable=False)  # JSON array of allowed endpoints
    methods = Column(Text, nullable=False)  # JSON array of allowed HTTP methods
    
    # Plan restrictions
    required_plan = Column(String(20), nullable=True)  # free, starter, pro, enterprise
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<APIPermission(name='{self.name}', required_plan='{self.required_plan}')>"
