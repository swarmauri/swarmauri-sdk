from __future__ import annotations

from typing import Any

ANCHOR = "prex_tx_begin:dep"


async def run(_obj: Any, ctx: Any) -> None:
    from ._common import run_deps

    await run_deps(ctx, kind="dep")
