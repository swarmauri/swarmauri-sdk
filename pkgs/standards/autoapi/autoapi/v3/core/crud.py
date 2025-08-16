# autoapi/v3/core/crud.py
from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import builtins as _builtins

try:
    from sqlalchemy import select, delete, and_, asc, desc
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.exc import NoResultFound  # type: ignore
except Exception:  # pragma: no cover
    # Minimal shims so type-checkers don't explode if SQLAlchemy isn't present at import
    select = delete = and_ = asc = desc = None  # type: ignore
    Session = object  # type: ignore
    AsyncSession = object  # type: ignore

    class NoResultFound(LookupError):  # type: ignore
        pass


# ───────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────────────────────────────────────


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


def _model_columns(model: type) -> Tuple[str, ...]:
    table = getattr(model, "__table__", None)
    if table is None:
        return ()
    return tuple(c.name for c in table.columns)


def _coerce_filters(model: type, filters: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Keep only valid column names, drop paging keys."""
    cols = set(_model_columns(model))
    raw = dict(filters or {})
    return {k: v for k, v in raw.items() if k in cols}


def _apply_equality_filters(model: type, filters: Mapping[str, Any]) -> Any:
    """
    Convert simple equality filters into a SQLAlchemy WHERE clause.
    """
    if select is None:  # pragma: no cover
        return None
    clauses = []
    for k, v in filters.items():
        col = getattr(model, k, None)
        if col is not None:
            clauses.append(col == v)
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return and_(*clauses)


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
                # For replace semantics, we null out unspecified scalar columns
                # (If DB forbids, flush will raise → mapped by runtime.errors)
                setattr(obj, c, None)


# Normalizers to tolerate positional, keyword and bound-method calls -------------
def _pop_bound_self(args: list[Any]) -> None:
    # If the first positional thing isn't a type, it's likely the bound "self".
    if args and not isinstance(args[0], type):
        args.pop(0)


def _extract_db(args: list[Any], kwargs: dict[str, Any]) -> Union[Session, AsyncSession]:
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


def _normalize_list_call(_args: tuple[Any, ...], _kwargs: dict[str, Any]) -> tuple[type, Dict[str, Any]]:
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


    # If there are leftover ints, try to assign as skip/limit
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
    return model, {"filters": filters, "skip": skip, "limit": limit, "db": db, "sort": sort}


# ───────────────────────────────────────────────────────────────────────────────
# Canonical CRUD
# ───────────────────────────────────────────────────────────────────────────────


async def create(
    model: type, data: Mapping[str, Any], db: Union[Session, AsyncSession]
) -> Any:
    """
    Insert a single row. Returns the persisted model instance.
    Flush-only (commit happens later in END_TX).
    """
    obj = model(**dict(data or {}))
    if hasattr(db, "add"):
        db.add(obj)
    await _maybe_flush(db)
    return obj


async def read(model: type, ident: Any, db: Union[Session, AsyncSession]) -> Any:
    """
    Load a single row by primary key. Raises NoResultFound if not found.
    """
    obj = await _maybe_get(db, model, ident)
    if obj is None:
        raise NoResultFound(f"{model.__name__}({ident!r}) not found")
    return obj


async def update(
    model: type, ident: Any, data: Mapping[str, Any], db: Union[Session, AsyncSession]
) -> Any:
    """
    Partial update by primary key. Missing keys are left unchanged.
    Returns the updated model instance. Flush-only.
    """
    obj = await read(model, ident, db)
    _set_attrs(obj, data or {}, allow_missing=True)
    await _maybe_flush(db)
    return obj


async def replace(
    model: type, ident: Any, data: Mapping[str, Any], db: Union[Session, AsyncSession]
) -> Any:
    """
    Replace semantics: attributes not provided are nulled (except PK).
    Returns the updated model instance. Flush-only.
    """
    obj = await read(model, ident, db)
    _set_attrs(obj, data or {}, allow_missing=False)
    await _maybe_flush(db)
    return obj


async def delete(
    model: type, ident: Any, db: Union[Session, AsyncSession]
) -> Dict[str, int]:
    """
    Delete by primary key. Returns {"deleted": 1} if removed, else raises NoResultFound.
    Flush-only.
    """
    obj = await read(model, ident, db)
    if hasattr(db, "delete"):
        db.delete(obj)  # type: ignore[attr-defined]
    await _maybe_flush(db)
    return {"deleted": 1}


# NOTE: tolerant signature: accepts positional/keyword and ignores stray args
async def list(*_args: Any, **_kwargs: Any) -> List[Any]:  # noqa: A001  (shadow built-in)
    """
    Simple list with equality filters + skip/limit (+ optional sort).
    Tolerant to:
      - missing filters (defaults to {})
      - accidental bound-method 'self' (first positional arg)
      - positional or keyword args
      - stray extras (e.g., request) which are ignored
    """

    model, params = _normalize_list_call(_args, _kwargs)

    filters: Mapping[str, Any] = _coerce_filters(model, params["filters"])

    skip: Optional[int] = params["skip"]
    limit: Optional[int] = params["limit"]
    db: Union[Session, AsyncSession] = params["db"]

    sort = params["sort"]

    if select is None:  # pragma: no cover
        # Fallback: legacy query API
        q = db.query(model)  # type: ignore[attr-defined]
        if filters:
            q = q.filter_by(**filters)  # type: ignore[attr-defined]
        if isinstance(skip, int):
            q = q.offset(max(skip, 0))  # type: ignore[attr-defined]
        if isinstance(limit, int) and limit is not None:
            q = q.limit(max(limit, 0))  # type: ignore[attr-defined]
        return _builtins.list(q.all())  # type: ignore[attr-defined]

    where = _apply_equality_filters(model, filters)
    stmt = select(model)
    if where is not None:
        stmt = stmt.where(where)

    order_exprs = _apply_sort(model, sort)
    if order_exprs:
        for ob in order_exprs:
            stmt = stmt.order_by(ob)

    if isinstance(skip, int):
        stmt = stmt.offset(max(skip, 0))
    if isinstance(limit, int) and limit is not None:
        stmt = stmt.limit(max(limit, 0))

    result = await _maybe_execute(db, stmt)
    return _builtins.list(result.scalars().all())  # type: ignore[attr-defined]


async def clear(
    *args: Any, **kwargs: Any,
) -> Dict[str, int]:
    """
    Delete many rows matching equality filters. Returns {"deleted": N}.
    Flush-only. Tolerant to the same calling variations as `list`.
    """
    # Reuse normalizer to accept the same shapes
    model, params = _normalize_list_call(args, kwargs)
    raw_filters: Mapping[str, Any] = params["filters"]
    db: Union[Session, AsyncSession] = params["db"]

    if delete is None:  # pragma: no cover
        # Fallback path: manual iteration
        items = await list(model, raw_filters, db=db)
        n = 0
        for obj in items:
            db.delete(obj)  # type: ignore[attr-defined]
            n += 1
        await _maybe_flush(db)
        return {"deleted": n}

    filt = _coerce_filters(model, raw_filters)
    where = _apply_equality_filters(model, filt)
    stmt = delete(model)
    if where is not None:
        stmt = stmt.where(where)

    res = await _maybe_execute(db, stmt)
    await _maybe_flush(db)
    # Some dialects don't populate rowcount; best-effort
    n = int(getattr(res, "rowcount", 0) or 0)
    return {"deleted": n}


# ───────────────────────────────────────────────────────────────────────────────
# Bulk variants
# ───────────────────────────────────────────────────────────────────────────────


async def bulk_create(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """
    Insert many rows. Returns the list of persisted instances.
    Flush-only.
    """
    items = [model(**dict(r)) for r in (rows or ())]
    if not items:
        return []
    if hasattr(db, "add_all"):
        db.add_all(items)  # type: ignore[attr-defined]
    else:
        for it in items:
            db.add(it)  # type: ignore[attr-defined]
    await _maybe_flush(db)
    return items


async def bulk_update(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """
    Update many rows by PK. Each row must include the PK field.
    Returns the list of updated instances. Flush-only.
    """
    pk = _single_pk_name(model)
    updated: List[Any] = []
    for r in rows or ():
        ident = r.get(pk)
        if ident is None:
            raise ValueError(f"bulk_update requires '{pk}' in each row")
        obj = await read(model, ident, db)
        # remove pk to avoid accidental overwrite
        data = {k: v for k, v in r.items() if k != pk}
        _set_attrs(obj, data, allow_missing=True)
        updated.append(obj)
    if updated:
        await _maybe_flush(db)
    return updated


async def bulk_replace(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """
    Replace many rows by PK. Each row must include the PK field.
    Missing attributes are nulled (except PK). Flush-only.
    """
    pk = _single_pk_name(model)
    replaced: List[Any] = []
    for r in rows or ():
        ident = r.get(pk)
        if ident is None:
            raise ValueError(f"bulk_replace requires '{pk}' in each row")
        obj = await read(model, ident, db)
        data = {k: v for k, v in r.items() if k != pk}
        _set_attrs(obj, data, allow_missing=False)
        replaced.append(obj)
    if replaced:
        await _maybe_flush(db)
    return replaced


async def bulk_delete(
    model: type, idents: Iterable[Any], db: Union[Session, AsyncSession]
) -> Dict[str, int]:
    """
    Delete many rows by a sequence of PK values. Returns {"deleted": N}.
    Flush-only.
    """
    pk_name = _single_pk_name(model)
    id_seq = _builtins.list(idents or ())
    if not id_seq:
        return {"deleted": 0}

    # Prefer DELETE ... WHERE pk IN (...)
    if delete is not None:
        col = getattr(model, pk_name)
        stmt = delete(model).where(col.in_(id_seq))  # type: ignore[attr-defined]
        res = await _maybe_execute(db, stmt)
        await _maybe_flush(db)
        n = int(getattr(res, "rowcount", 0) or 0)
        return {"deleted": n}

    # Fallback: row-by-row
    n = 0
    for ident in id_seq:
        obj = await read(model, ident, db)
        db.delete(obj)  # type: ignore[attr-defined]
        n += 1
    await _maybe_flush(db)
    return {"deleted": n}


__all__ = [
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_delete",
]
