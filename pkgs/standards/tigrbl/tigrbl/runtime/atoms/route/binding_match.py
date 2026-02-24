from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_MATCH


def run(_obj: object | None, _ctx: Any) -> None:
    """route:binding_match@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
