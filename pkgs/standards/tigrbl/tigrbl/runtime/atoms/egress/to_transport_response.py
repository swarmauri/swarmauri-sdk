from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_TO_TRANSPORT_RESPONSE


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

    body = egress.get("enveloped")
    if body is None:
        body = egress.get("wire_payload")

    headers_obj = egress.get("headers", getattr(ctx, "response_headers", {})) or {}
    if isinstance(headers_obj, dict):
        headers = dict(headers_obj)
    else:
        data = getattr(headers_obj, "__dict__", None)
        if isinstance(data, dict):
            headers = dict(data)
        else:
            try:
                headers = dict(headers_obj)
            except Exception:
                headers = {}

    response = {
        "status_code": int(
            egress.get("status_code", getattr(ctx, "status_code", 200)) or 200
        ),
        "headers": headers,
        "body": body,
    }
    egress["transport_response"] = response
    setattr(ctx, "transport_response", response)


__all__ = ["ANCHOR", "run"]
