from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_TO_TRANSPORT_RESPONSE


def run(_obj: object | None, _ctx: Any) -> None:
    """egress:to_transport_response@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
