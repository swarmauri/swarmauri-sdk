from __future__ import annotations

from ...types import Atom, Ctx, ExecutingCtx
from ...stages import Executing

from typing import Any, Optional
import logging

from ... import events as _ev

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

    ov = getattr(ctx, "opview", None)
    if ov is None:
        raise RuntimeError("ctx_missing:opview")

    by_field = ov.schema_in.by_field
    required = tuple(name for name, entry in by_field.items() if entry.get("required"))
    temp["schema_in"] = {
        "fields": ov.schema_in.fields,
        "by_field": by_field,
        "required": required,
    }


class AtomImpl(Atom[Executing, Executing]):
    name = "schema.collect_in"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Executing]) -> Ctx[Executing]:
        _run(obj, ctx)
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
