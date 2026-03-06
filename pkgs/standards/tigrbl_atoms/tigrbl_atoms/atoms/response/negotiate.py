from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Operated, Encoded
from typing import Any, Optional

from ... import events as _ev
from .negotiation import negotiate_media_type
from .renderer import ResponseHints

ANCHOR = _ev.OUT_DUMP  # "out:dump"


def _run(obj: Optional[object], ctx: Any) -> None:
    """response:negotiate@out:dump

    Determine the response media type if not already set.
    """
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = ResponseHints(status_code=int(getattr(ctx, "status_code", 200) or 200))
        resp_ns.hints = hints
    if not hints.media_type:
        accept = getattr(req, "headers", {}).get("accept", "*/*")
        default_media = getattr(resp_ns, "default_media", "application/json")
        hints.media_type = negotiate_media_type(accept, default_media)


class AtomImpl(Atom[Operated, Encoded]):
    name = "response.negotiate"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

run = _run

__all__ = ["ANCHOR", "INSTANCE"]
