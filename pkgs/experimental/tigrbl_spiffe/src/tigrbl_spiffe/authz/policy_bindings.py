from __future__ import annotations

from typing import Any, Callable, Awaitable, Iterable

class RequireTrustDomain:
    """Simple authz middleware to require a SPIFFE trust domain for the principal.

    In real deployments, prefer integrating with the platform's security dependency system.

    """
    def __init__(self, allowed_trust_domains: Iterable[str]):
        self._domains = set(allowed_trust_domains)

    @staticmethod
    def _domain_of(spiffe_id: str | None) -> str | None:
        if not spiffe_id:
            return None
        # naive parse: spiffe://<td>/<rest>
        if spiffe_id.startswith("spiffe://"):
            rest = spiffe_id[len("spiffe://"):]
            return rest.split("/", 1)[0]
        return None

    async def __call__(self, ctx: dict[str, Any], next_handler: Callable[[dict[str, Any]], Awaitable[Any]]):
        principal = ctx.get("principal") or {}
        spiffe_id = principal.get("spiffe_id")
        td = self._domain_of(spiffe_id)
        if td is None or (self._domains and td not in self._domains):
            # Let the framework translate to 403; we keep the middleware framework-agnostic
            raise PermissionError("forbidden: trust domain not allowed")
        return await next_handler(ctx)
