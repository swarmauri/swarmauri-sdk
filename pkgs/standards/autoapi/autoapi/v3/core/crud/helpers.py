# autoapi/v3/core/crud/helpers.py
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple, Union

import builtins as _builtins

try:
    from sqlalchemy import select, delete as sa_delete, and_, asc, desc, Enum as SAEnum
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.exc import NoResultFound  # type: ignore
except Exception:  # pragma: no cover
    select = sa_delete = and_ = asc = desc = None  # type: ignore
    SAEnum = None  # type: ignore
    Session = object  # type: ignore
    AsyncSession = object  # type: ignore

    class NoResultFound(LookupError):  # type: ignore
        pass


# Normalized filter operation names
_CANON_OPS = {
    "eq": "eq",
    "=": "eq",
    "==": "eq",
    "ne": "ne",
    "!=": "ne",
    "<>": "ne",
    "lt": "lt",
    "<": "lt",
    "gt": "gt",
    ">": "gt",
    "lte": "lte",
    "le": "lte",
    "<=": "lte",
    "gte": "gte",
    "ge": "gte",
    ">=": "gte",
    "like": "like",
    "not_like": "not_like",
    "ilike": "ilike",
    "not_ilike": "not_ilike",
    "in": "in",
    "not_in": "not_in",
    "nin": "not_in",
}

# ────────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ────────────────────────────────────────────────────────────────────────────────


def _is_async_db(db: Any) -> bool:
    return isinstance(db, AsyncSession) or hasattr(db, "run_sync")


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
    return pks[0].name


def _coerce_pk_value(model: type, value: Any) -> Any:
    """Coerce a provided primary key value to the model's python type."""
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
        return py_type(value)
    except Exception:  # pragma: no cover - fallback to original
        return value


def _model_columns(model: type) -> Tuple[str, ...]:
    table = getattr(model, "__table__", None)
    if table is None:
        return ()
    return tuple(c.name for c in table.columns)


def _colspecs(model: type) -> Mapping[str, Any]:
    """Return mapping of column name to ColumnSpec if defined."""
    specs = getattr(model, "__autoapi_colspecs__", None)
    if isinstance(specs, Mapping):
        return specs
    specs = getattr(model, "__autoapi_cols__", None)
    if isinstance(specs, Mapping):
        return specs
    return {}


def _filter_in_values(
    model: type, data: Mapping[str, Any], verb: str
) -> Dict[str, Any]:
    """Filter inbound values by ColumnSpec IO verbs."""
    specs = _colspecs(model)
    if not specs:
        return dict(data)
    out: Dict[str, Any] = {}
    for k, v in data.items():
        sp = specs.get(k)
        if sp is None:
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
            out[k] = v
    return out


def _immutable_columns(model: type, verb: str) -> set[str]:
    """Columns that should not be mutated for this verb."""
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


def _coerce_filters(
    model: type, filters: Optional[Mapping[str, Any]]
) -> Dict[str, Any]:
    """Keep only valid, filterable column names/ops."""
    cols = set(_model_columns(model))
    specs = _colspecs(model)
    raw = dict(filters or {})
    out: Dict[str, Any] = {}
    for k, v in raw.items():
        name, op = k.split("__", 1) if "__" in k else (k, "eq")
        if name not in cols:
            continue
        canon = _CANON_OPS.get(op, op)
        sp = specs.get(name)
        if sp is not None:
            io = getattr(sp, "io", None)
            ops = set(getattr(io, "filter_ops", ()) or [])
            ops = {_CANON_OPS.get(o, o) for o in ops}
            if not ops or canon not in ops:
                continue
            key = name if canon == "eq" else f"{name}__{canon}"
            out[key] = v
    return out


def _apply_filters(model: type, filters: Mapping[str, Any]) -> Any:
    """Convert filters with optional operators into a WHERE clause."""
    if select is None:  # pragma: no cover
        return None
    clauses = []
    for k, v in filters.items():
        name, op = k.split("__", 1) if "__" in k else (k, "eq")
        canon = _CANON_OPS.get(op, op)
        col = getattr(model, name, None)
        if col is None:
            continue
        if canon == "eq":
            clauses.append(col == v)
        elif canon == "ne":
            clauses.append(col != v)
        elif canon == "lt":
            clauses.append(col < v)
        elif canon == "gt":
            clauses.append(col > v)
        elif canon == "lte":
            clauses.append(col <= v)
        elif canon == "gte":
            clauses.append(col >= v)
        elif canon == "like":
            clauses.append(col.like(v))
        elif canon == "not_like":
            clauses.append(~col.like(v))
        elif canon == "ilike":
            clauses.append(col.ilike(v))
        elif canon == "not_ilike":
            clauses.append(~col.ilike(v))
        elif canon == "in":
            seq = list(v) if isinstance(v, (list, tuple, set)) else [v]
            clauses.append(col.in_(seq))
        elif canon == "not_in":
            seq = list(v) if isinstance(v, (list, tuple, set)) else [v]
            clauses.append(~col.in_(seq))
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else and_(*clauses)


