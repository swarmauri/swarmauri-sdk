# autoapi/v3/bindings/handlers/identifiers.py
from __future__ import annotations
import logging

import uuid
from typing import Any, Mapping, Optional

from .ctx import _ctx_payload, _ctx_path_params

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/handlers/identifiers")

try:  # pragma: no cover
    from sqlalchemy.inspection import inspect as _sa_inspect  # type: ignore
except Exception:  # pragma: no cover
    _sa_inspect = None  # type: ignore
try:  # pragma: no cover
    from sqlalchemy.sql import ClauseElement as SAClause  # type: ignore
except Exception:  # pragma: no cover
    SAClause = None  # type: ignore


def _pk_name(model: type) -> str:
    """Best-effort primary-key column name."""
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            if len(pk_cols) == 1:
                col = pk_cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass

    table = getattr(model, "__table__", None)
    if table is not None:
        try:
            pk = getattr(table, "primary_key", None)
            cols_iter = getattr(pk, "columns", None)
            cols = [c for c in cols_iter] if cols_iter is not None else []
            if len(cols) == 1:
                col = cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass

    return "id"


def _pk_type_info(model: type) -> tuple[Optional[type], Optional[Any]]:
    """Return (python_type, sqlatype_instance) for the PK column if discoverable."""
    col = None
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            if len(pk_cols) == 1:
                col = pk_cols[0]
        except Exception:
            col = None

    if col is None:
        table = getattr(model, "__table__", None)
        if table is not None:
            try:
                pk = getattr(table, "primary_key", None)
                cols_iter = getattr(pk, "columns", None)
                cols = [c for c in cols_iter] if cols_iter is not None else []
                if len(cols) == 1:
                    col = cols[0]
            except Exception:
                col = None

    if col is None:
        return (None, None)

    try:
        coltype = getattr(col, "type", None)
    except Exception:
        coltype = None

    py_t = None
    try:
        py_t = getattr(coltype, "python_type", None)
    except Exception:
        py_t = None

    return (py_t, coltype)


def _looks_like_uuid_string(s: str) -> bool:
    if not isinstance(s, str):
        return False
    try:
        uuid.UUID(s)
        return True
    except Exception:
        return False


def _is_uuid_type(py_t: Optional[type], sa_type: Optional[Any]) -> bool:
    if py_t is uuid.UUID:
        return True
    try:
        if getattr(sa_type, "as_uuid", False):
            return True
    except Exception:
        pass
    try:
        tname = type(sa_type).__name__.lower() if sa_type is not None else ""
        if "uuid" in tname:
            return True
    except Exception:
        pass
    return False


def _coerce_ident_to_pk_type(model: type, value: Any) -> Any:
    py_t, sa_t = _pk_type_info(model)
    if SAClause is not None and isinstance(value, SAClause):  # pragma: no cover
        return value
    if _is_uuid_type(py_t, sa_t):
        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, str):
            return uuid.UUID(value)
        if isinstance(value, (bytes, bytearray)) and len(value) == 16:
            return uuid.UUID(bytes=bytes(value))
        if _looks_like_uuid_string(str(value)):
            return uuid.UUID(str(value))
        return value
    if py_t is int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception:
            return value
    return value


def _is_clause(x: Any) -> bool:
    return SAClause is not None and isinstance(x, SAClause)  # type: ignore[truthy-bool]


def _resolve_ident(model: type, ctx: Mapping[str, Any]) -> Any:
    payload = _ctx_payload(ctx)
    path = _ctx_path_params(ctx)
    pk = _pk_name(model)

    candidates_keys = [
        (path, pk),
        (payload, pk),
        (path, "id"),
        (payload, "id"),
        (path, "item_id"),
        (payload, "item_id"),
    ]
    if pk != "id":
        candidates_keys.extend(
            [
                (path, f"{pk}_id"),
                (payload, f"{pk}_id"),
            ]
        )
    candidates_keys.append((payload, "ident"))

    for source, key in candidates_keys:
        try:
            v = source.get(key)  # type: ignore[call-arg]
        except Exception:
            v = None
        if v is None:
            continue
        if _is_clause(v):
            continue
        try:
            return _coerce_ident_to_pk_type(model, v)
        except Exception:
            raise TypeError(f"Invalid identifier for '{pk}': {v!r}")

    raise TypeError(f"Missing identifier '{pk}' in path or payload")


__all__ = [
    "_pk_name",
    "_pk_type_info",
    "_resolve_ident",
    "_coerce_ident_to_pk_type",
]
