from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Executing

from typing import Any, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_in

# Runs at the very beginning of the lifecycle, before in-model build/validation.
ANCHOR = _ev.SCHEMA_COLLECT_IN  # "schema:collect_in"

logger = logging.getLogger("uvicorn")


def _run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled inbound schema into ctx.temp."""
    ov = opview_from_ctx(ctx)
    ensure_schema_in(ctx, ov)


class AtomImpl(Atom[Executing, Executing]):
    name = "schema.collect_in"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Executing]) -> Ctx[Executing]:
        _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
