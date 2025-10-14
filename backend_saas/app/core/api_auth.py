"""
API Authentication middleware and dependencies
"""

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import time

from app.core.database import get_db, async_session_maker
from app.services.api_key_service import api_key_service
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

# Security scheme for API key authentication
security = HTTPBearer(auto_error=False)


class APIKeyAuth:
    """API Key authentication class"""
    
    def __init__(self):
        self.service = api_key_service
    
    async def authenticate(
        self, 
        request: Request,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate API key from request
        
        Args:
            request: FastAPI request object
            db: Database session
            
        Returns:
            Authentication info if valid, None if invalid
        """
        try:
            # Get API key from header
            api_key = self._extract_api_key(request)
            if not api_key:
                return None
            
            # Authenticate the key
            auth_info = await self.service.authenticate_api_key(db, api_key)
            if not auth_info:
                return None
            
            # Check for rate limit error
            if isinstance(auth_info, dict) and "error" in auth_info:
                return auth_info
            
            return auth_info
            
        except Exception as e:
            logger.error(f"API authentication error: {e}")
            return None
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers"""
        # Check X-API-Key header first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        # Check Authorization header as fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        return None
    
    async def check_permission(
        self,
        auth_info: Dict[str, Any],
        endpoint: str,
        method: str
    ) -> bool:
        """Check if API key has permission for endpoint and method"""
        return await self.service.check_permission(auth_info, endpoint, method)
    
    async def log_request(
        self,
        db: AsyncSession,
        request: Request,
        response_status: int,
        response_time_ms: int,
        auth_info: Dict[str, Any]
    ):
        """Log API request for analytics"""
        try:
            await self.service.log_api_usage(
                db=db,
                api_key_id=auth_info["api_key_id"],
                user_id=auth_info["user_id"],
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response_status,
                response_time_ms=response_time_ms,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None,
                request_size=request.headers.get("Content-Length"),
                response_size=None  # Would need to be passed from response
            )
        except Exception as e:
            logger.error(f"Error logging API request: {e}")


# Global auth instance
api_auth = APIKeyAuth()


async def get_api_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency to get authenticated API user
    
    This can be used as a dependency for API endpoints that require
    API key authentication instead of JWT authentication.
    """
    try:
        # Authenticate API key
        auth_info = await api_auth.authenticate(request, db)
        
        if not auth_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key"
            )
        
        # Check for rate limit error
        if isinstance(auth_info, dict) and "error" in auth_info:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=auth_info["error"]
            )
        
        return auth_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API user authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def require_api_permission(
    endpoint: str,
    method: str,
    auth_info: Dict[str, Any] = Depends(get_api_user)
) -> Dict[str, Any]:
    """
    Dependency to check API permissions for specific endpoint and method
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        auth_info: Authentication info from get_api_user
        
    Returns:
        Authentication info if permission granted
        
    Raises:
        HTTPException: If permission denied
    """
    try:
        async with async_session_maker() as db:
            has_permission = await api_auth.check_permission(auth_info, endpoint, method)
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"API key does not have permission for {method} {endpoint}"
                )
            
            return auth_info
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Permission check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission check failed"
        )


class APIRateLimitMiddleware:
    """Middleware to add rate limit headers to API responses"""
    
    def __init__(self):
        self.service = api_key_service
    
    async def add_rate_limit_headers(
        self,
        request: Request,
        call_next,
        auth_info: Optional[Dict[str, Any]] = None
    ):
        """Add rate limit headers to response"""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Add rate limit headers if authenticated
        if auth_info and isinstance(auth_info, dict) and "api_key_id" in auth_info:
            response.headers["X-RateLimit-Limit"] = str(auth_info.get("rate_limit_per_hour", 100))
            response.headers["X-RateLimit-Remaining"] = str(
                auth_info.get("rate_limit_per_hour", 100) - auth_info.get("requests_this_hour", 0)
            )
            
            # Calculate reset time (next hour)
            now = datetime.now(timezone.utc)
            reset_time = now.replace(minute=0, second=0, microsecond=0) + timezone.utc.localize(
                datetime(now.year, now.month, now.day, now.hour + 1)
            )
            response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))
        
        # Add response time header
        response.headers["X-Response-Time"] = f"{response_time_ms}ms"
        
        # Add API version header
        response.headers["X-API-Version"] = "v1"
        
        return response


# Global middleware instance
api_rate_limit_middleware = APIRateLimitMiddleware()


def get_plan_limits(plan: str) -> Dict[str, Any]:
    """Get API limits for a specific plan"""
    return api_key_service.plan_permissions.get(
        plan, 
        api_key_service.plan_permissions["free"]
    )


def is_endpoint_allowed(plan: str, endpoint: str, method: str) -> bool:
    """Check if endpoint is allowed for plan"""
    plan_config = get_plan_limits(plan)
    endpoints = plan_config.get("endpoints", [])
    
    full_endpoint = f"{method} {endpoint}"
    
    for allowed_endpoint in endpoints:
        if allowed_endpoint == full_endpoint:
            return True
        if allowed_endpoint.endswith("*") and endpoint.startswith(allowed_endpoint[:-1]):
            return True
        if allowed_endpoint.startswith("*"):
            return True
    
    return False
