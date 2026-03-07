from __future__ import annotations

from typing import Any

import tigrbl_ops_oltp as _core

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    model = obj if isinstance(obj, type) else getattr(ctx, "model", None)
    if not isinstance(model, type):
        raise TypeError("handler_update requires a model type")
    ident = _ctx.ident(model, ctx)
    payload = _ctx.payload(ctx)
    setattr(ctx, "result", await _core.update(model, ident, payload, db=_ctx.db(ctx)))


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_update"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
