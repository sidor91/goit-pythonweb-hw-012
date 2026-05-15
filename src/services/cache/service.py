from typing import Optional
import json
import logging

from redis import asyncio as aioredis

from src.utils.env_variables import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Simple Redis cache wrapper for user objects.

    Uses `redis.asyncio` to store serialized user data under `user:{id}` keys.
    """

    def __init__(self, url: str = settings.REDIS_URL, ttl: int = settings.USER_CACHE_TTL):
        self._url = url
        self._ttl = ttl
        self._client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis client connection."""
        if self._client is None:
            self._client = aioredis.from_url(self._url, encoding="utf-8", decode_responses=True)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None

    async def set_user(self, user_id: int, user_data: dict) -> None:
        """Cache user data as JSON with TTL."""
        await self.connect()
        key = f"user:{user_id}"
        try:
            await self._client.set(key, json.dumps(user_data), ex=self._ttl)
        except Exception as e:
            logger.exception("Failed to set user cache: %s", e)

    async def set_user_by_username(self, username: str, user_data: dict) -> None:
        """Cache user data under a username-based key."""
        await self.connect()
        key = f"user:username:{username}"
        try:
            await self._client.set(key, json.dumps(user_data), ex=self._ttl)
        except Exception as e:
            logger.exception("Failed to set username-based user cache: %s", e)

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get cached user data or None if not present."""
        await self.connect()
        key = f"user:{user_id}"
        try:
            raw = await self._client.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.exception("Failed to get user cache: %s", e)
            return None

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get cached user data by username-based key."""
        await self.connect()
        key = f"user:username:{username}"
        try:
            raw = await self._client.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.exception("Failed to get username-based user cache: %s", e)
            return None

    async def delete_user(self, user_id: int) -> None:
        """Delete user cache key."""
        await self.connect()
        key = f"user:{user_id}"
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.exception("Failed to delete user cache: %s", e)

    async def delete_user_by_username(self, username: str) -> None:
        """Delete username-based user cache key."""
        await self.connect()
        key = f"user:username:{username}"
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.exception("Failed to delete username-based user cache: %s", e)


# Module-level default cache instance for convenience.
cache_service = CacheService()