def _apply_sort(model: type, sort: Any) -> Sequence[Any] | None:
    """
    Parse sort specifications into SQLAlchemy order_by expressions.
    Accepts:
      - "name" | "-name" | "name:asc" | "name:desc"
      - Comma-separated string "a,-b,c:desc"
      - Iterable[str] with the same tokens
    Unknown columns are ignored.
    """
    if select is None or sort is None:  # pragma: no cover
        return None

    def _tokenize(s: str) -> list[str]:
        return [t.strip() for t in s.split(",") if t.strip()]

    tokens: list[str] = []
    if isinstance(sort, str):
        tokens = _tokenize(sort)
    elif isinstance(sort, Iterable):
        for t in sort:
            if isinstance(t, str):
                tokens.extend(_tokenize(t))

    if not tokens:
        return None

    specs = _colspecs(model)
    order_by_exprs: list[Any] = []
    for tok in tokens:
        direction = "asc"
        name = tok

        if ":" in tok:
            name, dirpart = tok.split(":", 1)
            name = name.strip()
            dirpart = dirpart.strip().lower()
            if dirpart in ("desc", "descending"):
                direction = "desc"
        elif tok.startswith("-"):
            name = tok[1:]
            direction = "desc"

        col = getattr(model, name, None)
        if col is None:
            continue  # ignore unknown column names
        sp = specs.get(name)
        if sp is not None:
            io = getattr(sp, "io", None)
            if io is not None and not getattr(io, "sortable", False):
                continue
        if direction == "desc":
            order_by_exprs.append(desc(col))
        else:
            order_by_exprs.append(asc(col))

    return order_by_exprs or None


async def _maybe_get(db: Union[Session, AsyncSession], model: type, pk_value: Any):
    if _is_async_db(db):
        return await db.get(model, pk_value)  # type: ignore[attr-defined]
    return db.get(model, pk_value)  # type: ignore[attr-defined]


async def _maybe_execute(db: Union[Session, AsyncSession], stmt: Any):
    if _is_async_db(db):
        return await db.execute(stmt)  # type: ignore[attr-defined]
    return db.execute(stmt)  # type: ignore[attr-defined]


async def _maybe_flush(db: Union[Session, AsyncSession]) -> None:
    if _is_async_db(db):
        await db.flush()  # type: ignore[attr-defined]
    else:
        db.flush()  # type: ignore[attr-defined]


async def _maybe_delete(db: Union[Session, AsyncSession], obj: Any) -> None:
    if not hasattr(db, "delete"):
        return
    if _is_async_db(db):
        await db.delete(obj)  # type: ignore[attr-defined]
    else:
        db.delete(obj)  # type: ignore[attr-defined]


def _set_attrs(
    obj: Any,
    values: Mapping[str, Any],
    *,
    allow_missing: bool = True,
    skip: Sequence[str] = (),
) -> None:
    """
    Assign attributes present in `values`. Missing keys are skipped (for update).
    When allow_missing=False (replace), non-PK columns missing from `values` are set to None.
    """
    cols = set(_model_columns(type(obj)))
    pk = _single_pk_name(type(obj))
    skip_set = set(skip) | {pk}

    if allow_missing:
        for k, v in values.items():
            if k in cols and k not in skip_set:
                setattr(obj, k, v)
    else:
        for c in cols:
            if c in skip_set:
                continue
            if c in values:
                setattr(obj, c, values[c])
            else:
                setattr(obj, c, None)


# ────────────────────────────────────────────────────────────────────────────────
# Enum validation on writes
# ────────────────────────────────────────────────────────────────────────────────


