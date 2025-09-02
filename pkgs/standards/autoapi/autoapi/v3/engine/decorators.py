# autoapi/autoapi/v3/engine/decorators.py
from __future__ import annotations

import inspect
from typing import Any, Optional

# EngineSpec provides the canonical parsing; EngineCfg is the accepted input type
# (DSN string or mapping) attached by @engine_ctx.
from .engine_spec import EngineCfg


def _normalize(ctx: Optional[EngineCfg] = None, **kw: Any) -> EngineCfg:
    """
    Accept either:
      • ctx: a DSN string (e.g., "sqlite:///file.db", "postgresql+asyncpg://…")
      • ctx: a mapping like {"kind":"sqlite","async":True,"mode":"memory"} or
             {"kind":"postgres","async":True,"host":"db","db":"app_db",...}
      • **kw: keyword form that will be converted to the mapping shape

    Returns an EngineCfg (string or mapping) suitable for EngineSpec.from_any(...).
    """
    if ctx is not None:
        return ctx

    kind = kw.get("kind")
    if not kind:
        dsn = kw.get("dsn")
        if not dsn:
            raise ValueError(
                "Provide engine_ctx=<DSN|mapping> or kind=sqlite|postgres (with fields)"
            )
        return str(dsn)

    m: dict[str, Any] = {
        "kind": kind,
        "async": bool(kw.get("async_", kw.get("async", False))),
    }

    if kind == "sqlite":
        # memory modes: mode="memory" OR memory=True OR no path supplied
        if kw.get("mode") == "memory" or kw.get("memory") or not kw.get("path"):
            m["mode"] = "memory"
        else:
            m["path"] = kw.get("path")

    elif kind == "postgres":
        for k in ("user", "pwd", "host", "port", "db", "pool_size", "max"):
            if k in kw:
                m[k] = kw[k]
    else:
        raise ValueError("kind must be 'sqlite' or 'postgres'")

    return m


def engine_ctx(ctx: Optional[EngineCfg] = None, **kw: Any):
    """
    Object-agnostic decorator to attach engine configuration to:
      - App classes/instances     (app-level default)
      - API classes/instances     (api-level default)
      - ORM model classes         (table-level)
      - Op callables              (op-level)

    What it stores:
      • For ops (functions/methods): sets __autoapi_engine_ctx__ (and legacy __autoapi_db__).
      • For ORM table classes: injects mapping under model.table_config["engine"] (and legacy "db").
      • For App/API classes or instances: sets attribute .engine = EngineCfg (and legacy .db).

    Downstream:
      • engine.install_from_objects(...) discovers these and registers
        Providers with resolver precedence: op > table(model) > api > app.
    """
    spec = _normalize(ctx, **kw)

    def _decorate(obj: Any):
        # Op-level: functions or methods
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            # New attribute name for clarity
            setattr(obj, "__autoapi_engine_ctx__", spec)
            # Back-compat: some collectors still look for __autoapi_db__
            setattr(obj, "__autoapi_db__", spec)
            return obj

        # ORM model class?
        if inspect.isclass(obj) and hasattr(obj, "__tablename__"):
            cfg = dict(getattr(obj, "table_config", {}) or {})
            cfg["engine"] = spec
            cfg["db"] = spec  # legacy key for backward compatibility
            setattr(obj, "table_config", cfg)
            return obj

        # API/App classes or instances: keep a simple attribute
        setattr(obj, "engine", spec)
        setattr(obj, "db", spec)  # legacy attribute
        return obj

    return _decorate


__all__ = ["engine_ctx"]
