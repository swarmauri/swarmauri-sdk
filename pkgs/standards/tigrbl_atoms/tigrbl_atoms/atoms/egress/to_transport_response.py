from __future__ import annotations

from ...types import Atom, Ctx, EmittingCtx
from ...stages import Encoded, Emitting

import json
from typing import Any, Mapping

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.EGRESS_TO_TRANSPORT_RESPONSE


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
    request_id = _jsonrpc_request_id(ctx)
    if request_id is None:
        normalized["status_code"] = 204
        normalized["body"] = b""
        return normalized

    body = normalized.get("body")
    if body is None:
        body = getattr(ctx, "result", None)
    if isinstance(body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            body = bytes(body).decode("utf-8", errors="replace")

    if not (isinstance(body, Mapping) and body.get("jsonrpc") == "2.0"):
        body = {"jsonrpc": "2.0", "result": body, "id": request_id}

    normalized["status_code"] = 200
    normalized["body"] = body
    return normalized


def _run(obj: object | None, ctx: Any) -> None:
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
    if body is None:
        body = getattr(ctx, "result", None)
    if body is None:
        response_ns = getattr(ctx, "response", None)
        if response_ns is not None:
            body = getattr(response_ns, "result", None)

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


class AtomImpl(Atom[Encoded, Emitting]):
    name = "egress.to_transport_response"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Emitting]:
        _run(obj, ctx)
        return ctx.promote(EmittingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
