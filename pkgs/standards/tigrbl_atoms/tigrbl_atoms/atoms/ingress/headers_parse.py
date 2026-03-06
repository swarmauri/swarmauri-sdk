from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Ingress, Ingress

from collections import defaultdict
from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_HEADERS_PARSE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _parse_raw_headers(scope: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    raw_headers = scope.get("headers")
    if not isinstance(raw_headers, list):
        return {}

    for item in raw_headers:
        if (
            isinstance(item, tuple)
            and len(item) == 2
            and isinstance(item[0], (bytes, bytearray))
            and isinstance(item[1], (bytes, bytearray))
        ):
            key = bytes(item[0]).decode("latin-1").lower()
            value = bytes(item[1]).decode("latin-1")
            out[key].append(value)
    return dict(out)


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    parsed: dict[str, Any] | None = None

    request = getattr(ctx, "request", None)
    headers = getattr(request, "headers", None) if request is not None else None
    if headers is not None:
        parsed = dict(headers)

    if parsed is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        gw_headers = getattr(gw_raw, "headers", None) if gw_raw is not None else None
        if gw_headers is not None:
            parsed = dict(gw_headers)

    if parsed is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict):
            parsed = _parse_raw_headers(scope)

    if parsed is None:
        return

    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["headers"] = parsed
    setattr(ctx, "headers", parsed)




class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.headers_parse"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
