from __future__ import annotations

from typing import Any, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_out

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled outbound schema into ctx.temp."""
    ov = opview_from_ctx(ctx)
    ensure_schema_out(ctx, ov)


__all__ = ["ANCHOR", "run"]
