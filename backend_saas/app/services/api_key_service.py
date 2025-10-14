"""
API Key Service for managing API access
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.api_key import APIKey, APIUsage, APIPermission
from app.models.user import User
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing API keys and access control"""
    
    def __init__(self):
        # Define plan-based API permissions
        self.plan_permissions = {
            "free": {
                "rate_limit_per_hour": 100,
                "endpoints": [
                    "GET /api/v1/monitors",
                    "GET /api/v1/monitors/{id}",
                    "GET /api/v1/health",
                    "GET /api/v1/analytics/overview"
                ],
                "max_keys": 1
            },
            "starter": {
                "rate_limit_per_hour": 1000,
                "endpoints": [
                    "GET /api/v1/monitors",
                    "POST /api/v1/monitors",
                    "GET /api/v1/monitors/{id}",
                    "PUT /api/v1/monitors/{id}",
                    "DELETE /api/v1/monitors/{id}",
                    "GET /api/v1/notifications",
                    "POST /api/v1/notifications",
                    "GET /api/v1/analytics/*"
                ],
                "max_keys": 3
            },
            "pro": {
                "rate_limit_per_hour": 10000,
                "endpoints": [
                    "GET /api/v1/*",
                    "POST /api/v1/*",
                    "PUT /api/v1/*",
                    "DELETE /api/v1/*"
                ],
                "max_keys": 10
            },
            "enterprise": {
                "rate_limit_per_hour": 100000,
                "endpoints": ["*"],
                "max_keys": -1  # Unlimited
            }
        }
    
    async def create_api_key(
        self, 
        db: AsyncSession, 
        user: User, 
        name: str,
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new API key for user
        
        Args:
            db: Database session
            user: User object
            name: User-friendly name for the key
            expires_in_days: Optional expiration in days
            
        Returns:
            Dictionary with key details
        """
        try:
            # Check if user can create more keys
            current_keys_count = await self.get_user_api_keys_count(db, user.id)
            max_keys = self.plan_permissions.get(user.current_plan, {}).get("max_keys", 1)
            
            if max_keys != -1 and current_keys_count >= max_keys:
                return {
                    "success": False,
                    "error": f"Maximum API keys limit reached for {user.current_plan} plan"
                }
            
            # Generate new API key
            full_key, key_hash, key_prefix = APIKey.generate_key()
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
            
            # Get plan permissions
            plan_config = self.plan_permissions.get(user.current_plan, self.plan_permissions["free"])
            
            # Create API key record
            api_key = APIKey(
                user_id=user.id,
                name=name,
                key_hash=key_hash,
                key_prefix=key_prefix,
                is_active=True,
                permissions=json.dumps(plan_config["endpoints"]),
                rate_limit_per_hour=plan_config["rate_limit_per_hour"],
                expires_at=expires_at
            )
            
            db.add(api_key)
            await db.commit()
            await db.refresh(api_key)
            
            logger.info(f"Created API key {key_prefix}... for user {user.id}")
            
            return {
                "success": True,
                "api_key": {
                    "id": api_key.id,
                    "name": api_key.name,
                    "key": full_key,  # Only returned once!
                    "key_prefix": api_key.key_prefix,
                    "permissions": plan_config["endpoints"],
                    "rate_limit_per_hour": api_key.rate_limit_per_hour,
                    "created_at": api_key.created_at.isoformat(),
                    "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            await db.rollback()
            return {"success": False, "error": str(e)}
    
    async def get_user_api_keys(
        self, 
        db: AsyncSession, 
        user_id: int,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            query = select(APIKey).where(APIKey.user_id == user_id)
            
            if not include_inactive:
                query = query.where(APIKey.is_active == True)
            
            query = query.order_by(APIKey.created_at.desc())
            
            result = await db.execute(query)
            api_keys = result.scalars().all()
            
            return [
                {
                    "id": key.id,
                    "name": key.name,
                    "key_prefix": key.key_prefix,
                    "is_active": key.is_active,
                    "permissions": json.loads(key.permissions) if key.permissions else [],
                    "rate_limit_per_hour": key.rate_limit_per_hour,
                    "total_requests": key.total_requests,
                    "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None
                }
                for key in api_keys
            ]
            
        except Exception as e:
            logger.error(f"Error getting user API keys: {e}")
            return []
    
    async def get_user_api_keys_count(self, db: AsyncSession, user_id: int) -> int:
        """Get count of active API keys for user"""
        try:
            query = select(func.count(APIKey.id)).where(
                and_(APIKey.user_id == user_id, APIKey.is_active == True)
            )
            result = await db.scalar(query)
            return result or 0
        except Exception as e:
            logger.error(f"Error getting API keys count: {e}")
            return 0
    
    async def revoke_api_key(
        self, 
        db: AsyncSession, 
        user_id: int, 
        key_id: int
    ) -> Dict[str, Any]:
        """Revoke (deactivate) an API key"""
        try:
            query = select(APIKey).where(
                and_(APIKey.id == key_id, APIKey.user_id == user_id)
            )
            result = await db.execute(query)
            api_key = result.scalar_one_or_none()
            
            if not api_key:
                return {"success": False, "error": "API key not found"}
            
            api_key.is_active = False
            await db.commit()
            
            logger.info(f"Revoked API key {api_key.key_prefix}... for user {user_id}")
            
            return {"success": True, "message": "API key revoked successfully"}
            
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            await db.rollback()
            return {"success": False, "error": str(e)}
    
    async def authenticate_api_key(
        self, 
        db: AsyncSession, 
        api_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate API key and return user info
        
        Args:
            db: Database session
            api_key: The API key to authenticate
            
        Returns:
            Dictionary with user and key info if valid, None if invalid
        """
        try:
            # Hash the provided key
            key_hash = APIKey.hash_key(api_key)
            
            # Find the API key
            query = select(APIKey).options(
                selectinload(APIKey.user)
            ).where(
                and_(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True
                )
            )
            
            result = await db.execute(query)
            api_key_obj = result.scalar_one_or_none()
            
            if not api_key_obj:
                return None
            
            # Check if expired
            if api_key_obj.is_expired():
                return None
            
            # Check rate limit
            if not api_key_obj.can_make_request():
                return {"error": "Rate limit exceeded"}
            
            # Update usage
            api_key_obj.increment_usage()
            await db.commit()
            
            # Parse permissions
            permissions = []
            if api_key_obj.permissions:
                try:
                    permissions = json.loads(api_key_obj.permissions)
                except json.JSONDecodeError:
                    permissions = []
            
            return {
                "user_id": api_key_obj.user_id,
                "user_email": api_key_obj.user.email,
                "user_plan": api_key_obj.user.current_plan,
                "api_key_id": api_key_obj.id,
                "key_prefix": api_key_obj.key_prefix,
                "permissions": permissions,
                "rate_limit_per_hour": api_key_obj.rate_limit_per_hour,
                "requests_this_hour": api_key_obj.requests_this_hour,
                "total_requests": api_key_obj.total_requests
            }
            
        except Exception as e:
            logger.error(f"Error authenticating API key: {e}")
            return None
    
    async def check_permission(
        self, 
        auth_info: Dict[str, Any], 
        endpoint: str, 
        method: str
    ) -> bool:
        """
        Check if API key has permission for endpoint and method
        
        Args:
            auth_info: Authentication info from authenticate_api_key
            endpoint: API endpoint (e.g., "/api/v1/monitors")
            method: HTTP method (GET, POST, etc.)
            
        Returns:
            True if permission granted, False otherwise
        """
        try:
            permissions = auth_info.get("permissions", [])
            
            # Enterprise plan has access to everything
            if auth_info.get("user_plan") == "enterprise":
                return True
            
            # Check specific permissions
            full_endpoint = f"{method} {endpoint}"
            
            for permission in permissions:
                # Exact match
                if permission == full_endpoint:
                    return True
                
                # Wildcard match for methods
                if permission.endswith("*") and endpoint.startswith(permission[:-1]):
                    return True
                
                # Wildcard match for endpoints
                if permission.startswith("*"):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def log_api_usage(
        self,
        db: AsyncSession,
        api_key_id: int,
        user_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: Optional[int] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None
    ):
        """Log API usage for analytics"""
        try:
            usage = APIUsage(
                api_key_id=api_key_id,
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                user_agent=user_agent,
                ip_address=ip_address,
                request_size_bytes=request_size,
                response_size_bytes=response_size
            )
            
            db.add(usage)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error logging API usage: {e}")
            # Don't raise exception for logging errors
    
    async def get_api_usage_stats(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get API usage statistics for user"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Total requests
            total_query = select(func.count(APIUsage.id)).where(
                and_(
                    APIUsage.user_id == user_id,
                    APIUsage.created_at >= start_date
                )
            )
            total_requests = await db.scalar(total_query) or 0
            
            # Requests by status code
            status_query = select(
                APIUsage.status_code,
                func.count(APIUsage.id).label('count')
            ).where(
                and_(
                    APIUsage.user_id == user_id,
                    APIUsage.created_at >= start_date
                )
            ).group_by(APIUsage.status_code)
            
            status_results = await db.execute(status_query)
            status_breakdown = {row.status_code: row.count for row in status_results}
            
            # Requests by endpoint
            endpoint_query = select(
                APIUsage.endpoint,
                func.count(APIUsage.id).label('count')
            ).where(
                and_(
                    APIUsage.user_id == user_id,
                    APIUsage.created_at >= start_date
                )
            ).group_by(APIUsage.endpoint).order_by(func.count(APIUsage.id).desc()).limit(10)
            
            endpoint_results = await db.execute(endpoint_query)
            top_endpoints = [
                {"endpoint": row.endpoint, "count": row.count}
                for row in endpoint_results
            ]
            
            # Average response time
            avg_response_query = select(func.avg(APIUsage.response_time_ms)).where(
                and_(
                    APIUsage.user_id == user_id,
                    APIUsage.created_at >= start_date,
                    APIUsage.response_time_ms.isnot(None)
                )
            )
            avg_response_time = await db.scalar(avg_response_query) or 0
            
            return {
                "total_requests": total_requests,
                "status_breakdown": status_breakdown,
                "top_endpoints": top_endpoints,
                "avg_response_time_ms": round(avg_response_time, 2),
                "period_days": days,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting API usage stats: {e}")
            return {"error": str(e)}


# Global service instance
api_key_service = APIKeyService()
