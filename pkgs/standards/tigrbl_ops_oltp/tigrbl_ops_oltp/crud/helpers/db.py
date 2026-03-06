from __future__ import annotations

from typing import Any, Mapping, Sequence, Union

import logging

from . import AsyncSession, Session
from .model import _model_columns, _single_pk_name

logger = logging.getLogger("uvicorn")


def _is_async_db(db: Any) -> bool:
    logger.debug("_is_async_db called with db=%s", db)
    result = isinstance(db, AsyncSession) or hasattr(db, "run_sync")
    logger.debug("_is_async_db returning %s", result)
    return result


async def _maybe_get(db: Union[Session, AsyncSession], model: type, pk_value: Any):
    logger.debug("_maybe_get model=%s pk_value=%s", model, pk_value)
    if _is_async_db(db):
        result = await db.get(model, pk_value)  # type: ignore[attr-defined]
    else:
        result = db.get(model, pk_value)  # type: ignore[attr-defined]
    logger.debug("_maybe_get returning %s", result)
    return result


async def _maybe_execute(db: Union[Session, AsyncSession], stmt: Any):
    logger.debug("_maybe_execute stmt=%s", stmt)
    if _is_async_db(db):
        result = await db.execute(stmt)  # type: ignore[attr-defined]
    else:
        result = db.execute(stmt)  # type: ignore[attr-defined]
    logger.debug("_maybe_execute returning %s", result)
    return result


async def _maybe_flush(db: Union[Session, AsyncSession]) -> None:
    logger.debug("_maybe_flush called")
    if _is_async_db(db):
        await db.flush()  # type: ignore[attr-defined]
    else:
        db.flush()  # type: ignore[attr-defined]
    logger.debug("_maybe_flush completed")


async def _maybe_delete(db: Union[Session, AsyncSession], obj: Any) -> None:
    logger.debug("_maybe_delete called with obj=%s", obj)
    if not hasattr(db, "delete"):
        logger.debug("_maybe_delete skipping delete; no attribute")
        return
    if _is_async_db(db):
        await db.delete(obj)  # type: ignore[attr-defined]
    else:
        db.delete(obj)  # type: ignore[attr-defined]
    logger.debug("_maybe_delete completed for obj=%s", obj)


def _set_attrs(
    obj: Any,
    values: Mapping[str, Any],
    *,
    allow_missing: bool = True,
    skip: Sequence[str] = (),
) -> None:
    logger.debug(
        "_set_attrs called on obj=%s values=%s allow_missing=%s skip=%s",
        obj,
        values,
        allow_missing,
        skip,
    )
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
    logger.debug("_set_attrs completed for obj=%s", obj)
