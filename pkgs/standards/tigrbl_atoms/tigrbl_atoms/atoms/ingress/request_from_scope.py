from __future__ import annotations

from ...types import Atom, Ctx, IngressCtx
from ...stages import Ingress

from typing import Any

from ... import events as _ev
from .._temp import _ensure_temp

Request = Any

ANCHOR = _ev.INGRESS_REQUEST_FROM_SCOPE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not isinstance(scope, dict):
        return

    req = Request(scope, app=getattr(ctx, "app", None))
    setattr(ctx, "request", req)

    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["request"] = req


class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.request_from_scope"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
