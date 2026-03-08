from __future__ import annotations

import json
from typing import Any, Mapping
from uuid import uuid4

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def _normalize_rpc_envelope(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    method = payload.get("method")
    if not isinstance(method, str) or not method.strip():
        return None

    jsonrpc = payload.get("jsonrpc")
    params = payload.get("params")
    if jsonrpc != "2.0" and params is None:
        return None

    normalized: dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": payload.get("id"),
    }
    if normalized["id"] is None and jsonrpc != "2.0":
        normalized["id"] = str(uuid4())
    return normalized


def _payload_from_ctx(route: Mapping[str, Any], ctx: Any) -> Mapping[str, Any] | None:
    rpc = route.get("rpc")
    if isinstance(rpc, Mapping):
        return rpc

    for candidate in (getattr(ctx, "payload", None), getattr(ctx, "body", None)):
        if isinstance(candidate, Mapping):
            return candidate

    gw_raw = getattr(ctx, "gw_raw", None)
    body = getattr(gw_raw, "body", None) if gw_raw is not None else None
    if isinstance(body, Mapping):
        return body

    if isinstance(body, (bytes, bytearray, memoryview)):
        try:
            parsed = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            return None
        if isinstance(parsed, Mapping):
            return parsed

    return None


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    payload = _payload_from_ctx(route if isinstance(route, Mapping) else {}, ctx)
    if not isinstance(payload, Mapping):
        return

    rpc = _normalize_rpc_envelope(payload)
    if not isinstance(rpc, dict):
        return

    route["rpc"] = rpc
    route["rpc_envelope"] = rpc
    route["rpc_method"] = rpc["method"]


class AtomImpl(Atom[Ingress, Ingress]):
    name = "route.rpc_envelope_parse"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
