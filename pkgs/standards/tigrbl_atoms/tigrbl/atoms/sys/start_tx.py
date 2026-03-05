from __future__ import annotations

from typing import Any

from ... import events as _ev
from ... import system as _sys

ANCHOR = _ev.SYS_TX_BEGIN
_run = _sys.get("txn", "begin")[1]


def run(obj: object | None, ctx: Any) -> None:
    _run(obj, ctx)


__all__ = ["ANCHOR", "run"]
