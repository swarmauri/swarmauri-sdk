from __future__ import annotations

from enum import Enum
from typing import (
    Any,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    Annotated,
)


def _strip_optional(tp: Any) -> Tuple[Any, bool]:
    """Return (inner_type, is_optional) for Optional[T] / Union[T, None]."""
    origin = get_origin(tp)
    if origin is Union:
        args = tuple(a for a in get_args(tp))
        if len(args) == 2 and type(None) in args:
            inner = args[0] if args[1] is type(None) else args[1]
            return inner, True
    return tp, False


def _strip_annotated(tp: Any) -> Tuple[Any, Tuple[Any, ...]]:
    """Return (base, metadata) for Annotated[base, *meta]; otherwise (tp, ())."""
    origin = get_origin(tp)
    if origin is Annotated:
        args = get_args(tp)
        if len(args) >= 1:
            base, meta = args[0], tuple(args[1:])
            return base, meta
    return tp, ()


def _array_item(tp: Any) -> Optional[Any]:
    origin = get_origin(tp)
    if origin in (list, List, tuple, Tuple, set, frozenset):
        args = get_args(tp)
        if not args:
            return Any
        if origin in (tuple, Tuple) and len(args) == 2 and args[1] is Ellipsis:
            return args[0]
        if len(args) == 1:
            return args[0]
        return Any
    return None


def _is_enum(tp: Any) -> Optional[Type[Enum]]:
    try:
        if isinstance(tp, type) and issubclass(tp, Enum):
            return tp
    except Exception:
        pass
    return None
