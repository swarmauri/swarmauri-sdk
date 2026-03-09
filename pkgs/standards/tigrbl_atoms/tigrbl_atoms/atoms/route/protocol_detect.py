from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Ingress, Routed
from ...types import Atom, Ctx, RoutedCtx

ANCHOR = _ev.ROUTE_PROTOCOL_DETECT


def _looks_like_jsonrpc(route: dict[str, object], ctx: Any) -> bool:
    rpc = route.get("rpc")
    if isinstance(rpc, dict):
        if rpc.get("jsonrpc") == "2.0" and isinstance(rpc.get("method"), str):
            return True

    body = getattr(ctx, "body", None)
    if isinstance(body, dict):
        if body.get("jsonrpc") == "2.0" and isinstance(body.get("method"), str):
            return True

    headers = getattr(ctx, "headers", None)
    if isinstance(headers, dict):
        content_type = headers.get("content-type") or headers.get("Content-Type")
        if isinstance(content_type, str) and "json" in content_type.lower():
            if isinstance(body, dict) and "method" in body:
                return True

    gw_raw = getattr(ctx, "gw_raw", None)
    kind = getattr(gw_raw, "kind", None) if gw_raw is not None else None
    return kind == "jsonrpc"


def _http_scheme(ctx: Any) -> str | None:
    gw_raw = getattr(ctx, "gw_raw", None)
    if gw_raw is not None:
        scheme = getattr(gw_raw, "scheme", None)
        if scheme in {"http", "https"}:
            return str(scheme)

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if isinstance(scope, dict):
        scheme = scope.get("scheme")
        if scheme in {"http", "https"}:
            return str(scheme)

    request = getattr(ctx, "request", None)
    scope = getattr(request, "scope", None) if request is not None else None
    if isinstance(scope, dict):
        scheme = scope.get("scheme")
        if scheme in {"http", "https"}:
            return str(scheme)

    return None


def _ws_scheme(ctx: Any) -> str | None:
    gw_raw = getattr(ctx, "gw_raw", None)
    if gw_raw is not None:
        scheme = getattr(gw_raw, "scheme", None)
        if scheme in {"ws", "wss"}:
            return str(scheme)

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if isinstance(scope, dict) and scope.get("type") == "websocket":
        scheme = scope.get("scheme")
        if scheme in {"ws", "wss"}:
            return str(scheme)
        return "ws"

    request = getattr(ctx, "request", None)
    scope = getattr(request, "scope", None) if request is not None else None
    if isinstance(scope, dict) and scope.get("type") == "websocket":
        scheme = scope.get("scheme")
        if scheme in {"ws", "wss"}:
            return str(scheme)
        return "ws"

    return None


def _route_transport(ctx: Any) -> str | None:
    gw_raw = getattr(ctx, "gw_raw", None)
    if gw_raw is not None:
        transport = getattr(gw_raw, "transport", None)
        if transport in {"http", "ws"}:
            return str(transport)

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if isinstance(scope, dict):
        scope_type = scope.get("type")
        if scope_type == "http":
            return "http"
        if scope_type == "websocket":
            return "ws"

    request = getattr(ctx, "request", None)
    scope = getattr(request, "scope", None) if request is not None else None
    if isinstance(scope, dict):
        scope_type = scope.get("type")
        if scope_type == "http":
            return "http"
        if scope_type == "websocket":
            return "ws"

    return None


def _dedupe_keep_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route_obj = temp.setdefault("route", {})
    route = route_obj if isinstance(route_obj, dict) else {}
    if route is not route_obj:
        temp["route"] = route

    transport = _route_transport(ctx)
    method = str(getattr(ctx, "method", "") or "").upper()
    candidates: list[str] = []

    if transport == "ws":
        scheme = _ws_scheme(ctx) or "ws"
        candidates.append(scheme)
        route["transport"] = "ws"
        route["scheme"] = scheme
        route["route_kind"] = "duplex"

    elif transport == "http":
        scheme = _http_scheme(ctx) or "http"
        route["transport"] = "http"
        route["scheme"] = scheme
        route["route_kind"] = "request_response"

        if _looks_like_jsonrpc(route, ctx):
            candidates.append(f"{scheme}.jsonrpc")

        candidates.append(f"{scheme}.rest")

        if method in {"GET", "HEAD", "OPTIONS", "DELETE"}:
            candidates = [f"{scheme}.rest"]

    else:
        # Unknown transport. Leave room for fallback matching.
        route["transport"] = transport or ""
        route["scheme"] = route.get("scheme", "")
        route["route_kind"] = "unknown"

    candidates = _dedupe_keep_order(candidates)

    route["protocol_candidates"] = candidates
    route["protocol"] = candidates[0] if candidates else ""
    route["binding"] = route.get("binding")
    route["matched"] = False

    setattr(ctx, "proto", route["protocol"])
    setattr(ctx, "protocol", route["protocol"])


class AtomImpl(Atom[Ingress, Routed]):
    name = "route.protocol_detect"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Routed]:
        _run(obj, ctx)
        return ctx.promote(
            RoutedCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
