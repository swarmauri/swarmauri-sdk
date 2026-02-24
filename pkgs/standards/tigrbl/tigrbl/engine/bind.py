"""Bind collected engine configuration to the resolver."""

from __future__ import annotations

from typing import Any, Dict, Iterable

<<<<<<< HEAD
from .resolver import register_router, register_op, register_table, set_default
=======
from .resolver import register_op, register_router, register_table, set_default
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c


def bind(collected: Dict[str, Any]) -> None:
    """Bind a collected configuration mapping into the resolver."""
    default_db = collected.get("default")
    if default_db is not None:
        set_default(default_db)

<<<<<<< HEAD
    for router_obj, db in collected.get("router", {}).items():
        register_router(router_obj, db)
=======
    for api_obj, db in collected.get("router", {}).items():
        register_router(api_obj, db)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c

    for table_obj, db in collected.get("tables", {}).items():
        register_table(table_obj, db)

    for (model, alias), db in collected.get("ops", {}).items():
        register_op(model, alias, db)


def install_from_objects(
<<<<<<< HEAD
    *,
    app: Any | None = None,
    router: Any | None = None,
    tables: Iterable[Any] = (),
    models: Iterable[Any] | None = None,
=======
    *, app: Any | None = None, router: Any | None = None, models: Iterable[Any] = ()
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
) -> None:
    """Collect engine config from objects and bind them to the resolver."""
    from .collect import collect_engine_config

<<<<<<< HEAD
    effective_tables = tuple(models) if models is not None else tables
    collected = collect_engine_config(app=app, router=router, tables=effective_tables)
=======
    collected = collect_engine_config(app=app, router=router, models=models)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    bind(collected)
