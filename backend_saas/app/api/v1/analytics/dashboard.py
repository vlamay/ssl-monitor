"""
Analytics Dashboard API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.core.database import get_db, async_session_maker
from app.core.security import get_current_user
from app.models.user import User
from app.services.analytics import analytics_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardMetricsResponse(BaseModel):
    """Dashboard metrics response model"""
    monitor_overview: Dict[str, Any]
    ssl_health: Dict[str, Any]
    notifications: Dict[str, Any]
    uptime: Dict[str, Any]
    cost_savings: Dict[str, Any]
    trends: Dict[str, Any]
    generated_at: str
    period_days: int


class ROICalculatorRequest(BaseModel):
    """ROI calculator request model"""
    monthly_revenue: float = Field(..., description="Monthly revenue in EUR")
    avg_downtime_cost_per_hour: float = Field(default=1000, description="Average downtime cost per hour")
    expected_downtime_hours_per_month: float = Field(default=2, description="Expected downtime hours per month without monitoring")
    current_plan_cost: float = Field(..., description="Current plan cost per month")


class ROICalculatorResponse(BaseModel):
    """ROI calculator response model"""
    potential_monthly_loss: float
    monitoring_cost: float
    net_savings: float
    roi_percentage: float
    payback_period_months: float
    break_even_downtime_hours: float


@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard metrics for user"""
    try:
        metrics = await analytics_service.get_user_dashboard_metrics(
            user_id=current_user.id,
            days=days
        )
        
        if "error" in metrics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get dashboard metrics: {metrics['error']}"
            )
        
        return DashboardMetricsResponse(**metrics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard metrics"
        )


@router.get("/monitor-overview")
async def get_monitor_overview(
    current_user: User = Depends(get_current_user)
):
    """Get monitor overview metrics"""
    try:
        async with async_session_maker() as db:
            metrics = await analytics_service._get_monitor_metrics(db, current_user.id)
            
            if "error" in metrics:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get monitor metrics: {metrics['error']}"
                )
            
            return metrics
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitor overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitor overview"
        )


@router.get("/ssl-health")
async def get_ssl_health_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get SSL health metrics"""
    try:
        async with async_session_maker() as db:
            metrics = await analytics_service._get_ssl_health_metrics(db, current_user.id, days)
            
            if "error" in metrics:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get SSL health metrics: {metrics['error']}"
                )
            
            return metrics
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SSL health metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get SSL health metrics"
        )


@router.get("/notifications")
async def get_notification_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get notification metrics"""
    try:
        async with async_session_maker() as db:
            metrics = await analytics_service._get_notification_metrics(db, current_user.id, days)
            
            if "error" in metrics:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get notification metrics: {metrics['error']}"
                )
            
            return metrics
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification metrics"
        )


@router.get("/uptime")
async def get_uptime_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get uptime and availability metrics"""
    try:
        async with async_session_maker() as db:
            metrics = await analytics_service._get_uptime_metrics(db, current_user.id, days)
            
            if "error" in metrics:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get uptime metrics: {metrics['error']}"
                )
            
            return metrics
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting uptime metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get uptime metrics"
        )


@router.get("/cost-savings")
async def get_cost_savings_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get cost savings and ROI metrics"""
    try:
        async with async_session_maker() as db:
            metrics = await analytics_service._get_cost_savings_metrics(db, current_user.id, days)
            
            if "error" in metrics:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get cost savings metrics: {metrics['error']}"
                )
            
            return metrics
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cost savings metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cost savings metrics"
        )


@router.get("/trends")
async def get_trends_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get trends and insights"""
    try:
        async with async_session_maker() as db:
            metrics = await analytics_service._get_trends_metrics(db, current_user.id, days)
            
            if "error" in metrics:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get trends metrics: {metrics['error']}"
                )
            
            return metrics
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trends metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trends metrics"
        )


@router.post("/roi-calculator", response_model=ROICalculatorResponse)
async def calculate_roi(
    request: ROICalculatorRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate ROI for SSL monitoring investment"""
    try:
        # Calculate potential monthly loss without monitoring
        potential_monthly_loss = (
            request.avg_downtime_cost_per_hour * 
            request.expected_downtime_hours_per_month
        )
        
        # Net savings (potential loss - monitoring cost)
        net_savings = potential_monthly_loss - request.current_plan_cost
        
        # ROI percentage
        roi_percentage = (net_savings / request.current_plan_cost * 100) if request.current_plan_cost > 0 else 0
        
        # Payback period in months
        payback_period = request.current_plan_cost / potential_monthly_loss if potential_monthly_loss > 0 else 0
        
        # Break-even downtime hours
        break_even_hours = request.current_plan_cost / request.avg_downtime_cost_per_hour
        
        return ROICalculatorResponse(
            potential_monthly_loss=round(potential_monthly_loss, 2),
            monitoring_cost=request.current_plan_cost,
            net_savings=round(net_savings, 2),
            roi_percentage=round(roi_percentage, 1),
            payback_period_months=round(payback_period, 2),
            break_even_downtime_hours=round(break_even_hours, 2)
        )
        
    except Exception as e:
        logger.error(f"Error calculating ROI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate ROI"
        )


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user)
):
    """Get actionable insights and recommendations"""
    try:
        async with async_session_maker() as db:
            # Get trends for insights generation
            trends = await analytics_service._get_trends_metrics(db, current_user.id, 30)
            
            if "error" in trends:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get insights: {trends['error']}"
                )
            
            # Get monitor overview for additional insights
            monitor_overview = await analytics_service._get_monitor_metrics(db, current_user.id)
            
            insights = trends.get("insights", [])
            
            # Add monitor-specific insights
            if monitor_overview.get("expiring_soon", 0) > 0:
                insights.append(f"⚠️ {monitor_overview['expiring_soon']} certificates expiring soon - take action now")
            
            if monitor_overview.get("inactive_monitors", 0) > 0:
                insights.append(f"🔧 {monitor_overview['inactive_monitors']} inactive monitors - consider cleaning up")
            
            return {
                "insights": insights[:10],  # Return top 10 insights
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_insights": len(insights)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get insights"
        )


@router.get("/export")
async def export_analytics_data(
    format: str = Query(default="json", description="Export format: json, csv"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to export"),
    current_user: User = Depends(get_current_user)
):
    """Export analytics data"""
    try:
        metrics = await analytics_service.get_user_dashboard_metrics(
            user_id=current_user.id,
            days=days
        )
        
        if "error" in metrics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to export data: {metrics['error']}"
            )
        
        if format.lower() == "csv":
            # Convert to CSV format (simplified)
            csv_data = self._convert_to_csv(metrics)
            return {
                "data": csv_data,
                "format": "csv",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "filename": f"ssl_analytics_{current_user.id}_{days}days.csv"
            }
        else:
            # Return JSON format
            return {
                "data": metrics,
                "format": "json",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "filename": f"ssl_analytics_{current_user.id}_{days}days.json"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export analytics data"
        )


def _convert_to_csv(metrics: Dict[str, Any]) -> str:
    """Convert metrics to CSV format"""
    # Simplified CSV conversion - in production, use pandas or similar
    csv_lines = []
    
    # Add header
    csv_lines.append("metric,value,category")
    
    # Add monitor overview
    for key, value in metrics.get("monitor_overview", {}).items():
        if isinstance(value, (int, float, str)):
            csv_lines.append(f"{key},{value},monitor_overview")
    
    # Add SSL health
    for key, value in metrics.get("ssl_health", {}).items():
        if isinstance(value, (int, float, str)):
            csv_lines.append(f"{key},{value},ssl_health")
    
    return "\n".join(csv_lines)
