from __future__ import annotations

import inspect
from typing import Any

from ... import events as _ev

ANCHOR = _ev.PRE_TX_SECDEP


async def run(dep: object | None, ctx: Any) -> Any:
    fn = getattr(dep, "dependency", dep)
    if not callable(fn):
        return None
    try:
        rv = fn(ctx)
    except TypeError:
        rv = fn()
    if inspect.isawaitable(rv):
        return await rv
    return rv
