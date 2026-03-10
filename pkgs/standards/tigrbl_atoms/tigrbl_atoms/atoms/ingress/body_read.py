from __future__ import annotations

from ...types import Atom, Ctx, IngressCtx
from ...stages import Ingress

from typing import Any

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_BODY_READ


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})

    body = getattr(ctx, "body", None)
    if body is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        body = getattr(gw_raw, "body", None) if gw_raw is not None else None
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

    if body is None:
        return

    if isinstance(body, bytearray):
        body = bytes(body)
    elif isinstance(body, memoryview):
        body = body.tobytes()
    elif isinstance(body, str):
        body = body.encode("utf-8")

    ingress["body"] = body
    setattr(ctx, "body", body)
    if isinstance(body, bytes):
        setattr(ctx, "body_bytes", body)


class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.body_read"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        await _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
