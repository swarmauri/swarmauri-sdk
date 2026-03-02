from __future__ import annotations

import json
from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route = temp.setdefault("route", {})
    rpc_envelope = route.get("rpc_envelope")
    if isinstance(rpc_envelope, dict):
        payload = rpc_envelope.get("params", {})
        route["payload"] = payload
        setattr(ctx, "payload", payload)
        return

    payload = getattr(ctx, "payload", None)
    if payload is None:
        ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
        payload = ingress.get("body") if isinstance(ingress, dict) else None

    if isinstance(payload, (bytes, bytearray, memoryview)):
        try:
            payload = json.loads(bytes(payload).decode("utf-8"))
        except Exception:
            payload = {}

    if payload is not None:
        route["payload"] = payload
        setattr(ctx, "payload", payload)


__all__ = ["ANCHOR", "run"]
