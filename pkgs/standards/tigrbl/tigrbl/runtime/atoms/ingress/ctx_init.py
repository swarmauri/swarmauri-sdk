from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_INIT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    temp.setdefault("ingress", {})
    temp["ingress"].setdefault("ctx_initialized", True)


__all__ = ["ANCHOR", "run"]
