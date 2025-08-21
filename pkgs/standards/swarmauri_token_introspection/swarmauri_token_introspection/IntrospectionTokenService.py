from __future__ import annotations

import time
import json
import base64
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Tuple

try:
    import httpx
except Exception as e:  # pragma: no cover
    raise ImportError(
        "IntrospectionTokenService requires 'httpx'. Install with: pip install httpx"
    ) from e

try:  # pragma: no cover - fallback for isolated tests
    from swarmauri_base.tokens.TokenServiceBase import TokenServiceBase
except Exception:  # pragma: no cover

    class TokenServiceBase:  # type: ignore
        """Minimal fallback base class."""


@dataclass
class _CacheEntry:
    ok: bool
    claims: Dict[str, Any]
    expires_at: float


def _b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


class IntrospectionTokenService(TokenServiceBase):
    """
    OAuth 2.0 Token Introspection client (RFC 7662) — VERIFY ONLY.

    - POSTs opaque tokens to the configured `endpoint` and validates the response.
    - Authentication:
        * client_secret_basic  → Authorization: Basic base64(client_id:client_secret)
        * client_secret_post   → client_id/client_secret in form body
        * bearer               → Authorization: Bearer <authorization_value>
    - Caching:
        * Positive hits cached up to min(cache_ttl_s, exp-leeway) when 'exp' is present.
        * Negative hits cached for negative_ttl_s.
    - Validation:
        * Requires "active": true from the AS.
        * Enforces exp/nbf/iat drift (leeway_s), optional iss/aud checks.

    Notes:
    - This service intentionally DOES NOT mint tokens. `mint()` raises NotImplementedError.
    - `jwks()` returns {} by default; if `jwks_url` is configured, it fetches and returns that set.
    """

    type: Literal["IntrospectionTokenService"] = "IntrospectionTokenService"

    def __init__(
        self,
        endpoint: str,
        *,
        # auth
        client_auth: Literal[
            "client_secret_basic", "client_secret_post", "bearer"
        ] = "client_secret_basic",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        authorization: Optional[
            str
        ] = None,  # for bearer auth against introspection endpoint
        # behavior
        token_type_hint: Optional[str] = "access_token",
        default_issuer: Optional[str] = None,
        # http
        timeout_s: float = 6.0,
        verify_tls: bool | str = True,
        # caching
        cache_ttl_s: int = 60,
        negative_ttl_s: int = 15,
        # validation
        leeway_s: int = 60,
        # optional remote jwks passthrough (e.g., if you also serve JWTs)
        jwks_url: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._endpoint = endpoint
        self._client_auth = client_auth
        self._client_id = client_id
        self._client_secret = client_secret
        self._authorization = authorization
        self._hint = token_type_hint
        self._iss = default_issuer
        self._timeout = timeout_s
        self._verify = verify_tls
        self._cache_ttl = max(0, int(cache_ttl_s))
        self._neg_ttl = max(0, int(negative_ttl_s))
        self._leeway = max(0, int(leeway_s))
        self._jwks_url = jwks_url

        self._client: Optional[httpx.AsyncClient] = None
        self._cache: Dict[str, _CacheEntry] = {}
        self._jwks_cache: Optional[Tuple[dict, float]] = None  # (value, expires_at)

        # Basic sanity for auth config
        if self._client_auth == "client_secret_basic":
            if not (self._client_id and self._client_secret):
                raise ValueError(
                    "client_secret_basic requires client_id and client_secret"
                )
        elif self._client_auth == "client_secret_post":
            if not (self._client_id and self._client_secret):
                raise ValueError(
                    "client_secret_post requires client_id and client_secret"
                )
        elif self._client_auth == "bearer":
            if not self._authorization:
                raise ValueError(
                    "bearer client_auth requires 'authorization' (a token string)"
                )

    # ------------------------ lifecycle ------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                verify=self._verify,
                headers={"Accept": "application/json"},
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------ ITokenService ------------------------

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "formats": ("opaque", "introspection"),
            "algs": ("remote",),  # remote decision by AS; no local signing
        }

    async def mint(  # type: ignore[override]
        self,
        claims: Dict[str, Any],
        *,
        alg: str,
        kid: Optional[str] = None,
        key_version: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        raise NotImplementedError("IntrospectionTokenService does not mint tokens.")

    async def verify(  # type: ignore[override]
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = -1,
    ) -> Dict[str, Any]:
        """
        POST token to the introspection endpoint, validate standard fields, and return claims.
        Raises ValueError on inactive/invalid tokens, or httpx.HTTPError on transport errors.
        """
        if not isinstance(token, str) or not token:
            raise ValueError("token must be a non-empty string")

        # Cache lookup
        now = time.time()
        entry = self._cache.get(token)
        if entry and entry.expires_at > now:
            if not entry.ok:
                raise ValueError("inactive_token (cached)")
            claims = dict(entry.claims)
            self._validate_claims(
                claims, issuer=issuer, audience=audience, leeway_s=leeway_s
            )
            return claims

        # Build request
        form: Dict[str, Any] = {"token": token}
        if self._hint:
            form["token_type_hint"] = self._hint

        headers = {}
        if self._client_auth == "client_secret_basic":
            headers["Authorization"] = "Basic " + _b64(
                f"{self._client_id}:{self._client_secret}"
            )
        elif self._client_auth == "bearer":
            headers["Authorization"] = f"Bearer {self._authorization}"
        elif self._client_auth == "client_secret_post":
            form["client_id"] = self._client_id
            form["client_secret"] = self._client_secret

        # Call endpoint
        client = await self._get_client()
        resp = await client.post(self._endpoint, data=form, headers=headers)
        # Accept 200 only; some AS return 400 for malformed tokens (treat as inactive w/ negative cache)
        if resp.status_code == 401 or resp.status_code == 403:
            # Auth to introspection endpoint failed → configuration error
            resp.raise_for_status()
        if resp.status_code >= 500:
            resp.raise_for_status()
        if resp.status_code not in (200, 400):
            resp.raise_for_status()

        # Parse JSON
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise ValueError("introspection_response_not_json")

        # RFC 7662: must include "active" boolean
        active = bool(data.get("active", False))
        if not active:
            # Negative cache
            if self._neg_ttl:
                self._cache[token] = _CacheEntry(
                    ok=False, claims={}, expires_at=now + self._neg_ttl
                )
            raise ValueError("inactive_token")

        # Normalize claims (copy)
        claims: Dict[str, Any] = dict(data)

        # Standardize time fields to int if present
        for k in ("exp", "iat", "nbf"):
            if k in claims:
                try:
                    claims[k] = int(claims[k])
                except Exception:
                    raise ValueError(f"invalid_{k}_claim")

        # Optionally enforce iss/aud, exp/nbf/iat
        self._validate_claims(
            claims, issuer=issuer, audience=audience, leeway_s=leeway_s
        )

        # Cache positive results
        ttl = self._cache_ttl
        # If exp present, restrict TTL so we never cache past expiry
        if "exp" in claims:
            eff_leeway = self._leeway if leeway_s < 0 else int(leeway_s)
            ttl = min(ttl, max(0, claims["exp"] - int(now) + eff_leeway))
        if ttl > 0:
            self._cache[token] = _CacheEntry(
                ok=True, claims=claims, expires_at=now + ttl
            )

        return claims

    async def jwks(self) -> dict:  # type: ignore[override]
        """
        Opaque tokens have no public keys. If `jwks_url` is configured, fetch and expose it
        (useful when the same issuer also serves JWTs); otherwise return {}.
        """
        if not self._jwks_url:
            return {"keys": []}
        # Light cache (60s) to avoid hammering the URL
        now = time.time()
        if self._jwks_cache and self._jwks_cache[1] > now:
            return self._jwks_cache[0]
        client = await self._get_client()
        r = await client.get(self._jwks_url)
        r.raise_for_status()
        payload = r.json()
        self._jwks_cache = (payload, now + 60.0)
        return payload

    # ------------------------ helpers ------------------------

    def _validate_claims(
        self,
        claims: Dict[str, Any],
        *,
        issuer: Optional[str],
        audience: Optional[str | list[str]],
        leeway_s: int,
    ) -> None:
        """Apply local policy checks to introspection claims."""
        now = int(time.time())
        leeway = self._leeway if leeway_s < 0 else max(0, int(leeway_s))

        # Time checks
        if "exp" in claims and now > int(claims["exp"]) + leeway:
            raise ValueError("token_expired")
        if "nbf" in claims and now + leeway < int(claims["nbf"]):
            raise ValueError("token_not_yet_valid")
        if "iat" in claims and int(claims["iat"]) - leeway > now:
            raise ValueError("token_issued_in_future")

        # Issuer
        iss_expected = issuer or self._iss
        if iss_expected is not None:
            iss_claim = claims.get("iss")
            if iss_claim is not None and iss_claim != iss_expected:
                raise ValueError("issuer_mismatch")

        # Audience
        if audience is not None:
            tok_aud = claims.get("aud")
            if isinstance(audience, list):
                if isinstance(tok_aud, list):
                    if not any(a in tok_aud for a in audience):
                        raise ValueError("audience_mismatch")
                else:
                    if tok_aud not in audience:
                        raise ValueError("audience_mismatch")
            else:
                if isinstance(tok_aud, list):
                    if audience not in tok_aud:
                        raise ValueError("audience_mismatch")
                else:
                    if tok_aud != audience:
                        raise ValueError("audience_mismatch")
