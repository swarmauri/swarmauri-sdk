from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_RPC_METHOD_MATCH


def run(_obj: object | None, _ctx: Any) -> None:
    """route:rpc_method_match@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
