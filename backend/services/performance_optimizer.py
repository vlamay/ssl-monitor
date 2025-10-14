"""
Performance Optimization Service for SSL Monitor Pro
Implements caching, query optimization, and performance monitoring
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
import asyncio

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization service with caching and monitoring"""
    
    def __init__(self, db_session: Session = None, redis_client: redis.Redis = None):
        self.db = db_session
        self.redis = redis_client or self._get_redis_client()
        
        # Cache TTL settings (in seconds)
        self.cache_ttl = {
            'ssl_status': 300,      # 5 minutes
            'domain_list': 60,      # 1 minute
            'statistics': 300,      # 5 minutes
            'user_preferences': 3600,  # 1 hour
            'analytics': 900,       # 15 minutes
            'health_check': 30,     # 30 seconds
            'api_response': 60      # 1 minute
        }
        
        # Performance monitoring
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'db_queries': 0,
            'db_query_time': 0,
            'api_requests': 0,
            'api_response_time': 0
        }
    
    def _get_redis_client(self) -> redis.Redis:
        """Get Redis client"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            return redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            return None
    
    def cache_key(self, prefix: str, *args) -> str:
        """Generate cache key"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    async def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.redis:
                return None
            
            value = self.redis.get(key)
            if value:
                self.metrics['cache_hits'] += 1
                return json.loads(value)
            else:
                self.metrics['cache_misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if not self.redis:
                return False
            
            serialized = json.dumps(value, default=str)
            if ttl:
                return bool(self.redis.setex(key, ttl, serialized))
            else:
                return bool(self.redis.set(key, serialized))
                
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete_cache(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if not self.redis:
                return False
            
            return bool(self.redis.delete(key))
            
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def cached(self, cache_type: str, ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache_key(cache_type, *args, *kwargs.values())
                
                # Try to get from cache
                cached_result = await self.get_from_cache(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                cache_ttl = ttl or self.cache_ttl.get(cache_type, 300)
                await self.set_cache(cache_key, result, cache_ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def monitor_performance(self, operation_type: str):
        """Decorator for monitoring function performance"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    execution_time = time.time() - start_time
                    
                    # Update metrics
                    if operation_type == 'db_query':
                        self.metrics['db_queries'] += 1
                        self.metrics['db_query_time'] += execution_time
                    elif operation_type == 'api_request':
                        self.metrics['api_requests'] += 1
                        self.metrics['api_response_time'] += execution_time
                    
                    # Log slow operations
                    if execution_time > 1.0:  # More than 1 second
                        logger.warning(f"Slow {operation_type}: {func.__name__} took {execution_time:.2f}s")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Error in {operation_type} {func.__name__}: {e} (took {execution_time:.2f}s)")
                    raise
            
            return wrapper
        return decorator
    
    @monitor_performance('db_query')
    async def get_domain_ssl_status(self, domain_id: int) -> Optional[Dict[str, Any]]:
        """Get SSL status for domain with caching"""
        cache_key = self.cache_key('ssl_status', domain_id)
        
        # Try cache first
        cached_result = await self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Query database
        if not self.db:
            return None
        
        try:
            query = text("""
                SELECT d.name, sc.expires_in, sc.is_valid, sc.checked_at, 
                       sc.issuer, sc.subject, sc.not_valid_after
                FROM domains d
                LEFT JOIN (
                    SELECT DISTINCT ON (domain_id) 
                        domain_id, expires_in, is_valid, checked_at, issuer, subject, not_valid_after
                    FROM ssl_checks 
                    ORDER BY domain_id, checked_at DESC
                ) sc ON sc.domain_id = d.id
                WHERE d.id = :domain_id
            """)
            
            result = self.db.execute(query, {"domain_id": domain_id}).fetchone()
            
            if result:
                ssl_status = {
                    "domain_name": result.name,
                    "expires_in": result.expires_in,
                    "is_valid": result.is_valid,
                    "checked_at": result.checked_at.isoformat() if result.checked_at else None,
                    "issuer": result.issuer,
                    "subject": result.subject,
                    "not_valid_after": result.not_valid_after.isoformat() if result.not_valid_after else None
                }
                
                # Cache result
                await self.set_cache(cache_key, ssl_status, self.cache_ttl['ssl_status'])
                
                return ssl_status
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting SSL status: {e}")
            return None
    
    @monitor_performance('db_query')
    async def get_domain_list(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get domain list with caching"""
        cache_key = self.cache_key('domain_list', user_id, limit)
        
        # Try cache first
        cached_result = await self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Query database
        if not self.db:
            return []
        
        try:
            query = text("""
                SELECT d.id, d.name, d.is_active, d.alert_threshold_days, d.created_at,
                       sc.expires_in, sc.is_valid, sc.checked_at
                FROM domains d
                LEFT JOIN (
                    SELECT DISTINCT ON (domain_id) 
                        domain_id, expires_in, is_valid, checked_at
                    FROM ssl_checks 
                    ORDER BY domain_id, checked_at DESC
                ) sc ON sc.domain_id = d.id
                ORDER BY d.created_at DESC
                LIMIT :limit
            """)
            
            results = self.db.execute(query, {"limit": limit}).fetchall()
            
            domains = []
            for result in results:
                domains.append({
                    "id": result.id,
                    "name": result.name,
                    "is_active": result.is_active,
                    "alert_threshold_days": result.alert_threshold_days,
                    "created_at": result.created_at.isoformat(),
                    "ssl_status": {
                        "expires_in": result.expires_in,
                        "is_valid": result.is_valid,
                        "checked_at": result.checked_at.isoformat() if result.checked_at else None
                    }
                })
            
            # Cache result
            await self.set_cache(cache_key, domains, self.cache_ttl['domain_list'])
            
            return domains
            
        except Exception as e:
            logger.error(f"Error getting domain list: {e}")
            return []
    
    @monitor_performance('db_query')
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics with caching"""
        cache_key = self.cache_key('statistics')
        
        # Try cache first
        cached_result = await self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Query database
        if not self.db:
            return {}
        
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_domains,
                    COUNT(CASE WHEN is_active = true THEN 1 END) as active_domains,
                    COUNT(CASE WHEN sc.is_valid = false THEN 1 END) as domains_with_errors,
                    COUNT(CASE WHEN sc.expires_in <= 30 AND sc.expires_in > 0 THEN 1 END) as domains_expiring_soon,
                    COUNT(CASE WHEN sc.expires_in <= 0 THEN 1 END) as domains_expired
                FROM domains d
                LEFT JOIN (
                    SELECT DISTINCT ON (domain_id) 
                        domain_id, expires_in, is_valid
                    FROM ssl_checks 
                    ORDER BY domain_id, checked_at DESC
                ) sc ON sc.domain_id = d.id
            """)
            
            result = self.db.execute(query).fetchone()
            
            statistics = {
                "total_domains": result.total_domains or 0,
                "active_domains": result.active_domains or 0,
                "domains_with_errors": result.domains_with_errors or 0,
                "domains_expiring_soon": result.domains_expiring_soon or 0,
                "domains_expired": result.domains_expired or 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache result
            await self.set_cache(cache_key, statistics, self.cache_ttl['statistics'])
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    @monitor_performance('db_query')
    async def get_analytics_data(self, period: str = '30d') -> Dict[str, Any]:
        """Get analytics data with caching"""
        cache_key = self.cache_key('analytics', period)
        
        # Try cache first
        cached_result = await self.get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Query database for analytics
        if not self.db:
            return {}
        
        try:
            # Parse period
            days = self._parse_period(period)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get SSL trends
            query = text("""
                SELECT DATE(checked_at) as date,
                       COUNT(CASE WHEN is_valid = true AND expires_in > 30 THEN 1 END) as healthy,
                       COUNT(CASE WHEN is_valid = true AND expires_in <= 30 AND expires_in > 7 THEN 1 END) as warning,
                       COUNT(CASE WHEN is_valid = true AND expires_in <= 7 AND expires_in > 0 THEN 1 END) as critical,
                       COUNT(CASE WHEN expires_in <= 0 THEN 1 END) as expired
                FROM ssl_checks
                WHERE checked_at >= :start_date
                GROUP BY DATE(checked_at)
                ORDER BY date
            """)
            
            results = self.db.execute(query, {"start_date": start_date}).fetchall()
            
            ssl_trends = []
            for result in results:
                ssl_trends.append({
                    "date": result.date.isoformat(),
                    "healthy_domains": result.healthy,
                    "warning_domains": result.warning,
                    "critical_domains": result.critical,
                    "expired_domains": result.expired,
                    "error_domains": 0
                })
            
            analytics_data = {
                "ssl_trends": ssl_trends,
                "period": period,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache result
            await self.set_cache(cache_key, analytics_data, self.cache_ttl['analytics'])
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            return {}
    
    def _parse_period(self, period: str) -> int:
        """Parse period string to days"""
        period_map = {
            '1d': 1,
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        return period_map.get(period, 30)
    
    async def invalidate_cache(self, cache_pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        try:
            if not self.redis:
                return 0
            
            keys = self.redis.keys(cache_pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not self.redis:
                return {"status": "disabled"}
            
            info = self.redis.info()
            
            return {
                "status": "enabled",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "total_keys": info.get("db0", {}).get("keys", 0),
                "uptime": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            # Get cache stats
            cache_stats = await self.get_cache_stats()
            
            # Calculate averages
            avg_db_query_time = 0
            if self.metrics['db_queries'] > 0:
                avg_db_query_time = self.metrics['db_query_time'] / self.metrics['db_queries']
            
            avg_api_response_time = 0
            if self.metrics['api_requests'] > 0:
                avg_api_response_time = self.metrics['api_response_time'] / self.metrics['api_requests']
            
            return {
                "cache_stats": cache_stats,
                "db_metrics": {
                    "total_queries": self.metrics['db_queries'],
                    "total_query_time": self.metrics['db_query_time'],
                    "average_query_time": avg_db_query_time
                },
                "api_metrics": {
                    "total_requests": self.metrics['api_requests'],
                    "total_response_time": self.metrics['api_response_time'],
                    "average_response_time": avg_api_response_time
                },
                "cache_metrics": {
                    "cache_hits": self.metrics['cache_hits'],
                    "cache_misses": self.metrics['cache_misses'],
                    "hit_rate": self._calculate_cache_hit_rate()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate from metrics"""
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total == 0:
            return 0.0
        return (self.metrics['cache_hits'] / total) * 100
    
    async def optimize_database_queries(self) -> Dict[str, Any]:
        """Optimize database queries"""
        try:
            if not self.db:
                return {"status": "no_database"}
            
            optimizations = []
            
            # Check for missing indexes
            missing_indexes = await self._check_missing_indexes()
            if missing_indexes:
                optimizations.extend(missing_indexes)
            
            # Check for slow queries
            slow_queries = await self._check_slow_queries()
            if slow_queries:
                optimizations.extend(slow_queries)
            
            return {
                "status": "completed",
                "optimizations": optimizations,
                "recommendations": self._get_optimization_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _check_missing_indexes(self) -> List[Dict[str, Any]]:
        """Check for missing indexes"""
        optimizations = []
        
        try:
            # Check ssl_checks table indexes
            query = text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'ssl_checks' 
                AND indexname LIKE '%domain_id%'
            """)
            result = self.db.execute(query).fetchone()
            
            if not result:
                optimizations.append({
                    "type": "missing_index",
                    "table": "ssl_checks",
                    "column": "domain_id",
                    "recommendation": "CREATE INDEX idx_ssl_checks_domain_id ON ssl_checks(domain_id);"
                })
            
        except Exception as e:
            logger.error(f"Error checking indexes: {e}")
        
        return optimizations
    
    async def _check_slow_queries(self) -> List[Dict[str, Any]]:
        """Check for slow queries"""
        optimizations = []
        
        try:
            # This would check PostgreSQL's pg_stat_statements
            # For now, return empty list
            pass
            
        except Exception as e:
            logger.error(f"Error checking slow queries: {e}")
        
        return optimizations
    
    def _get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        return [
            "Consider adding indexes on frequently queried columns",
            "Use connection pooling to reduce connection overhead",
            "Implement query result caching for expensive operations",
            "Monitor slow queries and optimize them",
            "Use prepared statements for repeated queries",
            "Consider read replicas for analytics queries"
        ]

# Global optimizer instance
_performance_optimizer = None

def get_performance_optimizer(db_session: Session = None) -> PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer(db_session=db_session)
    return _performance_optimizer

# Utility functions
async def cache_ssl_status(domain_id: int, db_session: Session = None):
    """Cache SSL status for domain"""
    optimizer = get_performance_optimizer(db_session)
    return await optimizer.get_domain_ssl_status(domain_id)

async def cache_domain_list(user_id: Optional[str] = None, limit: int = 100, db_session: Session = None):
    """Cache domain list"""
    optimizer = get_performance_optimizer(db_session)
    return await optimizer.get_domain_list(user_id, limit)

async def cache_statistics(db_session: Session = None):
    """Cache statistics"""
    optimizer = get_performance_optimizer(db_session)
    return await optimizer.get_statistics()

async def cache_analytics(period: str = '30d', db_session: Session = None):
    """Cache analytics data"""
    optimizer = get_performance_optimizer(db_session)
    return await optimizer.get_analytics_data(period)
