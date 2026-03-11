from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Final, Tuple, cast, final

from collections.abc import Mapping

from typing_extensions import Generic, TypeAlias, TypeVar

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
E = TypeVar("E", default=Exception)


PHASE_SEQUENCE: Final[tuple[str, ...]] = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",
    "POST_COMMIT",
    "POST_RESPONSE",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
)

INGRESS_PHASES: Final[tuple[str, ...]] = PHASE_SEQUENCE[:4]
HANDLER_PHASES: Final[tuple[str, ...]] = PHASE_SEQUENCE[5:8]
EGRESS_PHASES: Final[tuple[str, ...]] = PHASE_SEQUENCE[-3:]


@dataclass(slots=True)
class BaseCtx(Generic[S, E]):
    env: object | None = None
    bag: dict[str, object] = field(default_factory=dict)
    temp: dict[str, object] = field(default_factory=dict)
    error: E | None = None
    current_phase: str | None = None
    error_phase: str | None = None

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

    def safe_view(
        self,
        *,
        include_temp: bool = False,
        temp_keys: tuple[str, ...] | None = None,
    ) -> Mapping[str, object]:
        """
        Return a compact read-only mapping intended for user callables.

        By default, temp is excluded to avoid exposing runtime internals.
        """
        base: dict[str, object] = {
            "op": getattr(self, "op", None),
            "persist": getattr(self, "persist", True),
            "model": getattr(self, "model", None),
            "specs": getattr(self, "specs", None),
            "user": getattr(self, "user", None),
            "tenant": getattr(self, "tenant", None),
            "now": getattr(self, "now", None),
        }
        if include_temp:
            allowed = set(temp_keys or ("assembled_values", "virtual_in"))
            exposed: dict[str, object] = {}
            for key in allowed:
                if key in self.temp:
                    exposed[key] = self.temp[key]
            base["temp"] = MappingProxy(exposed)
        return MappingProxy(base)


class MappingProxy(Mapping[str, object]):
    __slots__ = ("_d",)

    def __init__(self, data: Mapping[str, object]):
        self._d = dict(data)

    def __getitem__(self, key: str) -> object:
        return self._d[key]

    def __iter__(self):
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def get(self, key: str, default: object = None) -> object:
        return self._d.get(key, default)


Ctx: TypeAlias = BaseCtx[S, E]


class HookPhase(str, Enum):
    PRE_TX_BEGIN = "PRE_TX_BEGIN"
    START_TX = "START_TX"
    PRE_HANDLER = "PRE_HANDLER"
    HANDLER = "HANDLER"
    POST_HANDLER = "POST_HANDLER"
    PRE_COMMIT = "PRE_COMMIT"
    END_TX = "END_TX"
    POST_COMMIT = "POST_COMMIT"
    POST_RESPONSE = "POST_RESPONSE"
    ON_ERROR = "ON_ERROR"
    ON_PRE_TX_BEGIN_ERROR = "ON_PRE_TX_BEGIN_ERROR"
    ON_START_TX_ERROR = "ON_START_TX_ERROR"
    ON_PRE_HANDLER_ERROR = "ON_PRE_HANDLER_ERROR"
    ON_HANDLER_ERROR = "ON_HANDLER_ERROR"
    ON_POST_HANDLER_ERROR = "ON_POST_HANDLER_ERROR"
    ON_PRE_COMMIT_ERROR = "ON_PRE_COMMIT_ERROR"
    ON_END_TX_ERROR = "ON_END_TX_ERROR"
    ON_POST_COMMIT_ERROR = "ON_POST_COMMIT_ERROR"
    ON_POST_RESPONSE_ERROR = "ON_POST_RESPONSE_ERROR"
    ON_ROLLBACK = "ON_ROLLBACK"


HookPhases: Tuple[HookPhase, ...] = tuple(HookPhase)
VALID_HOOK_PHASES: set[str] = {hook_phase.value for hook_phase in HookPhases}
StepFn = Callable[[Ctx[Any, Exception]], Awaitable[Any] | Any]
HookPredicate = Callable[[Ctx[Any, Exception]], bool]


def promote(ctx: Ctx[S, E], cls: type[U], /, **updates: object) -> U:
    return ctx.promote(cls, **updates)


def has_error(ctx: BaseCtx[S, E]) -> bool:
    return ctx.error is not None


@dataclass(slots=True)
class BootCtx(BaseCtx[Boot, E], Generic[E]):
    pass


