from __future__ import annotations

import json
from typing import Any, MutableMapping

from ... import events as _ev
from ...._concrete._response import Response
from ....mapping.rest.helpers import _ensure_jsonable

ANCHOR = _ev.EGRESS_RESULT_NORMALIZE


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

    if "result" not in egress:
        if "response_payload" in temp:
            egress["result"] = temp.get("response_payload")
        elif hasattr(ctx, "result"):
            result = getattr(ctx, "result")
            if isinstance(result, Response):
                body = getattr(result, "body", None)
                if isinstance(body, (bytes, bytearray)):
                    try:
                        egress["result"] = json.loads(bytes(body).decode("utf-8"))
                    except Exception:
                        egress["result"] = None
                else:
                    egress["result"] = None
            else:
                egress["result"] = _ensure_jsonable(result)

    if "status_code" not in egress and getattr(ctx, "op_target", None) == "create":
        egress["status_code"] = 201


__all__ = ["ANCHOR", "run"]
