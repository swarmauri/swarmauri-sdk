from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_BODY_READ


async def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    ingress = temp.setdefault("ingress", {})

    body = getattr(ctx, "body", None)
    if body is None:
        body = ingress.get("body")

    if body is None:
        raw = getattr(ctx, "raw", None)
        receive = getattr(raw, "receive", None) if raw is not None else None
        scope = getattr(raw, "scope", None) if raw is not None else None
        scope_type = scope.get("type") if isinstance(scope, dict) else None
        if callable(receive) and scope_type == "http":
            chunks: list[bytes] = []
            while True:
                message = await receive()
                if not isinstance(message, dict):
                    break
                if message.get("type") != "http.request":
                    break
                chunk = message.get("body", b"")
                if isinstance(chunk, (bytes, bytearray)):
                    chunks.append(bytes(chunk))
                if not bool(message.get("more_body", False)):
                    break
            body = b"".join(chunks)

    if body is not None:
        if isinstance(body, bytearray):
            body = bytes(body)
        ingress["body"] = body
        setattr(ctx, "body", body)
        if isinstance(body, bytes):
            setattr(ctx, "body_bytes", body)


__all__ = ["ANCHOR", "run"]
