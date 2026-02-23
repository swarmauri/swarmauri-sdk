"""Decorators for registering routes against Router-like instances."""

from __future__ import annotations

from typing import Any, Callable, Iterable


def route_ctx(
    *,
    router: Any,
    path: str,
    methods: Iterable[str],
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register the decorated handler on ``router`` with ``router.add_route``."""

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        router.add_route(path, fn, methods=methods, **kwargs)
        return fn

    return deco


__all__ = ["route_ctx"]
