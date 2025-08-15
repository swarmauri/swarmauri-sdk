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

try:
    from sqlalchemy import select, delete, and_
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.exc import NoResultFound  # type: ignore
except Exception:  # pragma: no cover
    # Minimal shims so type-checkers don't explode if SQLAlchemy isn't present at import
    select = delete = and_ = None  # type: ignore
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


def _coerce_filters(model: type, filters: Mapping[str, Any]) -> Dict[str, Any]:
    """Keep only valid column names, drop paging keys."""
    cols = set(_model_columns(model))
    return {k: v for k, v in (filters or {}).items() if k in cols}


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


async def list(
    model: type,
    filters: Mapping[str, Any],
    *,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    db: Union[Session, AsyncSession],
) -> List[Any]:
    """
    Simple list with equality filters + skip/limit. Returns a list of model instances.
    """
    if select is None:  # pragma: no cover
        # Fallback: load all via legacy query API (unlikely in supported envs)
        q = db.query(model)  # type: ignore[attr-defined]
        filt = _coerce_filters(model, filters or {})
        if filt:
            q = q.filter_by(**filt)  # type: ignore[attr-defined]
        if isinstance(skip, int):
            q = q.offset(max(skip, 0))  # type: ignore[attr-defined]
        if isinstance(limit, int) and limit is not None:
            q = q.limit(max(limit, 0))  # type: ignore[attr-defined]
        return list(q.all())  # type: ignore[attr-defined]

    filt = _coerce_filters(model, filters or {})
    where = _apply_equality_filters(model, filt)
    stmt = select(model)
    if where is not None:
        stmt = stmt.where(where)
    if isinstance(skip, int):
        stmt = stmt.offset(max(skip, 0))
    if isinstance(limit, int) and limit is not None:
        stmt = stmt.limit(max(limit, 0))

    result = await _maybe_execute(db, stmt)
    return list(result.scalars().all())  # type: ignore[attr-defined]


async def clear(
    model: type,
    filters: Mapping[str, Any],
    db: Union[Session, AsyncSession],
) -> Dict[str, int]:
    """
    Delete many rows matching equality filters. Returns {"deleted": N}.
    Flush-only.
    """
    if delete is None:  # pragma: no cover
        # Fallback path: manual iteration
        items = await list(model, filters, db=db)
        n = 0
        for obj in items:
            db.delete(obj)  # type: ignore[attr-defined]
            n += 1
        await _maybe_flush(db)
        return {"deleted": n}

    filt = _coerce_filters(model, filters or {})
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
    idents = list(idents or ())
    if not idents:
        return {"deleted": 0}

    # Prefer DELETE ... WHERE pk IN (...)
    if delete is not None:
        col = getattr(model, pk_name)
        stmt = delete(model).where(col.in_(idents))  # type: ignore[attr-defined]
        res = await _maybe_execute(db, stmt)
        await _maybe_flush(db)
        n = int(getattr(res, "rowcount", 0) or 0)
        return {"deleted": n}

    # Fallback: row-by-row
    n = 0
    for ident in idents:
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
