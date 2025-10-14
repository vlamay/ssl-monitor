"""
Production Health Checks for SSL Monitor Pro
Provides comprehensive health monitoring for all services
"""

from flask import jsonify, request
import psycopg2
import redis
import os
import logging
from datetime import datetime, timezone
import requests
import json

logger = logging.getLogger(__name__)

def check_database():
    """Check PostgreSQL database connectivity"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Test basic query
        cur.execute('SELECT 1')
        result = cur.fetchone()
        
        # Check database size
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()))
        """)
        db_size = cur.fetchone()[0]
        
        # Check active connections
        cur.execute("""
            SELECT count(*) FROM pg_stat_activity 
            WHERE state = 'active'
        """)
        active_connections = cur.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "details": {
                "database_size": db_size,
                "active_connections": active_connections,
                "response_time_ms": 0  # Could add timing if needed
            }
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_redis():
    """Check Redis connectivity"""
    try:
        r = redis.from_url(os.getenv('UPSTASH_REDIS_REST_URL'))
        
        # Test ping
        r.ping()
        
        # Get Redis info
        info = r.info()
        
        return {
            "status": "healthy",
            "details": {
                "redis_version": info.get('redis_version', 'unknown'),
                "used_memory_human": info.get('used_memory_human', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "response_time_ms": 0
            }
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_telegram():
    """Check Telegram Bot API connectivity"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return {
                "status": "not_configured",
                "error": "TELEGRAM_BOT_TOKEN not set"
            }
        
        # Test bot API
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        bot_info = response.json()
        
        return {
            "status": "healthy",
            "details": {
                "bot_username": bot_info.get('result', {}).get('username', 'unknown'),
                "response_time_ms": int(response.elapsed.total_seconds() * 1000)
            }
        }
    except Exception as e:
        logger.error(f"Telegram health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_external_services():
    """Check external service dependencies"""
    services = {}
    
    # Check Stripe API
    try:
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if stripe_key:
            # Simple test - check if key format is valid
            if stripe_key.startswith('sk_'):
                services['stripe'] = {
                    "status": "healthy",
                    "details": {"key_format": "valid"}
                }
            else:
                services['stripe'] = {
                    "status": "unhealthy",
                    "error": "Invalid key format"
                }
        else:
            services['stripe'] = {
                "status": "not_configured",
                "error": "STRIPE_SECRET_KEY not set"
            }
    except Exception as e:
        services['stripe'] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check N8N (if configured)
    try:
        n8n_webhook = os.getenv('N8N_WEBHOOK_URL')
        if n8n_webhook:
            # Test N8N webhook endpoint
            response = requests.get(n8n_webhook.replace('/webhook/', '/health/'), timeout=5)
            if response.status_code == 200:
                services['n8n'] = {
                    "status": "healthy",
                    "details": {"response_time_ms": int(response.elapsed.total_seconds() * 1000)}
                }
            else:
                services['n8n'] = {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
        else:
            services['n8n'] = {
                "status": "not_configured",
                "error": "N8N_WEBHOOK_URL not set"
            }
    except Exception as e:
        services['n8n'] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return services

@app.route('/health', methods=['GET'])
def health_check():
    """
    Comprehensive health check endpoint
    Returns 200 if all critical services are healthy, 503 otherwise
    """
    start_time = datetime.now(timezone.utc)
    
    health = {
        "status": "healthy",
        "timestamp": start_time.isoformat(),
        "version": "1.0.0",
        "environment": os.getenv('FLASK_ENV', 'development'),
        "uptime": "unknown",  # Could add uptime tracking
        "services": {}
    }
    
    # Check critical services
    health["services"]["database"] = check_database()
    health["services"]["redis"] = check_redis()
    health["services"]["telegram"] = check_telegram()
    
    # Check external services
    health["services"]["external"] = check_external_services()
    
    # Determine overall health
    critical_services = ['database', 'redis']
    unhealthy_services = []
    
    for service_name in critical_services:
        if health["services"][service_name]["status"] != "healthy":
            unhealthy_services.append(service_name)
    
    if unhealthy_services:
        health["status"] = "unhealthy"
        health["unhealthy_services"] = unhealthy_services
    
    # Calculate response time
    response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    health["response_time_ms"] = round(response_time, 2)
    
    # Return appropriate status code
    status_code = 200 if health["status"] == "healthy" else 503
    
    return jsonify(health), status_code

@app.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes-style liveness probe
    Simple check that the application is running
    """
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes-style readiness probe
    Check if the application is ready to serve traffic
    """
    try:
        # Quick database check
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute('SELECT 1')
        conn.close()
        
        # Quick Redis check
        r = redis.from_url(os.getenv('UPSTASH_REDIS_REST_URL'))
        r.ping()
        
        return jsonify({
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503

@app.route('/health/startup', methods=['GET'])
def startup_check():
    """
    Kubernetes-style startup probe
    Check if the application has finished starting up
    """
    # For now, just return ready status
    # In the future, you could check if migrations are complete, etc.
    return jsonify({
        "status": "started",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus-style metrics endpoint
    Returns basic application metrics
    """
    metrics = []
    
    # Application info
    metrics.append("# HELP ssl_monitor_info Application information")
    metrics.append("# TYPE ssl_monitor_info gauge")
    metrics.append(f'ssl_monitor_info{{version="1.0.0",environment="{os.getenv("FLASK_ENV", "development")}"}} 1')
    
    # Health status
    health_status = 1 if health_check()[1] == 200 else 0
    metrics.append("# HELP ssl_monitor_health_status Health status (1=healthy, 0=unhealthy)")
    metrics.append("# TYPE ssl_monitor_health_status gauge")
    metrics.append(f"ssl_monitor_health_status {health_status}")
    
    # Database connections (if available)
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        active_connections = cur.fetchone()[0]
        conn.close()
        
        metrics.append("# HELP ssl_monitor_db_connections_active Active database connections")
        metrics.append("# TYPE ssl_monitor_db_connections_active gauge")
        metrics.append(f"ssl_monitor_db_connections_active {active_connections}")
    except Exception:
        pass
    
    # Redis info (if available)
    try:
        r = redis.from_url(os.getenv('UPSTASH_REDIS_REST_URL'))
        info = r.info()
        connected_clients = info.get('connected_clients', 0)
        
        metrics.append("# HELP ssl_monitor_redis_connected_clients Redis connected clients")
        metrics.append("# TYPE ssl_monitor_redis_connected_clients gauge")
        metrics.append(f"ssl_monitor_redis_connected_clients {connected_clients}")
    except Exception:
        pass
    
    return "\n".join(metrics), 200, {'Content-Type': 'text/plain'}

@app.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with more information
    Useful for debugging and monitoring
    """
    detailed_health = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "flask_env": os.getenv('FLASK_ENV', 'development'),
            "python_version": os.sys.version,
            "platform": os.sys.platform
        },
        "services": {}
    }
    
    # Detailed database check
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Database version
        cur.execute("SELECT version()")
        db_version = cur.fetchone()[0]
        
        # Database size
        cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        db_size = cur.fetchone()[0]
        
        # Table count
        cur.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cur.fetchone()[0]
        
        conn.close()
        
        detailed_health["services"]["database"] = {
            "status": "healthy",
            "version": db_version,
            "size": db_size,
            "table_count": table_count
        }
    except Exception as e:
        detailed_health["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Detailed Redis check
    try:
        r = redis.from_url(os.getenv('UPSTASH_REDIS_REST_URL'))
        info = r.info()
        
        detailed_health["services"]["redis"] = {
            "status": "healthy",
            "version": info.get('redis_version', 'unknown'),
            "memory_used": info.get('used_memory_human', 'unknown'),
            "connected_clients": info.get('connected_clients', 0),
            "total_commands_processed": info.get('total_commands_processed', 0)
        }
    except Exception as e:
        detailed_health["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return jsonify(detailed_health), 200
