# tigrbl/v3/runtime/executor/types.py
from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Union,
    Protocol,
    runtime_checkable,
)

try:
    from fastapi import Request  # type: ignore
except Exception:  # pragma: no cover
    Request = Any  # type: ignore

try:
    from sqlalchemy.orm import Session  # type: ignore
    from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
except Exception:  # pragma: no cover
    Session = Any  # type: ignore
    AsyncSession = Any  # type: ignore


@runtime_checkable
class _Step(Protocol):
    def __call__(self, ctx: "_Ctx") -> Union[Any, Awaitable[Any]]: ...


HandlerStep = Union[
    _Step,
    Callable[["_Ctx"], Any],
    Callable[["_Ctx"], Awaitable[Any]],
]
PhaseChains = Mapping[str, Sequence[HandlerStep]]


class _Ctx(dict):
    """Dict-like context with attribute access.

    Common keys:
      • request: FastAPI Request (optional)
      • db: Session | AsyncSession
      • api/model/op: optional metadata
      • result: last non-None step result
      • error: last exception caught (on failure paths)
      • response: SimpleNamespace(result=...) for POST_RESPONSE shaping
      • temp: scratch dict used by atoms/hook steps
    """

    __slots__ = ()
    __getattr__ = dict.get  # type: ignore[assignment]
    __setattr__ = dict.__setitem__  # type: ignore[assignment]

    @classmethod
    def ensure(
        cls,
        *,
        request: Optional[Request],
        db: Union[Session, AsyncSession, None],
        seed: Optional[MutableMapping[str, Any]] = None,
    ) -> "_Ctx":
        ctx = cls() if seed is None else (seed if isinstance(seed, _Ctx) else cls(seed))
        if request is not None:
            ctx.request = request
            state = getattr(request, "state", None)
            if state is not None and getattr(state, "ctx", None) is None:
                try:
                    state.ctx = ctx  # make ctx available to deps
                except Exception:  # pragma: no cover
                    pass
        if db is not None:
            ctx.db = db
        if "temp" not in ctx or not isinstance(ctx.get("temp"), dict):
            ctx.temp = {}
        return ctx


__all__ = ["_Ctx", "HandlerStep", "PhaseChains", "Request", "Session", "AsyncSession"]
