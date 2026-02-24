from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_METRICS_START


def run(_obj: object | None, _ctx: Any) -> None:
    """ingress:metrics_start@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
