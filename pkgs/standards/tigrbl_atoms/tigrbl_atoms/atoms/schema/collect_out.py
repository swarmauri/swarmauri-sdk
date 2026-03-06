from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Operated

from typing import Any, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_out

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def _run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled outbound schema into ctx.temp."""
    ov = opview_from_ctx(ctx)
    ensure_schema_out(ctx, ov)


class AtomImpl(Atom[Operated, Operated]):
    name = "schema.collect_out"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

run = _run

__all__ = ["ANCHOR", "INSTANCE"]
