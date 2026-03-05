from __future__ import annotations

import json
from typing import Any, Mapping

from ... import events as _ev
from ...._concrete._response import Response

ANCHOR = _ev.EGRESS_ASGI_SEND


NO_BODY_STATUS = set(range(100, 200)) | {204, 205, 304}


def finalize_transport_response(
    scope: Mapping[str, Any],
    status: int,
    headers: list[tuple[bytes, bytes]],
    body: bytes,
) -> tuple[list[tuple[bytes, bytes]], bytes]:
    method = str(scope.get("method", "GET")).upper()

    if method == "HEAD" or status in NO_BODY_STATUS:
        drop = {b"content-length", b"content-type", b"transfer-encoding"}
        headers = [(k, v) for (k, v) in headers if k.lower() not in drop]
        return headers, b""

    headers = [(k, v) for (k, v) in headers if k.lower() != b"content-length"]
    headers.append((b"content-length", str(len(body)).encode("latin-1")))
    return headers, body


async def _send_json(env: Any, status: int, payload: Any) -> None:
    body = json.dumps(payload).encode("utf-8")
    headers = [(b"content-type", b"application/json")]
    headers, body = finalize_transport_response(env.scope, status, headers, body)
    await env.send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": headers,
        }
    )
    await env.send(
        {
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        }
    )


async def _send_transport_response(env: Any, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    if not isinstance(egress, dict) or egress.get("response_sent"):
        return

    transport = egress.get("transport_response")
    if not isinstance(transport, dict):
        transport = {
            "status_code": int(getattr(ctx, "status_code", 200) or 200),
            "headers": {},
            "body": getattr(ctx, "result", None),
        }

    status = int(transport.get("status_code", getattr(ctx, "status_code", 200) or 200))
    headers_obj = transport.get("headers", {})
    headers: list[tuple[bytes, bytes]] = []
    if isinstance(headers_obj, dict):
        headers = [
            (str(k).encode("latin-1"), str(v).encode("latin-1"))
            for k, v in headers_obj.items()
            if v is not None
        ]

    body_obj = transport.get("body", b"")
    if isinstance(body_obj, (bytes, bytearray)):
        body = bytes(body_obj)
    elif body_obj is None:
        body = b""
    else:
        body = json.dumps(body_obj, separators=(",", ":"), default=str).encode("utf-8")
        if not any(k.lower() == b"content-type" for k, _ in headers):
            headers.append((b"content-type", b"application/json; charset=utf-8"))

    headers, body = finalize_transport_response(env.scope, status, headers, body)

    await env.send(
        {"type": "http.response.start", "status": status, "headers": headers}
    )
    await env.send({"type": "http.response.body", "body": body, "more_body": False})
    egress["response_sent"] = True


def _headers_to_asgi(headers: Mapping[str, Any]) -> list[tuple[bytes, bytes]]:
    out: list[tuple[bytes, bytes]] = []
    for k, v in (headers or {}).items():
        if v is None:
            continue
        out.append((str(k).encode("latin-1"), str(v).encode("latin-1")))
    return out


def _json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj, separators=(",", ":"), ensure_ascii=False, default=str
    ).encode("utf-8")


def _to_headers_mapping(headers: Any) -> dict[str, Any]:
    if isinstance(headers, dict):
        return dict(headers)
    data = getattr(headers, "__dict__", None)
    if isinstance(data, dict):
        return dict(data)
    try:
        return dict(headers)
    except Exception:
        return {}


async def run(obj: object | None, ctx: Any) -> None:
    del obj
    raw = getattr(ctx, "raw", None)
    send = getattr(raw, "send", None) if raw is not None else None
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not callable(send) or not isinstance(scope, dict) or scope.get("type") != "http":
        return

    temp = getattr(ctx, "temp", None)
    egress = temp.get("egress") if isinstance(temp, dict) else None
    if isinstance(egress, dict) and egress.get("suppress_asgi_send"):
        has_transport_response = "transport_response" in egress
        if not has_transport_response:
            return

    resp = None
    resp_ns = getattr(ctx, "response", None)
    if resp_ns is not None:
        candidate = getattr(resp_ns, "result", None)
        if isinstance(candidate, Response):
            resp = candidate

    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    if egress.get("response_sent"):
        return

    if resp is None:
        tr = egress.get("transport_response") if isinstance(egress, dict) else None

        status = int(tr.get("status_code", 200)) if isinstance(tr, dict) else 200
        headers = tr.get("headers", {}) if isinstance(tr, dict) else {}
        body_obj = tr.get("body", None) if isinstance(tr, dict) else None

        if isinstance(body_obj, (bytes, bytearray)):
            body = bytes(body_obj)
        elif body_obj is None:
            body = b""
        else:
            body = _json_bytes(body_obj)
            headers = _to_headers_mapping(headers)
            headers.setdefault("content-type", "application/json; charset=utf-8")

        egress["transport_response"] = {
            "status_code": status,
            "headers": _to_headers_mapping(headers),
            "body": body,
        }
        asgi_headers = _headers_to_asgi(headers)
        asgi_headers, body = finalize_transport_response(
            scope, status, asgi_headers, body
        )
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": asgi_headers,
            }
        )
        await send({"type": "http.response.body", "body": body, "more_body": False})
        egress["response_sent"] = True
        return

    egress["transport_response"] = {
        "status_code": int(resp.status_code),
        "headers": {
            k.decode("latin-1"): v.decode("latin-1") for k, v in resp.raw_headers
        },
        "body": resp.body or b"",
    }
    body = resp.body or b""
    headers = list(resp.raw_headers)
    headers, body = finalize_transport_response(
        scope, int(resp.status_code), headers, body
    )
    await send(
        {
            "type": "http.response.start",
            "status": int(resp.status_code),
            "headers": headers,
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        }
    )
    egress["response_sent"] = True


__all__ = [
    "ANCHOR",
    "NO_BODY_STATUS",
    "finalize_transport_response",
    "_send_json",
    "_send_transport_response",
    "run",
]
