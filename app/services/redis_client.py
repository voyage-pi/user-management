import redis.asyncio as redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "maps_wrapper_cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    async def set(self, key: str, value: str, expire: int = 3600):
        """Set a key-value pair in Redis with an expiration time."""
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str):
        """Retrieve a value from Redis by key."""
        return await self.redis.get(key)

    async def delete(self, key: str):
        """Delete a key from Redis."""
        await self.redis.delete(key)

redis_client = RedisClient()
