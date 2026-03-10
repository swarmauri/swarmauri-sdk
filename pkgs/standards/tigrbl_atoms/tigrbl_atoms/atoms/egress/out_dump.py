from __future__ import annotations

from ...types import Atom, Ctx, EncodedCtx
from ...stages import Encoded

from typing import Any

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.EGRESS_OUT_DUMP


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})
    if "wire_payload" in egress:
        return

    wire_payload = temp.get("response_payload")
    if wire_payload is None:
        wire_payload = egress.get("result", getattr(ctx, "result", None))

    if wire_payload is not None:
        egress["wire_payload"] = wire_payload


class AtomImpl(Atom[Encoded, Encoded]):
    name = "egress.out_dump"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
