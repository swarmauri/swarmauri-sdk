from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_RESULT_NORMALIZE


def run(_obj: object | None, _ctx: Any) -> None:
    """egress:result_normalize@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
