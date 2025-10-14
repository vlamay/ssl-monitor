"""
Rate Limiting for SSL Monitor Pro
Redis-based rate limiting with flexible configuration
"""

import redis
import time
import json
from functools import wraps
from flask import request, jsonify, g
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.from_url(os.getenv('UPSTASH_REDIS_REST_URL'))
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None

class RateLimitExceeded(Exception):
    """Custom exception for rate limit exceeded"""
    def __init__(self, message, retry_after=None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)

def get_client_identifier():
    """
    Get unique identifier for rate limiting
    Priority: API Key > User ID > IP Address
    """
    # Check for API key in headers
    api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
    if api_key:
        return f"api_key:{api_key}"
    
    # Check for user ID in JWT token (if implemented)
    user_id = getattr(g, 'user_id', None)
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP address
    return f"ip:{request.remote_addr}"

def rate_limit(max_requests=60, window=60, per='ip', skip_successful=False):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum requests allowed in window
        window: Time window in seconds
        per: Rate limit per 'ip', 'user', or 'api_key'
        skip_successful: Skip rate limiting for successful requests
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client:
                # If Redis is down, allow request but log warning
                logger.warning("Redis unavailable, skipping rate limiting")
                return f(*args, **kwargs)
            
            # Get client identifier
            if per == 'ip':
                identifier = request.remote_addr
            elif per == 'user':
                identifier = getattr(g, 'user_id', request.remote_addr)
            elif per == 'api_key':
                api_key = request.headers.get('X-API-Key')
                if not api_key:
                    return jsonify({
                        "error": "API key required",
                        "message": "Include X-API-Key header"
                    }), 401
                identifier = f"api_key:{api_key}"
            else:
                identifier = get_client_identifier()
            
            # Create rate limit key
            key = f"rate_limit:{identifier}:{window}"
            
            try:
                # Get current count
                current = redis_client.get(key)
                if current is None:
                    # First request in window
                    redis_client.setex(key, window, 1)
                    current = 1
                else:
                    current = int(current)
                    if current >= max_requests:
                        # Rate limit exceeded
                        ttl = redis_client.ttl(key)
                        retry_after = ttl if ttl > 0 else window
                        
                        logger.warning(f"Rate limit exceeded for {identifier}: {current}/{max_requests}")
                        
                        return jsonify({
                            "error": "Rate limit exceeded",
                            "limit": max_requests,
                            "window": window,
                            "retry_after": retry_after,
                            "message": f"Too many requests. Try again in {retry_after} seconds."
                        }), 429
                    else:
                        # Increment counter
                        redis_client.incr(key)
                
                # Execute the function
                response = f(*args, **kwargs)
                
                # Skip successful requests if configured
                if skip_successful and hasattr(response, 'status_code') and response[1] < 400:
                    # Don't count successful requests
                    redis_client.decr(key)
                
                # Add rate limit headers
                if hasattr(response, 'headers'):
                    response[0].headers['X-RateLimit-Limit'] = max_requests
                    response[0].headers['X-RateLimit-Remaining'] = max_requests - current - 1
                    response[0].headers['X-RateLimit-Reset'] = int(time.time()) + redis_client.ttl(key)
                
                return response
                
            except redis.RedisError as e:
                # If Redis is down, allow request but log error
                logger.error(f"Rate limiting error: {e}")
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def check_rate_limit(identifier, max_requests=60, window=60):
    """
    Check rate limit without decorator
    Useful for custom rate limiting logic
    """
    if not redis_client:
        return True, 0, 0  # Allow if Redis is down
    
    key = f"rate_limit:{identifier}:{window}"
    
    try:
        current = redis_client.get(key)
        if current is None:
            redis_client.setex(key, window, 1)
            return True, 1, max_requests - 1
        else:
            current = int(current)
            if current >= max_requests:
                ttl = redis_client.ttl(key)
                return False, current, 0
            else:
                redis_client.incr(key)
                return True, current + 1, max_requests - current - 1
    except redis.RedisError as e:
        logger.error(f"Rate limiting error: {e}")
        return True, 0, max_requests

def reset_rate_limit(identifier, window=60):
    """
    Reset rate limit for a specific identifier
    Useful for admin functions or testing
    """
    if not redis_client:
        return False
    
    key = f"rate_limit:{identifier}:{window}"
    
    try:
        redis_client.delete(key)
        return True
    except redis.RedisError as e:
        logger.error(f"Failed to reset rate limit: {e}")
        return False

def get_rate_limit_status(identifier, window=60):
    """
    Get current rate limit status for an identifier
    """
    if not redis_client:
        return None
    
    key = f"rate_limit:{identifier}:{window}"
    
    try:
        current = redis_client.get(key)
        ttl = redis_client.ttl(key)
        
        if current is None:
            return {
                "current": 0,
                "remaining": 60,  # Default limit
                "reset_time": int(time.time()) + window,
                "ttl": 0
            }
        else:
            current = int(current)
            return {
                "current": current,
                "remaining": 60 - current,  # Default limit
                "reset_time": int(time.time()) + ttl,
                "ttl": ttl
            }
    except redis.RedisError as e:
        logger.error(f"Failed to get rate limit status: {e}")
        return None

# Predefined rate limit configurations
RATE_LIMITS = {
    'api_general': {'max_requests': 100, 'window': 60, 'per': 'ip'},
    'api_strict': {'max_requests': 10, 'window': 60, 'per': 'ip'},
    'auth': {'max_requests': 5, 'window': 300, 'per': 'ip'},  # 5 attempts per 5 minutes
    'ssl_check': {'max_requests': 30, 'window': 60, 'per': 'ip'},
    'domain_add': {'max_requests': 10, 'window': 60, 'per': 'user'},
    'webhook': {'max_requests': 1000, 'window': 60, 'per': 'ip'},  # Webhooks need higher limits
    'admin': {'max_requests': 1000, 'window': 60, 'per': 'api_key'},
}

def apply_rate_limit(limit_name):
    """
    Apply predefined rate limit configuration
    """
    if limit_name not in RATE_LIMITS:
        raise ValueError(f"Unknown rate limit configuration: {limit_name}")
    
    config = RATE_LIMITS[limit_name]
    return rate_limit(**config)

# Example usage in routes:
"""
@app.route('/api/domains', methods=['POST'])
@apply_rate_limit('domain_add')
def add_domain():
    # Your domain addition logic
    pass

@app.route('/api/auth/login', methods=['POST'])
@apply_rate_limit('auth')
def login():
    # Your login logic
    pass

@app.route('/api/ssl/check', methods=['POST'])
@apply_rate_limit('ssl_check')
def check_ssl():
    # Your SSL check logic
    pass
"""

# Admin endpoint for rate limit management
@app.route('/admin/rate-limits/<identifier>', methods=['GET'])
def get_rate_limit_info(identifier):
    """Get rate limit information for debugging"""
    status = get_rate_limit_status(identifier)
    if status:
        return jsonify({
            "identifier": identifier,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "Failed to get rate limit status"
        }), 500

@app.route('/admin/rate-limits/<identifier>', methods=['DELETE'])
def reset_rate_limit_admin(identifier):
    """Reset rate limit for an identifier (admin only)"""
    if reset_rate_limit(identifier):
        return jsonify({
            "message": f"Rate limit reset for {identifier}",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "Failed to reset rate limit"
        }), 500
