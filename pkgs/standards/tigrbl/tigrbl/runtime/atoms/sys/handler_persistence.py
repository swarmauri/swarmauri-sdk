from __future__ import annotations

from typing import Any

from ... import events as _ev
from ... import system as _sys

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE
_run = _sys.get("handler", "crud")[1]


def run(obj: object | None, ctx: Any) -> None:
    _run(obj, ctx)


__all__ = ["ANCHOR", "run"]
