from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.DEP_EXTRA


async def run(_obj: Any, ctx: Any) -> None:
    from ._common import run_deps

    await run_deps(ctx, kind="dep")
