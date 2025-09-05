from __future__ import annotations

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


from .model import (
    _pk_columns,
    _single_pk_name,
    _coerce_pk_value,
    _model_columns,
    _colspecs,
    _filter_in_values,
    _immutable_columns,
)
from .filters import _CANON_OPS, _coerce_filters, _apply_filters, _apply_sort
from .db import (
    _is_async_db,
    _maybe_get,
    _maybe_execute,
    _maybe_flush,
    _maybe_delete,
    _set_attrs,
)
from .enum import _validate_enum_values
from .normalize import (
    _normalize_list_call,
    _pop_bound_self,
    _extract_db,
    _as_pos_int,
)

__all__ = [
    "AsyncSession",
    "Session",
    "NoResultFound",
    "select",
    "sa_delete",
    "_apply_filters",
    "_apply_sort",
    "_CANON_OPS",
    "_coerce_filters",
    "_coerce_pk_value",
    "_colspecs",
    "_filter_in_values",
    "_immutable_columns",
    "_is_async_db",
    "_maybe_delete",
    "_maybe_execute",
    "_maybe_flush",
    "_maybe_get",
    "_model_columns",
    "_normalize_list_call",
    "_pop_bound_self",
    "_extract_db",
    "_as_pos_int",
    "_pk_columns",
    "_set_attrs",
    "_single_pk_name",
    "_validate_enum_values",
    "SAEnum",
    "asc",
    "desc",
    "and_",
]
