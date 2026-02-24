from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_TO_TRANSPORT_RESPONSE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    response = {
        "status_code": egress.get("status_code", 200),
        "headers": egress.get("headers", {}),
        "body": egress.get("enveloped", egress.get("wire_payload")),
    }
    egress["transport_response"] = response


__all__ = ["ANCHOR", "run"]
