"""Bind collected engine configuration to the resolver."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from .resolver import register_router, register_op, register_table, set_default


def bind(collected: Dict[str, Any]) -> None:
    """Bind a collected configuration mapping into the resolver."""
    default_db = collected.get("default")
    if default_db is not None:
        set_default(default_db)

    for router_obj, db in collected.get("router", {}).items():
        register_router(router_obj, db)

    for table_obj, db in collected.get("tables", {}).items():
        register_table(table_obj, db)

    for (model, alias), db in collected.get("ops", {}).items():
        register_op(model, alias, db)


def install_from_objects(
    *, app: Any | None = None, router: Any | None = None, models: Iterable[Any] = ()
) -> None:
    """Collect engine config from objects and bind them to the resolver."""
    from .collect import collect_engine_config

    collected = collect_engine_config(app=app, router=router, models=models)
    bind(collected)
