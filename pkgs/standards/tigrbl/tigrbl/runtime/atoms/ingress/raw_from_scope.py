from __future__ import annotations

from urllib.parse import parse_qsl

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope

ANCHOR = _ev.INGRESS_RAW_FROM_SCOPE


def _decode_headers(headers: object) -> dict[str, str]:
    if not isinstance(headers, list):
        return {}
    out: dict[str, str] = {}
    for pair in headers:
        if not isinstance(pair, tuple) or len(pair) != 2:
            continue
        k, v = pair
        if isinstance(k, bytes) and isinstance(v, bytes):
            out[k.decode("latin-1").lower()] = v.decode("latin-1")
    return out


def _parse_query(raw_query: object) -> dict[str, str]:
    if not isinstance(raw_query, (bytes, bytearray)):
        return {}
    return {
        k: v
        for k, v in parse_qsl(
            bytes(raw_query).decode("latin-1"), keep_blank_values=True
        )
    }


def run(obj: object | None, ctx: object) -> None:
    del obj
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not isinstance(scope, dict):
        return

    scope_type = scope.get("type")
    headers = _decode_headers(scope.get("headers"))
    query = _parse_query(scope.get("query_string", b""))
    path = scope.get("path", "/")
    scheme = scope.get("scheme", "http")

    if scope_type == "http":
        method = scope.get("method", "GET")
        route_envelope = GwRouteEnvelope(
            transport="http",
            scheme="https" if scheme == "https" else "http",
            kind="maybe-jsonrpc"
            if "application/json" in headers.get("content-type", "")
            else "rest",
            method=method,
            path=path,
            headers=headers,
            query=query,
            body=getattr(ctx, "body", None),
            ws_event=None,
            rpc=None,
        )
    elif scope_type == "websocket":
        route_envelope = GwRouteEnvelope(
            transport="ws",
            scheme="wss" if scheme in {"wss", "https"} else "ws",
            kind="unknown",
            method=None,
            path=path,
            headers=headers,
            query=query,
            body=None,
            ws_event=getattr(ctx, "raw_event", None),
            rpc=None,
        )
    else:
        return

    setattr(ctx, "gw_raw", route_envelope)
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    temp.setdefault("route", {})["gw_raw"] = route_envelope
