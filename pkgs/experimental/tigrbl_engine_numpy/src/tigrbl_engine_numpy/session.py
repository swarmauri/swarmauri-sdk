from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

import numpy as np
from tigrbl.core.crud.helpers import NoResultFound
from tigrbl.core.crud.helpers.model import _model_columns, _single_pk_name
from tigrbl.session.base import TigrblSessionBase

from .engine import atomic_save_array

if TYPE_CHECKING:
    from .engine import NumpyEngine


class _ScalarResult:
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


class _ExecuteResult(_ScalarResult):
    rowcount: int = 0


class NumpySession(TigrblSessionBase):
    """Tigrbl first-class session for a single NumPy-backed table database."""

    def __init__(self, engine: "NumpyEngine") -> None:
        super().__init__()
        self._engine = engine
        self._puts: dict[tuple[type, Any], dict[str, Any]] = {}
        self._dels: set[tuple[type, Any]] = set()

    def array(self) -> np.ndarray:
        return np.asarray(self._engine.array).copy()

    def to_records(self) -> list[dict[str, Any]]:
        return [row.copy() for row in self._engine.catalog.rows]

    def to_dataframe(self) -> list[dict[str, Any]]:
        return self.to_records()

    async def _tx_begin_impl(self) -> None:
        self._puts.clear()
        self._dels.clear()

    async def _tx_commit_impl(self) -> None:
        with self._engine.catalog.lock:
            rows = [row.copy() for row in self._engine.catalog.rows]
            pk = self._engine.pk
            by_pk = {row.get(pk): row for row in rows}

            for _, ident in self._dels:
                by_pk.pop(ident, None)

            for (_, ident), row in self._puts.items():
                by_pk[ident] = row.copy()

            ordered = sorted(by_pk.values(), key=lambda row: str(row.get(pk)))
            self._engine.catalog.rows = ordered
            self._engine.catalog.bump()
            self._engine.array = np.asarray(
                [[row.get(col) for col in self._engine.columns] for row in ordered]
            )

            if self._engine.path:
                atomic_save_array(
                    self._engine.array, self._engine.path, npz_key=self._engine.npz_key
                )

        self._puts.clear()
        self._dels.clear()

    async def _tx_rollback_impl(self) -> None:
        self._puts.clear()
        self._dels.clear()

    def _add_impl(self, obj: Any) -> Any:
        model = obj.__class__
        pk = _single_pk_name(model)
        ident = getattr(obj, pk)
        if ident is None:
            raise ValueError(f"primary key {pk!r} must be set")
        row = {column: getattr(obj, column, None) for column in _model_columns(model)}
        self._puts[(model, ident)] = row
        self._dels.discard((model, ident))
        return None

    async def _delete_impl(self, obj: Any) -> None:
        model = obj.__class__
        pk = _single_pk_name(model)
        ident = getattr(obj, pk)
        self._puts.pop((model, ident), None)
        self._dels.add((model, ident))

    async def _flush_impl(self) -> None:
        return

    async def _refresh_impl(self, obj: Any) -> None:
        pk = _single_pk_name(obj.__class__)
        ident = getattr(obj, pk)
        fresh = await self._get_impl(obj.__class__, ident)
        if fresh is None:
            return
        for column in _model_columns(obj.__class__):
            setattr(obj, column, getattr(fresh, column, None))

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        row = self._puts.get((model, ident))
        if row is not None:
            return self._inflate(model, row)
        if (model, ident) in self._dels:
            return None

        pk = _single_pk_name(model)
        for current in self._engine.catalog.rows:
            if current.get(pk) == ident:
                return self._inflate(model, current)
        return None

    async def _execute_impl(self, stmt: Any) -> Any:
        kind = type(stmt).__name__.lower()
        if "select" in kind:
            model = self._extract_model(stmt)
            where = self._extract_predicates(stmt)
            items = [
                obj for obj in self._scan_model(model) if self._matches_obj(obj, where)
            ]
            return _ExecuteResult(items)
        if "delete" in kind:
            model = self._extract_model(stmt)
            where = self._extract_predicates(stmt)
            items = [
                obj for obj in self._scan_model(model) if self._matches_obj(obj, where)
            ]
            pk = _single_pk_name(model)
            for obj in items:
                ident = getattr(obj, pk)
                self._puts.pop((model, ident), None)
                self._dels.add((model, ident))
            result = _ExecuteResult([])
            result.rowcount = len(items)
            return result
        raise NotImplementedError(f"Unsupported statement: {type(stmt)}")

    async def _close_impl(self) -> None:
        return

    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        out = fn(self)
        return await out if hasattr(out, "__await__") else out

    def _inflate(self, model: type, data: Mapping[str, Any]) -> Any:
        obj = model()
        for column in _model_columns(model):
            if column in data:
                setattr(obj, column, data[column])
        return obj

    def _scan_model(self, model: type) -> list[Any]:
        pk = _single_pk_name(model)
        merged = {row.get(pk): row.copy() for row in self._engine.catalog.rows}
        for (current_model, ident), row in self._puts.items():
            if current_model is model:
                merged[ident] = row.copy()
        for current_model, ident in self._dels:
            if current_model is model:
                merged.pop(ident, None)
        return [self._inflate(model, row) for row in merged.values()]

    def _extract_model(self, stmt: Any) -> type:
        for attr in ("_propagate_attrs", "_from_obj"):
            value = getattr(stmt, attr, None)
            if isinstance(value, dict):
                plugin_subject = value.get("plugin_subject")
                if plugin_subject is not None:
                    return plugin_subject.class_
        columns = getattr(stmt, "_raw_columns", None) or getattr(stmt, "columns", None)
        if columns:
            entity = columns[0]
            model = getattr(entity, "entity", None)
            if model is not None:
                return model
        raise RuntimeError("Cannot resolve model from statement")

    def _extract_predicates(self, stmt: Any) -> list[tuple[str, str, Any]]:
        where = getattr(stmt, "whereclause", None) or getattr(
            stmt, "_whereclause", None
        )
        if where is None:
            return []
        clauses = getattr(where, "clauses", None) or [where]
        out: list[tuple[str, str, Any]] = []
        for clause in clauses:
            left = getattr(clause, "left", None)
            right = getattr(clause, "right", None)
            operator = getattr(clause, "operator", None)
            name = getattr(left, "key", None) or getattr(left, "name", None)
            if name is None:
                continue
            op_name = getattr(operator, "__name__", str(operator))
            if "eq" in op_name:
                out.append((str(name), "eq", getattr(right, "value", None)))
        return out

    def _matches_obj(self, obj: Any, where: list[tuple[str, str, Any]]) -> bool:
        for name, operator, value in where:
            if operator == "eq" and getattr(obj, name, None) != value:
                return False
        return True
