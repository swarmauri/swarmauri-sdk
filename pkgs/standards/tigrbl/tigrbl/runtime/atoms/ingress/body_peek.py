from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_BODY_PEEK


def run(_obj: object | None, _ctx: Any) -> None:
    """ingress:body_peek@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
