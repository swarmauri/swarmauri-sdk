# tigrbl_auth/v2/adapters/remote_adapter.py
from __future__ import annotations

import time
from typing import Final

import httpx
from tigrbl_auth.deps import (
    APIKeyHeader,
    AuthNProvider,
    HTTPException,
    Request,
    Security,
    TIGRBL_AUTH_CONTEXT_ATTR,
    status,
)
from ..principal_ctx import principal_var


def _set_auth_context(request: Request, principal: dict | None) -> None:
    ctx: dict[str, str] = {}
    if principal:
        tid = principal.get("tid") or principal.get("tenant_id")
        uid = principal.get("sub") or principal.get("user_id")
        if tid is not None:
            ctx["tenant_id"] = tid
        if uid is not None:
            ctx["user_id"] = uid
    setattr(request.state, TIGRBL_AUTH_CONTEXT_ATTR, ctx)


# OpenAPI-advertised security scheme (header-based API key)
_API_KEY_REQUIRED = APIKeyHeader(name="X-API-Key", auto_error=True)
_API_KEY_OPTIONAL = APIKeyHeader(name="X-API-Key", auto_error=False)


class RemoteAuthNAdapter(AuthNProvider):
    """
    Authenticate every request by calling a *remote* AuthN service.

    Parameters
    ----------
    base_url:
        Full origin of the AuthN deployment, *without* trailing slash,
        e.g. ``"https://authn.internal:8080"``.
    timeout:
        Float seconds for the outbound HTTP POST (default **0.4 s**).
    cache_ttl:
        TTL in seconds for the in-process API-key cache (default **10 s**).
    cache_size:
        Maximum number of distinct API-keys to cache (default **10,000**).
    client:
        Optional pre-configured ``httpx.AsyncClient``. If omitted, one is created.
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
        self._introspect = f"{self.base_url}/introspect"
        self._client = client or httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": "autoauthn-remote-adapter"},
        )
        self._ttl: Final[int] = cache_ttl
        self._max: Final[int] = cache_size
        self._cache: dict[str, tuple[dict, float]] = {}  # api_key -> (principal, ts)

    # ------------------------------------------------------------------ #
    # AuthNProvider : FastAPI dependencies                                #
    # ------------------------------------------------------------------ #
    async def get_principal(  # strict: header is required (401 on invalid)
        self,
        request: Request,
        api_key: str = Security(_API_KEY_REQUIRED),
    ) -> dict:
        """
        Resolve and return the principal for a required API key.

        Emits a 401 when the key is invalid/expired. Missing header is handled
        by the security scheme (auto_error=True).
        """
        principal = self._cache_get(api_key)
        if principal is None:
            principal = await self._introspect_key(api_key)
            if principal is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Invalid or expired API key"
                )
            self._cache_put(api_key, principal)

        request.state.principal = principal
        principal_var.set(principal)
        _set_auth_context(request, principal)
        return principal

    async def get_principal_optional(  # optional: header may be absent
        self,
        request: Request,
        api_key: str | None = Security(_API_KEY_OPTIONAL),
    ) -> dict | None:
        """
        Resolve and return the principal when the API key header is optional.

        Returns ``None`` when no API key is provided or when introspection fails.
        Never raises due to missing header (auto_error=False).
        """
        if not api_key:
            request.state.principal = None
            principal_var.set(None)
            _set_auth_context(request, None)
            return None

        principal = self._cache_get(api_key)
        if principal is None:
            principal = await self._introspect_key(api_key)
            if principal is None:
                # For optional auth we do not raise; return None to allow anon flows.
                request.state.principal = None
                principal_var.set(None)
                _set_auth_context(request, None)
                return None
            self._cache_put(api_key, principal)

        request.state.principal = principal
        principal_var.set(principal)
        _set_auth_context(request, principal)
        return principal

    # ------------------------------------------------------------------ #
    # internal helpers                                                    #
    # ------------------------------------------------------------------ #
    async def _introspect_key(self, api_key: str) -> dict | None:
        try:
            resp = await self._client.post(self._introspect, data={"token": api_key})
        except Exception:
            return None

        if resp.status_code != 200:
            return None

        try:
            body = resp.json()
        except Exception:
            return None

        if not isinstance(body, dict) or not body.get("active"):
            return None
        return body

    def _cache_get(self, key: str) -> dict | None:
        hit = self._cache.get(key)
        if hit and time.monotonic() - hit[1] < self._ttl:
            return hit[0]
        self._cache.pop(key, None)
        return None

    def _cache_put(self, key: str, principal: dict) -> None:
        if len(self._cache) >= self._max:
            # FIFO eviction
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = (principal, time.monotonic())


__all__ = ["RemoteAuthNAdapter"]
