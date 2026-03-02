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


def _normalize_path(path: str | None) -> str:
    if not isinstance(path, str) or not path:
        return "/"
    if path == "/":
        return "/"
    return path.rstrip("/") or "/"


def _is_jsonrpc_endpoint(ctx: Any, env: GwRouteEnvelope) -> bool:
    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    if not isinstance(prefix, str):
        return False
    return _normalize_path(env.path) == _normalize_path(prefix)


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

    route_proto = route.get("protocol")
    binding_preselected_rpc = (
        isinstance(route_proto, str)
        and route_proto.endswith(".jsonrpc")
        and route.get("binding") is not None
    )

    rest_jsonrpc_endpoint = env.kind == "rest" and _is_jsonrpc_endpoint(ctx, env)

    if (
        env.kind not in {"maybe-jsonrpc", "rest"}
        and not binding_preselected_rpc
        and not rest_jsonrpc_endpoint
    ):
        return

    if env.kind == "rest" and not rest_jsonrpc_endpoint and not binding_preselected_rpc:
        return

    parsed_payload = getattr(ctx, "payload", None)
    if not isinstance(parsed_payload, Mapping):
        parsed_payload = getattr(ctx, "body", None)
    if (
        isinstance(parsed_payload, Mapping)
        and parsed_payload.get("jsonrpc") == "2.0"
        and "method" in parsed_payload
    ):
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

    if (
        isinstance(parsed, dict)
        and parsed.get("jsonrpc") == "2.0"
        and "method" in parsed
    ):
        _set_rpc_route(ctx, route, env, parsed)
    else:
        setattr(ctx, "gw_raw", replace(env, kind="rest"))
