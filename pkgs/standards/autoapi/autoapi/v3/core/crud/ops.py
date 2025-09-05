from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Union

import builtins as _builtins

from .helpers import (
    AsyncSession,
    Session,
    NoResultFound,
    select,
    sa_delete,
    _apply_filters,
    _apply_sort,
    _coerce_filters,
    _coerce_pk_value,
    _filter_in_values,
    _immutable_columns,
    _maybe_delete,
    _maybe_execute,
    _maybe_flush,
    _maybe_get,
    _normalize_list_call,
    _set_attrs,
    _single_pk_name,
    _validate_enum_values,
)


async def create(
    model: type, data: Mapping[str, Any], db: Union[Session, AsyncSession]
) -> Any:
    """
    Insert a single row. Returns the persisted model instance.
    Flush-only (commit happens later in END_TX).
    """
    data = _filter_in_values(model, data or {}, "create")
    _validate_enum_values(model, data)
    obj = model(**data)
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
    data = _filter_in_values(model, data or {}, "update")
    _validate_enum_values(model, data)
    obj = await read(model, ident, db)
    skip = _immutable_columns(model, "update")
    _set_attrs(obj, data, allow_missing=True, skip=skip)
    await _maybe_flush(db)
    return obj


async def replace(
    model: type, ident: Any, data: Mapping[str, Any], db: Union[Session, AsyncSession]
) -> Any:
    """
    PUT semantics with upsert behaviour.

    If the row exists it is replaced entirely (missing attributes are nulled).
    If the row does not exist it is created with the provided identifier.
    Flush-only.
    """
    data = _filter_in_values(model, data or {}, "replace")
    _validate_enum_values(model, data)
    pk = _single_pk_name(model)
    obj = await _maybe_get(db, model, ident)
    if obj is None:
        payload = {pk: ident, **data}
        return await create(model, payload, db=db)
    skip = _immutable_columns(model, "replace")
    _set_attrs(obj, data, allow_missing=False, skip=skip)
    await _maybe_flush(db)
    return obj


async def merge(
    model: type, ident: Any, data: Mapping[str, Any], db: Union[Session, AsyncSession]
) -> Any:
    """PATCH semantics with upsert behaviour."""
    pk = _single_pk_name(model)
    ident = _coerce_pk_value(model, ident)
    obj = await _maybe_get(db, model, ident)

    # Respect create-only fields when upserting a new row
    verb = "update" if obj is not None else "create"
    data = _filter_in_values(model, data or {}, verb)
    _validate_enum_values(model, data)
    data_no_pk = {k: v for k, v in data.items() if k != pk}
    if obj is None:
        payload = {pk: ident, **data_no_pk}
        return await create(model, payload, db=db)
    skip = _immutable_columns(model, "update")
    _set_attrs(obj, data_no_pk, allow_missing=True, skip=skip)
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
    await _maybe_delete(db, obj)
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

    where = _apply_filters(model, filters)
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
    *args: Any,
    **kwargs: Any,
) -> Dict[str, int]:
    """
    Delete many rows matching equality filters. Returns {"deleted": N}.
    Flush-only. Tolerant to the same calling variations as `list`.
    """
    # Reuse normalizer to accept the same shapes
    model, params = _normalize_list_call(args, kwargs)
    raw_filters: Mapping[str, Any] = params["filters"]
    db: Union[Session, AsyncSession] = params["db"]

    if sa_delete is None:  # pragma: no cover
        # Fallback path: manual iteration
        items = await list(model, raw_filters, db=db)
        n = 0
        for obj in items:
            await _maybe_delete(db, obj)
            n += 1
        await _maybe_flush(db)
        return {"deleted": n}

    filt = _coerce_filters(model, raw_filters)
    where = _apply_filters(model, filt)
    stmt = sa_delete(model)
    if where is not None:
        stmt = stmt.where(where)

    res = await _maybe_execute(db, stmt)
    await _maybe_flush(db)
    # Some dialects don't populate rowcount; best-effort
    n = int(getattr(res, "rowcount", 0) or 0)
    return {"deleted": n}
