from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from typing import Generic, TypeVar

from .stages import (
    Boot,
    Failed,
)

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
class BaseCtx(Generic[S]):
    env: object | None = None
    bag: dict[str, object] = field(default_factory=dict)
    temp: dict[str, object] = field(default_factory=dict)
    error: Exception | None = None

    def promote(self, cls: type[U], /, **updates: object) -> U:
        if not is_dataclass(cls):
            raise TypeError(f"promote target must be a dataclass type, got {cls!r}")

        data: dict[str, object] = {}
        missing_required: list[str] = []

        for f in fields(cls):
            if f.name in updates:
                continue
            if hasattr(self, f.name):
                data[f.name] = getattr(self, f.name)
                continue
            if f.default is MISSING and f.default_factory is MISSING:
                missing_required.append(f.name)

        if missing_required:
            raise TypeError(
                f"cannot promote {type(self).__name__} -> {cls.__name__}; "
                f"missing required fields: {', '.join(missing_required)}"
            )

        data.update(updates)
        return cls(**data)

    def put_temp(self, key: str, value: object) -> None:
        self.temp[key] = value

    def require_temp(self, key: str) -> object:
        try:
            return self.temp[key]
        except KeyError as e:
            raise KeyError(f"missing temp field: {key!r}") from e


@dataclass(slots=True)
class BootCtx(BaseCtx[Boot]):
    pass


@dataclass(slots=True)
class IngressCtx(BootCtx):
    raw: object | None = None
    request: object | None = None
    method: str = ""
    path: str = ""
    headers: dict[str, object] = field(default_factory=dict)
    query: dict[str, object] = field(default_factory=dict)
    body: object | None = None


@dataclass(slots=True)
class RoutedCtx(IngressCtx):
    protocol: str = ""
    path_params: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class BoundCtx(RoutedCtx):
    binding: object | None = None
    model: object | None = None
    op: str = ""


@dataclass(slots=True)
class PlannedCtx(BoundCtx):
    payload: object | None = None
    plan: object | None = None
    opmeta: object | None = None
    opview: object | None = None


@dataclass(slots=True)
class GuardedCtx(PlannedCtx):
    authz: object | None = None


@dataclass(slots=True)
class ExecutingCtx(GuardedCtx):
    pass


@dataclass(slots=True)
class ResolvedCtx(ExecutingCtx):
    schema_in: object | None = None
    in_values: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class OperatedCtx(ResolvedCtx):
    result: object | None = None


@dataclass(slots=True)
class EncodedCtx(OperatedCtx):
    schema_out: object | None = None
    response_payload: object | None = None
    response_headers: dict[str, object] = field(default_factory=dict)
    status_code: int = 200


@dataclass(slots=True)
class EmittingCtx(EncodedCtx):
    transport_response: object | None = None


@dataclass(slots=True)
class EgressedCtx(EmittingCtx):
    pass


@dataclass(slots=True)
class FailedCtx(BaseCtx[Failed]):
    error: Exception | None = None


class Atom(ABC, Generic[S, T]):
    name: str = "atom"
    anchor: str = ""

    @abstractmethod
    async def __call__(self, obj: object | None, ctx: BaseCtx[S]) -> BaseCtx[T]:
        raise NotImplementedError


__all__ = [
    "S",
    "T",
    "U",
    "BaseCtx",
    "BootCtx",
    "IngressCtx",
    "RoutedCtx",
    "BoundCtx",
    "PlannedCtx",
    "GuardedCtx",
    "ExecutingCtx",
    "ResolvedCtx",
    "OperatedCtx",
    "EncodedCtx",
    "EmittingCtx",
    "EgressedCtx",
    "FailedCtx",
    "Atom",
    "DependencyLike",
    "ResponseLike",
    "is_dependency_like",
    "is_response_like",
]
