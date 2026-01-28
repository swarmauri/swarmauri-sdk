# tigrbl/v3/bindings/handlers/identifiers.py
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
    logger.debug("Resolving PK name for %s", model.__name__)
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            logger.debug("SQLAlchemy mapper found %d PK cols", len(pk_cols))
            if len(pk_cols) == 1:
                col = pk_cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                logger.debug("PK name via mapper: %s", name)
                if isinstance(name, str) and name:
                    return name
        except Exception as exc:
            logger.debug("SQLAlchemy inspection failed: %s", exc)

    table = getattr(model, "__table__", None)
    if table is not None:
        try:
            pk = getattr(table, "primary_key", None)
            cols_iter = getattr(pk, "columns", None)
            cols = [c for c in cols_iter] if cols_iter is not None else []
            logger.debug("Table inspection found %d PK cols", len(cols))
            if len(cols) == 1:
                col = cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                logger.debug("PK name via table: %s", name)
                if isinstance(name, str) and name:
                    return name
        except Exception as exc:
            logger.debug("Table inspection failed: %s", exc)

    logger.debug("Falling back to default PK name 'id'")
    return "id"


def _pk_type_info(model: type) -> tuple[Optional[type], Optional[Any]]:
    """Return (python_type, sqlatype_instance) for the PK column if discoverable."""
    logger.debug("Resolving PK type info for %s", model.__name__)
    col = None
    if _sa_inspect is not None:
        try:
            mapper = _sa_inspect(model)
            pk_cols = list(getattr(mapper, "primary_key", []) or [])
            logger.debug("Mapper returned %d PK cols", len(pk_cols))
            if len(pk_cols) == 1:
                col = pk_cols[0]
        except Exception as exc:
            logger.debug("Mapper inspection failed: %s", exc)
            col = None

    if col is None:
        table = getattr(model, "__table__", None)
        if table is not None:
            try:
                pk = getattr(table, "primary_key", None)
                cols_iter = getattr(pk, "columns", None)
                cols = [c for c in cols_iter] if cols_iter is not None else []
                logger.debug("Table inspection yielded %d PK cols", len(cols))
                if len(cols) == 1:
                    col = cols[0]
            except Exception as exc:
                logger.debug("Table inspection failed: %s", exc)
                col = None

    if col is None:
        logger.debug("PK column not found; returning (None, None)")
        return (None, None)

    try:
        coltype = getattr(col, "type", None)
    except Exception as exc:
        logger.debug("Failed to get column type: %s", exc)
        coltype = None

    py_t = None
    try:
        py_t = getattr(coltype, "python_type", None)
    except Exception as exc:
        logger.debug("Failed to get python_type: %s", exc)
        py_t = None

    logger.debug("Resolved PK type info py_t=%s sa_type=%s", py_t, coltype)
    return (py_t, coltype)


def _looks_like_uuid_string(s: str) -> bool:
    if not isinstance(s, str):
        logger.debug("Value %r is not a string; cannot be UUID", s)
        return False
    try:
        uuid.UUID(s)
        logger.debug("Value %s looks like a UUID string", s)
        return True
    except Exception:
        logger.debug("Value %s is not a valid UUID string", s)
        return False


def _is_uuid_type(py_t: Optional[type], sa_type: Optional[Any]) -> bool:
    if py_t is uuid.UUID:
        logger.debug("PK python type is UUID")
        return True
    try:
        if getattr(sa_type, "as_uuid", False):
            logger.debug("SQLAlchemy type %r uses as_uuid", sa_type)
            return True
    except Exception:
        pass
    try:
        tname = type(sa_type).__name__.lower() if sa_type is not None else ""
        if "uuid" in tname:
            logger.debug("SQLAlchemy type name contains 'uuid': %s", tname)
            return True
    except Exception:
        pass
    return False


def _coerce_ident_to_pk_type(model: type, value: Any) -> Any:
    py_t, sa_t = _pk_type_info(model)
    logger.debug("Coercing identifier %r to PK type %s", value, py_t)
    if SAClause is not None and isinstance(value, SAClause):  # pragma: no cover
        logger.debug("Value is SAClause; returning as-is")
        return value
    if _is_uuid_type(py_t, sa_t):
        logger.debug("PK type identified as UUID")
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
        logger.debug("PK type identified as int")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception as exc:
            logger.debug("Failed int coercion: %s", exc)
            return value
    return value


def _is_clause(x: Any) -> bool:
    return SAClause is not None and isinstance(x, SAClause)  # type: ignore[truthy-bool]


def _resolve_ident(model: type, ctx: Mapping[str, Any]) -> Any:
    payload = _ctx_payload(ctx)
    path = _ctx_path_params(ctx)
    pk = _pk_name(model)
    logger.debug("Resolving identifier for %s using pk %s", model.__name__, pk)

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
        logger.debug("Checking candidate key '%s' → %r", key, v)
        if v is None:
            continue
        if _is_clause(v):
            logger.debug("Value for key '%s' is a clause; skipping", key)
            continue
        try:
            return _coerce_ident_to_pk_type(model, v)
        except Exception:
            logger.debug("Invalid identifier %r for pk %s", v, pk)
            raise TypeError(f"Invalid identifier for '{pk}': {v!r}")

    logger.debug("Identifier for pk %s not found", pk)
    raise TypeError(f"Missing identifier '{pk}' in path or payload")


__all__ = [
    "_pk_name",
    "_pk_type_info",
    "_resolve_ident",
    "_coerce_ident_to_pk_type",
]
