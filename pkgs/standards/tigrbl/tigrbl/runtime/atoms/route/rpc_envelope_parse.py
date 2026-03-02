from __future__ import annotations

import json
from dataclasses import replace
from typing import Any, Mapping

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def _set_rpc_route(
    ctx: Any, route: dict[str, Any], env: GwRouteEnvelope, rpc: Mapping[str, Any]
) -> None:
    route["rpc_envelope"] = dict(rpc)
    setattr(ctx, "gw_raw", replace(env, kind="jsonrpc", rpc=dict(rpc)))


def _is_rpc_payload(payload: Mapping[str, Any]) -> bool:
    if "method" not in payload:
        return False
    # Accept both strict JSON-RPC 2.0 envelopes and shorthand method/params
    # payloads used by compatibility clients.
    return payload.get("jsonrpc") == "2.0" or "params" in payload


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

    parsed_payload = getattr(ctx, "payload", None)
    if not isinstance(parsed_payload, Mapping):
        parsed_payload = getattr(ctx, "body", None)
    if isinstance(parsed_payload, Mapping) and _is_rpc_payload(parsed_payload):
        _set_rpc_route(ctx, route, env, parsed_payload)
        return

    body = env.body
    if body is None:
        body = getattr(ctx, "body", None)
    if not isinstance(body, (bytes, bytearray)):
        body = getattr(ctx, "body", None)
    if not isinstance(body, (bytes, bytearray)):
        ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
        body = ingress.get("body") if isinstance(ingress, dict) else None
    if not isinstance(body, (bytes, bytearray)):
        return

    try:
        parsed = json.loads(bytes(body).decode("utf-8"))
    except Exception:
        return

    if isinstance(parsed, dict) and _is_rpc_payload(parsed):
        _set_rpc_route(ctx, route, env, parsed)
    else:
        setattr(ctx, "gw_raw", replace(env, kind="rest"))
