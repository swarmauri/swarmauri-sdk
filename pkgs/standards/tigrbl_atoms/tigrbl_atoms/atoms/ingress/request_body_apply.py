from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Ingress, Prepared

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_REQUEST_BODY_APPLY


def _run(obj: object | None, ctx: Any) -> None:
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




class AtomImpl(Atom[Ingress, Prepared]):
    name = "ingress.request_body_apply"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Prepared]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
