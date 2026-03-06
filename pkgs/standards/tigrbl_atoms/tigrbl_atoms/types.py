from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, MutableMapping, TypeVar, cast

from tigrbl_typing.protocols import (
    DependencyLike,
    ResponseLike,
    is_dependency_like,
    is_response_like,
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


__all__ = [
    "Atom",
    "Ctx",
    "cast_ctx",
    "DependencyLike",
    "ResponseLike",
    "is_dependency_like",
    "is_response_like",
]
