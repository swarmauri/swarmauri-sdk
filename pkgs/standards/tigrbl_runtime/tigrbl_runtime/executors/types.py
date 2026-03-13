# tigrbl/runtime/executor/types.py
from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Union,
    runtime_checkable,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from tigrbl_atoms.types import BaseCtx
from tigrbl_concrete._concrete._request import Request


class _ResponseState:
    """Context-bound response namespace.

    Keeps ``ctx['result']`` synchronized with ``ctx.response.result`` updates so
    POST_RESPONSE hooks can safely shape egress payloads.
    """

    __slots__ = ("_ctx", "_data")

    def __init__(self, ctx: "_Ctx", value: Any = None) -> None:
        object.__setattr__(self, "_ctx", ctx)
        object.__setattr__(self, "_data", {})

        source = getattr(value, "__dict__", None)
        if isinstance(source, dict):
            for key, item in source.items():
                setattr(self, key, item)
        elif value is not None:
            result = getattr(value, "result", None)
            setattr(self, "result", result)

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        return data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        data = object.__getattribute__(self, "_data")
        data[name] = value
        if name == "result":
            ctx = object.__getattribute__(self, "_ctx")
            dict.__setitem__(ctx, "result", value)


@runtime_checkable
class _Step(Protocol):
    def __call__(self, ctx: "_Ctx") -> Union[Any, Awaitable[Any]]: ...


HandlerStep = Union[
    _Step,
    Callable[["_Ctx"], Any],
    Callable[["_Ctx"], Awaitable[Any]],
]
PhaseChains = Mapping[str, Sequence[HandlerStep]]


class _Ctx(BaseCtx[Any, Any]):
    """Dict-like runtime context with attribute access and atom promotion support."""

    __slots__ = ()

    def __getattribute__(self, name: str) -> Any:
        # Keep core context methods callable even when runtime data shadows
        # method names (for example: ctx["promote"] = None).
        if name == "promote":
            return _Ctx.promote.__get__(self, type(self))
        return dict.__getattribute__(self, name)

    def __getattr__(self, name: str) -> Any:
        return dict.get(self, name)

    def __setitem__(self, key: str, value: Any) -> None:
        if (
            key == "response"
            and value is not None
            and not isinstance(value, _ResponseState)
            and (
                (isinstance(value, Mapping) and "result" in value)
                or hasattr(value, "result")
            )
        ):
            value = _ResponseState(self, value)
        if key == "result":
            response = dict.get(self, "response")
            if isinstance(response, _ResponseState):
                data = object.__getattribute__(response, "_data")
                data["result"] = value
        dict.__setitem__(self, key, value)

    __setattr__ = __setitem__  # type: ignore[assignment]

    def promote(self, cls: type[Any], /, **updates: object) -> Any:
        """Promote runtime contexts into atom dataclass contexts."""
        if not is_dataclass(cls):
            raise TypeError(f"promote target must be a dataclass type, got {cls!r}")

        data: dict[str, object] = {}
        missing_required: list[str] = []

        for f in fields(cls):
            if f.name in updates:
                continue
            if f.name in self:
                data[f.name] = self[f.name]
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

    @classmethod
    def ensure(
        cls,
        *,
        request: Optional[Request],
        db: Union[Session, AsyncSession, None],
        seed: Optional[MutableMapping[str, Any] | BaseCtx[Any, Any]] = None,
    ) -> "_Ctx":
        if seed is None:
            ctx = cls()
        elif isinstance(seed, _Ctx):
            ctx = seed
        elif isinstance(seed, BaseCtx):
            ctx = cls({f.name: getattr(seed, f.name) for f in fields(type(seed))})
        else:
            ctx = cls(seed)

        if request is not None:
            ctx.request = request
            state = getattr(request, "state", None)
            if state is not None and getattr(state, "ctx", None) is None:
                try:
                    state.ctx = ctx  # make ctx available to deps
                except Exception:  # pragma: no cover
                    pass
        if db is not None:
            ctx._raw_db = db
            if "db" not in ctx:
                ctx.db = None
        if "temp" not in ctx or not isinstance(ctx.get("temp"), dict):
            ctx.temp = {}
        return ctx


__all__ = ["_Ctx", "HandlerStep", "PhaseChains", "Request", "Session", "AsyncSession"]
