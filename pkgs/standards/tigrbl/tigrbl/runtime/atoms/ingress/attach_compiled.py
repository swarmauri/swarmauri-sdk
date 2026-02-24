from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_ATTACH_COMPILED


def run(_obj: object | None, _ctx: Any) -> None:
    """ingress:attach_compiled@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
