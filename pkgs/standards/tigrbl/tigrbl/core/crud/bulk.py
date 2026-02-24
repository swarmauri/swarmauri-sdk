from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Union

import builtins as _builtins
import logging

from .helpers import (
    AsyncSession,
    Session,
    sa_delete,
    _coerce_pk_value,
    _immutable_columns,
    _maybe_delete,
    _maybe_execute,
    _maybe_flush,
    _maybe_get,
    _set_attrs,
    _single_pk_name,
    _validate_enum_values,
)
from .ops import merge, read

logger = logging.getLogger("uvicorn")


async def bulk_create(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """
    Insert many rows. Returns the list of persisted instances.
    Flush-only.
    """
    logger.debug("bulk_create called with model=%s rows=%s", model, rows)
    items_data = [dict(r) for r in (rows or ())]
    for r in items_data:
        _validate_enum_values(model, r)
    items = [model(**r) for r in items_data]
    if not items:
        logger.debug("bulk_create no items to create")
        return []
    if hasattr(db, "add_all"):
        db.add_all(items)  # type: ignore[attr-defined]
    else:
        for it in items:
            db.add(it)  # type: ignore[attr-defined]
    await _maybe_flush(db)
    logger.debug("bulk_create persisted %d items", len(items))
    return items


async def bulk_update(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """
    Update many rows by PK. Each row must include the PK field.
    Returns the list of updated instances. Flush-only.
    """
    logger.debug("bulk_update called with model=%s rows=%s", model, rows)
    pk = _single_pk_name(model)
    skip = _immutable_columns(model, "update")
    updated: List[Any] = []
    for r in rows or ():
        r = dict(r)
        _validate_enum_values(model, r)
        ident = r.get(pk)
        if ident is None:
            raise ValueError(f"bulk_update requires '{pk}' in each row")
        obj = await read(model, ident, db)
        data = {k: v for k, v in r.items() if k != pk}
        _set_attrs(obj, data, allow_missing=True, skip=skip)
        updated.append(obj)
    if updated:
        await _maybe_flush(db)
    logger.debug("bulk_update updated %d items", len(updated))
    return updated


async def bulk_replace(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """
    Replace many rows by PK. Each row must include the PK field.
    Missing attributes are nulled (except PK). Flush-only.
    """
    logger.debug("bulk_replace called with model=%s rows=%s", model, rows)
    pk = _single_pk_name(model)
    skip = _immutable_columns(model, "replace")
    replaced: List[Any] = []
    for r in rows or ():
        r = dict(r)
        _validate_enum_values(model, r)
        ident = r.get(pk)
        if ident is None:
            raise ValueError(f"bulk_replace requires '{pk}' in each row")
        obj = await read(model, ident, db)
        data = {k: v for k, v in r.items() if k != pk}
        _set_attrs(obj, data, allow_missing=False, skip=skip)
        replaced.append(obj)
    if replaced:
        await _maybe_flush(db)
    logger.debug("bulk_replace replaced %d items", len(replaced))
    return replaced


async def bulk_merge(
    model: type, rows: Iterable[Mapping[str, Any]], db: Union[Session, AsyncSession]
) -> List[Any]:
    """Merge many rows by primary key with upsert semantics."""
    logger.debug("bulk_merge called with model=%s rows=%s", model, rows)
    pk = _single_pk_name(model)
    results: List[Any] = []
    to_create: List[Mapping[str, Any]] = []
    for r in rows or ():
        r = dict(r)
        ident = _coerce_pk_value(model, r.get(pk))
        if ident is not None:
            existing = await _maybe_get(db, model, ident)
            if existing is not None:
                data = {k: v for k, v in r.items() if k != pk}
                merged = await merge(model, ident, data, db=db)
                results.append(merged)
                continue
            r[pk] = ident
        to_create.append(r)
    if to_create:
        created = await bulk_create(model, to_create, db)
        results.extend(created)
    logger.debug(
        "bulk_merge returning %d results (%d created)",
        len(results),
        len(to_create),
    )
    return results


async def bulk_delete(
    model: type, idents: Iterable[Any], db: Union[Session, AsyncSession]
) -> Dict[str, int]:
    """
    Delete many rows by a sequence of PK values. Returns {"deleted": N}.
    Flush-only.
    """
    logger.debug("bulk_delete called with model=%s idents=%s", model, idents)
    pk_name = _single_pk_name(model)
    id_seq = _builtins.list(idents or ())
    if not id_seq:
        logger.debug("bulk_delete no ids supplied")
        return {"deleted": 0}

    if sa_delete is not None:
        col = getattr(model, pk_name)
        stmt = sa_delete(model).where(col.in_(id_seq))  # type: ignore[attr-defined]
        res = await _maybe_execute(db, stmt)
        await _maybe_flush(db)
        n = int(getattr(res, "rowcount", 0) or 0)
        logger.debug("bulk_delete removed %d rows via stmt", n)
        return {"deleted": n}

    n = 0
    for ident in id_seq:
        obj = await read(model, ident, db)
        await _maybe_delete(db, obj)
        n += 1
    await _maybe_flush(db)
    logger.debug("bulk_delete removed %d rows individually", n)
    return {"deleted": n}
