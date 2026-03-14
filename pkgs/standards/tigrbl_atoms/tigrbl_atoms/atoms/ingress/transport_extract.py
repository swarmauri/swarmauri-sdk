from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence
from urllib.parse import parse_qs

from tigrbl_typing.gw.raw import GwRouteEnvelope

from ... import events as _ev
from ..._request import Request
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_TRANSPORT_EXTRACT


def _decode_headers(raw_headers: object) -> dict[str, str]:
    if not isinstance(raw_headers, list):
        return {}
    headers: dict[str, str] = {}
    for item in raw_headers:
        if not (isinstance(item, tuple) and len(item) == 2):
            continue
        key, value = item
        if isinstance(key, (bytes, bytearray)) and isinstance(
            value, (bytes, bytearray)
        ):
            headers[bytes(key).decode("latin-1").lower()] = bytes(value).decode(
                "latin-1"
            )
    return headers


def _decode_headers_multi(raw_headers: object) -> dict[str, list[str]]:
    if not isinstance(raw_headers, list):
        return {}
    out: dict[str, list[str]] = defaultdict(list)
    for item in raw_headers:
        if not (isinstance(item, tuple) and len(item) == 2):
            continue
        key, value = item
        if isinstance(key, (bytes, bytearray)) and isinstance(
            value, (bytes, bytearray)
        ):
            out[bytes(key).decode("latin-1").lower()].append(
                bytes(value).decode("latin-1")
            )
    return dict(out)


def _normalize_query(query: object) -> dict[str, list[Any]]:
    if query is None:
        return {}
    if isinstance(query, Mapping):
        out: dict[str, list[Any]] = {}
        for key, value in query.items():
            if isinstance(value, Sequence) and not isinstance(
                value, (str, bytes, bytearray)
            ):
                out[str(key)] = list(value)
            else:
                out[str(key)] = [value]
        return out
    return {}


def _parse_query(raw_query: object) -> dict[str, list[str]]:
    if isinstance(raw_query, (bytes, bytearray)):
        return parse_qs(bytes(raw_query).decode("latin-1"), keep_blank_values=True)
    if isinstance(raw_query, str):
        return parse_qs(raw_query, keep_blank_values=True)
    return {}


async def _read_http_body(ctx: Any) -> object | None:
    body = getattr(ctx, "body", None)
    if body is not None:
        return body

    raw = getattr(ctx, "raw", None)
    receive = getattr(raw, "receive", None) if raw is not None else None
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not (
        callable(receive) and isinstance(scope, dict) and scope.get("type") == "http"
    ):
        return None

    chunks: list[bytes] = []
    while True:
        message = await receive()
        if not isinstance(message, dict) or message.get("type") != "http.request":
            break
        chunk = message.get("body", b"")
        if isinstance(chunk, (bytes, bytearray)):
            chunks.append(bytes(chunk))
        if not bool(message.get("more_body", False)):
            break
    return b"".join(chunks)


async def _run(obj: object | None, ctx: Any) -> None:
    del obj

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not isinstance(scope, dict):
        return

    request = getattr(ctx, "request", None)
    if request is None:
        request = Request(scope, app=getattr(ctx, "app", None))
        setattr(ctx, "request", request)

    method = str(scope.get("method", getattr(request, "method", "") or "")).upper()
    path = str(scope.get("path", getattr(request, "path", "/") or "/"))
    query = _normalize_query(getattr(request, "query_params", None)) or _parse_query(
        scope.get("query_string", b"")
    )
    headers = dict(getattr(request, "headers", {}) or {}) or _decode_headers_multi(
        scope.get("headers")
    )

    body = await _read_http_body(ctx)
    if body is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        body = getattr(gw_raw, "body", None) if gw_raw is not None else None

    if isinstance(body, bytearray):
        body = bytes(body)
    if isinstance(body, memoryview):
        body = body.tobytes()
    if isinstance(body, str):
        body = body.encode("utf-8")

    transport = "ws" if scope.get("type") == "websocket" else "http"
    scheme = str(scope.get("scheme", "http")).lower()

    gw_raw = GwRouteEnvelope(
        transport=transport,
        scheme="wss"
        if scheme in {"wss", "https"} and transport == "ws"
        else (
            "https" if scheme == "https" else ("ws" if transport == "ws" else "http")
        ),
        kind="unknown",
        method=method if transport == "http" else None,
        path=path,
        headers=_decode_headers(scope.get("headers")),
        query={str(k): [str(vv) for vv in values] for k, values in query.items()},
        body=body if transport == "http" else None,
        ws_event=getattr(ctx, "raw_event", None) if transport == "ws" else None,
        rpc=None,
    )
    setattr(ctx, "gw_raw", gw_raw)

    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})
    ingress.update(
        {
            "transport": transport,
            "scheme": gw_raw.scheme,
            "method": method,
            "path": path,
            "headers": headers,
            "query": query,
            "body": body,
            "request": request,
        }
    )
    setattr(ctx, "method", method)
    setattr(ctx, "path", path)
    setattr(ctx, "headers", headers)
    setattr(ctx, "query", query)
    if body is not None:
        setattr(ctx, "body", body)


class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.transport_extract"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        await _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
