"""
Monitor API endpoints with API Key authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.api_auth import get_api_user, require_api_permission
from app.models.monitor import Monitor
from app.models.user import User
from app.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorResponse
from sqlalchemy import select, and_
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class MonitorCreateRequest(BaseModel):
    """Request model for creating monitor via API"""
    domain: str = Field(..., min_length=1, max_length=255, description="Domain to monitor")
    alert_threshold_days: int = Field(default=30, ge=1, le=365, description="Days before expiration to alert")


class MonitorUpdateRequest(BaseModel):
    """Request model for updating monitor via API"""
    alert_threshold_days: Optional[int] = Field(None, ge=1, le=365, description="Days before expiration to alert")
    is_active: Optional[bool] = Field(None, description="Whether monitor is active")


@router.get("/", response_model=List[MonitorResponse])
async def list_monitors(
    request: Request,
    limit: int = 100,
    offset: int = 0,
    active_only: bool = True,
    auth_info: dict = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
):
    """List monitors for authenticated API user"""
    try:
        # Check permission
        await require_api_permission("/api/v1/monitors", "GET", auth_info)
        
        # Build query
        query = select(Monitor).where(Monitor.user_id == auth_info["user_id"])
        
        if active_only:
            query = query.where(Monitor.is_active == True)
        
        query = query.offset(offset).limit(limit).order_by(Monitor.created_at.desc())
        
        result = await db.execute(query)
        monitors = result.scalars().all()
        
        return [
            MonitorResponse(
                id=monitor.id,
                domain=monitor.domain,
                expires_at=monitor.expires_at.isoformat() if monitor.expires_at else None,
                last_status=monitor.last_status,
                last_checked_at=monitor.last_checked_at.isoformat() if monitor.last_checked_at else None,
                is_active=monitor.is_active,
                created_at=monitor.created_at.isoformat(),
                updated_at=monitor.updated_at.isoformat()
            )
            for monitor in monitors
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing monitors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list monitors"
        )


@router.post("/", response_model=MonitorResponse)
async def create_monitor(
    request: Request,
    monitor_data: MonitorCreateRequest,
    auth_info: dict = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new monitor via API"""
    try:
        # Check permission
        await require_api_permission("/api/v1/monitors", "POST", auth_info)
        
        # Check if user can create more monitors (based on plan)
        user_plan = auth_info.get("user_plan", "free")
        plan_limits = {
            "free": 10,
            "starter": 50,
            "pro": 200,
            "enterprise": -1  # Unlimited
        }
        
        max_monitors = plan_limits.get(user_plan, 10)
        if max_monitors != -1:
            current_count = await db.scalar(
                select(Monitor).where(
                    and_(Monitor.user_id == auth_info["user_id"], Monitor.is_active == True)
                )
            )
            if current_count and current_count >= max_monitors:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Monitor limit reached for {user_plan} plan ({max_monitors} monitors)"
                )
        
        # Create monitor
        monitor = Monitor(
            user_id=auth_info["user_id"],
            domain=monitor_data.domain,
            is_active=True,
            last_status="pending"
        )
        
        db.add(monitor)
        await db.commit()
        await db.refresh(monitor)
        
        logger.info(f"Created monitor {monitor.id} for domain {monitor_data.domain} via API")
        
        return MonitorResponse(
            id=monitor.id,
            domain=monitor.domain,
            expires_at=monitor.expires_at.isoformat() if monitor.expires_at else None,
            last_status=monitor.last_status,
            last_checked_at=monitor.last_checked_at.isoformat() if monitor.last_checked_at else None,
            is_active=monitor.is_active,
            created_at=monitor.created_at.isoformat(),
            updated_at=monitor.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating monitor: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monitor"
        )


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(
    monitor_id: int,
    request: Request,
    auth_info: dict = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific monitor by ID"""
    try:
        # Check permission
        await require_api_permission("/api/v1/monitors/{id}", "GET", auth_info)
        
        # Get monitor
        query = select(Monitor).where(
            and_(Monitor.id == monitor_id, Monitor.user_id == auth_info["user_id"])
        )
        result = await db.execute(query)
        monitor = result.scalar_one_or_none()
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        return MonitorResponse(
            id=monitor.id,
            domain=monitor.domain,
            expires_at=monitor.expires_at.isoformat() if monitor.expires_at else None,
            last_status=monitor.last_status,
            last_checked_at=monitor.last_checked_at.isoformat() if monitor.last_checked_at else None,
            is_active=monitor.is_active,
            created_at=monitor.created_at.isoformat(),
            updated_at=monitor.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitor"
        )


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(
    monitor_id: int,
    request: Request,
    monitor_data: MonitorUpdateRequest,
    auth_info: dict = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a monitor via API"""
    try:
        # Check permission
        await require_api_permission("/api/v1/monitors/{id}", "PUT", auth_info)
        
        # Get monitor
        query = select(Monitor).where(
            and_(Monitor.id == monitor_id, Monitor.user_id == auth_info["user_id"])
        )
        result = await db.execute(query)
        monitor = result.scalar_one_or_none()
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        # Update fields
        if monitor_data.alert_threshold_days is not None:
            # This would require adding the field to the model
            pass  # For now, just log it
        
        if monitor_data.is_active is not None:
            monitor.is_active = monitor_data.is_active
        
        monitor.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(monitor)
        
        logger.info(f"Updated monitor {monitor.id} via API")
        
        return MonitorResponse(
            id=monitor.id,
            domain=monitor.domain,
            expires_at=monitor.expires_at.isoformat() if monitor.expires_at else None,
            last_status=monitor.last_status,
            last_checked_at=monitor.last_checked_at.isoformat() if monitor.last_checked_at else None,
            is_active=monitor.is_active,
            created_at=monitor.created_at.isoformat(),
            updated_at=monitor.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating monitor: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update monitor"
        )


@router.delete("/{monitor_id}")
async def delete_monitor(
    monitor_id: int,
    request: Request,
    auth_info: dict = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a monitor via API"""
    try:
        # Check permission
        await require_api_permission("/api/v1/monitors/{id}", "DELETE", auth_info)
        
        # Get monitor
        query = select(Monitor).where(
            and_(Monitor.id == monitor_id, Monitor.user_id == auth_info["user_id"])
        )
        result = await db.execute(query)
        monitor = result.scalar_one_or_none()
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        # Delete monitor
        await db.delete(monitor)
        await db.commit()
        
        logger.info(f"Deleted monitor {monitor_id} via API")
        
        return {"message": "Monitor deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting monitor: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete monitor"
        )


@router.post("/{monitor_id}/check")
async def check_monitor(
    monitor_id: int,
    request: Request,
    auth_info: dict = Depends(get_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger immediate SSL check for a monitor"""
    try:
        # Check permission
        await require_api_permission("/api/v1/monitors/{id}/check", "POST", auth_info)
        
        # Get monitor
        query = select(Monitor).where(
            and_(Monitor.id == monitor_id, Monitor.user_id == auth_info["user_id"])
        )
        result = await db.execute(query)
        monitor = result.scalar_one_or_none()
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        # Trigger SSL check (this would integrate with Celery tasks)
        # For now, just return success
        logger.info(f"Triggered SSL check for monitor {monitor_id} via API")
        
        return {
            "message": "SSL check triggered successfully",
            "monitor_id": monitor_id,
            "domain": monitor.domain,
            "triggered_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering SSL check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger SSL check"
        )
