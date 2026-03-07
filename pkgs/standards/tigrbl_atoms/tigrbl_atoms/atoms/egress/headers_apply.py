from __future__ import annotations

from ...types import Atom, Ctx, EncodedCtx
from ...stages import Encoded

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_HEADERS_APPLY


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    headers_obj = getattr(ctx, "response_headers", None)
    if headers_obj is None:
        headers_obj = egress.get("headers")

    headers: dict[str, str] = {}

    def _to_mapping(obj: Any) -> dict[str, Any]:
        if isinstance(obj, dict):
            return obj
        data = getattr(obj, "__dict__", None)
        if isinstance(data, dict):
            return data
        try:
            return dict(obj)
        except Exception:
            return {}

    if isinstance(headers_obj, dict):
        headers = {str(k): str(v) for k, v in headers_obj.items()}
    elif headers_obj is not None:
        headers = {str(k): str(v) for k, v in _to_mapping(headers_obj).items()}

    body = egress.get("enveloped", egress.get("wire_payload"))
    if "content-type" not in {k.lower() for k in headers}:
        if isinstance(body, (dict, list, tuple)):
            headers["content-type"] = "application/json"
        elif isinstance(body, (bytes, bytearray, memoryview)):
            headers["content-type"] = "application/octet-stream"
        else:
            headers.setdefault("content-type", "text/plain; charset=utf-8")

    egress["headers"] = headers
    setattr(ctx, "response_headers", headers)


class AtomImpl(Atom[Encoded, Encoded]):
    name = "egress.headers_apply"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
