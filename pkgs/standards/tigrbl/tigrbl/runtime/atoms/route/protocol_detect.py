from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PROTOCOL_DETECT


def run(_obj: object | None, _ctx: Any) -> None:
    """route:protocol_detect@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
