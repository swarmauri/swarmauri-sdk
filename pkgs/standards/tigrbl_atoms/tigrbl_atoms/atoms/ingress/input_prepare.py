from __future__ import annotations

import json
import importlib.util as _importlib_util
from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_INPUT_PREPARE
_HAS_ORJSON = _importlib_util.find_spec("orjson") is not None
if _HAS_ORJSON:
    import orjson as _orjson  # type: ignore[import-not-found]


def _loads_json_bytes(payload: bytes) -> Any:
    if _HAS_ORJSON:
        return _orjson.loads(payload)
    return json.loads(payload.decode("utf-8"))


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})

    body = getattr(ctx, "body", ingress.get("body"))
    if isinstance(body, (bytes, bytearray, memoryview)):
        raw_bytes = bytes(body)
        ingress["body_peek"] = raw_bytes[:256]
        content_type = str(
            (getattr(ctx, "headers", {}) or {}).get("content-type", "")
        ).lower()
        if "json" in content_type:
            try:
                ingress["body_json"] = _loads_json_bytes(raw_bytes)
            except Exception:
                pass
    elif body is not None:
        ingress["body_peek"] = str(body)[:256]

    request = getattr(ctx, "request", None)
    if request is not None and body is not None and hasattr(request, "body"):
        request.body = body


class AtomImpl(Atom[Ingress, Ingress]):
    name = "ingress.input_prepare"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
