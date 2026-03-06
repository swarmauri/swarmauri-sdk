from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RequestLike(Protocol):
    query_params: dict[str, Any]
    path_params: dict[str, Any]
    headers: dict[str, Any]

    def json_sync(self) -> Any: ...


@runtime_checkable
class DependencyLike(Protocol):
    dependency: Any


@runtime_checkable
class ResponseLike(Protocol):
    status_code: int
    raw_headers: list[tuple[bytes, bytes]]
    body: bytes | None


def is_dependency_like(obj: Any) -> bool:
    return isinstance(obj, DependencyLike) and callable(
        getattr(obj, "dependency", None)
    )


def is_response_like(obj: Any) -> bool:
    if not isinstance(obj, ResponseLike):
        return False
    return isinstance(getattr(obj, "raw_headers", None), list)


__all__ = [
    "RequestLike",
    "DependencyLike",
    "ResponseLike",
    "is_dependency_like",
    "is_response_like",
]
