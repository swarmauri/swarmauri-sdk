"""Internal helper utilities for schema building."""

from __future__ import annotations

from types import UnionType
from typing import Any, Dict, Tuple, Union, get_args, get_origin, get_type_hints

from pydantic import Field


def _bool(x: Any) -> bool:
    try:
        return bool(x)
    except Exception:  # pragma: no cover
        return False


def _normalize_py_type(py_t: type | Any) -> type | Any:
    """Normalize dynamic field type declarations for safe schema generation."""
    if isinstance(py_t, property):
        getter = py_t.fget
        if getter is None:
            return Any

        try:
            return _normalize_py_type(get_type_hints(getter).get("return", Any))
        except Exception:  # pragma: no cover
            return Any

    # ``typing.Union[..., <property object>]`` can appear when extras or
    # computed columns accidentally register a ``property`` INSTANCE in a type
    # declaration. Recursively normalize union members so we can safely rebuild
    # a pydantic-compatible annotation.
    origin = get_origin(py_t)
    if origin in (Union, UnionType):
        args = tuple(_normalize_py_type(arg) for arg in get_args(py_t))
        filtered = tuple(arg for arg in args if arg is not None)
        if not filtered:
            return Any
        rebuilt = filtered[0]
        for arg in filtered[1:]:
            rebuilt = rebuilt | arg
        return rebuilt

    return py_t


def _add_field(
    sink: Dict[str, Tuple[type, Field]],
    *,
    name: str,
    py_t: type | Any,
    field: Field | None = None,
) -> None:
    # ``property`` descriptors can leak into extras definitions when callers
    # register computed attributes directly (instead of their return type).
    # Pydantic cannot generate schemas for a raw property object, so degrade to
    # ``Any`` and let runtime serializers provide the concrete value.
    py_t = _normalize_py_type(py_t)
    sink[name] = (py_t, field if field is not None else Field(None))


def _python_type(col: Any) -> type | Any:
    try:
        return col.type.python_type
    except Exception:  # pragma: no cover
        return Any


def _is_required(col: Any, verb: str) -> bool:
    """Decide if a column should be required for the given verb."""
    if getattr(col, "primary_key", False):
        if verb in {"update", "replace", "delete"}:
            return True
        auto = getattr(col, "autoincrement", False)
        if auto not in (False, None) or getattr(col, "identity", None) is not None:
            return False
    if verb == "update":
        return False
    is_nullable = bool(getattr(col, "nullable", True))
    has_default = (getattr(col, "default", None) is not None) or (
        getattr(col, "server_default", None) is not None
    )
    return not is_nullable and not has_default


__all__ = ["_bool", "_add_field", "_normalize_py_type", "_python_type", "_is_required"]
