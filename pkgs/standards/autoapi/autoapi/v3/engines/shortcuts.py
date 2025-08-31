Here’s a complete drop-in replacement for `autoapi/v3/engines/shortcuts.py`, with `ctxS` fully collapsed into `engS`. `engS` now accepts either an existing EngineCtx (DSN string or mapping) **or** keyword fields (kind/async\_/…); no double wrapping. Back-compat helpers (`mem`, `sqlitef`, `sqliteS`, `pgS`, `pg`, `pga`, `pgs`) remain and construct mappings inline.&#x20;

```python
# autoapi/autoapi/v3/engines/shortcuts.py
from __future__ import annotations

from typing import Any, Mapping, Optional, Union

from .engine_spec import EngineSpec
from ._engine import Provider, Engine
from . import (
    blocking_sqlite_engine,
    blocking_postgres_engine,
    async_sqlite_engine,
    async_postgres_engine,
)

EngineCtx = Union[str, Mapping[str, object]]  # DSN string or structured mapping


# ---------------------------------------------------------------------------
# EngineSpec / Provider / Engine helpers  (ctx builder collapsed into engS)
# ---------------------------------------------------------------------------

def engS(spec: Union[EngineCtx, Mapping[str, Any], str, None] = None, **kw: Any) -> EngineSpec:
    """
    Build an EngineSpec from:
      • spec: DSN string or mapping (EngineCtx), or
      • **kw: keyword fields (collapsed former ctxS), e.g.:
            engS(kind="sqlite", mode="memory", async_=True)
            engS(kind="sqlite", path="./x.sqlite")
            engS(kind="postgres", async_=True, host="db", name="app_db")
            engS(dsn="postgresql+asyncpg://app:secret@db:5432/app_db")
    """
    if spec is None and kw:
        # Inline the former ctxS(...) behavior (no double wrap)
        dsn: Optional[str] = kw.get("dsn")
        if dsn:
            spec = dsn
        else:
            kind = kw.get("kind")
            if not kind:
                raise ValueError("Provide spec=<DSN|mapping> or kind=('sqlite'|'postgres') with appropriate fields")
            async_ = bool(kw.get("async_", kw.get("async", False)))

            if kind == "sqlite":
                path = kw.get("path")
                mode = kw.get("mode")
                memory = kw.get("memory")
                # memory if: explicit mode="memory" OR memory=True OR no path
                if (mode == "memory") or (memory is True) or (not path and mode != "file"):
                    spec = {"kind": "sqlite", "async": async_, "mode": "memory"}
                else:
                    if not path:
                        raise ValueError("sqlite file requires 'path'")
                    spec = {"kind": "sqlite", "async": async_, "path": path}

            elif kind == "postgres":
                spec = {
                    "kind": "postgres",
                    "async": async_,
                    "user": kw.get("user", "app"),
                    "pwd": kw.get("pwd", "secret"),
                    "host": kw.get("host", "localhost"),
                    "port": kw.get("port", 5432),
                    "db": kw.get("name", kw.get("db", "app_db")),
                    "pool_size": kw.get("pool_size", 10),
                    "max": kw.get("max", 20),
                }
            else:
                raise ValueError("kind must be 'sqlite' or 'postgres'")

    return EngineSpec.from_any(spec)


def prov(spec: Union[EngineSpec, EngineCtx, Mapping[str, Any], str, None] = None, **kw: Any) -> Provider:
    """
    Get a lazy Provider (engine+sessionmaker).
    Accepts EngineSpec, EngineCtx (mapping/DSN), or kw fields (collapsed former ctxS).
    """
    if isinstance(spec, EngineSpec):
        return spec.to_provider()
    return engS(spec, **kw).to_provider()


def engine(spec: Union[EngineSpec, EngineCtx, Mapping[str, Any], str, None] = None, **kw: Any) -> Engine:
    """
    Return an Engine façade (wraps a Provider) for convenience in ad-hoc flows:
        e = engine(kind="sqlite", mode="memory", async_=True)
        async with e.asession() as s: ...
    """
    return Engine(prov(spec, **kw))


# ---------------------------------------------------------------------------
# Convenience helpers (construct EngineCtx mappings directly; no ctxS needed)
# ---------------------------------------------------------------------------

def sqliteS(path: Optional[str] = None, *, async_: bool = False, memory: Optional[bool] = None) -> EngineCtx:
    return {"kind": "sqlite", "async": async_, "mode": "memory"} if (memory or path is None) \
           else {"kind": "sqlite", "async": async_, "path": path}

def pgS(
    *, async_: bool = False, user: str = "app", pwd: str = "secret",
    host: str = "localhost", port: int = 5432, name: str = "app_db",
    pool_size: int = 10, max: int = 20
) -> EngineCtx:
    return {
        "kind": "postgres", "async": async_, "user": user, "pwd": pwd,
        "host": host, "port": port, "db": name, "pool_size": pool_size, "max": max,
    }

def mem(async_: bool = False) -> EngineCtx:
    """SQLite in-memory (StaticPool) EngineCtx mapping."""
    return {"kind": "sqlite", "async": async_, "mode": "memory"}

def sqlitef(path: str, *, async_: bool = False) -> EngineCtx:
    """SQLite file EngineCtx mapping."""
    return {"kind": "sqlite", "async": async_, "path": path}

def pg(**kw: Any) -> EngineCtx:
    """Postgres EngineCtx; set async_=True for asyncpg."""
    return pgS(**kw)

def pga(**kw: Any) -> EngineCtx:
    """Async Postgres EngineCtx (asyncpg)."""
    kw.setdefault("async_", True)
    return pgS(**kw)

def pgs(**kw: Any) -> EngineCtx:
    """Sync Postgres EngineCtx (psycopg/pg8000 depending on your builders)."""
    kw.setdefault("async_", False)
    return pgS(**kw)


# ---------------------------------------------------------------------------
# Provider one-liners (direct builder access, unchanged)
# ---------------------------------------------------------------------------

def provider_sqlite_memory(async_: bool = False) -> Provider:
    if async_:
        def build():
            eng, mk = async_sqlite_engine(path=None); return eng, mk
        return Provider("async", build)
    else:
        def build():
            eng, mk = blocking_sqlite_engine(path=None); return eng, mk
        return Provider("sync", build)

def provider_sqlite_file(path: str, async_: bool = False) -> Provider:
    if async_:
        def build():
            eng, mk = async_sqlite_engine(path=path); return eng, mk
        return Provider("async", build)
    else:
        def build():
            eng, mk = blocking_sqlite_engine(path=path); return eng, mk
        return Provider("sync", build)

def provider_postgres(
    *, async_: bool = False, user: str = "app", pwd: str = "secret",
    host: str = "localhost", port: int = 5432, name: str = "app_db",
    pool_size: int = 10, max: int = 20
) -> Provider:
    if async_:
        def build():
            eng, mk = async_postgres_engine(user=user, pwd=pwd, host=host, port=port, db=name,
                                            pool_size=pool_size, max_size=max)
            return eng, mk
        return Provider("async", build)
    else:
        def build():
            eng, mk = blocking_postgres_engine(user=user, pwd=pwd, host=host, port=port, db=name,
                                               pool_size=pool_size, max_overflow=max)
            return eng, mk
        return Provider("sync", build)


__all__ = [
    # EngineSpec / Provider / Engine helpers
    "engS", "prov", "engine",
    # convenience EngineCtx helpers
    "sqliteS", "pgS", "mem", "sqlitef", "pg", "pga", "pgs",
    # direct providers
    "provider_sqlite_memory", "provider_sqlite_file", "provider_postgres",
]
```
