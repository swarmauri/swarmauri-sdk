from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_HEADERS_PARSE


def run(_obj: object | None, _ctx: Any) -> None:
    """ingress:headers_parse@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
