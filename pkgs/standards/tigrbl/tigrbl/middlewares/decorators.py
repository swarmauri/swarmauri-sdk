"""Decorators for attaching middleware specs to apps/apis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MiddlewareConfig:
    cls: Any
    kwargs: dict[str, Any]


def middleware(middleware_class: Any, /, **kwargs: Any) -> MiddlewareConfig:
    """Build declarative middleware config objects for ``MIDDLEWARES``."""

    return MiddlewareConfig(cls=middleware_class, kwargs=kwargs)


def middlewares(*configs: MiddlewareConfig):
    """Attach middleware configs to class-level ``MIDDLEWARES``."""

    def _decorator(target: Any) -> Any:
        current = tuple(getattr(target, "MIDDLEWARES", ()))
        setattr(target, "MIDDLEWARES", current + tuple(configs))
        return target

    return _decorator


__all__ = ["MiddlewareConfig", "middleware", "middlewares"]
