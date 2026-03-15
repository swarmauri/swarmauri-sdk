from __future__ import annotations

import inspect
from typing import Any, Callable


def _unwrap(obj: Any) -> Callable[..., Any]:
    """Return the underlying function for class/static methods."""
    if isinstance(obj, (classmethod, staticmethod)):
        return obj.__func__  # type: ignore[attr-defined]
    return obj


def _maybe_await(v: Any):
    """Wrap non-awaitable values in an awaitable for uniform handling."""
    if inspect.isawaitable(v):
        return v

    async def _done():
        return v

    return _done()


def _normalize_persist(p: Any) -> str:
    """Normalize persist policy aliases to canonical values."""
    if p is None:
        return "default"
    p = str(p).lower()
    if p in {"none", "skip", "read"}:
        return "skip"
    if p in {"append"}:
        return "append"
    if p in {"override"}:
        return "override"
    if p in {"prepend"}:
        return "prepend"
    if p in {"write", "default", "persist"}:
        return "default"
    return "default"


__all__ = ["_maybe_await", "_normalize_persist", "_unwrap"]
