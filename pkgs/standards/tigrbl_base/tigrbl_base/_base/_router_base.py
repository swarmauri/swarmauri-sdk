from __future__ import annotations

from typing import Any, Dict, Sequence, Tuple

from tigrbl_core._spec.router_spec import RouterSpec


class RouterBase(RouterSpec):
    """Base router behaviors shared by concrete router implementations."""

    def _include_table_impl(
        self,
        table: type,
        *,
        app: Any | None = None,
        prefix: str | None = None,
        mount_router: bool = True,
    ) -> Tuple[type, Any]:
        raise NotImplementedError(
            "RouterBase._include_table_impl must be provided by concrete runtime."
        )

    def include_table(
        self,
        table: type,
        *,
        app: Any | None = None,
        prefix: str | None = None,
        mount_router: bool = True,
    ) -> Tuple[type, Any]:
        return self._include_table_impl(
            table,
            app=app,
            prefix=prefix,
            mount_router=mount_router,
        )

    def _include_tables_impl(
        self,
        tables: Sequence[type],
        *,
        app: Any | None = None,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        raise NotImplementedError(
            "RouterBase._include_tables_impl must be provided by concrete runtime."
        )

    def include_tables(
        self,
        tables: Sequence[type],
        *,
        app: Any | None = None,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        return self._include_tables_impl(
            tables,
            app=app,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )


__all__ = ["RouterBase"]
