from __future__ import annotations

from typing import Any, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_in, ensure_schema_out

# Runs at the very beginning of the lifecycle, before in-model build/validation.
ANCHOR = _ev.SCHEMA_COLLECT_IN  # "schema:collect_in"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled inbound schema into ctx.temp."""
    ov = opview_from_ctx(ctx)
    ensure_schema_in(ctx, ov)
    ensure_schema_out(ctx, ov)


__all__ = ["ANCHOR", "run"]
