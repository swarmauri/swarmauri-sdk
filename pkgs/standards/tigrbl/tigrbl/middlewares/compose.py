"""Helpers for composing ASGI/WSGI middleware stacks."""

from __future__ import annotations

from typing import Any


def apply_middlewares(
    app: Any, middleware_stack: list[tuple[Any, dict[str, Any]]]
) -> Any:
    wrapped = app
    for middleware_class, options in reversed(middleware_stack):
        wrapped = middleware_class(wrapped, **(options or {}))
    return wrapped


__all__ = ["apply_middlewares"]
