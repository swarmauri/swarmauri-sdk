from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    env = getattr(ctx, "gw_raw", None)
    if not isinstance(env, GwRouteEnvelope):
        payload = getattr(ctx, "payload", None)
        if isinstance(payload, dict) and payload.get("jsonrpc") == "2.0":
            route["rpc_envelope"] = payload
        return

    if env.kind != "maybe-jsonrpc":
        return

    body = env.body
    if not isinstance(body, (bytes, bytearray)):
        return

    try:
        parsed = json.loads(bytes(body).decode("utf-8"))
    except Exception:
        return

    if (
        isinstance(parsed, dict)
        and parsed.get("jsonrpc") == "2.0"
        and "method" in parsed
    ):
        route["rpc_envelope"] = parsed
        setattr(ctx, "gw_raw", replace(env, kind="jsonrpc", rpc=parsed))
    else:
        setattr(ctx, "gw_raw", replace(env, kind="rest"))
