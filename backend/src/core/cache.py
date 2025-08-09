"""
Cache management using Redis.
Handles Redis connection, caching operations, and session storage.
"""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from loguru import logger

from config.settings import settings


# Global Redis connection
redis_client: Optional[redis.Redis] = None


async def init_cache() -> None:
    """Initialize Redis connection."""
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=False,  # We'll handle encoding/decoding manually
            retry_on_timeout=True,
            health_check_interval=30,
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis cache initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis cache: {e}")
        raise


async def close_cache() -> None:
    """Close Redis connection."""
    global redis_client
    
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")


class CacheManager:
    """Redis cache manager with various caching strategies."""
    
    def __init__(self):
        self._client = redis_client
    
    async def get(
        self,
        key: str,
        default: Any = None,
        use_json: bool = True,
    ) -> Any:
        """Get value from cache."""
        try:
            if not self._client:
                return default
            
            value = await self._client.get(key)
            if value is None:
                return default
            
            if use_json:
                return json.loads(value.decode())
            else:
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None,
        use_json: bool = True,
    ) -> bool:
        """Set value in cache."""
        try:
            if not self._client:
                return False
            
            if use_json:
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = pickle.dumps(value)
            
            if ttl is None:
                ttl = settings.cache_ttl
            
            await self._client.set(key, serialized_value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self._client:
                return False
            
            deleted_count = await self._client.delete(key)
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self._client:
                return False
            
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache."""
        try:
            if not self._client:
                return None
            
            return await self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return None
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration time for a key."""
        try:
            if not self._client:
                return False
            
            return bool(await self._client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for key '{key}': {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get time-to-live for a key."""
        try:
            if not self._client:
                return None
            
            return await self._client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key '{key}': {e}")
            return None
    
    async def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            if not self._client:
                return 0
            
            keys = await self._client.keys(pattern)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache flush pattern error for pattern '{pattern}': {e}")
            return 0
    
    async def clear_all(self) -> bool:
        """Clear all cache entries."""
        try:
            if not self._client:
                return False
            
            await self._client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False


class SessionManager:
    """Session management using Redis."""
    
    def __init__(self, prefix: str = "session:"):
        self._cache = CacheManager()
        self._prefix = prefix
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"{self._prefix}{session_id}"
    
    async def create_session(
        self,
        session_id: str,
        data: dict,
        ttl: Optional[Union[int, timedelta]] = None,
    ) -> bool:
        """Create a new session."""
        key = self._get_session_key(session_id)
        return await self._cache.set(key, data, ttl=ttl)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        key = self._get_session_key(session_id)
        return await self._cache.get(key)
    
    async def update_session(
        self,
        session_id: str,
        data: dict,
        ttl: Optional[Union[int, timedelta]] = None,
    ) -> bool:
        """Update session data."""
        key = self._get_session_key(session_id)
        return await self._cache.set(key, data, ttl=ttl)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        key = self._get_session_key(session_id)
        return await self._cache.delete(key)
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        key = self._get_session_key(session_id)
        return await self._cache.exists(key)
    
    async def extend_session(
        self,
        session_id: str,
        ttl: Union[int, timedelta],
    ) -> bool:
        """Extend session expiration time."""
        key = self._get_session_key(session_id)
        return await self._cache.expire(key, ttl)


# Global cache and session managers
cache_manager = CacheManager()
session_manager = SessionManager()


async def check_cache_health() -> bool:
    """Check if Redis connection is healthy."""
    try:
        if not redis_client:
            return False
        
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return False


# Decorator for caching function results
def cached(
    ttl: Optional[Union[int, timedelta]] = None,
    key_prefix: str = "func:",
    use_json: bool = True,
):
    """Decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            import hashlib
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = f"{key_prefix}{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            result = await cache_manager.get(cache_key, use_json=use_json)
            if result is not None:
                return result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl=ttl, use_json=use_json)
            return result
        
        return wrapper
    return decorator
