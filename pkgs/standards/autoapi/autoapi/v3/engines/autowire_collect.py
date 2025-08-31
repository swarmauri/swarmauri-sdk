# autoapi/autoapi/v3/engines/autowire_collect.py
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterable, Mapping, Tuple

from .resolver import set_default, register_api, register_table, register_op

def _read_db_attr(obj: Any):
    for k in ("db", "database", "db_provider"):
        if hasattr(obj, k):
            return getattr(obj, k)
    for k in ("autoapi_db", "get_db", "get_database"):
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
                if callable(fn) and hasattr(fn, "__autoapi_db__"):
                    out[(model, alias)] = {"db": getattr(fn, "__autoapi_db__")}
                    break
    rpcns = getattr(model, "rpc", SimpleNamespace())
    for alias in dir(rpcns):
        if alias.startswith("_"):
            continue
        fn = getattr(rpcns, alias, None)
        if callable(fn) and hasattr(fn, "__autoapi_db__"):
            out[(model, alias)] = {"db": getattr(fn, "__autoapi_db__")}
    return out

def install_from_objects(*, app: Any | None = None, api: Any | None = None, models: Iterable[Any] = ()) -> None:
    # app default
    app_db = _read_db_attr(app) if app is not None else None
    if app_db is not None:
        set_default(app_db)

    # api
    api_db = _read_db_attr(api) if api is not None else None
    if api_db is not None:
        register_api(api, api_db)

    # tables and ops
    for m in models:
        # table-level
        cfg = getattr(m, "table_config", None)
        tdb = None
        if isinstance(cfg, Mapping):
            for k in ("db", "database", "db_provider"):
                if k in cfg:
                    tdb = cfg[k]
                    break
        if tdb is None:
            tdb = _read_db_attr(m)
        if tdb is not None:
            register_table(m, tdb)

        # op-level
        for (model, alias), ocfg in _iter_op_decorators(m).items():
            register_op(model, alias, ocfg.get("db"))
