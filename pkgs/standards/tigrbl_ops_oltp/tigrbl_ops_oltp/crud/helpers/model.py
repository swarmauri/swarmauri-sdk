from __future__ import annotations

import datetime as dt
from functools import lru_cache
from typing import Any, Dict, Mapping, Tuple

try:
    from tigrbl_core._spec.column_spec import mro_collect_columns
except Exception:  # pragma: no cover

    def mro_collect_columns(_model: type, _cache_bust: int | None = None):
        return {}


def _colspecs_cache_token(model: type) -> tuple[int, int, int, int]:
    table = getattr(model, "__table__", None)
    cols = getattr(table, "columns", None) if table is not None else None
    try:
        col_count = len(tuple(cols)) if cols is not None else 0
    except Exception:
        col_count = 0
    return (
        id(getattr(model, "__tigrbl_colspecs__", None)),
        id(getattr(model, "__tigrbl_cols__", None)),
        id(table),
        col_count,
    )


@lru_cache(maxsize=256)
def _colspecs_cached(
    model: type, cache_token: tuple[int, int, int, int]
) -> Mapping[str, Any]:
    del cache_token
    return mro_collect_columns(model, _cache_bust=hash(_colspecs_cache_token(model)))


@lru_cache(maxsize=512)
def _excluded_schema_fields(model: type, verb: str) -> frozenset[str]:
    schema_cls = getattr(getattr(model, "schemas", None), verb, None)
    schema_in = getattr(schema_cls, "in_", None) if schema_cls else None
    model_fields = (
        getattr(schema_in, "model_fields", None) if schema_in is not None else None
    )
    if not isinstance(model_fields, Mapping):
        return frozenset()
    return frozenset(
        name
        for name, field_info in model_fields.items()
        if getattr(field_info, "exclude", False)
    )


@lru_cache(maxsize=256)
def _table_python_types(model: type) -> Mapping[str, Any]:
    table = getattr(model, "__table__", None)
    columns = getattr(table, "columns", None)
    if columns is None:
        return {}
    resolved: dict[str, Any] = {}
    for col in columns:
        try:
            py_t = getattr(getattr(col, "type", None), "python_type", None)
        except Exception:
            py_t = None
        if py_t is not None:
            resolved[getattr(col, "name", "")] = py_t
    return resolved


@lru_cache(maxsize=512)
def _requires_filtering(model: type, verb: str) -> bool:
    specs = _colspecs(model)
    if not specs:
        return False
    excluded_fields = _excluded_schema_fields(model, verb)
    if excluded_fields:
        return True
    for sp in specs.values():
        io = getattr(sp, "io", None)
        if io is None:
            continue
        if getattr(io, "in_verbs", ()) or getattr(io, "mutable_verbs", ()):
            return True
    return False


def _pk_columns(model: type) -> Tuple[Any, ...]:
    table = getattr(model, "__table__", None)
    if table is None:
        raise ValueError(f"{model.__name__} has no __table__")
    pks = tuple(table.primary_key.columns)  # type: ignore[attr-defined]
    if not pks:
        raise ValueError(f"{model.__name__} has no primary key")
    return pks


def _single_pk_name(model: type) -> str:
    pks = _pk_columns(model)
    if len(pks) != 1:
        raise NotImplementedError(
            f"{model.__name__} has composite PK; not supported by default core"
        )
    name = pks[0].name
    return name


def _coerce_pk_value(model: type, value: Any) -> Any:
    if value is None:
        return None
    try:
        col = _pk_columns(model)[0]
        py_type = col.type.python_type  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - best effort
        return value
    if isinstance(value, py_type):
        return value
    try:
        coerced = py_type(value)
        return coerced
    except Exception:  # pragma: no cover - fallback to original
        return value


def _model_columns(model: type) -> Tuple[str, ...]:
    table = getattr(model, "__table__", None)
    if table is None:
        return ()
    cols = tuple(c.name for c in table.columns)
    return cols


def _colspecs(model: type) -> Mapping[str, Any]:
    return _colspecs_cached(model, _colspecs_cache_token(model))


def _filter_in_values(
    model: type, data: Mapping[str, Any], verb: str
) -> Dict[str, Any]:
    if not _requires_filtering(model, verb):
        return dict(data)
    specs = _colspecs(model)
    if not specs:
        return dict(data)
    excluded_fields = _excluded_schema_fields(model, verb)
    column_types = _table_python_types(model)
    out: Dict[str, Any] = {}
    for k, v in data.items():
        sp = specs.get(k)
        if sp is None:
            if k in excluded_fields:
                continue
            out[k] = v
            continue
        io = getattr(sp, "io", None)
        allowed = True
        if io is not None:
            in_verbs = getattr(io, "in_verbs", ())
            mutable = getattr(io, "mutable_verbs", ())
            if in_verbs and verb not in in_verbs:
                allowed = False
            if mutable and verb not in mutable:
                allowed = False
        if allowed:
            try:
                py_t = column_types.get(k)
                if py_t is not None and v is not None and not isinstance(v, py_t):
                    if py_t in (dt.datetime, dt.date) and isinstance(v, str):
                        parsed = py_t.fromisoformat(v)
                        out[k] = parsed
                    else:
                        out[k] = py_t(v)
                else:
                    out[k] = v
            except Exception:
                # Best effort coercion only; preserve original value on failure.
                out[k] = v
    return out


def _immutable_columns(model: type, verb: str) -> set[str]:
    specs = _colspecs(model)
    if not specs:
        return set()
    imm: set[str] = set()
    for name, sp in specs.items():
        io = getattr(sp, "io", None)
        mutable = getattr(io, "mutable_verbs", ()) if io else ()
        if mutable and verb not in mutable:
            imm.add(name)
    return imm
