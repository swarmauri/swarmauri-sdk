from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    payload = getattr(ctx, "payload", None)
    if isinstance(payload, dict) and "jsonrpc" in payload:
        temp.setdefault("route", {})["rpc_envelope"] = payload


__all__ = ["ANCHOR", "run"]
