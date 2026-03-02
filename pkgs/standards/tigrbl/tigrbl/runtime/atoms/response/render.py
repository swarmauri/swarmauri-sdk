from __future__ import annotations
from typing import Any, Optional

from ... import events as _ev
from .renderer import ResponseHints
from .renderer import render

ANCHOR = _ev.OUT_DUMP  # "out:dump"


def _is_jsonrpc_request(ctx: Any) -> bool:
    raw = getattr(ctx, "gw_raw", None) or getattr(ctx, "raw", None)
    if getattr(raw, "kind", None) == "jsonrpc":
        return True

    temp = getattr(ctx, "temp", None)
    route = temp.get("route", {}) if isinstance(temp, dict) else {}
    rpc_env = route.get("rpc_envelope") if isinstance(route, dict) else None
    if isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0":
        return True

    path = getattr(raw, "path", None)
    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    if isinstance(path, str) and isinstance(prefix, str):
        return (path.rstrip("/") or "/") == (prefix.rstrip("/") or "/")

    return False


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
    if hints is None:
        hints = ResponseHints(status_code=int(getattr(ctx, "status_code", 200) or 200))
    default_media = getattr(resp_ns, "default_media", "application/json")
    envelope_default = getattr(resp_ns, "envelope_default", False)
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
            if _is_jsonrpc_request(ctx) and isinstance(
                egress.get("transport_response"), dict
            ):
                return resp
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
