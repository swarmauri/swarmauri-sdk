from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Operated, Operated

from typing import Any

from ... import events as _ev
from ... import system as _sys

ANCHOR = _ev.SYS_TX_COMMIT
_delegate = _sys.get("txn", "commit")[1]


async def _run(obj: object | None, ctx: Any) -> None:
    await _run(obj, ctx)




class AtomImpl(Atom[Operated, Operated]):
    name = "sys.commit_tx"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
