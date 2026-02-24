from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_INIT


def run(_obj: object | None, _ctx: Any) -> None:
    """ingress:ctx_init@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
