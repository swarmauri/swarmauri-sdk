from __future__ import annotations

from typing import Any, Mapping, Optional

from ... import events as _ev
from .renderer import ResponseHints
from ...kernel import get_cached_specs

# Run after payload is prepared and before render. Other response atoms
# (negotiate/template/render) also bind to OUT_DUMP.
ANCHOR = _ev.OUT_DUMP  # "out:dump"


def _payload_from_ctx(ctx: Any) -> Optional[Mapping[str, Any]]:
    resp = getattr(ctx, "response", None)
    if resp is not None:
        # Prefer the result staged for rendering
        result = getattr(resp, "result", None)
        if isinstance(result, Mapping):
            return result
        # Some code may stash an interim payload
        payload = getattr(resp, "payload", None)
        if isinstance(payload, Mapping):
            return payload
    # Fallback to the temp buffer set by wire:dump
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, Mapping):
        out = temp.get("response_payload")
        if isinstance(out, Mapping):
            return out
    return None


def run(_: Optional[object], ctx: Any) -> None:
    """
    response:headers_from_payload@out:dump

    Mirror fields configured with `io.header_out` into HTTP response headers.
    - Does NOT remove fields from the response body (no header-only behavior).
    - Honors op-specific exposure via `io.out_verbs`.
    Complexity: O(#fields in opview/specs).
    """
    resp = getattr(ctx, "response", None)
    if resp is None:
        return

    hints = getattr(resp, "hints", None)
    if hints is None:
        hints = ResponseHints()
        resp.hints = hints

    payload = _payload_from_ctx(ctx)
    if not isinstance(payload, Mapping):
        return

    # Try to obtain column specs to inspect IO.header_out and out_verbs
    specs: Optional[Mapping[str, Any]] = None
    specs = getattr(ctx, "specs", None)
    if not isinstance(specs, Mapping):
        model = getattr(ctx, "model", None)
        if model is not None:
            try:
                specs = get_cached_specs(model)
            except Exception:
                specs = None
    if not specs:
        return

    op = getattr(ctx, "op", None)
    if not isinstance(op, str) or not op:
        return

    # Apply header_out for fields present in payload and exposed for this op
    for field_name, spec in specs.items():
        io = getattr(spec, "io", None)
        if io is None:
            continue
        header_name = getattr(io, "header_out", None)
        if not header_name:
            continue
        out_verbs = set(getattr(io, "out_verbs", ()) or ())
        if op not in out_verbs:
            continue
        if field_name in payload:
            value = payload[field_name]
            # Emit header whenever field is exposed; coerce None -> empty string
            hints.headers[header_name] = "" if value is None else str(value)


__all__ = ["ANCHOR", "run"]
