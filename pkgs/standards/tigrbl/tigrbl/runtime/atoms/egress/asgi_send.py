from __future__ import annotations

import json
from typing import Any, Mapping

from ... import events as _ev
from ...._concrete._response import Response

ANCHOR = _ev.EGRESS_ASGI_SEND


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


async def run(obj: object | None, ctx: Any) -> None:
    del obj
    raw = getattr(ctx, "raw", None)
    send = getattr(raw, "send", None) if raw is not None else None
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not callable(send) or not isinstance(scope, dict) or scope.get("type") != "http":
        return

    resp = None
    resp_ns = getattr(ctx, "response", None)
    if resp_ns is not None:
        candidate = getattr(resp_ns, "result", None)
        if isinstance(candidate, Response):
            resp = candidate

    if resp is None:
        temp = getattr(ctx, "temp", None)
        egress = temp.get("egress") if isinstance(temp, dict) else None
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
            headers = dict(headers)
            headers.setdefault("content-type", "application/json; charset=utf-8")

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": _headers_to_asgi(headers),
            }
        )
        await send({"type": "http.response.body", "body": body, "more_body": False})
        return

    await send(
        {
            "type": "http.response.start",
            "status": int(resp.status_code),
            "headers": resp.raw_headers,
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": resp.body or b"",
            "more_body": False,
        }
    )


__all__ = ["ANCHOR", "run"]
