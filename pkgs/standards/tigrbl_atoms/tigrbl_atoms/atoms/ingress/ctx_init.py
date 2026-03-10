from __future__ import annotations

from ...types import Atom, Ctx, BootCtx
from ...stages import Boot

from time import perf_counter
from typing import Any

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_CTX_INIT


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})
    ingress.setdefault("ctx_initialized", True)
    ingress.setdefault("started_at", perf_counter())


class AtomImpl(Atom[Boot, Boot]):
    name = "ingress.ctx_init"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Boot]) -> Ctx[Boot]:
        _run(obj, ctx)
        return ctx.promote(BootCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
