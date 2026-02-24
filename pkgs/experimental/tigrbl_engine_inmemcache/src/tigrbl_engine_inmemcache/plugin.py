from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .cache import InMemCache
from .session import AsyncCacheSession, CacheSession


def register() -> None:
    register_engine(
        kind="inmemcache",
        build=build_cache,
        capabilities=capabilities,
    )


def capabilities() -> dict:
    return {
        "engine": "inmemcache",
        "transactional": False,
        "async_native": True,
        "read_only_enforced": False,
        "persistence": "process",
        "features": {"ttl", "lru"},
    }


def build_cache(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))

    cache = InMemCache(
        namespace=str(mapping.get("namespace", "default")),
        max_items=int(mapping.get("max_items", 100_000)),
        default_ttl_s=float(mapping.get("default_ttl_s", 0.0)) or None,
    )

    if async_:

        def sessionmaker():
            return AsyncCacheSession(cache)
    else:

        def sessionmaker():
            return CacheSession(cache)

    return cache, sessionmaker
