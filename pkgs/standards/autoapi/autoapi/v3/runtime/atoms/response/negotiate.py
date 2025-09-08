from __future__ import annotations
from typing import Any, Optional
import logging

from ... import events as _ev
from .negotiation import negotiate_media_type
from .renderer import ResponseHints


logger = logging.getLogger("uvicorn")

ANCHOR = _ev.OUT_DUMP  # "out:dump"


def run(obj: Optional[object], ctx: Any) -> None:
    """response:negotiate@out:dump

    Determine the response media type if not already set.
    """
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = ResponseHints()
        resp_ns.hints = hints
    logger.debug("Negotiation atom starting with media_type=%s", hints.media_type)
    if not hints.media_type:
        accept = getattr(req, "headers", {}).get("accept", "*/*")
        default_media = getattr(resp_ns, "default_media", "application/json")
        logger.debug(
            "Negotiating media type for Accept=%s default=%s", accept, default_media
        )
        chosen = negotiate_media_type(accept, default_media)
        hints.media_type = chosen
        logger.debug("Negotiation atom chose media_type=%s", chosen)


__all__ = ["ANCHOR", "run"]
