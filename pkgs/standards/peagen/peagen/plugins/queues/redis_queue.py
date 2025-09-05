from __future__ import annotations

from typing import Any
from redis.asyncio import Redis


class RedisQueue:
    """Wrapper providing Redis-like async queue operations."""

    def __init__(self, uri: str, **_: object) -> None:
        self.client = Redis.from_url(uri, decode_responses=True)

    def get_client(self) -> "RedisQueue":
        return self

    async def sadd(self, key: str, member: str) -> None:
        await self.client.sadd(key, member)

    async def smembers(self, key: str) -> list[str]:
        result = await self.client.smembers(key)
        return list(result)

    async def rpush(self, key: str, value: str) -> None:
        await self.client.rpush(key, value)

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        return await self.client.lrange(key, start, end)

    async def blpop(self, keys: list[str], timeout: float) -> tuple[str, str] | None:
        return await self.client.blpop(keys, timeout)

    async def brpop(self, keys: list[str], timeout: float) -> tuple[str, str] | None:
        return await self.client.brpop(keys, timeout)

    async def get(self, key: str) -> dict[str, Any]:
        return self.client.get(key)

    async def set(self, key: str, mapping: dict[str, Any]) -> None:
        await self.client.set(key, mapping)

    async def hset(self, key: str, mapping: dict[str, Any]) -> None:
        await self.client.hset(key, mapping=mapping)

    async def hgetall(self, key: str) -> dict[str, Any]:
        return await self.client.hgetall(key)

    async def hget(self, key: str, field: str) -> str | None:
        return await self.client.hget(key, field)

    async def expire(self, key: str, ttl: int) -> None:
        await self.client.expire(key, ttl)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def keys(self, pattern: str) -> list[str]:
        return await self.client.keys(pattern)

    async def publish(self, channel: str, message: str) -> None:
        await self.client.publish(channel, message)
