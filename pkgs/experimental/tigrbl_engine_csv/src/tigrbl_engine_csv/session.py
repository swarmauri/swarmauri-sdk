from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import pandas as pd
from tigrbl.session.base import TigrblSessionBase
from tigrbl.session.spec import SessionSpec
from tigrbl_engine_pandas.session import TransactionalDataFrameSession

if TYPE_CHECKING:
    from .engine import CsvEngine


class CsvSession(TigrblSessionBase):
    """Tigrbl first-class session for a single CSV-backed table database."""

    def __init__(self, engine: "CsvEngine") -> None:
        super().__init__()
        self._engine = engine
        self._inner = TransactionalDataFrameSession(engine.catalog, spec=SessionSpec())

    def table(self, name: str | None = None) -> pd.DataFrame:
        key = name or self._engine.table
        return self._engine.catalog.get_live(key)

    def query(self, expression: str, *, table: str | None = None) -> pd.DataFrame:
        return self.table(table).query(expression)

    def apply_spec(self, spec: SessionSpec | None) -> None:
        super().apply_spec(spec)
        self._inner.apply_spec(spec)

    async def _tx_begin_impl(self) -> None:
        await self._inner._tx_begin_impl()

    async def _tx_commit_impl(self) -> None:
        await self._inner._tx_commit_impl()

    async def _tx_rollback_impl(self) -> None:
        await self._inner._tx_rollback_impl()

    def _add_impl(self, obj: Any) -> Any:
        return self._inner._add_impl(obj)

    async def _delete_impl(self, obj: Any) -> None:
        await self._inner._delete_impl(obj)

    async def _flush_impl(self) -> None:
        await self._inner._flush_impl()

    async def _refresh_impl(self, obj: Any) -> None:
        await self._inner._refresh_impl(obj)

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        return await self._inner._get_impl(model, ident)

    async def _execute_impl(self, stmt: Any) -> Any:
        return await self._inner._execute_impl(stmt)

    async def _close_impl(self) -> None:
        await self._inner._close_impl()

    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        return await self._inner.run_sync(fn)
