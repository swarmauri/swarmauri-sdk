from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional, Sequence

import duckdb

from tigrbl.session.base import TigrblSessionBase
from tigrbl.session.spec import SessionSpec
from tigrbl.core.crud.helpers.model import _single_pk_name, _model_columns
from tigrbl.core.crud.helpers import NoResultFound


class _ScalarResult:
    """Minimal result facade for Tigrbl core CRUD."""

    def __init__(self, items: Sequence[Any]) -> None:
        self._items = list(items)

    def scalars(self) -> "_ScalarResult":
        return self

    def all(self) -> list[Any]:
        return list(self._items)

    def scalar_one(self) -> Any:
        if len(self._items) != 1:
            raise NoResultFound("expected exactly one row")
        return self._items[0]


class DuckDBSession(TigrblSessionBase):
    """Transactional session over a synchronous duckdb.Connection."""

    def __init__(
        self, conn: duckdb.DuckDBPyConnection, spec: Optional[SessionSpec] = None
    ) -> None:
        super().__init__(spec)
        self._c = conn

    # ---------- async marker ----------
    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        return await asyncio.to_thread(fn, self._c)

    # ---------- TX primitives ----------
    async def _tx_begin_impl(self) -> None:
        await asyncio.to_thread(self._c.execute, "BEGIN")

    async def _tx_commit_impl(self) -> None:
        await asyncio.to_thread(self._c.execute, "COMMIT")

    async def _tx_rollback_impl(self) -> None:
        await asyncio.to_thread(self._c.execute, "ROLLBACK")

    # ---------- CRUD primitives ----------
    def _add_impl(self, obj: Any) -> Any:
        table = getattr(obj.__class__, "__tablename__", obj.__class__.__name__)
        cols = list(_model_columns(obj.__class__).keys())
        placeholders = ", ".join(["?"] * len(cols))
        col_list = ", ".join(cols)
        sql = f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})'
        values = [getattr(obj, c, None) for c in cols]

        def _exec():
            self._c.execute(sql, values)

        return _exec()

    async def _delete_impl(self, obj: Any) -> None:
        table = getattr(obj.__class__, "__tablename__", obj.__class__.__name__)
        pk = _single_pk_name(obj.__class__)
        ident = getattr(obj, pk)
        await asyncio.to_thread(
            self._c.execute, f'DELETE FROM "{table}" WHERE "{pk}" = ?', [ident]
        )

    async def _flush_impl(self) -> None:
        return

    async def _refresh_impl(self, obj: Any) -> None:
        pk = _single_pk_name(obj.__class__)
        ident = getattr(obj, pk)
        fresh = await self._get_impl(obj.__class__, ident)
        if fresh:
            for c in _model_columns(obj.__class__).keys():
                setattr(obj, c, getattr(fresh, c, None))

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        table = getattr(model, "__tablename__", model.__name__)
        pk = _single_pk_name(model)
        cols = list(_model_columns(model).keys())
        col_list = ", ".join([f'"{c}"' for c in cols])
        sql = f'SELECT {col_list} FROM "{table}" WHERE "{pk}" = ?'
        cur = await asyncio.to_thread(self._c.execute, sql, [ident])
        row = cur.fetchone()
        if not row:
            return None
        obj = model()
        for i, c in enumerate(cols):
            setattr(obj, c, row[i])
        return obj

    async def _execute_impl(self, stmt: Any) -> Any:
        if isinstance(stmt, tuple) and len(stmt) == 2 and isinstance(stmt[0], str):
            sql, params = stmt
            cur = await asyncio.to_thread(self._c.execute, sql, params or [])
            rows = cur.fetchall() or []
            return _ScalarResult(rows)

        if isinstance(stmt, str):
            cur = await asyncio.to_thread(self._c.execute, stmt)
            rows = cur.fetchall() or []
            return _ScalarResult(rows)

        raise NotImplementedError(f"Unsupported statement type: {type(stmt)}")

    async def _close_impl(self) -> None:
        try:
            await asyncio.to_thread(self._c.close)
        except Exception:
            pass
