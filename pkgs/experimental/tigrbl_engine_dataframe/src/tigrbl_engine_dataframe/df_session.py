from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import pandas as pd

# Prefer Tigrbl's base; provide a minimal fallback if missing (package can still import)
try:
    from tigrbl.session.base import TigrblSessionBase
except Exception:  # fallback minimal ABC
    from abc import ABC, abstractmethod

    class TigrblSessionBase(ABC):
        def __init__(self, spec=None):
            self._spec = spec
            self._open = False
            self._dirty = False

        async def begin(self):
            self._open = True

        async def commit(self):
            self._open = False
            self._dirty = False

        async def rollback(self):
            self._open = False
            self._dirty = False

        def in_transaction(self):
            return self._open

        async def run_sync(self, fn):
            rv = fn(self)
            return await rv if hasattr(rv, "__await__") else rv

        def apply_spec(self, spec):
            self._spec = spec

        # abstract CRUD/lifecycle
        @abstractmethod
        def _add_impl(self, obj): ...
        @abstractmethod
        async def _delete_impl(self, obj): ...
        @abstractmethod
        async def _flush_impl(self): ...
        @abstractmethod
        async def _refresh_impl(self, obj): ...
        @abstractmethod
        async def _get_impl(self, model, ident): ...
        @abstractmethod
        async def _execute_impl(self, stmt): ...
        @abstractmethod
        async def _tx_begin_impl(self): ...
        @abstractmethod
        async def _tx_commit_impl(self): ...
        @abstractmethod
        async def _tx_rollback_impl(self): ...
        @abstractmethod
        async def _close_impl(self): ...
        # public CRUD wrappers
        def add(self, obj):
            self._dirty = True
            return self._add_impl(obj)

        async def delete(self, obj):
            self._dirty = True
            return await self._delete_impl(obj)

        async def flush(self):
            return await self._flush_impl()

        async def refresh(self, obj):
            return await self._refresh_impl(obj)

        async def get(self, model, ident):
            return await self._get_impl(model, ident)

        async def execute(self, stmt):
            return await self._execute_impl(stmt)

        async def close(self):
            return await self._close_impl()


try:
    from tigrbl.session.spec import SessionSpec
except Exception:

    class SessionSpec:
        def __init__(self, isolation=None, read_only=None):
            self.isolation = isolation
            self.read_only = read_only


try:
    from tigrbl.core.crud.helpers.model import _single_pk_name, _model_columns
except Exception:
    # Minimal fallbacks
    def _single_pk_name(model):
        return "id"

    def _model_columns(model):
        return getattr(model, "__annotations__", {}) or {"id": int}


try:
    from tigrbl.core.crud.helpers import NoResultFound
except Exception:

    class NoResultFound(Exception):
        pass


from .df_engine import DataFrameCatalog

# ---- Result facades compatible with Tigrbl CRUD ----


class _ScalarResult:
    def __init__(self, items: Sequence[Any]) -> None:
        self._items = list(items)

    def scalars(self) -> "_ScalarResult":
        return self

    def all(self) -> List[Any]:
        return list(self._items)

    def scalar_one(self) -> Any:
        if len(self._items) != 1:
            raise NoResultFound("expected exactly one row")
        return self._items[0]


class _ExecuteResult(_ScalarResult):
    rowcount: int = 0


# ---- Transactional DataFrame Session ----


