from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_PATH_EXTRACT


def run(_obj: object | None, _ctx: Any) -> None:
    """ingress:path_extract@{ANCHOR}."""
    return None


__all__ = ["ANCHOR", "run"]
