from __future__ import annotations

import json
from typing import Any, Mapping, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_TO_TRANSPORT_RESPONSE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _jsonrpc_request_id(ctx: Any) -> Any:
    temp = getattr(ctx, "temp", None)
    route = temp.get("route", {}) if isinstance(temp, dict) else {}
    rpc_env = route.get("rpc_envelope") if isinstance(route, dict) else None
    if isinstance(rpc_env, Mapping):
        return rpc_env.get("id")

    raw = getattr(ctx, "gw_raw", None) or getattr(ctx, "raw", None)
    rpc = getattr(raw, "rpc", None)
    if isinstance(rpc, Mapping):
        return rpc.get("id")
    return None


def _is_jsonrpc_request(ctx: Any) -> bool:
    raw = getattr(ctx, "gw_raw", None) or getattr(ctx, "raw", None)
    if getattr(raw, "kind", None) == "jsonrpc":
        return True

    temp = getattr(ctx, "temp", None)
    route = temp.get("route", {}) if isinstance(temp, dict) else {}
    rpc_env = route.get("rpc_envelope") if isinstance(route, dict) else None
    if isinstance(rpc_env, Mapping) and rpc_env.get("jsonrpc") == "2.0":
        return True

    path = getattr(raw, "path", None)
    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    if isinstance(path, str) and isinstance(prefix, str):
        return (path.rstrip("/") or "/") == (prefix.rstrip("/") or "/")

    return False


def _normalize_jsonrpc_transport_response(
    ctx: Any, response: dict[str, Any]
) -> dict[str, Any]:
    normalized = dict(response)
    body = normalized.get("body")
    if body is None:
        body = getattr(ctx, "result", None)
    if isinstance(body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            body = bytes(body).decode("utf-8", errors="replace")

    if not (isinstance(body, Mapping) and body.get("jsonrpc") == "2.0"):
        body = {"jsonrpc": "2.0", "result": body, "id": _jsonrpc_request_id(ctx)}

    normalized["status_code"] = 200
    normalized["body"] = body
    return normalized


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    existing = egress.get("transport_response")
    if isinstance(existing, dict):
        if _is_jsonrpc_request(ctx):
            normalized = _normalize_jsonrpc_transport_response(ctx, existing)
            egress["transport_response"] = normalized
            setattr(ctx, "transport_response", normalized)
        return

    body = egress.get("enveloped")
    if body is None:
        body = egress.get("wire_payload")

    headers_obj = egress.get("headers", getattr(ctx, "response_headers", {})) or {}
    if isinstance(headers_obj, dict):
        headers = dict(headers_obj)
    else:
        data = getattr(headers_obj, "__dict__", None)
        if isinstance(data, dict):
            headers = dict(data)
        else:
            try:
                headers = dict(headers_obj)
            except Exception:
                headers = {}

    status_code = int(
        egress.get("status_code", getattr(ctx, "status_code", 200)) or 200
    )
    response = {
        "status_code": status_code,
        "headers": headers,
        "body": body,
    }
    if _is_jsonrpc_request(ctx):
        response = _normalize_jsonrpc_transport_response(ctx, response)

    egress["transport_response"] = response
    setattr(ctx, "transport_response", response)


__all__ = ["ANCHOR", "run"]
