from __future__ import annotations

from ...types import Atom, Ctx, IngressCtx
from ...stages import Ingress

from typing import Any

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_METHOD_EXTRACT


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    method = None

    request = getattr(ctx, "request", None)
    if request is not None:
        method = getattr(request, "method", None)

    if method is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        method = getattr(gw_raw, "method", None) if gw_raw is not None else None

    if method is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict):
            method = scope.get("method")

    if method is None:
        return

    value = str(method).upper()
    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["method"] = value
    setattr(ctx, "method", value)


class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.method_extract"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
