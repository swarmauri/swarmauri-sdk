from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from ... import events as _ev
from ...stages import Operated, Ready
from ...types import Atom, Ctx, cast_ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE

HandlerFn = Callable[[object | None, Any], object | Awaitable[object]]


class BoundAtom(Atom[Ready, Operated]):
    name = "handler.custom"
    anchor = ANCHOR

    def __init__(self, fn: HandlerFn, *, name: str | None = None) -> None:
        self._fn = fn
        if name:
            self.name = name

    async def __call__(self, obj: object | None, ctx: Ctx[Ready]) -> Ctx[Operated]:
        result = self._fn(obj, ctx)
        if inspect.isawaitable(result):
            result = await result
        setattr(ctx, "result", result)
        return cast_ctx(ctx)


def bind(fn: HandlerFn, *, name: str | None = None) -> Atom[Ready, Operated]:
    return BoundAtom(fn, name=name)


__all__ = ["ANCHOR", "HandlerFn", "BoundAtom", "bind"]
