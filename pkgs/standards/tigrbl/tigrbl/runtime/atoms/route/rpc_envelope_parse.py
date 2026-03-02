from __future__ import annotations

import json
from dataclasses import replace
from typing import Any, Mapping

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def _is_rpc_envelope(payload: Mapping[str, Any]) -> bool:
    method = payload.get("method")
    if not isinstance(method, str) or not method.strip():
        return False

    marker = payload.get("jsonrpc")
    if marker is None:
        return True
    return marker == "2.0"


def _set_rpc_route(
    ctx: Any, route: dict[str, Any], env: GwRouteEnvelope, rpc: Mapping[str, Any] | Any
) -> None:
    rpc_dict = _to_rpc_dict(rpc)
    route["rpc_envelope"] = rpc_dict
    setattr(ctx, "gw_raw", replace(env, kind="jsonrpc", rpc=rpc_dict))


def _to_rpc_dict(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        return dict(payload)
    data = getattr(payload, "__dict__", None)
    if isinstance(data, dict):
        return dict(data)
    return {}


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
        if isinstance(payload, Mapping) and _is_rpc_envelope(payload):
            route["rpc_envelope"] = payload
        return

    if env.kind != "maybe-jsonrpc":
        return

    def _has_rpc_method(payload: Mapping[str, Any] | Any) -> bool:
        if isinstance(payload, Mapping):
            method = payload.get("method")
        else:
            method = getattr(payload, "method", None)
        return isinstance(method, str) and bool(method.strip())

    parsed_payload = getattr(ctx, "payload", None)
    if not isinstance(parsed_payload, Mapping):
        parsed_payload = getattr(ctx, "body", None)
    if _has_rpc_method(parsed_payload):
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
    if _has_rpc_method(body):
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
