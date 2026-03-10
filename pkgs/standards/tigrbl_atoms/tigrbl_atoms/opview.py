from __future__ import annotations

from typing import Any


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp
