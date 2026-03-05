from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_REQUEST_BODY_APPLY


def run(obj: object | None, ctx: Any) -> None:
    del obj
    req = getattr(ctx, "request", None)
    body = getattr(ctx, "body", None)
    if req is None or body is None:
        return
    if isinstance(body, bytearray):
        body = bytes(body)
    if isinstance(body, memoryview):
        body = body.tobytes()
    if isinstance(body, str):
        body = body.encode("utf-8")
    if isinstance(body, bytes):
        req.body = body


__all__ = ["ANCHOR", "run"]
