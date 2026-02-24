from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_POLICY_APPLY


def run(_obj: object | None, _ctx: Any) -> None:
    """route:binding_policy_apply@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
