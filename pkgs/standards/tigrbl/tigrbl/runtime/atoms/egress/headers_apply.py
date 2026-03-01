from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_HEADERS_APPLY


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    headers_obj = getattr(ctx, "response_headers", None)
    if headers_obj is None:
        headers_obj = egress.get("headers")

    headers: dict[str, str] = {}
    if isinstance(headers_obj, dict):
        headers = {str(k): str(v) for k, v in headers_obj.items()}
    elif headers_obj is not None:
        headers = {str(k): str(v) for k, v in dict(headers_obj).items()}

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


__all__ = ["ANCHOR", "run"]
