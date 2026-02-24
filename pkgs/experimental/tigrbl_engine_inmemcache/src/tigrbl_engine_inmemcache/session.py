from __future__ import annotations

from .cache import InMemCache


class CacheSession:
    def __init__(self, cache: InMemCache) -> None:
        self._cache = cache
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def get(self, key: str, default=None):
        self._require_open()
        return self._cache.get(key, default)

    def set(self, key: str, value, *, ttl_s: float | None = None) -> None:
        self._require_open()
        self._cache.set(key, value, ttl_s=ttl_s)

    def delete(self, key: str) -> bool:
        self._require_open()
        return self._cache.delete(key)

    def clear(self) -> None:
        self._require_open()
        self._cache.clear()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncCacheSession(CacheSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
