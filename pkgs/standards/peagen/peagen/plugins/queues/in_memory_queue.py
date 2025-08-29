from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class InMemoryQueue:
    """In-memory stand-in for Redis with minimal async APIs."""

    def __init__(self, maxsize: int = 0, **_: object) -> None:
        self.lists: dict[str, list[str]] = defaultdict(list)
        self.sets: dict[str, set[str]] = defaultdict(set)
        self.hashes: dict[str, dict[str, Any]] = defaultdict(dict)
        self.expiry: dict[str, float] = {}
        self.pubsub: dict[str, list[str]] = defaultdict(list)
        self._loop = asyncio.get_event_loop()
        self._cond = asyncio.Condition()
        self.maxsize = maxsize

    def get_client(self) -> "InMemoryQueue":
        return self

    async def _cleanup(self) -> None:
        now = self._loop.time()
        for key, ts in list(self.expiry.items()):
            if ts <= now:
                self.hashes.pop(key, None)
                self.expiry.pop(key, None)

    # -------------------- set ops --------------------
    async def sadd(self, key: str, member: str) -> None:
        self.sets[key].add(member)

    async def smembers(self, key: str) -> list[str]:
        return list(self.sets.get(key, set()))

    # -------------------- list ops -------------------
    async def rpush(self, key: str, value: str) -> None:
        self.lists[key].append(value)
        async with self._cond:
            self._cond.notify_all()

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        lst = self.lists.get(key, [])
        if end == -1:
            end = len(lst) - 1
        return lst[start : end + 1]

    async def blpop(self, keys: list[str], timeout: float) -> tuple[str, str] | None:
        end_time = self._loop.time() + timeout
        while True:
            await self._cleanup()
            for k in keys:
                lst = self.lists.get(k)
                if lst:
                    value = lst.pop(0)
                    return k, value
            remaining = end_time - self._loop.time()
            if remaining <= 0:
                return None
            async with self._cond:
                try:
                    await asyncio.wait_for(self._cond.wait(), remaining)
                except asyncio.TimeoutError:
                    return None

    async def brpop(self, keys: list[str], timeout: float) -> tuple[str, str] | None:
        end_time = self._loop.time() + timeout
        while True:
            await self._cleanup()
            for k in keys:
                lst = self.lists.get(k)
                if lst:
                    value = lst.pop()
                    return k, value
            remaining = end_time - self._loop.time()
            if remaining <= 0:
                return None
            async with self._cond:
                try:
                    await asyncio.wait_for(self._cond.wait(), remaining)
                except asyncio.TimeoutError:
                    return None

    # -------------------- hash ops -------------------
    async def get(self, key: str) -> None:
        return self.client.get(key)

    async def set(self, key: str, mapping: dict[str, Any]) -> None:
        self.hashes[key] = mapping

    async def hset(self, key: str, mapping: dict[str, Any]) -> None:
        self.hashes[key].update(mapping)

    async def hgetall(self, key: str) -> dict[str, Any]:
        await self._cleanup()
        return dict(self.hashes.get(key, {}))

    async def hget(self, key: str, field: str) -> str | None:
        await self._cleanup()
        return self.hashes.get(key, {}).get(field)

    async def expire(self, key: str, ttl: int) -> None:
        self.expiry[key] = self._loop.time() + ttl

    async def exists(self, key: str) -> bool:
        await self._cleanup()
        return key in self.hashes

    async def keys(self, pattern: str) -> list[str]:
        await self._cleanup()
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [k for k in self.hashes if k.startswith(prefix)]
        return [k for k in self.hashes if k == pattern]

    async def publish(self, channel: str, message: str) -> None:
        self.pubsub[channel].append(message)
