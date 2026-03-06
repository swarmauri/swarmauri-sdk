from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Encoded

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_RESULT_NORMALIZE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    if isinstance(temp.get("rpc_error"), dict):
        egress["result"] = None
        setattr(ctx, "result", None)
        return

    if "result" not in egress:
        if hasattr(ctx, "result"):
            egress["result"] = getattr(ctx, "result")
        elif "response_payload" in temp:
            egress["result"] = temp.get("response_payload")


class AtomImpl(Atom[Encoded, Encoded]):
    name = "egress.result_normalize"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

run = _run

__all__ = ["ANCHOR", "INSTANCE"]
