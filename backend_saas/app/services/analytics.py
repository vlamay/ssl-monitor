"""
Analytics Service for SSL Monitor Pro
Provides comprehensive analytics and metrics for user dashboard
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import logging

from app.core.database import async_session_maker
from app.models.monitor import Monitor
from app.models.notification import Notification, NotificationLog
from app.models.check_result import CheckResult
from app.models.user import User
from app.models.subscription import Subscription

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Analytics service for dashboard metrics and insights"""
    
    def __init__(self):
        pass
    
    async def get_user_dashboard_metrics(
        self, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics for user
        
        Args:
            user_id: User ID
            days: Number of days to analyze (default 30)
        
        Returns:
            Dictionary with all dashboard metrics
        """
        async with async_session_maker() as db:
            try:
                # Get all metrics in parallel
                metrics_tasks = [
                    self._get_monitor_metrics(db, user_id),
                    self._get_ssl_health_metrics(db, user_id, days),
                    self._get_notification_metrics(db, user_id, days),
                    self._get_uptime_metrics(db, user_id, days),
                    self._get_cost_savings_metrics(db, user_id, days),
                    self._get_trends_metrics(db, user_id, days)
                ]
                
                results = await asyncio.gather(*metrics_tasks)
                
                return {
                    "monitor_overview": results[0],
                    "ssl_health": results[1],
                    "notifications": results[2],
                    "uptime": results[3],
                    "cost_savings": results[4],
                    "trends": results[5],
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "period_days": days
                }
                
            except Exception as e:
                logger.error(f"Error getting dashboard metrics: {e}")
                return {"error": str(e)}
    
    async def _get_monitor_metrics(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get monitor overview metrics"""
        try:
            # Total monitors
            total_monitors_query = select(func.count(Monitor.id)).where(
                Monitor.user_id == user_id
            )
            total_monitors = await db.scalar(total_monitors_query)
            
            # Active monitors
            active_monitors_query = select(func.count(Monitor.id)).where(
                and_(Monitor.user_id == user_id, Monitor.is_active == True)
            )
            active_monitors = await db.scalar(active_monitors_query)
            
            # Monitors by status
            status_query = select(
                Monitor.last_status,
                func.count(Monitor.id).label('count')
            ).where(
                and_(Monitor.user_id == user_id, Monitor.is_active == True)
            ).group_by(Monitor.last_status)
            
            status_results = await db.execute(status_query)
            status_breakdown = {row.last_status: row.count for row in status_results}
            
            # Monitors expiring soon
            expiring_soon_query = select(func.count(Monitor.id)).where(
                and_(
                    Monitor.user_id == user_id,
                    Monitor.is_active == True,
                    Monitor.expires_at <= datetime.now(timezone.utc) + timedelta(days=30),
                    Monitor.expires_at > datetime.now(timezone.utc)
                )
            )
            expiring_soon = await db.scalar(expiring_soon_query)
            
            # Recently added monitors (last 7 days)
            recent_monitors_query = select(func.count(Monitor.id)).where(
                and_(
                    Monitor.user_id == user_id,
                    Monitor.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
                )
            )
            recent_monitors = await db.scalar(recent_monitors_query)
            
            return {
                "total_monitors": total_monitors or 0,
                "active_monitors": active_monitors or 0,
                "status_breakdown": status_breakdown,
                "expiring_soon": expiring_soon or 0,
                "recent_monitors": recent_monitors or 0,
                "inactive_monitors": (total_monitors or 0) - (active_monitors or 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting monitor metrics: {e}")
            return {"error": str(e)}
    
    async def _get_ssl_health_metrics(self, db: AsyncSession, user_id: int, days: int) -> Dict[str, Any]:
        """Get SSL health metrics"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # SSL certificate health distribution
            health_query = select(
                Monitor.last_status,
                func.count(Monitor.id).label('count'),
                func.avg(
                    func.extract('epoch', Monitor.expires_at - datetime.now(timezone.utc)) / 86400
                ).label('avg_days_remaining')
            ).where(
                and_(Monitor.user_id == user_id, Monitor.is_active == True)
            ).group_by(Monitor.last_status)
            
            health_results = await db.execute(health_query)
            health_breakdown = {}
            total_days_remaining = 0
            total_certificates = 0
            
            for row in health_results:
                health_breakdown[row.last_status] = {
                    'count': row.count,
                    'avg_days_remaining': round(row.avg_days_remaining, 1) if row.avg_days_remaining else 0
                }
                total_days_remaining += row.avg_days_remaining * row.count
                total_certificates += row.count
            
            avg_days_remaining = total_days_remaining / total_certificates if total_certificates > 0 else 0
            
            # Certificate expiration timeline
            timeline_query = select(
                func.date_trunc('week', Monitor.expires_at).label('week'),
                func.count(Monitor.id).label('expiring_count')
            ).where(
                and_(
                    Monitor.user_id == user_id,
                    Monitor.is_active == True,
                    Monitor.expires_at >= datetime.now(timezone.utc),
                    Monitor.expires_at <= datetime.now(timezone.utc) + timedelta(days=90)
                )
            ).group_by(func.date_trunc('week', Monitor.expires_at)).order_by('week')
            
            timeline_results = await db.execute(timeline_query)
            expiration_timeline = [
                {
                    'week': row.week.isoformat(),
                    'expiring_count': row.expiring_count
                }
                for row in timeline_results
            ]
            
            # SSL grade distribution (if available)
            grade_distribution = {
                'A+': 0,
                'A': 0,
                'B': 0,
                'C': 0,
                'D': 0,
                'F': 0,
                'Unknown': 0
            }
            
            return {
                "health_breakdown": health_breakdown,
                "avg_days_remaining": round(avg_days_remaining, 1),
                "expiration_timeline": expiration_timeline,
                "grade_distribution": grade_distribution,
                "total_certificates": total_certificates,
                "healthy_certificates": health_breakdown.get('valid', {}).get('count', 0),
                "expired_certificates": health_breakdown.get('expired', {}).get('count', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting SSL health metrics: {e}")
            return {"error": str(e)}
    
    async def _get_notification_metrics(self, db: AsyncSession, user_id: int, days: int) -> Dict[str, Any]:
        """Get notification metrics"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Total notifications sent
            total_notifications_query = select(func.count(NotificationLog.id)).where(
                and_(
                    NotificationLog.created_at >= start_date,
                    NotificationLog.notification.has(user_id=user_id)
                )
            )
            total_notifications = await db.scalar(total_notifications_query)
            
            # Notifications by type
            type_query = select(
                Notification.type,
                func.count(NotificationLog.id).label('count')
            ).join(Notification).where(
                and_(
                    NotificationLog.created_at >= start_date,
                    Notification.user_id == user_id
                )
            ).group_by(Notification.type)
            
            type_results = await db.execute(type_query)
            notification_types = {row.type.value: row.count for row in type_results}
            
            # Notification success rate
            success_query = select(
                NotificationLog.status,
                func.count(NotificationLog.id).label('count')
            ).where(
                and_(
                    NotificationLog.created_at >= start_date,
                    NotificationLog.notification.has(user_id=user_id)
                )
            ).group_by(NotificationLog.status)
            
            success_results = await db.execute(success_query)
            success_breakdown = {row.status: row.count for row in success_results}
            
            total_sent = sum(success_breakdown.values())
            successful_sent = success_breakdown.get('sent', 0)
            success_rate = (successful_sent / total_sent * 100) if total_sent > 0 else 0
            
            # Recent notification activity
            recent_query = select(
                func.date_trunc('day', NotificationLog.created_at).label('day'),
                func.count(NotificationLog.id).label('count')
            ).where(
                and_(
                    NotificationLog.created_at >= start_date,
                    NotificationLog.notification.has(user_id=user_id)
                )
            ).group_by(func.date_trunc('day', NotificationLog.created_at)).order_by('day')
            
            recent_results = await db.execute(recent_query)
            recent_activity = [
                {
                    'day': row.day.isoformat(),
                    'count': row.count
                }
                for row in recent_results
            ]
            
            return {
                "total_notifications": total_notifications or 0,
                "notification_types": notification_types,
                "success_rate": round(success_rate, 1),
                "success_breakdown": success_breakdown,
                "recent_activity": recent_activity,
                "avg_daily_notifications": round((total_notifications or 0) / days, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting notification metrics: {e}")
            return {"error": str(e)}
    
    async def _get_uptime_metrics(self, db: AsyncSession, user_id: int, days: int) -> Dict[str, Any]:
        """Get uptime and availability metrics"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Check results for uptime calculation
            check_query = select(
                CheckResult.status,
                func.count(CheckResult.id).label('count')
            ).where(
                and_(
                    CheckResult.checked_at >= start_date,
                    CheckResult.monitor.has(user_id=user_id)
                )
            ).group_by(CheckResult.status)
            
            check_results = await db.execute(check_query)
            status_breakdown = {row.status: row.count for row in check_results}
            
            total_checks = sum(status_breakdown.values())
            successful_checks = status_breakdown.get('valid', 0)
            uptime_percentage = (successful_checks / total_checks * 100) if total_checks > 0 else 0
            
            # Uptime by day
            daily_query = select(
                func.date_trunc('day', CheckResult.checked_at).label('day'),
                func.count(CheckResult.id).label('total_checks'),
                func.count(CheckResult.id).filter(CheckResult.status == 'valid').label('successful_checks')
            ).where(
                and_(
                    CheckResult.checked_at >= start_date,
                    CheckResult.monitor.has(user_id=user_id)
                )
            ).group_by(func.date_trunc('day', CheckResult.checked_at)).order_by('day')
            
            daily_results = await db.execute(daily_query)
            daily_uptime = []
            
            for row in daily_results:
                daily_percentage = (row.successful_checks / row.total_checks * 100) if row.total_checks > 0 else 0
                daily_uptime.append({
                    'day': row.day.isoformat(),
                    'uptime_percentage': round(daily_percentage, 2),
                    'total_checks': row.total_checks,
                    'successful_checks': row.successful_checks
                })
            
            return {
                "overall_uptime": round(uptime_percentage, 2),
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "failed_checks": total_checks - successful_checks,
                "daily_uptime": daily_uptime,
                "status_breakdown": status_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error getting uptime metrics: {e}")
            return {"error": str(e)}
    
    async def _get_cost_savings_metrics(self, db: AsyncSession, user_id: int, days: int) -> Dict[str, Any]:
        """Get cost savings and ROI metrics"""
        try:
            # Get user subscription info
            subscription_query = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == 'active'
                )
            )
            subscription_result = await db.execute(subscription_query)
            subscription = subscription_result.scalar_one_or_none()
            
            # Calculate potential downtime cost savings
            # Assume average downtime cost is €1000/hour for business
            avg_downtime_cost_per_hour = 1000  # EUR
            
            # Get failed checks (potential downtime events)
            failed_checks_query = select(func.count(CheckResult.id)).where(
                and_(
                    CheckResult.checked_at >= datetime.now(timezone.utc) - timedelta(days=days),
                    CheckResult.status != 'valid',
                    CheckResult.monitor.has(user_id=user_id)
                )
            )
            failed_checks = await db.scalar(failed_checks_query) or 0
            
            # Estimate downtime prevented (assuming 1 hour per failure)
            downtime_hours_prevented = failed_checks
            cost_savings = downtime_hours_prevented * avg_downtime_cost_per_hour
            
            # Calculate ROI
            monthly_cost = 0
            if subscription:
                if subscription.stripe_price_id == 'price_starter':
                    monthly_cost = 29  # EUR
                elif subscription.stripe_price_id == 'price_pro':
                    monthly_cost = 59  # EUR
            
            roi_percentage = ((cost_savings - monthly_cost) / monthly_cost * 100) if monthly_cost > 0 else 0
            
            # SSL certificate renewal savings
            # Assume manual renewal costs €50 per certificate
            manual_renewal_cost = 50
            total_monitors_query = select(func.count(Monitor.id)).where(
                and_(Monitor.user_id == user_id, Monitor.is_active == True)
            )
            total_monitors = await db.scalar(total_monitors_query) or 0
            renewal_savings = total_monitors * manual_renewal_cost
            
            return {
                "downtime_hours_prevented": downtime_hours_prevented,
                "cost_savings": cost_savings,
                "monthly_cost": monthly_cost,
                "roi_percentage": round(roi_percentage, 1),
                "renewal_savings": renewal_savings,
                "total_savings": cost_savings + renewal_savings,
                "avg_downtime_cost_per_hour": avg_downtime_cost_per_hour,
                "manual_renewal_cost_per_cert": manual_renewal_cost
            }
            
        except Exception as e:
            logger.error(f"Error getting cost savings metrics: {e}")
            return {"error": str(e)}
    
    async def _get_trends_metrics(self, db: AsyncSession, user_id: int, days: int) -> Dict[str, Any]:
        """Get trends and insights"""
        try:
            # Monitor growth trend
            growth_query = select(
                func.date_trunc('week', Monitor.created_at).label('week'),
                func.count(Monitor.id).label('new_monitors')
            ).where(
                and_(
                    Monitor.user_id == user_id,
                    Monitor.created_at >= datetime.now(timezone.utc) - timedelta(days=days)
                )
            ).group_by(func.date_trunc('week', Monitor.created_at)).order_by('week')
            
            growth_results = await db.execute(growth_query)
            growth_trend = [
                {
                    'week': row.week.isoformat(),
                    'new_monitors': row.new_monitors
                }
                for row in growth_results
            ]
            
            # Notification trend
            notification_trend_query = select(
                func.date_trunc('week', NotificationLog.created_at).label('week'),
                func.count(NotificationLog.id).label('notifications')
            ).where(
                and_(
                    NotificationLog.created_at >= datetime.now(timezone.utc) - timedelta(days=days),
                    NotificationLog.notification.has(user_id=user_id)
                )
            ).group_by(func.date_trunc('week', NotificationLog.created_at)).order_by('week')
            
            notification_trend_results = await db.execute(notification_trend_query)
            notification_trend = [
                {
                    'week': row.week.isoformat(),
                    'notifications': row.notifications
                }
                for row in notification_trend_results
            ]
            
            return {
                "growth_trend": growth_trend,
                "notification_trend": notification_trend,
                "insights": self._generate_insights(growth_trend, notification_trend)
            }
            
        except Exception as e:
            logger.error(f"Error getting trends metrics: {e}")
            return {"error": str(e)}
    
    def _generate_insights(self, growth_trend: List[Dict], notification_trend: List[Dict]) -> List[str]:
        """Generate actionable insights from trends"""
        insights = []
        
        # Growth insights
        if len(growth_trend) >= 2:
            recent_growth = growth_trend[-1]['new_monitors'] if growth_trend else 0
            previous_growth = growth_trend[-2]['new_monitors'] if len(growth_trend) >= 2 else 0
            
            if recent_growth > previous_growth:
                insights.append(f"📈 Monitor growth increased by {recent_growth - previous_growth} this week")
            elif recent_growth < previous_growth:
                insights.append(f"📉 Monitor growth decreased by {previous_growth - recent_growth} this week")
        
        # Notification insights
        if len(notification_trend) >= 2:
            recent_notifications = notification_trend[-1]['notifications'] if notification_trend else 0
            if recent_notifications > 10:
                insights.append("🔔 High notification volume detected - consider reviewing alert thresholds")
        
        # General insights
        insights.extend([
            "💡 Consider setting up automated SSL certificate renewal",
            "📊 Review SSL health metrics weekly to prevent issues",
            "🚀 Upgrade to Pro plan for advanced analytics and API access"
        ])
        
        return insights[:5]  # Return top 5 insights


# Global analytics service instance
analytics_service = AnalyticsService()
