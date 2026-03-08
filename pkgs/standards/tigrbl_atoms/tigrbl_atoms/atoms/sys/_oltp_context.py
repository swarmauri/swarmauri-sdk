from __future__ import annotations

import uuid
from typing import Any, Mapping, Optional, Sequence

try:  # pragma: no cover
    from sqlalchemy.inspection import inspect as _sa_inspect  # type: ignore
except Exception:  # pragma: no cover
    _sa_inspect = None  # type: ignore

try:  # pragma: no cover
    from sqlalchemy.sql import ClauseElement as SAClause  # type: ignore
except Exception:  # pragma: no cover
    SAClause = None  # type: ignore


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)


def payload(ctx: Mapping[str, Any]) -> Any:
    temp = _ctx_get(ctx, "temp", None)
    raw = _ctx_get(ctx, "payload", None)
    if isinstance(temp, Mapping):
        assembled_values = temp.get("assembled_values")
        if isinstance(assembled_values, Mapping) and isinstance(raw, Mapping):
            merged = dict(raw)
            merged.update(assembled_values)
            return merged

    if isinstance(raw, Mapping):
        return raw
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        return raw
    return {}


def db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db")


def request(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "request")


def path_params(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    params = _ctx_get(ctx, "path_params", None)
    if isinstance(params, Mapping):
        return params

    temp = _ctx_get(ctx, "temp", None)
    if isinstance(temp, Mapping):
        route = temp.get("route")
        if isinstance(route, Mapping):
            route_params = route.get("path_params")
            if isinstance(route_params, Mapping):
                return route_params
    return {}


def _pk_name(model: type) -> str:
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
            cols = [col for col in cols_iter] if cols_iter is not None else []
            if len(cols) == 1:
                col = cols[0]
                name = getattr(col, "key", None) or getattr(col, "name", None)
                if isinstance(name, str) and name:
                    return name
        except Exception:
            pass
    return "id"


def _pk_type_info(model: type) -> tuple[Optional[type], Optional[Any]]:
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
                cols = [item for item in cols_iter] if cols_iter is not None else []
                if len(cols) == 1:
                    col = cols[0]
            except Exception:
                col = None

    if col is None:
        return (None, None)

    try:
        col_type = getattr(col, "type", None)
    except Exception:
        col_type = None

    py_t = None
    try:
        py_t = getattr(col_type, "python_type", None)
    except Exception:
        py_t = None

    return (py_t, col_type)


def _is_uuid_type(py_t: Optional[type], sa_type: Optional[Any]) -> bool:
    if py_t is uuid.UUID:
        return True
    try:
        if getattr(sa_type, "as_uuid", False):
            return True
    except Exception:
        pass
    try:
        type_name = type(sa_type).__name__.lower() if sa_type is not None else ""
        if "uuid" in type_name:
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


def _is_clause(value: Any) -> bool:
    return SAClause is not None and isinstance(value, SAClause)  # type: ignore[truthy-bool]


def ident(model: type, ctx: Mapping[str, Any]) -> Any:
    model_payload = payload(ctx)
    model_path = path_params(ctx)
    pk = _pk_name(model)

    candidates: list[tuple[Mapping[str, Any], str]] = [
        (model_path, pk),
        (model_payload, pk),
        (model_path, "id"),
        (model_payload, "id"),
        (model_path, "item_id"),
        (model_payload, "item_id"),
    ]
    if pk != "id":
        candidates.extend([(model_path, f"{pk}_id"), (model_payload, f"{pk}_id")])
    candidates.append((model_payload, "ident"))

    for source, key in candidates:
        try:
            value = source.get(key)
        except Exception:
            value = None
        if value is None or _is_clause(value):
            continue
        try:
            return _coerce_ident_to_pk_type(model, value)
        except Exception as exc:
            raise TypeError(f"Invalid identifier for '{pk}': {value!r}") from exc

    raise TypeError(f"Missing identifier '{pk}' in path or payload")


__all__ = ["db", "ident", "path_params", "payload", "request"]
