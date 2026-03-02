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
    gw_raw = getattr(ctx, "gw_raw", None)
    rpc = getattr(gw_raw, "rpc", None)
    if isinstance(rpc, Mapping):
        return rpc.get("id")
    temp = getattr(ctx, "temp", None)
    route = temp.get("route", {}) if isinstance(temp, dict) else {}
    rpc_env = route.get("rpc_envelope") if isinstance(route, dict) else None
    if isinstance(rpc_env, Mapping):
        return rpc_env.get("id")
    return None


def _is_jsonrpc_request(ctx: Any) -> bool:
    gw_raw = getattr(ctx, "gw_raw", None)
    if getattr(gw_raw, "kind", None) == "jsonrpc":
        return True
    path = getattr(gw_raw, "path", None)
    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    if isinstance(path, str) and isinstance(prefix, str):
        return (path.rstrip("/") or "/") == (prefix.rstrip("/") or "/")
    return False


def _jsonrpc_envelope(ctx: Any, body: Any) -> Mapping[str, Any]:
    if isinstance(body, Mapping) and body.get("jsonrpc") == "2.0":
        return body
    return {"jsonrpc": "2.0", "result": body, "id": _jsonrpc_request_id(ctx)}


def _normalize_body_for_jsonrpc(ctx: Any, body: Any) -> Mapping[str, Any]:
    if isinstance(body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            body = bytes(body).decode("utf-8", errors="replace")
    return _jsonrpc_envelope(ctx, body)


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    existing = egress.get("transport_response")
    if isinstance(existing, dict):
        if _is_jsonrpc_request(ctx):
            normalized = dict(existing)
            normalized["status_code"] = 200
            normalized["body"] = _normalize_body_for_jsonrpc(ctx, existing.get("body"))
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
    if _is_jsonrpc_request(ctx):
        status_code = 200
        body = _normalize_body_for_jsonrpc(ctx, body)

    response = {
        "status_code": status_code,
        "headers": headers,
        "body": body,
    }
    egress["transport_response"] = response
    setattr(ctx, "transport_response", response)


__all__ = ["ANCHOR", "run"]
