from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Boot

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_ATTACH_COMPILED


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})

    compiled = getattr(ctx, "compiled", None)
    if compiled is None:
        plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
        compiled = getattr(plan, "compiled", None)

    if compiled is not None:
        ingress["compiled"] = compiled


class AtomImpl(Atom[Boot, Boot]):
    name = "ingress.attach_compiled"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Boot]) -> Ctx[Boot]:
        _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

run = _run

__all__ = ["ANCHOR", "INSTANCE"]
