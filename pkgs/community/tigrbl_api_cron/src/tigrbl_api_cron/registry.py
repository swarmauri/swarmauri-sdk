"""Registry for cron job handlers keyed by package UID."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from .tables.cron_job import CronJob


class CronJobHandler(Protocol):
    """Callable signature for cron job execution handlers."""

    def __call__(
        self,
        *,
        job: CronJob,
        session: Any,
        scheduled_for: Any,
        now: Any,
    ) -> Awaitable[Any] | Any: ...


_Handler = Callable[..., Awaitable[Any] | Any]
_registry: dict[str, _Handler] = {}


def register_cron_job(
    pkg_uid: str, handler: _Handler | None = None
) -> Callable[[_Handler], _Handler]:
    """Register a cron job handler.

    Can be used as a decorator::

        @register_cron_job("demo.pkg")
        async def handler(*, job, session, scheduled_for, now):
            ...

    Or called with a function::

        register_cron_job("demo.pkg", handler)
    """

    def decorator(fn: _Handler) -> _Handler:
        _registry[pkg_uid] = fn
        return fn

    if handler is not None:
        return decorator(handler)
    return decorator


def unregister_cron_job(pkg_uid: str) -> None:
    """Remove a cron job handler if it exists."""

    _registry.pop(pkg_uid, None)


def get_handler(pkg_uid: str) -> _Handler | None:
    """Return the registered handler for ``pkg_uid`` if any."""

    return _registry.get(pkg_uid)


def clear_registry() -> None:
    """Remove all registered handlers (useful for testing)."""

    _registry.clear()


__all__ = [
    "CronJobHandler",
    "register_cron_job",
    "unregister_cron_job",
    "get_handler",
    "clear_registry",
]
