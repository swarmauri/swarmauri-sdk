from __future__ import annotations

from urllib.parse import parse_qsl
from typing import Any, MutableMapping

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope

ANCHOR = _ev.INGRESS_RAW_FROM_SCOPE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _decode_headers(headers: object) -> dict[str, str]:
    if not isinstance(headers, list):
        return {}
    out: dict[str, str] = {}
    for pair in headers:
        if not isinstance(pair, tuple) or len(pair) != 2:
            continue
        k, v = pair
        if isinstance(k, (bytes, bytearray)) and isinstance(v, (bytes, bytearray)):
            out[bytes(k).decode("latin-1").lower()] = bytes(v).decode("latin-1")
    return out


def _parse_query(raw_query: object) -> dict[str, str]:
    if isinstance(raw_query, (bytes, bytearray)):
        pairs = parse_qsl(bytes(raw_query).decode("latin-1"), keep_blank_values=True)
    elif isinstance(raw_query, str):
        pairs = parse_qsl(raw_query, keep_blank_values=True)
    else:
        return {}
    return {k: v for k, v in pairs}


def run(obj: object | None, ctx: object) -> None:
    del obj
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not isinstance(scope, dict):
        return

    scope_type = scope.get("type")
    headers = _decode_headers(scope.get("headers"))
    query = _parse_query(scope.get("query_string", b""))
    path = str(scope.get("path", "/"))
    scheme = str(scope.get("scheme", "http")).lower()

    route_envelope: GwRouteEnvelope | None = None
    if scope_type == "http":
        method = str(scope.get("method", "GET")).upper()
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

    if route_envelope is None:
        return

    setattr(ctx, "gw_raw", route_envelope)
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})
    ingress.update(
        {
            "transport": route_envelope.transport,
            "scheme": route_envelope.scheme,
            "kind": route_envelope.kind,
            "raw_headers": headers,
            "raw_query": query,
            "raw_path": path,
        }
    )
    temp.setdefault("route", {})["gw_raw"] = route_envelope


__all__ = ["ANCHOR", "run"]
