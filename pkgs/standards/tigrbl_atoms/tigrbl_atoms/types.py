from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    MutableMapping,
    cast,
    runtime_checkable,
)

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")


@dataclass(slots=True)
class Ctx(Generic[S]):
    env: Any | None = None
    bag: dict[str, Any] = field(default_factory=dict)
    temp: MutableMapping[str, Any] = field(default_factory=dict)
    error: Exception | None = None


class Atom(ABC, Generic[S, T]):
    name: str = "atom"
    anchor: str = ""

    @abstractmethod
    async def __call__(self, obj: object | None, ctx: Ctx[S]) -> Ctx[T]:
        raise NotImplementedError


def cast_ctx(ctx: Any) -> Ctx[Any]:
    return cast(Ctx[Any], ctx)


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
