"""
Periodic tasks for SSL Monitor Pro
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from celery import current_task
from app.tasks.celery_app import celery_app
from app.core.database import async_session_maker
from app.models.monitor import Monitor
from app.models.check_result import MonitorCheckResult
from app.models.user import User
from app.models.calendly import CalendlyEvent
from app.tasks.ssl_tasks import check_ssl_certificate
from app.tasks.notification_tasks import send_bulk_notifications
from sqlalchemy import select, delete, func
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def check_all_ssl_certificates() -> Dict[str, Any]:
    """
    Check SSL certificates for all active monitors that need checking
    
    Returns:
        Dict with check results summary
    """
    try:
        logger.info("Starting periodic SSL certificate checks")
        
        async with async_session_maker() as session:
            # Get monitors that need checking
            now = datetime.now(timezone.utc)
            result = await session.execute(
                select(Monitor).where(
                    Monitor.status == "active",
                    Monitor.last_checked_at.is_(None) | 
                    (Monitor.last_checked_at <= now - timedelta(seconds=Monitor.check_interval))
                ).limit(100)  # Process in batches
            )
            monitors = result.scalars().all()
            
            if not monitors:
                logger.info("No monitors need checking")
                return {"message": "No monitors need checking", "processed": 0}
            
            # Queue SSL checks
            task_ids = []
            for monitor in monitors:
                try:
                    task = check_ssl_certificate.delay(monitor.id)
                    task_ids.append({
                        "monitor_id": monitor.id,
                        "domain": monitor.domain,
                        "task_id": task.id
                    })
                except Exception as e:
                    logger.error(f"Failed to queue SSL check for monitor {monitor.id}: {e}")
            
            logger.info(f"Queued SSL checks for {len(task_ids)} monitors")
            return {
                "message": f"Queued SSL checks for {len(task_ids)} monitors",
                "processed": len(task_ids),
                "task_ids": task_ids
            }
            
    except Exception as exc:
        logger.error(f"Failed to check SSL certificates: {exc}")
        return {"error": str(exc)}


@celery_app.task
def send_weekly_reports() -> Dict[str, Any]:
    """
    Send weekly SSL monitoring reports to users
    
    Returns:
        Dict with report sending results
    """
    try:
        logger.info("Starting weekly reports generation")
        
        async with async_session_maker() as session:
            # Get all active users with monitors
            result = await session.execute(
                select(User).where(
                    User.is_active == True,
                    User.monitors.any()
                )
            )
            users = result.scalars().all()
            
            if not users:
                logger.info("No users found for weekly reports")
                return {"message": "No users found", "processed": 0}
            
            # Generate reports for each user
            reports_sent = 0
            for user in users:
                try:
                    # Get user's monitors and their stats
                    monitors_result = await session.execute(
                        select(Monitor).where(Monitor.user_id == user.id)
                    )
                    monitors = monitors_result.scalars().all()
                    
                    if not monitors:
                        continue
                    
                    # Calculate stats
                    total_monitors = len(monitors)
                    active_monitors = len([m for m in monitors if m.status == "active"])
                    expired_certs = len([m for m in monitors if m.ssl_status == "expired"])
                    expiring_soon = len([m for m in monitors if m.ssl_status == "expiring_soon"])
                    
                    # Get recent check results
                    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                    checks_result = await session.execute(
                        select(MonitorCheckResult).join(Monitor).where(
                            Monitor.user_id == user.id,
                            MonitorCheckResult.checked_at >= week_ago
                        )
                    )
                    recent_checks = checks_result.scalars().all()
                    
                    # Calculate uptime
                    successful_checks = len([c for c in recent_checks if c.success])
                    total_checks = len(recent_checks)
                    uptime = (successful_checks / total_checks * 100) if total_checks > 0 else 100
                    
                    # Prepare report data
                    report_data = {
                        "user_id": user.id,
                        "total_monitors": total_monitors,
                        "active_monitors": active_monitors,
                        "expired_certificates": expired_certs,
                        "expiring_soon": expiring_soon,
                        "total_checks_this_week": total_checks,
                        "successful_checks": successful_checks,
                        "uptime_percentage": round(uptime, 2),
                        "report_period": "7 days",
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Send report notification
                    # TODO: Implement email report sending
                    logger.info(f"Weekly report generated for user {user.id}: {report_data}")
                    reports_sent += 1
                    
                except Exception as e:
                    logger.error(f"Failed to generate report for user {user.id}: {e}")
            
            logger.info(f"Weekly reports sent to {reports_sent} users")
            return {
                "message": f"Weekly reports sent to {reports_sent} users",
                "processed": reports_sent,
                "total_users": len(users)
            }
            
    except Exception as exc:
        logger.error(f"Failed to send weekly reports: {exc}")
        return {"error": str(exc)}


@celery_app.task
def cleanup_old_check_results() -> Dict[str, Any]:
    """
    Clean up old check results to keep database size manageable
    
    Returns:
        Dict with cleanup results
    """
    try:
        logger.info("Starting cleanup of old check results")
        
        async with async_session_maker() as session:
            # Delete check results older than 90 days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            
            result = await session.execute(
                select(func.count(MonitorCheckResult.id)).where(
                    MonitorCheckResult.checked_at < cutoff_date
                )
            )
            old_results_count = result.scalar()
            
            if old_results_count == 0:
                logger.info("No old check results to clean up")
                return {"message": "No old results found", "deleted": 0}
            
            # Delete old results
            delete_result = await session.execute(
                delete(MonitorCheckResult).where(
                    MonitorCheckResult.checked_at < cutoff_date
                )
            )
            
            await session.commit()
            
            deleted_count = delete_result.rowcount
            logger.info(f"Cleaned up {deleted_count} old check results")
            
            return {
                "message": f"Cleaned up {deleted_count} old check results",
                "deleted": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
    except Exception as exc:
        logger.error(f"Failed to cleanup old check results: {exc}")
        return {"error": str(exc)}


@celery_app.task
def sync_calendly_events() -> Dict[str, Any]:
    """
    Sync Calendly events from the API
    
    Returns:
        Dict with sync results
    """
    try:
        logger.info("Starting Calendly events sync")
        
        # TODO: Implement Calendly API integration
        # For now, just log that the task ran
        logger.info("Calendly sync task completed (not implemented yet)")
        
        return {
            "message": "Calendly sync completed (not implemented yet)",
            "processed": 0
        }
        
    except Exception as exc:
        logger.error(f"Failed to sync Calendly events: {exc}")
        return {"error": str(exc)}


@celery_app.task
def update_monitor_statistics() -> Dict[str, Any]:
    """
    Update monitor statistics and uptime calculations
    
    Returns:
        Dict with update results
    """
    try:
        logger.info("Starting monitor statistics update")
        
        async with async_session_maker() as session:
            # Get all active monitors
            result = await session.execute(
                select(Monitor).where(Monitor.status == "active")
            )
            monitors = result.scalars().all()
            
            updated_count = 0
            for monitor in monitors:
                try:
                    # Calculate uptime for the last 24 hours
                    day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
                    
                    checks_result = await session.execute(
                        select(MonitorCheckResult).where(
                            MonitorCheckResult.monitor_id == monitor.id,
                            MonitorCheckResult.checked_at >= day_ago
                        )
                    )
                    recent_checks = checks_result.scalars().all()
                    
                    if recent_checks:
                        successful_checks = len([c for c in recent_checks if c.success])
                        uptime = (successful_checks / len(recent_checks)) * 100
                        
                        # Update monitor uptime
                        monitor.uptime_percentage = round(uptime, 2)
                        updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to update statistics for monitor {monitor.id}: {e}")
            
            await session.commit()
            
            logger.info(f"Updated statistics for {updated_count} monitors")
            return {
                "message": f"Updated statistics for {updated_count} monitors",
                "updated": updated_count,
                "total_monitors": len(monitors)
            }
            
    except Exception as exc:
        logger.error(f"Failed to update monitor statistics: {exc}")
        return {"error": str(exc)}


@celery_app.task
def health_check_task() -> Dict[str, Any]:
    """
    Health check task to monitor system status
    
    Returns:
        Dict with health check results
    """
    try:
        logger.info("Running health check task")
        
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Check database connection
        try:
            async with async_session_maker() as session:
                await session.execute(select(1))
                health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Redis connection
        try:
            import redis
            from app.core.config import settings
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["checks"]["redis"] = "healthy"
        except Exception as e:
            health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Celery workers
        try:
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            if active_workers:
                health_status["checks"]["celery_workers"] = f"healthy ({len(active_workers)} workers)"
            else:
                health_status["checks"]["celery_workers"] = "unhealthy: no workers"
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["checks"]["celery_workers"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        logger.info(f"Health check completed: {health_status['status']}")
        return health_status
        
    except Exception as exc:
        logger.error(f"Health check task failed: {exc}")
        return {"error": str(exc), "status": "unhealthy"}
