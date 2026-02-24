from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def run(_obj: object | None, _ctx: Any) -> None:
    """route:rpc_envelope_parse@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
