"""
Redis cache service for price data and session management
"""
import json
import logging
from typing import Optional, Any, Dict
import os

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache service"""

    def __init__(self):
        self.client = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self._connect()

    def _connect(self):
        """Connect to Redis"""
        try:
            import redis.asyncio as redis
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            logger.info("✅ Redis cache service initialized")
        except ImportError:
            logger.warning("redis package not installed. Redis cache disabled.")
            self.client = None
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache will be disabled.")
            self.client = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire_seconds: int = 300):
        """Set value in cache with expiration"""
        if not self.client:
            return
        try:
            await self.client.setex(key, expire_seconds, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def cache_price_data(self, product_name: str, price_data: Dict):
        """Cache price data for a product"""
        key = f"price:{product_name}"
        await self.set(key, price_data, expire_seconds=3600)
        logger.info(f"Cached price data for {product_name}")

    async def get_cached_price(self, product_name: str) -> Optional[Dict]:
        """Get cached price data"""
        key = f"price:{product_name}"
        return await self.get(key)

    async def invalidate_product_cache(self, product_name: str):
        """Invalidate cache for a product"""
        key = f"price:{product_name}"
        await self.delete(key)
        logger.info(f"Invalidated cache for {product_name}")


# Create singleton instance
redis_cache = RedisCache()