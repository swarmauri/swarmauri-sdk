from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .crud import ops

Executor = Callable[..., Awaitable[Any]]


REGISTRY: dict[str, Executor] = {
    "oltp:create": ops.create,
    "oltp:read": ops.read,
    "oltp:update": ops.update,
    "oltp:replace": ops.replace,
    "oltp:merge": ops.merge,
    "oltp:delete": ops.delete,
    "oltp:list": ops.list,
}


def register_executor(key: str, executor: Executor) -> None:
    REGISTRY[key] = executor


def resolve_executor(key: str) -> Executor:
    try:
        return REGISTRY[key]
    except KeyError as exc:
        raise KeyError(f"unknown executor key: {key}") from exc


async def dispatch(key: str, /, **kwargs: Any) -> Any:
    return await resolve_executor(key)(**kwargs)


__all__ = ["Executor", "REGISTRY", "register_executor", "resolve_executor", "dispatch"]
