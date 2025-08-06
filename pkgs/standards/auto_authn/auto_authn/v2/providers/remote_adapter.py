# auto_authn/v2/providers/remote_adapter.py
from __future__ import annotations

import time
from typing import Final

import httpx
from fastapi import HTTPException, Request, status

from autoapi.v2.types.authn_abc import AuthNProvider
from ..hooks import register_inject_hook  # ← existing helper
from ..fastapi_deps import principal_var  # ← ContextVar used by filters


class RemoteAuthNAdapter(AuthNProvider):
    """
    Authenticate every request by calling a *remote* AuthN service.

    Parameters
    ----------
    base_url:
        Full origin of the AuthN deployment, *without* trailing slash,
        e.g. ``"https://authn.internal:8080"``.
    timeout:
        Float seconds for the outbound HTTP POST (default **0.4 s**).
    cache_ttl:
        TTL in seconds for the in‑process API‑key cache (default **10 s**).
    cache_size:
        Maximum number of distinct API‑keys to cache (default **10 000**).
    client:
        Optional pre‑configured ``httpx.AsyncClient``.
        If omitted, one is created with the given *timeout* and shared.
    """

    # ------------------------------------------------------------------ #
    # construction                                                       #
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float = 0.4,
        cache_ttl: int = 10,
        cache_size: int = 10_000,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._introspect = f"{self.base_url}/apikeys/introspect"
        self._client = client or httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": "autoauthn-remote-adapter"},
        )
        self._ttl: Final[int] = cache_ttl
        self._max: Final[int] = cache_size
        self._cache: dict[str, tuple[dict, float]] = {}  # api_key -> (principal, ts)

    # ------------------------------------------------------------------ #
    # AuthNProvider : FastAPI dependency                                 #
    # ------------------------------------------------------------------ #
    async def get_principal(self, request: Request) -> dict:  # noqa: D401
        api_key: str | None = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "x-api-key header required"
            )

        # ------- tiny TTL cache to save RTT ---------------------------
        principal = self._cache_get(api_key)
        if principal is None:
            resp = await self._client.post(self._introspect, json={"api_key": api_key})
            if resp.status_code != 200:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    "Invalid or expired API key",
                )
            principal = resp.json()
            self._cache_put(api_key, principal)

        # make principal visible to hooks and row filters
        request.state.principal = principal
        principal_var.set(principal)
        return principal

    # ------------------------------------------------------------------ #
    # AuthNProvider : hook bootstrap                                     #
    # ------------------------------------------------------------------ #
    def register_inject_hook(self, api) -> None:  # noqa: D401
        """Register the PRE_TX_BEGIN injection hook without assuming shadow tables.

        The hook merely injects ``tenant_id`` and ``owner_id`` fields when they
        exist on the target models; it does not require the consumer to create
        local shadow ``Tenant`` or ``User`` tables.
        """
        register_inject_hook(api)

    # ------------------------------------------------------------------ #
    # internal cache helpers                                             #
    # ------------------------------------------------------------------ #
    def _cache_get(self, key: str) -> dict | None:
        hit = self._cache.get(key)
        if hit and time.monotonic() - hit[1] < self._ttl:
            return hit[0]
        self._cache.pop(key, None)
        return None

    def _cache_put(self, key: str, principal: dict) -> None:
        if len(self._cache) >= self._max:
            self._cache.pop(next(iter(self._cache)))  # FIFO eviction
        self._cache[key] = (principal, time.monotonic())


__all__ = ["RemoteAuthNAdapter"]
