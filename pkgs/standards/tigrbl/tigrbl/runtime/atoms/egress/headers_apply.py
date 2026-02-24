from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_HEADERS_APPLY


def run(_obj: object | None, _ctx: Any) -> None:
    """egress:headers_apply@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
