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

    def include_tables(
        self,
        tables: Sequence[type],
        *,
        app: Any | None = None,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        included: Dict[str, Any] = {}
        for table in tables:
            table_name = getattr(table, "__name__", str(table))
            _, router = self.include_table(
                table,
                app=app,
                prefix=base_prefix,
                mount_router=mount_router,
            )
            included[table_name] = router

        return included


__all__ = ["RouterBase"]
