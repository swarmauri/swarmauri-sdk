from __future__ import annotations

from typing import Any, Callable, Awaitable, Optional

class SpiffeAuthn:
    """Authenticates inbound requests bearing JWT/CWT SVIDs.

    Extracts token from headers (Authorization: Bearer <token>) and validates via SvidValidator.

    """
    def __init__(self, validator: Any, bundle_lookup: Optional[callable] = None):
        self._validator = validator
        self._bundle_lookup = bundle_lookup or (lambda _ctx: None)

    async def __call__(self, ctx: dict[str, Any], next_handler: Callable[[dict[str, Any]], Awaitable[Any]]):
        headers = (ctx.get("http") or {}).get("headers", {})  # framework-agnostic
        auth = headers.get("authorization") or headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            await self._validator.validate(kind="jwt", material=token.encode("utf-8"), bundle_id=None, ctx=ctx)
            # Attach principal (minimal)
            ctx["principal"] = {"spiffe_id": None, "token": token, "kind": "jwt"}
        return await next_handler(ctx)
