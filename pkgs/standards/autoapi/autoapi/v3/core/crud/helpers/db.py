from __future__ import annotations

from typing import Any, Mapping, Sequence, Union

from . import AsyncSession, Session
from .model import _model_columns, _single_pk_name


def _is_async_db(db: Any) -> bool:
    return isinstance(db, AsyncSession) or hasattr(db, "run_sync")


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
