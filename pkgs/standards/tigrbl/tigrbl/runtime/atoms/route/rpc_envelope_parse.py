from __future__ import annotations

import json
from dataclasses import replace
from typing import Any, Mapping

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def _set_rpc_route(
    ctx: Any,
    route: dict[str, Any],
    env: GwRouteEnvelope,
    rpc: Mapping[str, Any] | Any,
) -> None:
    if isinstance(rpc, Mapping):
        rpc_dict = dict(rpc)
    else:
        data = getattr(rpc, "__dict__", None)
        rpc_dict = dict(data) if isinstance(data, dict) else {}
    route["rpc_envelope"] = rpc_dict
    setattr(ctx, "gw_raw", replace(env, kind="jsonrpc", rpc=rpc_dict))


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

    def _is_rpc_envelope(payload: Mapping[str, Any] | Any) -> bool:
        method = payload.get("method") if isinstance(payload, Mapping) else None
        if method is None:
            method = getattr(payload, "method", None)
        return isinstance(method, str) and bool(method.strip())

    parsed_payload = getattr(ctx, "payload", None)
    if not isinstance(parsed_payload, Mapping):
        parsed_payload = getattr(ctx, "body", None)
    if _is_rpc_envelope(parsed_payload):
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
    if _is_rpc_envelope(body):
        _set_rpc_route(ctx, route, env, body)
        return
    if not isinstance(body, (bytes, bytearray)):
        return

    try:
        parsed = json.loads(bytes(body).decode("utf-8"))
    except Exception:
        return

    if _is_rpc_envelope(parsed):
        _set_rpc_route(ctx, route, env, parsed)
    else:
        setattr(ctx, "gw_raw", replace(env, kind="rest"))
