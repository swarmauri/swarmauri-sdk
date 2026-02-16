from __future__ import annotations

import os
from pathlib import Path
import tempfile
from uuid import uuid4

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

import numpy as np
from tigrbl.session.base import TigrblSessionBase

try:
    from tigrbl.session.spec import SessionSpec
except Exception:

    class SessionSpec:  # pragma: no cover - fallback
        def __init__(self, isolation=None, read_only=None):
            self.isolation = isolation
            self.read_only = read_only


try:
    from tigrbl.core.crud.helpers.model import _single_pk_name, _model_columns
except Exception:

    def _single_pk_name(model):  # pragma: no cover - fallback
        return "id"

    def _model_columns(model):  # pragma: no cover - fallback
        return getattr(model, "__annotations__", {}) or {"id": int}


if TYPE_CHECKING:
    from .engine import NumpyEngine


class _ScalarResult:
    def __init__(self, items: Sequence[Any]) -> None:
        self._items = list(items)

    def scalars(self) -> "_ScalarResult":
        return self

    def all(self) -> List[Any]:
        return list(self._items)


class _ExecuteResult(_ScalarResult):
    rowcount: int = 0


class NumpySession(TigrblSessionBase):
    """Tigrbl session for a single NumPy-backed table database."""

    def __init__(self, engine: "NumpyEngine") -> None:
        super().__init__(SessionSpec())
        self._engine = engine
        self._snap: Optional[list[dict[str, Any]]] = None
        self._snap_ver: Optional[int] = None
        self._puts: dict[tuple[type, Any], dict[str, Any]] = {}
        self._dels: set[tuple[type, Any]] = set()

    def to_records(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._engine.catalog.rows]

    def array(self) -> np.ndarray:
        rows = self.to_records()
        values = [[row.get(col) for col in self._engine.columns] for row in rows]
        return np.asarray(values, dtype=object)

    def load(
        self, file: str, *, mmap_mode: str | None = None, npz_key: str | None = None
    ) -> np.ndarray:
        loaded = np.load(file, mmap_mode=mmap_mode, allow_pickle=True)
        if isinstance(loaded, np.lib.npyio.NpzFile):
            with loaded as archive:
                key = npz_key or (archive.files[0] if len(archive.files) == 1 else None)
                if key is None:
                    raise ValueError(
                        "npz_key is required when loading multi-array .npz files"
                    )
                return np.asarray(archive[key])
        return loaded

    def memmap(
        self,
        filename: str,
        *,
        dtype: Any = np.float64,
        mode: str = "r+",
        shape: Any = None,
    ) -> np.memmap:
        valid_modes = {"r", "r+", "w+", "c"}
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {sorted(valid_modes)}")
        if mode == "w+" and shape is None:
            raise ValueError("shape is required when mode='w+'")
        return np.memmap(filename, dtype=dtype, mode=mode, shape=shape)

    def save(
        self,
        file: str | None = None,
        array: np.ndarray | None = None,
        *,
        npz_key: str | None = None,
    ) -> None:
        target = file or self._engine.catalog.path
        if not target:
            raise ValueError("A target file path is required")

        payload = self.array() if array is None else np.asarray(array)
        self._atomic_save_numpy(target, payload, npz_key=npz_key)

    def _atomic_save_numpy(
        self, file: str, array: np.ndarray, *, npz_key: str | None = None
    ) -> None:
        path = Path(file)
        directory = str(path.parent if str(path.parent) else Path("."))
        suffix = path.suffix.lower()
        if suffix not in {".npy", ".npz"}:
            raise ValueError("file must use .npy or .npz suffix")

        fd, tmp = tempfile.mkstemp(
            dir=directory,
            prefix=".tmp_",
            suffix=suffix,
        )
        os.close(fd)
        try:
            if suffix == ".npz":
                key = npz_key or self._engine.catalog.npz_key or "data"
                np.savez(tmp, **{key: array})
            else:
                np.save(tmp, array)
            os.replace(tmp, str(path))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    async def run_sync(self, fn: Callable[[Any], Any]) -> Any:
        out = fn(self)
        return await out if hasattr(out, "__await__") else out

    async def _tx_begin_impl(self) -> None:
        self._snap = [dict(row) for row in self._engine.catalog.rows]
        self._snap_ver = self._engine.catalog.table_ver
        self._puts.clear()
        self._dels.clear()

    async def _tx_commit_impl(self) -> None:
        iso = (self._spec.isolation if self._spec else None) or "read_committed"
        if (
            iso in ("repeatable_read", "snapshot", "serializable")
            and self._snap_ver is not None
        ):
            if self._engine.catalog.table_ver != self._snap_ver:
                raise RuntimeError("transaction conflict on table")

        with self._engine.catalog.lock:
            live = list(self._engine.catalog.rows)
            for model, ident in self._dels:
                pk = _single_pk_name(model)
                live = [row for row in live if row.get(pk) != ident]
            for (model, ident), row in self._puts.items():
                pk = _single_pk_name(model)
                live = [existing for existing in live if existing.get(pk) != ident]
                live.append(dict(row))
            self._engine.catalog.rows = live
            self._engine.catalog.bump()
            if self._engine.catalog.path:
                self._atomic_save_numpy(
                    self._engine.catalog.path,
                    self.array(),
                    npz_key=self._engine.catalog.npz_key,
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
            ident = uuid4()
            setattr(obj, pk, ident)
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
        pk = _single_pk_name(model)
        for record in self._engine.catalog.rows:
            if record.get(pk) == ident:
                return self._inflate(model, record)
        return None

    async def _execute_impl(self, stmt: Any) -> Any:
        kind = type(stmt).__name__.lower()
        if "select" in kind:
            model, where, order, limit, offset = self._decompose_select(stmt)
            items = self._scan_model(model)
            items = [o for o in items if self._matches_obj(o, where)]
            return _ExecuteResult(self._order_slice(items, order, limit, offset))
        if "delete" in kind:
            model, where = self._decompose_delete(stmt)
            items = [o for o in self._scan_model(model) if self._matches_obj(o, where)]
            for obj in items:
                pk = _single_pk_name(model)
                ident = getattr(obj, pk)
                self._puts.pop((model, ident), None)
                self._dels.add((model, ident))
            res = _ExecuteResult([])
            res.rowcount = len(items)
            return res
        raise NotImplementedError(f"Unsupported statement: {type(stmt)}")

    async def _close_impl(self) -> None:
        return

    def _inflate(self, model: type, data: Mapping[str, Any]) -> Any:
        obj = model()
        for c in _model_columns(model):
            if c in data:
                setattr(obj, c, data[c])
        return obj

    def _scan_model(self, model: type) -> List[Any]:
        out = [self._inflate(model, row) for row in self._engine.catalog.rows]
        pk = _single_pk_name(model)
        by_id = {getattr(obj, pk): obj for obj in out}
        for (m, ident), row in self._puts.items():
            if m is model:
                by_id[ident] = self._inflate(model, row)
        for m, ident in self._dels:
            if m is model:
                by_id.pop(ident, None)
        return list(by_id.values())

    def _decompose_select(
        self, stmt: Any
    ) -> Tuple[
        type,
        list[Tuple[str, str, Any]],
        list[Tuple[str, str]],
        Optional[int],
        Optional[int],
    ]:
        return (
            self._extract_model(stmt),
            self._extract_predicates(stmt),
            self._extract_order_by(stmt),
            self._extract_int(stmt, ["_limit", "_limit_clause", "limit"]),
            self._extract_int(stmt, ["_offset", "_offset_clause", "offset"]),
        )

    def _decompose_delete(self, stmt: Any) -> Tuple[type, list[Tuple[str, str, Any]]]:
        return self._extract_model(stmt), self._extract_predicates(stmt)

    def _extract_model(self, stmt: Any) -> type:
        descs = getattr(stmt, "column_descriptions", None) or []
        for desc in descs:
            entity = desc.get("entity") if isinstance(desc, dict) else None
            if isinstance(entity, type):
                return entity

        def _all_subclasses(base: type) -> list[type]:
            out: list[type] = []
            stack = list(base.__subclasses__())
            while stack:
                cls = stack.pop()
                out.append(cls)
                stack.extend(cls.__subclasses__())
            return out

        def _find_by_table(name: str) -> type | None:
            for cls in _all_subclasses(object):
                if getattr(cls, "__tablename__", None) == name:
                    return cls
            return None

        for attr_name in ("_from_objects", "_froms", "froms"):
            value = getattr(stmt, attr_name, None)
            if value is not None:
                table = value[0] if isinstance(value, (list, tuple)) else value
                name = getattr(table, "name", None)
                if isinstance(name, str):
                    found = _find_by_table(name)
                    if found is not None:
                        return found
        raise RuntimeError("Cannot resolve model from statement")

    def _extract_predicates(self, stmt: Any) -> list[Tuple[str, str, Any]]:
        where = getattr(stmt, "whereclause", None) or getattr(
            stmt, "_whereclause", None
        )
        if where is None:
            return []
        nodes = list(getattr(where, "clauses", None) or [where])
        out: list[Tuple[str, str, Any]] = []
        for node in nodes:
            left, right, op = (
                getattr(node, "left", None),
                getattr(node, "right", None),
                getattr(node, "operator", None),
            )
            name = getattr(left, "key", None) or getattr(left, "name", None)
            if left is None or right is None or name is None:
                continue
            opname = getattr(op, "__name__", str(op))
            if "eq" in opname:
                out.append((str(name), "eq", getattr(right, "value", None)))
        return out

    def _extract_order_by(self, stmt: Any) -> list[Tuple[str, str]]:
        order = getattr(stmt, "_order_by_clause", None)
        if order is None:
            order = getattr(stmt, "_order_by_clauses", None)
        if order is None:
            return []
        clauses = getattr(order, "clauses", None) or order
        clauses = clauses if isinstance(clauses, (list, tuple)) else [clauses]
        for clause in clauses:
            col = getattr(clause, "element", None) or getattr(clause, "this", None)
            name = getattr(col, "key", None) or getattr(col, "name", None)
            if name:
                direction = "desc" if "desc" in type(clause).__name__.lower() else "asc"
                return [(str(name), direction)]
        return []

    def _extract_int(self, stmt: Any, names: Sequence[str]) -> Optional[int]:
        for name in names:
            value = getattr(stmt, name, None)
            if value is None:
                continue
            try:
                return int(value)
            except Exception:
                literal = getattr(value, "value", None)
                if literal is not None:
                    return int(literal)
        return None

    def _matches_obj(self, obj: Any, where: list[Tuple[str, str, Any]]) -> bool:
        for name, op, value in where:
            datum = getattr(obj, name, None)
            if op == "eq" and datum != value:
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
                key=lambda obj: getattr(obj, col, None), reverse=(direction == "desc")
            )
        if isinstance(offset, int):
            items = items[max(0, offset) :]
        if isinstance(limit, int):
            items = items[: max(0, limit)]
        return items
