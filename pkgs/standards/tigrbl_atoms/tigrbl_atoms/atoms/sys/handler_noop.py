from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Operated, Ready
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE
TARGET = "noop"


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    setattr(
        ctx,
        "result",
        {
            "ok": True,
            "noop": True,
            "alias": getattr(ctx, "op", None),
            "target": TARGET,
        },
    )


class AtomImpl(Atom[Ready, Operated]):
    name = "handler.noop"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ready]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "TARGET", "INSTANCE"]
