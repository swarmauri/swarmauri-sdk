from __future__ import annotations

from ...types import Atom, Ctx, EncodedCtx
from ...stages import Encoded

from ... import events as _ev
from typing import Mapping

ANCHOR = _ev.OUT_BUILD  # run after payload is prepared, before render


def _run(_, ctx) -> None:
    """Mirror fields configured with ``io.header_out`` into HTTP response headers.

    - Does NOT remove fields from the response body (no header-only behavior).
    - Honors op-specific exposure via ``io.out_verbs``.
    Complexity: O(#fields in opview).
    """
    from tigrbl_atoms.atoms.response.renderer import ResponseHints

    resp = getattr(ctx, "response", None)
    if resp is None:
        return

    hints = getattr(resp, "hints", None)
    if hints is None:
        hints = ResponseHints(status_code=int(getattr(ctx, "status_code", 200) or 200))
        resp.hints = hints

    payload = getattr(resp, "result", None)
    if payload is None:
        temp = getattr(ctx, "temp", None)
        if isinstance(temp, Mapping):
            payload = temp.get("response_payload")
    if not isinstance(payload, dict):
        return

    specs = getattr(ctx, "specs", None)
    if not isinstance(specs, Mapping):
        model = getattr(ctx, "model", None)
        specs = getattr(model, "__tigrbl_cols__", {}) if model is not None else {}

    op = getattr(ctx, "op", None)
    for field_name, spec in specs.items():
        io = getattr(spec, "io", None)
        if not io:
            continue

        header_name = getattr(io, "header_out", None)
        if not header_name:
            continue

        out_verbs = set(getattr(io, "out_verbs", ()) or ())
        if op not in out_verbs:
            continue

        if field_name in payload:
            value = payload[field_name]
            if value is not None:
                hints.headers[header_name] = str(value)


class AtomImpl(Atom[Encoded, Encoded]):
    name = "response.headers_from_payload"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
