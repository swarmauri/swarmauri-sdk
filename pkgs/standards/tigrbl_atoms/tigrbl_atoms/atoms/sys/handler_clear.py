from __future__ import annotations

from typing import Any

import tigrbl_ops_oltp as _core

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, cast_ctx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    model = obj if isinstance(obj, type) else getattr(ctx, "model", None)
    if not isinstance(model, type):
        raise TypeError("handler_clear requires a model type")
    setattr(ctx, "result", await _core.clear(model, {}, db=_ctx.db(ctx)))


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_clear"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
