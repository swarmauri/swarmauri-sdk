from __future__ import annotations

from functools import lru_cache
import inspect
from typing import Any, Mapping, Sequence, Union

import logging

from . import AsyncSession, Session
from .model import _model_columns, _single_pk_name

logger = logging.getLogger("uvicorn")


@lru_cache(maxsize=512)
def _is_async_db_type(db_type: type[Any]) -> bool:
    return db_type.__name__ == "AsyncSession" or hasattr(db_type, "run_sync")


def _is_async_db(db: Any) -> bool:
    logger.debug("_is_async_db called with db=%s", db)
    result = _is_async_db_type(type(db))
    logger.debug("_is_async_db returning %s", result)
    return result


async def _maybe_get(db: Union[Session, AsyncSession], model: type, pk_value: Any):
    logger.debug("_maybe_get model=%s pk_value=%s", model, pk_value)
    result = db.get(model, pk_value)  # type: ignore[attr-defined]
    if inspect.isawaitable(result):
        result = await result
    logger.debug("_maybe_get returning %s", result)
    return result


async def _maybe_execute(db: Union[Session, AsyncSession], stmt: Any):
    logger.debug("_maybe_execute stmt=%s", stmt)
    result = db.execute(stmt)  # type: ignore[attr-defined]
    if inspect.isawaitable(result):
        result = await result
    logger.debug("_maybe_execute returning %s", result)
    return result


async def _maybe_flush(db: Union[Session, AsyncSession]) -> None:
    logger.debug("_maybe_flush called")
    result = db.flush()  # type: ignore[attr-defined]
    if inspect.isawaitable(result):
        await result
    logger.debug("_maybe_flush completed")


async def _maybe_rollback(db: Union[Session, AsyncSession]) -> None:
    logger.debug("_maybe_rollback called")
    if not hasattr(db, "rollback"):
        logger.debug("_maybe_rollback skipping rollback; no attribute")
        return
    result = db.rollback()  # type: ignore[attr-defined]
    if inspect.isawaitable(result):
        await result
    logger.debug("_maybe_rollback completed")


async def _maybe_delete(db: Union[Session, AsyncSession], obj: Any) -> None:
    logger.debug("_maybe_delete called with obj=%s", obj)
    if not hasattr(db, "delete"):
        logger.debug("_maybe_delete skipping delete; no attribute")
        return
    result = db.delete(obj)  # type: ignore[attr-defined]
    if inspect.isawaitable(result):
        await result
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
