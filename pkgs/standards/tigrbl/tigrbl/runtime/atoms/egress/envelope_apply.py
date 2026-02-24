from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_ENVELOPE_APPLY


def run(_obj: object | None, _ctx: Any) -> None:
    """egress:envelope_apply@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
