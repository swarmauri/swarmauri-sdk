from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_CTX_FINALIZE


def run(_obj: object | None, _ctx: Any) -> None:
    """route:ctx_finalize@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
