from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Resolved, Executing

from typing import Any

from ... import events as _ev
from ... import system as _sys

ANCHOR = _ev.SYS_TX_BEGIN
_delegate = _sys.get("txn", "begin")[1]


def _run(obj: object | None, ctx: Any) -> None:
    _run(obj, ctx)




class AtomImpl(Atom[Resolved, Executing]):
    name = "sys.start_tx"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Executing]:
        rv = _delegate(obj, ctx)
        if hasattr(rv, "__await__"):
            await rv
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
