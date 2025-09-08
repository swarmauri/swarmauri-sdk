from __future__ import annotations
from typing import Any, Optional, Mapping

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
    temp = getattr(ctx, "temp", None)
    payload = getattr(resp_ns, "result", None)
    extras = None
    if isinstance(temp, Mapping):
        extras = temp.get("response_payload")
    if isinstance(payload, Mapping) and isinstance(extras, Mapping):
        merged = dict(payload)
        merged.update(extras)
        payload = merged
    elif extras is not None:
        payload = extras
    if payload is None:
        return None
    hints = getattr(resp_ns, "hints", None)
    default_media = getattr(resp_ns, "default_media", "application/json")
    envelope_default = getattr(resp_ns, "envelope_default", False)
    resp = render(
        req,
        payload,
        hints=hints,
        default_media=default_media,
        envelope_default=envelope_default,
    )
    resp_ns.result = resp
    return resp


__all__ = ["ANCHOR", "run"]
