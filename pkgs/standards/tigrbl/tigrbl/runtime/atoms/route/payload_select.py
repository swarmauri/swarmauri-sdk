from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def run(_obj: object | None, _ctx: Any) -> None:
    """route:payload_select@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
