from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, Sequence, Tuple

from tigrbl_core._spec.router_spec import RouterSpec


class RouterBase(RouterSpec):
    """Base router behaviors shared by concrete router implementations."""

    def include_table(
        self,
        table: type,
        *,
        app: Any | None = None,
        prefix: str | None = None,
        mount_router: bool = True,
    ) -> Tuple[type, Any]:
        include_table = import_module(
            "tigrbl_concrete._mapping.router.include"
        ).include_table

        return include_table(
            self,
            table,
            app=app,
            prefix=prefix,
            mount_router=mount_router,
        )

    def include_tables(
        self,
        tables: Sequence[type],
        *,
        app: Any | None = None,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        include_tables = import_module(
            "tigrbl_concrete._mapping.router.include"
        ).include_tables

        return include_tables(
            self,
            tables,
            app=app,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )


__all__ = ["RouterBase"]
