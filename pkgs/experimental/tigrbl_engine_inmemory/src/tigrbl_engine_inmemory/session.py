from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .engine import DatabaseState, InMemoryEngine, TableState


def _clone_state(base: DatabaseState) -> DatabaseState:
    return DatabaseState(tables=dict(base.tables))


def _clone_table(table: TableState) -> TableState:
    return TableState(pk=table.pk, rows=dict(table.rows), next_id=table.next_id)


@dataclass
class _Tx:
    base: DatabaseState
    work: DatabaseState
    dirty_tables: set[str]


class InMemorySession:
    def __init__(self, engine: InMemoryEngine) -> None:
        self._engine = engine
        base = engine._get_state()
        self._tx: _Tx | None = _Tx(
            base=base, work=_clone_state(base), dirty_tables=set()
        )
        self._closed = False

    def close(self) -> None:
        self._closed = True
        self._tx = None

    def begin(self) -> None:
        self._require_open()
        base = self._engine._get_state()
        self._tx = _Tx(base=base, work=_clone_state(base), dirty_tables=set())

    def commit(self) -> None:
        self._require_open()
        assert self._tx is not None
        self._engine._commit(self._tx.work)
        self.begin()

    def rollback(self) -> None:
        self._require_open()
        self.begin()

    def ensure_table(self, name: str, *, pk: str = "id") -> None:
        self._require_open()
        tx = self._tx
        assert tx is not None
        if name not in tx.work.tables:
            tx.work.tables[name] = TableState(pk=pk)

    def _table_for_write(self, name: str) -> TableState:
        tx = self._tx
        assert tx is not None
        if name not in tx.work.tables:
            if self._engine.enforce_schema:
                raise KeyError(f"unknown table: {name}")
            tx.work.tables[name] = TableState(pk="id")
            tx.dirty_tables.add(name)
            return tx.work.tables[name]
        if name not in tx.dirty_tables:
            tx.work.tables[name] = _clone_table(tx.work.tables[name])
            tx.dirty_tables.add(name)
        return tx.work.tables[name]

    def _table_for_read(self, name: str) -> TableState:
        tx = self._tx
        assert tx is not None
        try:
            return tx.work.tables[name]
        except KeyError:
            raise KeyError(f"unknown table: {name}") from None

    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        self._require_open()
        table_state = self._table_for_write(table)
        pk = table_state.pk
        out = dict(row)
        if pk not in out:
            out[pk] = table_state.next_id
            table_state.next_id += 1
        key = out[pk]
        table_state.rows[key] = out
        return dict(out)

    def get(self, table: str, pk_value: Any) -> dict[str, Any] | None:
        self._require_open()
        table_state = self._table_for_read(table)
        row = table_state.rows.get(pk_value)
        return dict(row) if row is not None else None

    def update(
        self, table: str, pk_value: Any, patch: dict[str, Any]
    ) -> dict[str, Any] | None:
        self._require_open()
        table_state = self._table_for_write(table)
        current = table_state.rows.get(pk_value)
        if current is None:
            return None
        next_row = dict(current)
        next_row.update(patch)
        table_state.rows[pk_value] = next_row
        return dict(next_row)

    def delete(self, table: str, pk_value: Any) -> bool:
        self._require_open()
        table_state = self._table_for_write(table)
        return table_state.rows.pop(pk_value, None) is not None

    def query(
        self,
        table: str,
        pred: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[dict[str, Any]]:
        self._require_open()
        table_state = self._table_for_read(table)
        rows: Iterable[dict[str, Any]] = table_state.rows.values()
        if pred is not None:
            rows = (row for row in rows if pred(row))
        return [dict(row) for row in rows]

    def _require_open(self) -> None:
        if self._closed or self._tx is None:
            raise RuntimeError("session is closed")


class AsyncInMemorySession(InMemorySession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