def _validate_enum_values(model: type, values: Mapping[str, Any]) -> None:
    """
    Reject any assignment to Enum-typed columns that isn't one of the allowed labels.
    Works for Python Enum-backed SQLA Enum (via .enum_class) and string-only SQLA Enum (via .enums).

    Accepts Python Enum members (of the right class), their .value strings, or .name strings.
    """
    if not values or SAEnum is None:
        return

    table = getattr(model, "__table__", None)
    if table is None:
        return

    # ColumnCollection supports .get(name) in SQLAlchemy 2.x
    get = getattr(table.c, "get", None)

    for key, v in values.items():
        col = get(key) if get else None
        if col is None:
            try:
                col = table.c[key]  # type: ignore[index]
            except Exception:
                col = None
        if col is None:
            continue

        col_type = getattr(col, "type", None)
        if col_type is None or not isinstance(col_type, SAEnum):
            continue  # not an Enum column

        if v is None:
            continue  # let DB nullability decide

        enum_cls = getattr(col_type, "enum_class", None)
        if enum_cls is not None:
            try:
                import enum as _enum  # local to avoid hard dep at import time
            except Exception:  # pragma: no cover
                _enum = None

            if _enum is not None and isinstance(v, _enum.Enum):
                if isinstance(v, enum_cls):
                    continue
                raise LookupError(
                    f"{v!r} is not among the defined enum values. "
                    f"Enum name: {enum_cls.__name__}. "
                    f"Possible values: {', '.join([e.value for e in enum_cls])}"
                )

            allowed_values = [e.value for e in enum_cls]
            allowed_names = [e.name for e in enum_cls]
            if isinstance(v, str) and (v in allowed_values or v in allowed_names):
                continue

            raise LookupError(
                f"{v!r} is not among the defined enum values. "
                f"Enum name: {enum_cls.__name__}. "
                f"Possible values: {', '.join(allowed_values)}"
            )
        else:
            # String-only SQLAlchemy Enum
            allowed = _builtins.list(getattr(col_type, "enums", []) or [])
            if isinstance(v, str) and v in allowed:
                continue
            raise LookupError(
                f"{v!r} is not among the defined enum values. "
                f"Enum name: {getattr(col_type, 'name', 'Enum')}. "
                f"Possible values: {', '.join(allowed) if allowed else '(none)'}"
            )


# Normalizers to tolerate positional, keyword and bound-method calls -------------
def _pop_bound_self(args: list[Any]) -> None:
    # If the first positional thing isn't a type, it's likely the bound "self".
    if args and not isinstance(args[0], type):
        args.pop(0)


def _extract_db(
    args: list[Any], kwargs: dict[str, Any]
) -> Union[Session, AsyncSession]:
    db = kwargs.pop("db", None)
    if db is not None:
        return db
    # Heuristic: first positional arg that looks like a session
    for i, a in enumerate(args):
        if isinstance(a, (Session, AsyncSession)) or hasattr(a, "execute"):
            args.pop(i)
            return a  # type: ignore[return-value]
    raise TypeError("db session is required")


def _as_pos_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    try:
        v = int(x)
        return v if v >= 0 else 0
    except Exception:
        return None


def _normalize_list_call(
    _args: tuple[Any, ...], _kwargs: dict[str, Any]
) -> tuple[type, Dict[str, Any]]:
    """
    Accept:
      list(model, filters, *, db, skip, limit, sort)
      list(model, *, db, filters=None, skip=None, limit=None, sort=None)
      <bound>.list(model, filters, db=...)
      <bound>.list(model, db=...)                    # filters default {}
      list(self, model, ...)                         # accidental bound 'self'
      list(model, filters, request, db=...)          # stray positional between
    """
    args = _builtins.list(_args)
    kwargs = dict(_kwargs)

    _pop_bound_self(args)

    # model
    if args and isinstance(args[0], type):
        model = args.pop(0)
    else:
        model = kwargs.pop("model", None)
        if not isinstance(model, type):
            raise TypeError("list(model, ...) requires a model class")

    # filters
    filters = kwargs.pop("filters", None)
    if filters is None and args:
        maybe = args[0]
        if isinstance(maybe, Mapping):
            filters = args.pop(0)

    # skip / limit / sort (prefer kwargs; tolerate stray ints positionally)
    skip = _as_pos_int(kwargs.pop("skip", None))
    limit = _as_pos_int(kwargs.pop("limit", None))
    sort = kwargs.pop("sort", None)

    # leftover ints → skip/limit
    if skip is None and args:
        skip = _as_pos_int(args[0])
        if skip is not None:
            args.pop(0)
    if limit is None and args:
        limit = _as_pos_int(args[0])
        if limit is not None:
            args.pop(0)

    # db
    db = _extract_db(args, kwargs)

    # Default filters
    if filters is None:
        filters = {}

    # Ignore any other stray args/kwargs (request, ctx, etc.)
    return model, {
        "filters": filters,
        "skip": skip,
        "limit": limit,
        "db": db,
        "sort": sort,
    }


__all__ = [
    "select",
    "sa_delete",
    "asc",
    "desc",
    "SAEnum",
    "Session",
    "AsyncSession",
    "NoResultFound",
    "_CANON_OPS",
    "_filter_in_values",
    "_immutable_columns",
    "_coerce_filters",
    "_apply_filters",
    "_apply_sort",
    "_maybe_get",
    "_maybe_execute",
    "_maybe_flush",
    "_maybe_delete",
    "_set_attrs",
    "_validate_enum_values",
    "_normalize_list_call",
    "_single_pk_name",
    "_coerce_pk_value",
    "_builtins",
]
