"""
Upstash Redis Client for User Profiles
Fast, serverless, and free tier (10k commands/day)
"""

import os
import requests
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class UpstashRedis:
    """Upstash Redis HTTP client for user management"""
    
    def __init__(self):
        self.base_url = os.getenv(
            "UPSTASH_REDIS_REST_URL",
            "https://helping-snapper-23185.upstash.io"
        )
        self.token = os.getenv(
            "UPSTASH_REDIS_REST_TOKEN",
            "AVqRAAIncDJmNjNiOGQ4MzRiY2I0MWU2OTIyMzEyMzM2OWMzM2FmY3AyMjMxODU"
        )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _execute(self, command: list) -> Any:
        """Execute Redis command via REST API"""
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=command,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('result')
            else:
                print(f"Redis error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Redis connection error: {e}")
            return None
    
    # Basic Redis commands
    def hset(self, key: str, data: dict) -> bool:
        """Set hash fields"""
        # Flatten dict to HSET format: HSET key field1 value1 field2 value2 ...
        command = ["HSET", key]
        for field, value in data.items():
            command.extend([field, str(value)])
        
        result = self._execute(command)
        return result is not None
    
    def hgetall(self, key: str) -> Optional[dict]:
        """Get all hash fields"""
        result = self._execute(["HGETALL", key])
        
        if not result:
            return None
        
        # Convert array [k1, v1, k2, v2] to dict {k1: v1, k2: v2}
        return {result[i]: result[i+1] for i in range(0, len(result), 2)}
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Get single hash field"""
        return self._execute(["HGET", key, field])
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        result = self._execute(["EXISTS", key])
        return result == 1
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        result = self._execute(["DEL", key])
        return result == 1
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration"""
        result = self._execute(["EXPIRE", key, seconds])
        return result == 1
    
    def keys(self, pattern: str) -> list:
        """Get keys matching pattern"""
        result = self._execute(["KEYS", pattern])
        return result if result else []


# Global Redis client
redis_client = UpstashRedis()
