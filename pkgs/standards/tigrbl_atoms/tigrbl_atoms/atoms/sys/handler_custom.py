from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE

HandlerFn = Callable[[object | None, Any], object | Awaitable[object]]


def _resolve_handler(obj: object | None, ctx: Any) -> HandlerFn | None:
    fn = getattr(ctx, "handler", None)
    if callable(fn):
        return fn

    model = getattr(ctx, "model", None)
    if model is None and obj is not None:
        model = type(obj)

    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if model is None or not isinstance(alias, str):
        return None

    model_fn = getattr(model, alias, None)
    if callable(model_fn):
        return lambda _obj, _ctx: model_fn(_ctx)

    return None


class BoundAtom(Atom[Resolved, Operated]):
    name = "handler.custom"
    anchor = ANCHOR

    def __init__(self, fn: HandlerFn, *, name: str | None = None) -> None:
        self._fn = fn
        if name:
            self.name = name

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        result = self._fn(obj, ctx)
        if inspect.isawaitable(result):
            result = await result
        setattr(ctx, "result", result)
        return ctx.promote(OperatedCtx)


def bind(fn: HandlerFn, *, name: str | None = None) -> Atom[Resolved, Operated]:
    return BoundAtom(fn, name=name)


class AtomImpl(Atom[Resolved, Operated]):
    name = "handler.custom"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        fn = _resolve_handler(obj, ctx)
        if fn is None:
            return ctx.promote(OperatedCtx)
        result = fn(obj, ctx)
        if inspect.isawaitable(result):
            result = await result
        setattr(ctx, "result", result)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()


__all__ = ["ANCHOR", "HandlerFn", "BoundAtom", "bind", "INSTANCE"]
