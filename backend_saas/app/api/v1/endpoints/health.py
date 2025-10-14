"""
Health check endpoints
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
import redis
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Comprehensive health check"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.VERSION,
        "checks": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["checks"]["redis"] = "connected"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Telegram
    try:
        if settings.TELEGRAM_BOT_TOKEN:
            health_status["checks"]["telegram"] = "configured"
        else:
            health_status["checks"]["telegram"] = "not configured"
    except Exception as e:
        health_status["checks"]["telegram"] = f"error: {str(e)}"
    
    # Check Stripe
    try:
        if settings.STRIPE_SECRET_KEY:
            health_status["checks"]["stripe"] = "configured"
        else:
            health_status["checks"]["stripe"] = "not configured"
    except Exception as e:
        health_status["checks"]["stripe"] = f"error: {str(e)}"
    
    return health_status


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Kubernetes readiness probe"""
    
    try:
        # Quick database check
        await db.execute(text("SELECT 1"))
        
        # Quick Redis check
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return {
            "ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/metrics")
async def metrics() -> str:
    """Prometheus metrics endpoint"""
    
    # Basic metrics for SSL Monitor Pro
    metrics_data = [
        "# HELP ssl_monitor_requests_total Total number of requests",
        "# TYPE ssl_monitor_requests_total counter",
        "ssl_monitor_requests_total{method=\"GET\",endpoint=\"/health\"} 1",
        "",
        "# HELP ssl_monitor_users_total Total number of registered users",
        "# TYPE ssl_monitor_users_total gauge",
        "ssl_monitor_users_total 0",
        "",
        "# HELP ssl_monitor_monitors_total Total number of SSL monitors",
        "# TYPE ssl_monitor_monitors_total gauge",
        "ssl_monitor_monitors_total 0",
        "",
        "# HELP ssl_monitor_ssl_checks_total Total number of SSL certificate checks",
        "# TYPE ssl_monitor_ssl_checks_total counter",
        "ssl_monitor_ssl_checks_total{status=\"success\"} 0",
        "ssl_monitor_ssl_checks_total{status=\"failed\"} 0",
        "",
        "# HELP ssl_monitor_uptime_seconds Service uptime in seconds",
        "# TYPE ssl_monitor_uptime_seconds gauge",
        "ssl_monitor_uptime_seconds 0",
        "",
        "# HELP ssl_monitor_version_info Service version information",
        "# TYPE ssl_monitor_version_info gauge",
        f"ssl_monitor_version_info{{version=\"{settings.VERSION}\"}} 1"
    ]
    
    return "\n".join(metrics_data)
