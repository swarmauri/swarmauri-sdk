from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_RPC_METHOD_MATCH


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    envelope = temp.setdefault("route", {}).get("rpc_envelope")
    if isinstance(envelope, dict) and "method" in envelope:
        temp["route"]["rpc_method"] = envelope["method"]


__all__ = ["ANCHOR", "run"]
