from __future__ import annotations

from ...types import Atom, Ctx, OperatedCtx
from ...stages import Operated

from typing import Any, Optional
import logging

from ... import events as _ev
from ..._opview_helpers import _ensure_schema_out

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def _run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled outbound schema into ctx.temp."""
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    if isinstance(temp.get("schema_out"), dict):
        return

    temp["schema_out"] = dict(_ensure_schema_out(ctx))


class AtomImpl(Atom[Operated, Operated]):
    name = "schema.collect_out"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
