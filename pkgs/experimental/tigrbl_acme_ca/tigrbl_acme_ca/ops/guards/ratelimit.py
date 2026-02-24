from __future__ import annotations
from fastapi import HTTPException


async def enforce_rate_limit(ctx, scope: str, key: str, cost: int = 1) -> None:
    limiter = ctx.get("rate_limiter")
    if not limiter:
        return
    allowed = await limiter.allow(scope=scope, key=key, cost=cost)
    if not allowed:
        raise HTTPException(status_code=429, detail="rate_limited")
