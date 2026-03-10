from __future__ import annotations

from typing import Any, Dict


def _ctx_view(ctx: Any) -> Dict[str, Any]:
    """Small read-only view for user callables."""
    safe_view = getattr(ctx, "safe_view", None)
    if callable(safe_view):
        view = safe_view(include_temp=True)
        return dict(view)

    return {
        "op": getattr(ctx, "op", None),
        "persist": getattr(ctx, "persist", True),
        "temp": getattr(ctx, "temp", None),
        "tenant": getattr(ctx, "tenant", None),
        "user": getattr(ctx, "user", None),
        "now": getattr(ctx, "now", None),
    }


__all__ = ["_ctx_view"]
