from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Prepared, Prepared

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_BODY_PEEK


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
    body = ingress.get("body", getattr(ctx, "body", None))
    if isinstance(body, (bytes, bytearray, memoryview)):
        ingress["body_peek"] = bytes(body)[:256]
    elif body is not None:
        ingress["body_peek"] = str(body)[:256]




class AtomImpl(Atom[Prepared, Prepared]):
    name = "ingress.body_peek"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Prepared]) -> Ctx[Prepared]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
