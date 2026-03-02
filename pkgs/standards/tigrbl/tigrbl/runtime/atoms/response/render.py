from __future__ import annotations
from typing import Any, Optional

from ... import events as _ev
from .renderer import render

ANCHOR = _ev.OUT_DUMP  # "out:dump"


def run(obj: Optional[object], ctx: Any) -> Any:
    """response:render@out:dump

    Render ``ctx.response.result`` into a concrete Response object.
    """
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return None
    result = getattr(resp_ns, "result", None)
    if result is None:
        return None
    hints = getattr(resp_ns, "hints", None)
    status_code = getattr(ctx, "status_code", None)
    if hints is not None and status_code is not None:
        hints.status_code = int(status_code)
    default_media = getattr(resp_ns, "default_media", "application/json")
    envelope_default = getattr(resp_ns, "envelope_default", False)
    temp = getattr(ctx, "temp", None)
    route_ns = temp.get("route") if isinstance(temp, dict) else None
    rpc_env = route_ns.get("rpc_envelope") if isinstance(route_ns, dict) else None
    if getattr(getattr(ctx, "gw_raw", None), "kind", None) == "jsonrpc" or (
        isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0"
    ):
        return None
    resp = render(
        req,
        result,
        hints=hints,
        default_media=default_media,
        envelope_default=envelope_default,
    )
    resp_ns.result = resp
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        egress = temp.setdefault("egress", {})
        if isinstance(egress, dict):
            egress["transport_response"] = {
                "status_code": int(resp.status_code),
                "headers": {
                    k.decode("latin-1"): v.decode("latin-1")
                    for k, v in getattr(resp, "raw_headers", ())
                },
                "body": resp.body or b"",
            }
    return resp


__all__ = ["ANCHOR", "run"]
