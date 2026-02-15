from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

from tigrbl.core.crud.helpers import NoResultFound
from tigrbl.core.crud.helpers.model import _model_columns, _single_pk_name
from tigrbl.session.base import TigrblSessionBase

from .engine import atomic_save_xlsx

if TYPE_CHECKING:
    from .engine import XlsxEngine


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


class XlsxSession(TigrblSessionBase):
    """Native transactional session over workbook sheets."""

    def __init__(self, engine: "XlsxEngine") -> None:
        super().__init__()
        self._engine = engine
        self._puts: dict[tuple[type, Any], dict[str, Any]] = {}
        self._dels: set[tuple[type, Any]] = set()

    def table(self, name: str) -> list[dict[str, Any]]:
        return [row.copy() for row in self._engine.catalog.get_live(name)]

    async def _tx_begin_impl(self) -> None:
        self._puts.clear()
        self._dels.clear()

    async def _tx_commit_impl(self) -> None:
        with self._engine.catalog.lock:
            touched_tables: set[str] = set()

            for model, ident in self._dels:
                table = self._table(model)
                touched_tables.add(table)
                pk = self._pk_of(table)
                live = self._engine.catalog.get_live(table)
                self._engine.catalog.tables[table] = [
                    row for row in live if row.get(pk) != ident
                ]
                self._engine.catalog.bump(table)

            for (model, ident), row in self._puts.items():
                table = self._table(model)
                touched_tables.add(table)
                pk = self._pk_of(table)
                live = self._engine.catalog.get_live(table)
                kept = [current for current in live if current.get(pk) != ident]
                kept.append(row.copy())
                self._engine.catalog.tables[table] = kept
                self._engine.catalog.bump(table)

            for table in touched_tables:
                if table in self._engine.catalog.workbook.sheetnames:
                    sheet = self._engine.catalog.workbook[table]
                else:
                    sheet = self._engine.catalog.workbook.create_sheet(table)

                rows = self._engine.catalog.get_live(table)
                columns = self._columns_for_table(table, rows)
                sheet.delete_rows(1, sheet.max_row)
                sheet.append(columns)
                for row in rows:
                    sheet.append([row.get(column) for column in columns])

            if touched_tables:
                atomic_save_xlsx(self._engine.catalog.workbook, self._engine.path)

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

        table = self._table(model)
        pk = self._pk_of(table)
        for current in self._engine.catalog.get_live(table):
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
        self._engine.catalog.workbook.close()

    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        out = fn(self)
        return await out if hasattr(out, "__await__") else out

    def _table(self, model: type) -> str:
        return getattr(model, "__tablename__", None) or model.__name__

    def _pk_of(self, table: str) -> str:
        return self._engine.catalog.pks.get(table, self._engine.pk)

    def _columns_for_table(self, table: str, rows: list[dict[str, Any]]) -> list[str]:
        if rows:
            return list(rows[0].keys())
        pk = self._pk_of(table)
        return [pk]

    def _inflate(self, model: type, data: Mapping[str, Any]) -> Any:
        obj = model()
        for column in _model_columns(model):
            if column in data:
                setattr(obj, column, data[column])
        return obj

    def _scan_model(self, model: type) -> list[Any]:
        table = self._table(model)
        pk = self._pk_of(table)
        merged = {
            row.get(pk): row.copy() for row in self._engine.catalog.get_live(table)
        }
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
