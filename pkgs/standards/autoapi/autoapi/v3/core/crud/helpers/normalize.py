from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Union
import builtins as _builtins

from . import AsyncSession, Session


def _pop_bound_self(args: list[Any]) -> None:
    if args and not isinstance(args[0], type):
        args.pop(0)


def _extract_db(
    args: list[Any], kwargs: dict[str, Any]
) -> Union[Session, AsyncSession]:
    db = kwargs.pop("db", None)
    if db is not None:
        return db
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
    args = _builtins.list(_args)
    kwargs = dict(_kwargs)

    _pop_bound_self(args)

    if args and isinstance(args[0], type):
        model = args.pop(0)
    else:
        model = kwargs.pop("model", None)
        if not isinstance(model, type):
            raise TypeError("list(model, ...) requires a model class")

    filters = kwargs.pop("filters", None)
    if filters is None and args:
        maybe = args[0]
        if isinstance(maybe, Mapping):
            filters = args.pop(0)

    skip = _as_pos_int(kwargs.pop("skip", None))
    limit = _as_pos_int(kwargs.pop("limit", None))
    sort = kwargs.pop("sort", None)

    if skip is None and args:
        skip = _as_pos_int(args[0])
        if skip is not None:
            args.pop(0)
    if limit is None and args:
        limit = _as_pos_int(args[0])
        if limit is not None:
            args.pop(0)

    db = _extract_db(args, kwargs)

    if filters is None:
        filters = {}

    return model, {
        "filters": filters,
        "skip": skip,
        "limit": limit,
        "db": db,
        "sort": sort,
    }
