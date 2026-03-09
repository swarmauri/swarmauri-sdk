from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE

HandlerFn = Callable[[object | None, Any], object | Awaitable[object]]


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


__all__ = ["ANCHOR", "HandlerFn", "BoundAtom", "bind"]
