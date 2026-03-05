from __future__ import annotations

from typing import Any

from ... import events as _ev
from ... import system as _sys

ANCHOR = _ev.SYS_TX_COMMIT
_run = _sys.get("txn", "commit")[1]


async def run(obj: object | None, ctx: Any) -> None:
    await _run(obj, ctx)


__all__ = ["ANCHOR", "run"]
