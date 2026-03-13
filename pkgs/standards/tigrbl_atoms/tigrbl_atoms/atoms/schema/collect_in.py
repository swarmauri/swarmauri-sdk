from __future__ import annotations

from ...types import Atom, Ctx, ExecutingCtx
from ...stages import Executing

from typing import Any, Optional
import logging

from ... import events as _ev
from ..._opview_helpers import _ensure_schema_in

# Runs at the very beginning of the lifecycle, before in-model build/validation.
ANCHOR = _ev.SCHEMA_COLLECT_IN  # "schema:collect_in"

logger = logging.getLogger("uvicorn")


def _run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled inbound schema into ctx.temp."""
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    if isinstance(temp.get("schema_in"), dict):
        return

    temp["schema_in"] = dict(_ensure_schema_in(ctx))


class AtomImpl(Atom[Executing, Executing]):
    name = "schema.collect_in"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Executing]) -> Ctx[Executing]:
        _run(obj, ctx)
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
