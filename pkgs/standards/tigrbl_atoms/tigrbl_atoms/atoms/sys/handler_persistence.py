from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Resolved, Operated
from ...types import Atom, Ctx, cast_ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    # Persistence handling is now implemented directly by sys atoms and
    # runtime-route plumbing; this atom remains as an ordered phase anchor.
    del obj, ctx


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_persistence"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
