from __future__ import annotations

from typing import Any, Callable, Awaitable

class InjectSpiffeExtras:
    """Middleware that injects SPIFFE adapter and config into ctx for downstream ops/hooks.

    Usage (pseudocode): app.use(InjectSpiffeExtras(adapter, cfg))

    """
    def __init__(self, adapter: Any, cfg: Any):
        self._adapter = adapter
        self._cfg = cfg

    async def __call__(self, ctx: dict[str, Any], next_handler: Callable[[dict[str, Any]], Awaitable[Any]]):
        ctx["spiffe_adapter"] = self._adapter
        ctx["spiffe_config"] = self._cfg
        return await next_handler(ctx)
