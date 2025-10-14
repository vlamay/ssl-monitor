"""
Advanced Analytics API for SSL Monitor Pro
Provides detailed analytics, charts data, and insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Pydantic models
class SSLTrendData(BaseModel):
    """SSL trend data model"""
    date: str
    healthy_domains: int
    warning_domains: int
    critical_domains: int
    expired_domains: int
    error_domains: int

class AlertAnalytics(BaseModel):
    """Alert analytics model"""
    alert_type: str
    count: int
    percentage: float
    trend: str  # 'up', 'down', 'stable'

class UserEngagement(BaseModel):
    """User engagement model"""
    metric: str
    value: int
    change_percent: float
    trend: str

class DomainAnalytics(BaseModel):
    """Domain analytics model"""
    total_domains: int
    active_domains: int
    average_days_until_expiry: float
    domains_expiring_soon: int
    domains_expired: int
    top_issuers: List[Dict[str, Any]]
    top_domains: List[Dict[str, Any]]

class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    metric: str
    value: float
    unit: str
    trend: str
    target: Optional[float] = None

class AnalyticsResponse(BaseModel):
    """Comprehensive analytics response"""
    period: str
    generated_at: datetime
    ssl_trends: List[SSLTrendData]
    alert_analytics: List[AlertAnalytics]
    user_engagement: List[UserEngagement]
    domain_analytics: DomainAnalytics
    performance_metrics: List[PerformanceMetrics]
    insights: List[str]

@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(
    period: str = Query("7d", description="Time period: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard analytics
    """
    try:
        # Parse period
        days = parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get SSL trends
        ssl_trends = await get_ssl_trends(start_date, db)
        
        # Get alert analytics
        alert_analytics = await get_alert_analytics(start_date, db)
        
        # Get user engagement
        user_engagement = await get_user_engagement(start_date, db)
        
        # Get domain analytics
        domain_analytics = await get_domain_analytics(db)
        
        # Get performance metrics
        performance_metrics = await get_performance_metrics(start_date, db)
        
        # Generate insights
        insights = generate_insights(ssl_trends, alert_analytics, user_engagement, domain_analytics)
        
        return AnalyticsResponse(
            period=period,
            generated_at=datetime.utcnow(),
            ssl_trends=ssl_trends,
            alert_analytics=alert_analytics,
            user_engagement=user_engagement,
            domain_analytics=domain_analytics,
            performance_metrics=performance_metrics,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.get("/ssl-trends", response_model=List[SSLTrendData])
async def get_ssl_trends_endpoint(
    period: str = Query("30d", description="Time period: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Get SSL certificate trends over time
    """
    try:
        days = parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        trends = await get_ssl_trends(start_date, db)
        return trends
        
    except Exception as e:
        logger.error(f"Error getting SSL trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SSL trends: {str(e)}"
        )

@router.get("/alerts", response_model=List[AlertAnalytics])
async def get_alert_analytics_endpoint(
    period: str = Query("30d", description="Time period: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Get alert analytics and statistics
    """
    try:
        days = parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        analytics = await get_alert_analytics(start_date, db)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting alert analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alert analytics: {str(e)}"
        )

@router.get("/domains", response_model=DomainAnalytics)
async def get_domain_analytics_endpoint(db: Session = Depends(get_db)):
    """
    Get domain analytics and statistics
    """
    try:
        analytics = await get_domain_analytics(db)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting domain analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get domain analytics: {str(e)}"
        )

@router.get("/performance", response_model=List[PerformanceMetrics])
async def get_performance_metrics_endpoint(
    period: str = Query("7d", description="Time period: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics
    """
    try:
        days = parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        metrics = await get_performance_metrics(start_date, db)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/insights")
async def get_insights(
    period: str = Query("30d", description="Time period: 1d, 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated insights and recommendations
    """
    try:
        days = parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get data for insights
        ssl_trends = await get_ssl_trends(start_date, db)
        alert_analytics = await get_alert_analytics(start_date, db)
        user_engagement = await get_user_engagement(start_date, db)
        domain_analytics = await get_domain_analytics(db)
        
        insights = generate_insights(ssl_trends, alert_analytics, user_engagement, domain_analytics)
        
        return {
            "period": period,
            "generated_at": datetime.utcnow(),
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )

@router.get("/export")
async def export_analytics(
    period: str = Query("30d", description="Time period: 1d, 7d, 30d, 90d"),
    format: str = Query("json", description="Export format: json, csv"),
    db: Session = Depends(get_db)
):
    """
    Export analytics data in various formats
    """
    try:
        days = parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all analytics data
        ssl_trends = await get_ssl_trends(start_date, db)
        alert_analytics = await get_alert_analytics(start_date, db)
        user_engagement = await get_user_engagement(start_date, db)
        domain_analytics = await get_domain_analytics(db)
        performance_metrics = await get_performance_metrics(start_date, db)
        
        if format.lower() == "csv":
            return export_to_csv(ssl_trends, alert_analytics, user_engagement, domain_analytics, performance_metrics)
        else:
            return {
                "period": period,
                "exported_at": datetime.utcnow(),
                "ssl_trends": ssl_trends,
                "alert_analytics": alert_analytics,
                "user_engagement": user_engagement,
                "domain_analytics": domain_analytics,
                "performance_metrics": performance_metrics
            }
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics: {str(e)}"
        )

# Helper functions
def parse_period(period: str) -> int:
    """Parse period string to days"""
    period_map = {
        "1d": 1,
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }
    return period_map.get(period, 30)

async def get_ssl_trends(start_date: datetime, db: Session) -> List[SSLTrendData]:
    """Get SSL certificate trends over time"""
    try:
        # This would query the actual database
        # For now, return mock data
        trends = []
        
        for i in range(30):  # Last 30 days
            date = start_date + timedelta(days=i)
            trends.append(SSLTrendData(
                date=date.strftime("%Y-%m-%d"),
                healthy_domains=50 + i % 10,
                warning_domains=5 + i % 3,
                critical_domains=2 + i % 2,
                expired_domains=1 if i % 7 == 0 else 0,
                error_domains=1 if i % 10 == 0 else 0
            ))
        
        return trends
        
    except Exception as e:
        logger.error(f"Error getting SSL trends: {e}")
        return []

async def get_alert_analytics(start_date: datetime, db: Session) -> List[AlertAnalytics]:
    """Get alert analytics"""
    try:
        # This would query the actual database
        # For now, return mock data
        return [
            AlertAnalytics(
                alert_type="SSL Warning",
                count=45,
                percentage=60.0,
                trend="stable"
            ),
            AlertAnalytics(
                alert_type="SSL Critical",
                count=15,
                percentage=20.0,
                trend="down"
            ),
            AlertAnalytics(
                alert_type="SSL Expired",
                count=5,
                percentage=6.7,
                trend="up"
            ),
            AlertAnalytics(
                alert_type="System Error",
                count=10,
                percentage=13.3,
                trend="stable"
            )
        ]
        
    except Exception as e:
        logger.error(f"Error getting alert analytics: {e}")
        return []

async def get_user_engagement(start_date: datetime, db: Session) -> List[UserEngagement]:
    """Get user engagement metrics"""
    try:
        # This would query the actual database
        # For now, return mock data
        return [
            UserEngagement(
                metric="Active Users",
                value=150,
                change_percent=12.5,
                trend="up"
            ),
            UserEngagement(
                metric="Notifications Sent",
                value=1250,
                change_percent=8.3,
                trend="up"
            ),
            UserEngagement(
                metric="Dashboard Views",
                value=890,
                change_percent=-2.1,
                trend="down"
            ),
            UserEngagement(
                metric="API Calls",
                value=4560,
                change_percent=15.7,
                trend="up"
            )
        ]
        
    except Exception as e:
        logger.error(f"Error getting user engagement: {e}")
        return []

async def get_domain_analytics(db: Session) -> DomainAnalytics:
    """Get domain analytics"""
    try:
        # This would query the actual database
        # For now, return mock data
        return DomainAnalytics(
            total_domains=200,
            active_domains=185,
            average_days_until_expiry=45.2,
            domains_expiring_soon=25,
            domains_expired=3,
            top_issuers=[
                {"name": "Let's Encrypt", "count": 120, "percentage": 60.0},
                {"name": "DigiCert", "count": 45, "percentage": 22.5},
                {"name": "Sectigo", "count": 20, "percentage": 10.0},
                {"name": "GoDaddy", "count": 15, "percentage": 7.5}
            ],
            top_domains=[
                {"domain": "example.com", "days_left": 89, "status": "healthy"},
                {"domain": "test.com", "days_left": 15, "status": "warning"},
                {"domain": "demo.com", "days_left": 3, "status": "critical"},
                {"domain": "sample.com", "days_left": 0, "status": "expired"}
            ]
        )
        
    except Exception as e:
        logger.error(f"Error getting domain analytics: {e}")
        return DomainAnalytics(
            total_domains=0,
            active_domains=0,
            average_days_until_expiry=0,
            domains_expiring_soon=0,
            domains_expired=0,
            top_issuers=[],
            top_domains=[]
        )

async def get_performance_metrics(start_date: datetime, db: Session) -> List[PerformanceMetrics]:
    """Get performance metrics"""
    try:
        # This would query the actual database
        # For now, return mock data
        return [
            PerformanceMetrics(
                metric="Average Response Time",
                value=245.5,
                unit="ms",
                trend="down",
                target=300.0
            ),
            PerformanceMetrics(
                metric="SSL Check Time",
                value=1.2,
                unit="s",
                trend="stable",
                target=2.0
            ),
            PerformanceMetrics(
                metric="Uptime",
                value=99.95,
                unit="%",
                trend="up",
                target=99.9
            ),
            PerformanceMetrics(
                metric="Error Rate",
                value=0.05,
                unit="%",
                trend="down",
                target=0.1
            )
        ]
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return []

def generate_insights(
    ssl_trends: List[SSLTrendData],
    alert_analytics: List[AlertAnalytics],
    user_engagement: List[UserEngagement],
    domain_analytics: DomainAnalytics
) -> List[str]:
    """Generate AI-powered insights"""
    insights = []
    
    # Analyze SSL trends
    if ssl_trends:
        recent_trends = ssl_trends[-7:]  # Last 7 days
        avg_healthy = sum(t.healthy_domains for t in recent_trends) / len(recent_trends)
        avg_expired = sum(t.expired_domains for t in recent_trends) / len(recent_trends)
        
        if avg_expired > 2:
            insights.append("⚠️ High number of expired certificates detected. Consider implementing automated renewal processes.")
        
        if avg_healthy > 80:
            insights.append("✅ Excellent SSL certificate health! Your domains are well-maintained.")
    
    # Analyze alert patterns
    warning_alerts = next((a for a in alert_analytics if a.alert_type == "SSL Warning"), None)
    if warning_alerts and warning_alerts.count > 50:
        insights.append("📈 High volume of warning alerts. Consider adjusting alert thresholds to reduce noise.")
    
    # Analyze domain analytics
    if domain_analytics.expired_domains > 0:
        insights.append(f"🚨 {domain_analytics.expired_domains} domains have expired certificates. Immediate action required.")
    
    if domain_analytics.domains_expiring_soon > 20:
        insights.append("⏰ Many domains expiring soon. Consider bulk certificate renewal.")
    
    # Analyze user engagement
    api_calls = next((u for u in user_engagement if u.metric == "API Calls"), None)
    if api_calls and api_calls.change_percent > 20:
        insights.append("📊 Significant increase in API usage. Consider scaling infrastructure.")
    
    # Default insights if none generated
    if not insights:
        insights.append("📊 All systems operating normally. No immediate actions required.")
        insights.append("💡 Consider setting up automated certificate renewal for better security.")
        insights.append("🔔 Review notification settings to ensure optimal alert frequency.")
    
    return insights

def export_to_csv(ssl_trends, alert_analytics, user_engagement, domain_analytics, performance_metrics):
    """Export data to CSV format"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write SSL trends
    writer.writerow(["SSL Trends"])
    writer.writerow(["Date", "Healthy", "Warning", "Critical", "Expired", "Error"])
    for trend in ssl_trends:
        writer.writerow([
            trend.date,
            trend.healthy_domains,
            trend.warning_domains,
            trend.critical_domains,
            trend.expired_domains,
            trend.error_domains
        ])
    
    # Write alert analytics
    writer.writerow([])
    writer.writerow(["Alert Analytics"])
    writer.writerow(["Type", "Count", "Percentage", "Trend"])
    for alert in alert_analytics:
        writer.writerow([alert.alert_type, alert.count, alert.percentage, alert.trend])
    
    return output.getvalue()
