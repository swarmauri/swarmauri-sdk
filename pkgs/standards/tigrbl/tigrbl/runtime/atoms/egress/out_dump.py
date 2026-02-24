from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_OUT_DUMP


def run(_obj: object | None, _ctx: Any) -> None:
    """egress:out_dump@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