class TransactionalDataFrameSession(TigrblSessionBase):
    """Native-transaction session over pandas DataFrames."""

    def __init__(
        self, catalog: DataFrameCatalog, spec: Optional[SessionSpec] = None
    ) -> None:
        super().__init__(spec)
        self._cat = catalog
        self._snap: Dict[str, pd.DataFrame] = {}
        self._snap_ver: Dict[str, int] = {}
        self._puts: Dict[Tuple[type, Any], Dict[str, Any]] = {}
        self._dels: set[Tuple[type, Any]] = set()

    # ---- lifecycle / async marker ----
    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        out = fn(self)
        return await out if hasattr(out, "__await__") else out

    # ---- TX primitives ----
    async def _tx_begin_impl(self) -> None:
        self._snap.clear()
        self._snap_ver.clear()
        self._puts.clear()
        self._dels.clear()

    async def _tx_commit_impl(self) -> None:
        iso = (self._spec.isolation if self._spec else None) or "read_committed"
        # Conflict detection (coarse, per-table)
        if iso in ("repeatable_read", "snapshot", "serializable"):
            for tbl, ver in self._snap_ver.items():
                if self._cat.table_ver.get(tbl, 0) != ver:
                    raise RuntimeError(f"transaction conflict on table '{tbl}'")

        # Apply mutations atomically
        with self._cat.lock:
            # deletes
            dels_by_tbl: Dict[str, List[Any]] = {}
            for model, ident in self._dels:
                tbl = self._table(model)
                dels_by_tbl.setdefault(tbl, []).append(ident)
            for tbl, idents in dels_by_tbl.items():
                pk = self._pk_of(tbl)
                live = self._cat.get_live(tbl)
                if pk in live.columns and not live.empty:
                    self._cat.tables[tbl] = live[~live[pk].isin(idents)].copy()
                self._cat.bump(tbl)

            # upserts
            puts_by_tbl: Dict[str, List[Dict[str, Any]]] = {}
            for (model, _), row in self._puts.items():
                puts_by_tbl.setdefault(self._table(model), []).append(row)
            for tbl, rows in puts_by_tbl.items():
                pk = self._pk_of(tbl)
                live = self._cat.get_live(tbl)
                df_new = pd.DataFrame(rows)
                if df_new.empty:
                    continue
                if pk not in df_new.columns:
                    raise RuntimeError(f"missing pk '{pk}' for table '{tbl}'")
                if live.empty:
                    combined = df_new.copy()
                else:
                    combined = live[~live[pk].isin(df_new[pk])].copy()
                    combined = pd.concat([combined, df_new], ignore_index=True)
                self._cat.tables[tbl] = combined
                self._cat.bump(tbl)

        self._puts.clear()
        self._dels.clear()

    async def _tx_rollback_impl(self) -> None:
        self._snap.clear()
        self._snap_ver.clear()
        self._puts.clear()
        self._dels.clear()

    # ---- CRUD primitives ----
    def _add_impl(self, obj: Any) -> Any:
        model = obj.__class__
        pk = _single_pk_name(model)
        ident = getattr(obj, pk)
        if ident is None:
            raise ValueError(f"primary key {pk!r} must be set")
        row = {c: getattr(obj, c, None) for c in _model_columns(model)}
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
        for c in _model_columns(obj.__class__):
            setattr(obj, c, getattr(fresh, c, None))

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        row = self._puts.get((model, ident))
        if row is not None:
            return self._inflate(model, row)
        if (model, ident) in self._dels:
            return None
        df = self._frame_for(model)
        pk = _single_pk_name(model)
        if pk not in df.columns or df.empty:
            return None
        m = df[df[pk] == ident]
        if m.empty:
            return None
        return self._inflate(model, m.iloc[0].to_dict())

    async def _execute_impl(self, stmt: Any) -> Any:
        kind = type(stmt).__name__.lower()
        if "select" in kind:
            model, where, order, limit, offset = self._decompose_select(stmt)
            items = self._scan_model(model)
            items = [o for o in items if self._matches_obj(o, where)]
            items = self._order_slice(items, order, limit, offset)
            return _ExecuteResult(items)
        if "delete" in kind:
            model, where = self._decompose_delete(stmt)
            items = self._scan_model(model)
            items = [o for o in items if self._matches_obj(o, where)]
            for o in items:
                pk = _single_pk_name(model)
                ident = getattr(o, pk)
                self._puts.pop((model, ident), None)
                self._dels.add((model, ident))
            res = _ExecuteResult([])
            res.rowcount = len(items)
            return res
        raise NotImplementedError(f"Unsupported statement: {type(stmt)}")

    async def _close_impl(self) -> None:
        return

    # ---- helpers ----
    def _table(self, model: type) -> str:
        return getattr(model, "__tablename__", None) or model.__name__

    def _pk_of(self, table: str) -> str:
        if table in self._cat.pks:
            return self._cat.pks[table]
        live = self._cat.get_live(table)
        if "id" in live.columns:
            return "id"
        raise RuntimeError(f"primary key for table '{table}' is unknown")

    def _frame_for(self, model: type) -> pd.DataFrame:
        table = self._table(model)
        iso = (self._spec.isolation if self._spec else None) or "read_committed"
        if (
            iso in ("repeatable_read", "snapshot", "serializable")
            and table not in self._snap
        ):
            live = self._cat.get_live(table)
            self._snap[table] = live.copy(deep=True)
            self._snap_ver[table] = self._cat.table_ver.get(table, 0)
        return (
            self._snap.get(table) if table in self._snap else self._cat.get_live(table)
        )

    def _inflate(self, model: type, data: Mapping[str, Any]) -> Any:
        obj = model()
        for c in _model_columns(model):
            if c in data:
                setattr(obj, c, data[c])
        return obj

    def _scan_model(self, model: type) -> List[Any]:
        df = self._frame_for(model)
        out: List[Any] = []
        if not df.empty:
            for _, row in df.iterrows():
                out.append(self._inflate(model, row.to_dict()))
        # overlay upserts / deletes
        pk = _single_pk_name(model)
        by_id = {getattr(o, pk): o for o in out}
        for (m, ident), row in self._puts.items():
            if m is model:
                by_id[ident] = self._inflate(model, row)
        for m, ident in list(self._dels):
            if m is model:
                by_id.pop(ident, None)
        return list(by_id.values())

    # ---- duck-typed stmt parsing (eq/IN/order/limit/offset) ----
    def _decompose_select(
        self, stmt: Any
    ) -> Tuple[
        type,
        list[Tuple[str, str, Any]],
        list[Tuple[str, str]],
        Optional[int],
        Optional[int],
    ]:
        model = self._extract_model(stmt)
        where = self._extract_predicates(stmt)
        order = self._extract_order_by(stmt)
        limit = self._extract_int(stmt, ["_limit", "_limit_clause", "limit"])
        offset = self._extract_int(stmt, ["_offset", "_offset_clause", "offset"])
        return model, where, order, limit, offset

    def _decompose_delete(self, stmt: Any) -> Tuple[type, list[Tuple[str, str, Any]]]:
        model = self._extract_model(stmt)
        where = self._extract_predicates(stmt)
        return model, where

    def _extract_model(self, stmt: Any) -> type:
        for a in ("_from_objects", "_froms", "froms"):
            v = getattr(stmt, a, None)
            if v:
                t = v[0] if isinstance(v, (list, tuple)) else v
                name = getattr(t, "name", None)
                if isinstance(name, str):
                    for cls in object.__subclasses__(object):
                        if getattr(cls, "__tablename__", None) == name:
                            return cls
        rc = getattr(stmt, "_raw_columns", None) or getattr(stmt, "columns", None)
        if rc:
            ent = rc[0]
            table = getattr(ent, "table", None)
            name = getattr(table, "name", None)
            if name:
                for cls in object.__subclasses__(object):
                    if getattr(cls, "__tablename__", None) == name:
                        return cls
        raise RuntimeError("Cannot resolve model from statement")

    def _extract_predicates(self, stmt: Any) -> list[Tuple[str, str, Any]]:
        where = getattr(stmt, "whereclause", None) or getattr(
            stmt, "_whereclause", None
        )
        if where is None:
            return []
        parts = (
            getattr(where, "clauses", None)
            or getattr(where, "get_children", lambda: [])()
        )
        nodes = list(parts) if parts else [where]
        out: list[Tuple[str, str, Any]] = []
        for n in nodes:
            left, right, op = (
                getattr(n, "left", None),
                getattr(n, "right", None),
                getattr(n, "operator", None),
            )
            if left is None or right is None:
                continue
            name = getattr(left, "key", None) or getattr(left, "name", None)
            if name is None:
                continue
            opname = getattr(op, "__name__", str(op))
            if "eq" in opname:
                val = (
                    getattr(right, "value", None)
                    if hasattr(right, "value")
                    else getattr(right, "literal", None)
                )
                out.append((str(name), "eq", val))
                continue
            rclauses = getattr(right, "clauses", None)
            if rclauses is not None and "in" in opname:
                vals = [
                    getattr(lit, "value", None)
                    if hasattr(lit, "value")
                    else getattr(lit, "literal", None)
                    for lit in rclauses
                ]
                out.append((str(name), "in", vals))
        return out

    def _extract_order_by(self, stmt: Any) -> list[Tuple[str, str]]:
        order = getattr(stmt, "_order_by_clause", None) or getattr(
            stmt, "_order_by_clauses", None
        )
        if not order:
            return []
        clauses = getattr(order, "clauses", None) or order
        clauses = clauses if isinstance(clauses, (list, tuple)) else [clauses]
        for ob in clauses:
            col = (
                getattr(ob, "element", None)
                or getattr(ob, "this", None)
                or getattr(ob, "expr", None)
            )
            name = getattr(col, "key", None) or getattr(col, "name", None)
            direction = "desc" if "desc" in type(ob).__name__.lower() else "asc"
            if name:
                return [(str(name), direction)]
        return []

    def _extract_int(self, stmt: Any, names: Sequence[str]) -> Optional[int]:
        for n in names:
            v = getattr(stmt, n, None)
            if v is None:
                continue
            try:
                return int(v)
            except Exception:
                val = getattr(v, "value", None)
                if val is not None:
                    try:
                        return int(val)
                    except Exception:
                        pass
        return None

    def _matches_obj(self, obj: Any, where: list[Tuple[str, str, Any]]) -> bool:
        for name, op, val in where:
            dv = getattr(obj, name, None)
            if op == "eq" and dv != val:
                return False
            if op == "in" and dv not in set(val):
                return False
        return True

    def _order_slice(
        self,
        items: List[Any],
        order: list[Tuple[str, str]],
        limit: Optional[int],
        offset: Optional[int],
    ) -> List[Any]:
        if order:
            col, direction = order[0]
            items.sort(
                key=lambda o: getattr(o, col, None), reverse=(direction == "desc")
            )
        if isinstance(offset, int):
            items = items[max(0, offset) :]
        if isinstance(limit, int):
            items = items[: max(0, limit)]
        return items
