from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Ingress

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_PATH_EXTRACT


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    request = getattr(ctx, "request", None)
    url = getattr(request, "url", None) if request is not None else None
    value = getattr(url, "path", None) if url is not None else None
    if value is None and request is not None:
        value = getattr(request, "path", None)

    if value is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        value = getattr(gw_raw, "path", None) if gw_raw is not None else None

    if value is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict):
            value = scope.get("path")

    if value is None:
        return

    path = str(value)
    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["path"] = path
    setattr(ctx, "path", path)


class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.path_extract"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

run = _run

__all__ = ["ANCHOR", "INSTANCE"]
