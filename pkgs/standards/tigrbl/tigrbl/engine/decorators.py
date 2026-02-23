# tigrbl/tigrbl/v3/engine/decorators.py
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

    async_kw = kw.get("async_")
    if async_kw is None:
        async_kw = kw.get("async")

    m: dict[str, Any] = {"kind": kind}

    if kind == "sqlite":
        path = kw.get("path")
        mode = kw.get("mode")
        memory_flag = kw.get("memory")
        # memory modes: mode="memory" OR memory=True OR no path supplied
        memory = (mode == "memory") or memory_flag or not path
        async_default = True if async_kw is None and memory else False
        m["async"] = bool(async_kw) if async_kw is not None else async_default
        if memory:
            m["mode"] = "memory"
        else:
            m["path"] = path

    elif kind == "postgres":
        m["async"] = bool(async_kw) if async_kw is not None else False
        for k in ("user", "pwd", "host", "port", "db", "pool_size", "max"):
            if k in kw:
                m[k] = kw[k]
    else:
        # Allow external engine kinds; pass mapping through unchanged.
        # Keep provided keys as-is so external builders can interpret them.
        m.update({k: v for k, v in kw.items() if k not in m})

    return m


def engine_ctx(ctx: Optional[EngineCfg] = None, **kw: Any):
    """
    Object-agnostic decorator to attach engine configuration to:
      - App classes/instances     (app-level default)
      - API classes/instances     (api-level default)
      - ORM model classes         (table-level)
      - Op callables              (op-level)

    What it stores:
      • For ops (functions/methods): sets __tigrbl_engine_ctx__ (and legacy __tigrbl_db__).
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
            setattr(obj, "__tigrbl_engine_ctx__", spec)
            # Back-compat: some collectors still look for __tigrbl_db__
            setattr(obj, "__tigrbl_db__", spec)
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
