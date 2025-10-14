"""
API Key Management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.api_key_service import api_key_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating API key"""
    name: str = Field(..., min_length=1, max_length=100, description="User-friendly name for the API key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Optional expiration in days")


class APIKeyResponse(BaseModel):
    """Response model for API key"""
    id: int
    name: str
    key_prefix: str
    is_active: bool
    permissions: List[str]
    rate_limit_per_hour: int
    total_requests: int
    last_used_at: Optional[str]
    created_at: str
    expires_at: Optional[str]


class CreateAPIKeyResponse(BaseModel):
    """Response model for API key creation"""
    success: bool
    api_key: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class APIUsageStatsResponse(BaseModel):
    """Response model for API usage statistics"""
    total_requests: int
    status_breakdown: Dict[int, int]
    top_endpoints: List[Dict[str, Any]]
    avg_response_time_ms: float
    period_days: int
    generated_at: str


@router.post("/create", response_model=CreateAPIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key for the current user"""
    try:
        result = await api_key_service.create_api_key(
            db=db,
            user=current_user,
            name=request.name,
            expires_in_days=request.expires_in_days
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return CreateAPIKeyResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.get("/", response_model=List[APIKeyResponse])
async def get_api_keys(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all API keys for the current user"""
    try:
        api_keys = await api_key_service.get_user_api_keys(
            db=db,
            user_id=current_user.id,
            include_inactive=include_inactive
        )
        
        return [APIKeyResponse(**key) for key in api_keys]
        
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API keys"
        )


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke (deactivate) an API key"""
    try:
        result = await api_key_service.revoke_api_key(
            db=db,
            user_id=current_user.id,
            key_id=key_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key"
        )


@router.get("/usage", response_model=APIUsageStatsResponse)
async def get_api_usage_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get API usage statistics for the current user"""
    try:
        stats = await api_key_service.get_api_usage_stats(
            db=db,
            user_id=current_user.id,
            days=days
        )
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats["error"]
            )
        
        return APIUsageStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API usage statistics"
        )


@router.get("/limits")
async def get_api_limits(
    current_user: User = Depends(get_current_user)
):
    """Get API limits and permissions for current user's plan"""
    try:
        plan_config = api_key_service.plan_permissions.get(
            current_user.current_plan, 
            api_key_service.plan_permissions["free"]
        )
        
        return {
            "plan": current_user.current_plan,
            "rate_limit_per_hour": plan_config["rate_limit_per_hour"],
            "allowed_endpoints": plan_config["endpoints"],
            "max_api_keys": plan_config["max_keys"],
            "features": {
                "create_monitors": "POST" in " ".join(plan_config["endpoints"]),
                "delete_monitors": "DELETE" in " ".join(plan_config["endpoints"]),
                "analytics_access": any("analytics" in ep for ep in plan_config["endpoints"]),
                "unlimited_requests": plan_config["rate_limit_per_hour"] >= 10000
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting API limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API limits"
        )


@router.get("/documentation")
async def get_api_documentation(
    current_user: User = Depends(get_current_user)
):
    """Get API documentation for current user's plan"""
    try:
        plan_config = api_key_service.plan_permissions.get(
            current_user.current_plan, 
            api_key_service.plan_permissions["free"]
        )
        
        documentation = {
            "plan": current_user.current_plan,
            "authentication": {
                "type": "API Key",
                "header": "X-API-Key",
                "example": "X-API-Key: sk_your_api_key_here"
            },
            "base_url": "https://ssl-monitor-api.onrender.com",
            "rate_limits": {
                "requests_per_hour": plan_config["rate_limit_per_hour"],
                "headers": {
                    "X-RateLimit-Limit": "Requests per hour limit",
                    "X-RateLimit-Remaining": "Requests remaining this hour",
                    "X-RateLimit-Reset": "Unix timestamp when limit resets"
                }
            },
            "endpoints": []
        }
        
        # Define common endpoints
        endpoints = [
            {
                "path": "/api/v1/monitors",
                "methods": ["GET", "POST"],
                "description": "List or create SSL monitors",
                "available": "GET" in " ".join(plan_config["endpoints"]) and "POST" in " ".join(plan_config["endpoints"])
            },
            {
                "path": "/api/v1/monitors/{id}",
                "methods": ["GET", "PUT", "DELETE"],
                "description": "Get, update, or delete a specific monitor",
                "available": any("monitors/{id}" in ep for ep in plan_config["endpoints"])
            },
            {
                "path": "/api/v1/notifications",
                "methods": ["GET", "POST"],
                "description": "Manage notification settings",
                "available": any("notifications" in ep for ep in plan_config["endpoints"])
            },
            {
                "path": "/api/v1/analytics/dashboard",
                "methods": ["GET"],
                "description": "Get dashboard analytics",
                "available": any("analytics" in ep for ep in plan_config["endpoints"])
            },
            {
                "path": "/api/v1/health",
                "methods": ["GET"],
                "description": "API health check",
                "available": True
            }
        ]
        
        # Filter endpoints based on plan permissions
        available_endpoints = []
        for endpoint in endpoints:
            if endpoint["available"]:
                available_endpoints.append(endpoint)
        
        documentation["endpoints"] = available_endpoints
        
        # Add examples
        documentation["examples"] = {
            "list_monitors": {
                "request": "GET /api/v1/monitors\nX-API-Key: sk_your_api_key_here",
                "response": {
                    "monitors": [
                        {
                            "id": 1,
                            "domain": "example.com",
                            "expires_at": "2024-12-31T23:59:59Z",
                            "status": "valid"
                        }
                    ]
                }
            },
            "create_monitor": {
                "request": "POST /api/v1/monitors\nX-API-Key: sk_your_api_key_here\nContent-Type: application/json\n\n{\"domain\": \"example.com\"}",
                "response": {
                    "id": 1,
                    "domain": "example.com",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
        }
        
        return documentation
        
    except Exception as e:
        logger.error(f"Error getting API documentation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API documentation"
        )
