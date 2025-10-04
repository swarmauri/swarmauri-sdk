from __future__ import annotations

from typing import Any, Callable, Awaitable

class AttachTlsContexts:
    """On-demand TLS contexts for outbound connectors using SPIFFE materials.

    This middleware does not construct contexts itself; it delegates to tls.context helpers on demand.

    """
    def __init__(self, tls_helper: Any):
        self._tls = tls_helper

    async def __call__(self, ctx: dict[str, Any], next_handler: Callable[[dict[str, Any]], Awaitable[Any]]):
        ctx.setdefault("tls", {})
        ctx["tls"]["builder"] = self._tls
        return await next_handler(ctx)
