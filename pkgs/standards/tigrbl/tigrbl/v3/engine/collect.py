"""Functions for inspecting objects for engine configuration."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Iterable, Mapping, Tuple


logger = logging.getLogger("uvicorn")


def _read_engine_attr(obj: Any):
    for k in ("engine", "db", "database", "engine_provider", "db_provider"):
        if hasattr(obj, k):
            return getattr(obj, k)
    for k in (
        "tigrbl_engine",
        "tigrbl_db",
        "get_engine",
    ):
        fn = getattr(obj, k, None)
        if callable(fn):
            return fn()
    return None


def _iter_op_decorators(model: Any) -> Dict[Tuple[Any, str], Mapping[str, Any]]:
    out: Dict[Tuple[Any, str], Mapping[str, Any]] = {}
    handlers = getattr(model, "handlers", None)
    if handlers:
        for alias in dir(handlers):
            h = getattr(handlers, alias, None)
            if h is None:
                continue
            for slot in ("handler", "core"):
                fn = getattr(h, slot, None)
                if callable(fn) and (
                    hasattr(fn, "__tigrbl_engine_ctx__") or hasattr(fn, "__tigrbl_db__")
                ):
                    spec = getattr(fn, "__tigrbl_engine_ctx__", None)
                    if spec is None:
                        spec = getattr(fn, "__tigrbl_db__")
                    out[(model, alias)] = {"engine": spec}
                    break
    rpcns = getattr(model, "rpc", SimpleNamespace())
    for alias in dir(rpcns):
        if alias.startswith("_"):
            continue
        fn = getattr(rpcns, alias, None)
        if callable(fn) and (
            hasattr(fn, "__tigrbl_engine_ctx__") or hasattr(fn, "__tigrbl_db__")
        ):
            spec = getattr(fn, "__tigrbl_engine_ctx__", None)
            if spec is None:
                spec = getattr(fn, "__tigrbl_db__")
            out[(model, alias)] = {"engine": spec}
    return out


def _iter_declared_ops(model: Any) -> Dict[Tuple[Any, str], Mapping[str, Any]]:
    out: Dict[Tuple[Any, str], Mapping[str, Any]] = {}
    for spec in getattr(model, "__tigrbl_ops__", ()) or ():
        eng = getattr(spec, "engine", None)
        alias = getattr(spec, "alias", None)
        if eng is not None and alias:
            out[(model, alias)] = {"engine": eng}
    return out


def collect_engine_config(
    *, app: Any | None = None, api: Any | None = None, models: Iterable[Any] = ()
) -> Dict[str, Any]:
    """Collect engine configuration from objects without binding them."""
    logger.info("Collecting engine configuration")
    app_engine = _read_engine_attr(app) if app is not None else None
    api_engine = _read_engine_attr(api) if api is not None else None

    tables: Dict[Any, Any] = {}
    ops: Dict[Tuple[Any, str], Any] = {}

    for m in models:
        cfg = getattr(m, "table_config", None)
        t_engine = None
        if isinstance(cfg, Mapping):
            for k in ("engine", "db", "database", "engine_provider", "db_provider"):
                if k in cfg:
                    t_engine = cfg[k]
                    break
        if t_engine is None:
            t_engine = _read_engine_attr(m)
        if t_engine is not None:
            tables[m] = t_engine

        for (model, alias), ocfg in _iter_op_decorators(m).items():
            ops[(model, alias)] = ocfg.get("engine")
        for (model, alias), ocfg in _iter_declared_ops(m).items():
            ops[(model, alias)] = ocfg.get("engine")

    api_map = {api: api_engine} if api_engine is not None and api is not None else {}

    logger.debug("Collected engine config for %d models", len(models))
    return {
        "default": app_engine,
        "api": api_map,
        "tables": tables,
        "ops": ops,
    }


__all__ = ["collect_engine_config"]
