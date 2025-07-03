"""
Common hooks and utilities shared across all entity types.
"""

from typing import Any, Dict

from ... import log
from ...autoapi import api


@api.hook(api.Phase.ON_ERROR)
async def global_error_handler(ctx: Dict[str, Any]) -> None:
    """Global error handler for all methods"""
    error = ctx.get("error")
    method = getattr(ctx.get("env"), "method", "unknown")

    if error:
        log.error("Error in %s: %s", method, str(error), exc_info=error)
