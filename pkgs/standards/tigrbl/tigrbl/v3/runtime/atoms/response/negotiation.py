from __future__ import annotations
from typing import List
import logging


def _parse(accept: str) -> List[str]:
    parts = [p.strip() for p in accept.split(",") if p.strip()]

    def q(p: str) -> float:
        for seg in p.split(";"):
            seg = seg.strip()
            if seg.startswith("q="):
                try:
                    return float(seg[2:])
                except Exception:
                    return 1.0
        return 1.0

    return sorted(parts, key=q, reverse=True)


logger = logging.getLogger("uvicorn")


def negotiate_media_type(accept: str, default_media: str) -> str:
    logger.debug("Negotiating media type from Accept header %s", accept)
    if not accept or accept == "*/*":
        return default_media
    for cand in _parse(accept):
        mt = cand.split(";")[0].strip()
        if mt in (
            "application/json",
            "text/html",
            "text/plain",
            "application/octet-stream",
        ):
            return mt
        if mt.startswith("text/"):
            return "text/plain"
    return default_media


__all__ = ["negotiate_media_type"]
