# tigrbl/tigrbl/v3/engine/shortcuts.py
from __future__ import annotations

from typing import Any, Mapping, Optional, Union

from .engine_spec import EngineSpec
from ._engine import Provider, Engine

EngineCfg = Union[str, Mapping[str, object]]  # DSN string or structured mapping


# ---------------------------------------------------------------------------
# EngineSpec / Provider / Engine helpers  (ctx builder collapsed into
# engine_spec)
# ---------------------------------------------------------------------------


def engine_spec(
    spec: Union[EngineCfg, Mapping[str, Any], str, None] = None, **kw: Any
) -> EngineSpec:
    """Build an :class:`EngineSpec` from a DSN string, mapping, or keyword fields."""
    if spec is None and kw:
        # Inline the former ctx builder behavior (no double wrap)
        dsn: Optional[str] = kw.get("dsn")
        if dsn:
            spec = dsn
        else:
            kind = kw.get("kind")
            if not kind:
                raise ValueError(
                    "Provide spec=<DSN|mapping> or kind=('sqlite'|'postgres') with appropriate fields"
                )

            async_kw = kw.get("async_")
            if async_kw is None:
                async_kw = kw.get("async")

            if kind == "sqlite":
                path = kw.get("path")
                mode = kw.get("mode")
                memory_flag = kw.get("memory")
                memory = (
                    (mode == "memory")
                    or (memory_flag is True)
                    or (not path and mode != "file")
                )
                async_default = True if async_kw is None and memory else False
                async_ = bool(async_kw) if async_kw is not None else async_default
                if memory:
                    spec = {"kind": "sqlite", "async": async_, "mode": "memory"}
                else:
                    if not path:
                        raise ValueError("sqlite file requires 'path'")
                    spec = {"kind": "sqlite", "async": async_, "path": path}

            elif kind == "postgres":
                async_ = bool(async_kw) if async_kw is not None else False
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


def prov(
    spec: Union[EngineSpec, EngineCfg, Mapping[str, Any], str, None] = None, **kw: Any
) -> Provider:
    """
    Get a lazy Provider (engine+sessionmaker).
    Accepts EngineSpec, EngineCfg (mapping/DSN), or kw fields (collapsed former ctxS).
    """
    if isinstance(spec, EngineSpec):
        return spec.to_provider()
    return engine_spec(spec, **kw).to_provider()


def engine(
    spec: Union[EngineSpec, EngineCfg, Mapping[str, Any], str, None] = None, **kw: Any
) -> Engine:
    """Return an Engine façade for convenience in ad-hoc flows."""
    if isinstance(spec, EngineSpec):
        return Engine(spec)
    return Engine(engine_spec(spec, **kw))


# ---------------------------------------------------------------------------
# Convenience helpers (construct EngineCfg mappings directly; no ctxS needed)
# ---------------------------------------------------------------------------


def sqlite_cfg(
    path: Optional[str] = None, *, async_: bool = True, memory: Optional[bool] = None
) -> EngineCfg:
    return (
        {"kind": "sqlite", "async": async_, "mode": "memory"}
        if (memory or path is None)
        else {"kind": "sqlite", "async": async_, "path": path}
    )


def pg_cfg(
    *,
    async_: bool = False,
    user: str = "app",
    pwd: str = "secret",
    host: str = "localhost",
    port: int = 5432,
    name: str = "app_db",
    pool_size: int = 10,
    max: int = 20,
) -> EngineCfg:
    return {
        "kind": "postgres",
        "async": async_,
        "user": user,
        "pwd": pwd,
        "host": host,
        "port": port,
        "db": name,
        "pool_size": pool_size,
        "max": max,
    }


def mem(async_: bool = True) -> EngineCfg:
    """SQLite in-memory (StaticPool) EngineCfg mapping."""
    return {"kind": "sqlite", "async": async_, "mode": "memory"}


def sqlitef(path: str, *, async_: bool = False) -> EngineCfg:
    """SQLite file EngineCfg mapping."""
    return {"kind": "sqlite", "async": async_, "path": path}


def pg(**kw: Any) -> EngineCfg:
    """Postgres EngineCfg; set async_=True for asyncpg."""
    return pg_cfg(**kw)


def pga(**kw: Any) -> EngineCfg:
    """Async Postgres EngineCfg (asyncpg)."""
    kw.setdefault("async_", True)
    return pg_cfg(**kw)


def pgs(**kw: Any) -> EngineCfg:
    """Sync Postgres EngineCfg (psycopg/pg8000 depending on your builders)."""
    kw.setdefault("async_", False)
    return pg_cfg(**kw)


# ---------------------------------------------------------------------------
# Provider one-liners
# ---------------------------------------------------------------------------


def provider_sqlite_memory(async_: bool = True) -> Provider:
    return engine_spec(kind="sqlite", mode="memory", async_=async_).to_provider()


def provider_sqlite_file(path: str, async_: bool = False) -> Provider:
    return engine_spec(kind="sqlite", path=path, async_=async_).to_provider()


def provider_postgres(
    *,
    async_: bool = False,
    user: str = "app",
    pwd: str = "secret",
    host: str = "localhost",
    port: int = 5432,
    name: str = "app_db",
    pool_size: int = 10,
    max: int = 20,
) -> Provider:
    return engine_spec(
        kind="postgres",
        async_=async_,
        user=user,
        pwd=pwd,
        host=host,
        port=port,
        name=name,
        pool_size=pool_size,
        max=max,
    ).to_provider()


__all__ = [
    # EngineSpec / Provider / Engine helpers
    "engine_spec",
    "prov",
    "engine",
    # convenience EngineCfg helpers
    "sqlite_cfg",
    "pg_cfg",
    "mem",
    "sqlitef",
    "pg",
    "pga",
    "pgs",
    # direct providers
    "provider_sqlite_memory",
    "provider_sqlite_file",
    "provider_postgres",
]