@dataclass(slots=True)
class IngressCtx(BootCtx[E], Generic[E]):
    raw: object | None = None
    request: object | None = None
    method: str = ""
    path: str = ""
    headers: dict[str, object] = field(default_factory=dict)
    query: dict[str, object] = field(default_factory=dict)
    body: object | None = None


@dataclass(slots=True)
class RoutedCtx(IngressCtx[E], Generic[E]):
    protocol: str = ""
    path_params: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class BoundCtx(RoutedCtx[E], Generic[E]):
    binding: object | None = None
    model: object | None = None
    op: str = ""


@dataclass(slots=True)
class PlannedCtx(BoundCtx[E], Generic[E]):
    payload: object | None = None
    plan: object | None = None
    opmeta: object | None = None
    opview: object | None = None


@dataclass(slots=True)
class GuardedCtx(PlannedCtx[E], Generic[E]):
    authz: object | None = None


@dataclass(slots=True)
class ExecutingCtx(GuardedCtx[E], Generic[E]):
    pass


@dataclass(slots=True)
class ResolvedCtx(ExecutingCtx[E], Generic[E]):
    schema_in: object | None = None
    in_values: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class OperatedCtx(ResolvedCtx[E], Generic[E]):
    result: object | None = None


@dataclass(slots=True)
class EncodedCtx(OperatedCtx[E], Generic[E]):
    schema_out: object | None = None
    response_payload: object | None = None
    response_headers: dict[str, object] = field(default_factory=dict)
    status_code: int = 200


@dataclass(slots=True)
class EmittingCtx(EncodedCtx[E], Generic[E]):
    transport_response: object | None = None


@dataclass(slots=True)
class EgressedCtx(EmittingCtx[E], Generic[E]):
    pass


@dataclass(slots=True)
class FailedCtx(BaseCtx[Failed, E], Generic[E]):
    error: E | None = None


AtomResult: TypeAlias = Ctx[T, E] | FailedCtx[E]


def fail(ctx: Ctx[S, E], error: E, /, **updates: object) -> FailedCtx[E]:
    return cast(
        FailedCtx[E],
        ctx.promote(
            FailedCtx,
            error=error,
            **updates,
        ),
    )


class AtomFailure(Exception):
    """
    Optional internal exception type for atoms that want to signal
    a mapped domain/runtime failure via raise instead of returning fail(...).
    """

    def __init__(self, error: object) -> None:
        super().__init__(str(error))
        self.error = error


class Atom(ABC, Generic[S, T, E]):
    name: str = "atom"
    anchor: str = ""

    @abstractmethod
    async def __call__(
        self,
        obj: object | None,
        ctx: Ctx[S, E],
    ) -> AtomResult[T, E]:
        raise NotImplementedError


class StandardAtom(Atom[S, T, E], ABC):
    """
    Template-method base:
      - handles pre-failed input
      - handles success promotion
      - handles fail normalization
      - optionally maps raised exceptions into E
    """

    target_ctx: type[BaseCtx[T, E]]

    @final
    async def __call__(
        self,
        obj: object | None,
        ctx: Ctx[S, E],
    ) -> AtomResult[T, E]:
        if has_error(ctx):
            assert ctx.error is not None
            return fail(ctx, ctx.error)

        try:
            result = await self._run(obj, ctx)
        except AtomFailure as ex:
            return fail(ctx, cast(E, ex.error))
        except Exception as ex:
            mapped = self._map_exception(ex)
            if mapped is None:
                raise
            return fail(ctx, mapped)

        if isinstance(result, FailedCtx):
            return result

        return promote(ctx, self.target_ctx, **result)

    @abstractmethod
    async def _run(
        self,
        obj: object | None,
        ctx: Ctx[S, E],
    ) -> dict[str, object] | FailedCtx[E]:
        raise NotImplementedError

    def _map_exception(self, ex: Exception) -> E | None:
        return None


__all__ = [
    "S",
    "T",
    "U",
    "E",
    "Ctx",
    "HookPhase",
    "HookPhases",
    "VALID_HOOK_PHASES",
    "StepFn",
    "HookPredicate",
    "AtomResult",
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
    "AtomFailure",
    "Atom",
    "StandardAtom",
    "promote",
    "fail",
    "has_error",
    "DependencyLike",
    "ResponseLike",
    "is_dependency_like",
    "is_response_like",
]
