from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Iterable, Mapping


def _read_engine_attr(obj: Any):
    for key in ("engine", "db", "database", "engine_provider", "db_provider"):
        if hasattr(obj, key):
            return getattr(obj, key)
    for key in ("tigrbl_engine", "tigrbl_db", "get_engine"):
        fn = getattr(obj, key, None)
        if callable(fn):
            return fn()
    return None


def _iter_op_decorators(model: Any) -> dict[tuple[Any, str], Mapping[str, Any]]:
    out: dict[tuple[Any, str], Mapping[str, Any]] = {}
    handlers = getattr(model, "handlers", None)
    if handlers:
        for alias in dir(handlers):
            handler = getattr(handlers, alias, None)
            if handler is None:
                continue
            for slot in ("handler", "core"):
                fn = getattr(handler, slot, None)
                if callable(fn) and (
                    hasattr(fn, "__tigrbl_engine_ctx__") or hasattr(fn, "__tigrbl_db__")
                ):
                    spec = getattr(fn, "__tigrbl_engine_ctx__", None)
                    if spec is None:
                        spec = getattr(fn, "__tigrbl_db__")
                    out[(model, alias)] = {"engine": spec}
                    break

    rpc_namespace = getattr(model, "rpc", SimpleNamespace())
    for alias in dir(rpc_namespace):
        if alias.startswith("_"):
            continue
        fn = getattr(rpc_namespace, alias, None)
        if callable(fn) and (
            hasattr(fn, "__tigrbl_engine_ctx__") or hasattr(fn, "__tigrbl_db__")
        ):
            spec = getattr(fn, "__tigrbl_engine_ctx__", None)
            if spec is None:
                spec = getattr(fn, "__tigrbl_db__")
            out[(model, alias)] = {"engine": spec}

    return out


def _iter_declared_ops(model: Any) -> dict[tuple[Any, str], Mapping[str, Any]]:
    out: dict[tuple[Any, str], Mapping[str, Any]] = {}
    for spec in getattr(model, "__tigrbl_ops__", ()) or ():
        engine = getattr(spec, "engine", None)
        alias = getattr(spec, "alias", None)
        if engine is not None and alias:
            out[(model, alias)] = {"engine": engine}
    return out


def collect_engine_bindings(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> dict[str, Any]:
    app_engine = _read_engine_attr(app) if app is not None else None
    router_engine = _read_engine_attr(router) if router is not None else None

    table_bindings: dict[Any, Any] = {}
    ops: dict[tuple[Any, str], Any] = {}
    tables = tuple(tables)

    for model in tables:
        cfg = getattr(model, "table_config", None)
        model_engine = None
        if isinstance(cfg, Mapping):
            for key in ("engine", "db", "database", "engine_provider", "db_provider"):
                if key in cfg:
                    model_engine = cfg[key]
                    break
        if model_engine is None:
            model_engine = _read_engine_attr(model)
        if model_engine is not None:
            table_bindings[model] = model_engine

        for (decl_model, alias), op_cfg in _iter_op_decorators(model).items():
            ops[(decl_model, alias)] = op_cfg.get("engine")
        for (decl_model, alias), op_cfg in _iter_declared_ops(model).items():
            ops[(decl_model, alias)] = op_cfg.get("engine")

    router_map = (
        {router: router_engine}
        if router_engine is not None and router is not None
        else {}
    )

    return {
        "default": app_engine,
        "router": router_map,
        "tables": table_bindings,
        "ops": ops,
    }
