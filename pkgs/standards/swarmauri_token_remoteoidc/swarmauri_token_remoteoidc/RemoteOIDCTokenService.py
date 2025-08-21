from __future__ import annotations

import json
import threading
import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import jwt
from jwt import algorithms

try:
    from swarmauri_base.tokens.TokenServiceBase import TokenServiceBase
except Exception:  # pragma: no cover - fallback for test envs

    class TokenServiceBase:  # type: ignore
        """Minimal fallback TokenServiceBase."""

        def __init__(self) -> None:
            pass


try:
    from swarmauri_core.tokens.ITokenService import ITokenService
except Exception:  # pragma: no cover - fallback for test envs

    class ITokenService:  # type: ignore
        pass


def _now() -> float:
    return time.time()


def _http_get_json(
    url: str,
    *,
    timeout_s: int,
    user_agent: str,
    etag: Optional[str] = None,
    last_modified: Optional[str] = None,
) -> tuple[dict, Optional[str], Optional[str], bool]:
    """
    Minimal dependency HTTP GET with conditional headers.
    Returns: (json_obj, new_etag, new_last_modified, not_modified)
    """
    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            status = getattr(resp, "status", 200)
            if status == 304:
                return {}, etag, last_modified, True
            data = resp.read()
            obj = json.loads(data.decode("utf-8"))
            new_etag = resp.headers.get("ETag") or etag
            new_last_mod = resp.headers.get("Last-Modified") or last_modified
            return obj, new_etag, new_last_mod, False
    except HTTPError as e:  # pragma: no cover - network errors
        if e.code == 304:
            return {}, etag, last_modified, True
        raise
    except URLError as e:  # pragma: no cover - network errors
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e


class RemoteOIDCTokenService(TokenServiceBase):
    """
    Verify-only OIDC token service backed by remote discovery + JWKS.

    Features
    --------
    - Resolves OIDC discovery: <issuer>/.well-known/openid-configuration → jwks_uri.
      (You may also pass jwks_url directly; that bypasses discovery.)
    - Caches discovery + JWKS in-memory with TTL; thread-safe refresh; honors
      ETag / Last-Modified for conditional GETs.
    - Strict issuer check (iss must equal configured issuer).
    - Audience validation (optional); clock skew leeway configurable.
    - Supports any JWS algs announced by the issuer; falls back to common algs.
    - Exposes jwks() for debugging/inspection.
    - No mint() (raises NotImplementedError).

    Constructor
    -----------
    RemoteOIDCTokenService(
        issuer: str,
        *,
        jwks_url: Optional[str] = None,
        cache_ttl_s: int = 300,
        request_timeout_s: int = 5,
        user_agent: str = "RemoteOIDCTokenService/1.0",
        expected_alg_whitelist: Optional[Iterable[str]] = None,
        accept_unsigned: bool = False,   # for test envs only; strongly discouraged
    )
    """

    type: Literal["RemoteOIDCTokenService"] = "RemoteOIDCTokenService"

    def __init__(
        self,
        issuer: str,
        *,
        jwks_url: Optional[str] = None,
        cache_ttl_s: int = 300,
        request_timeout_s: int = 5,
        user_agent: str = "RemoteOIDCTokenService/1.0",
        expected_alg_whitelist: Optional[Iterable[str]] = None,
        accept_unsigned: bool = False,
    ) -> None:
        super().__init__()
        if not issuer:
            raise ValueError("issuer is required")
        self._issuer = issuer.rstrip("/")
        self._jwks_url_config = jwks_url
        self._cache_ttl_s = int(cache_ttl_s)
        self._timeout_s = int(request_timeout_s)
        self._ua = user_agent
        self._accept_unsigned = bool(accept_unsigned)

        # Discovery cache
        self._disc_obj: Optional[dict] = None
        self._disc_at: float = 0.0
        self._disc_etag: Optional[str] = None
        self._disc_lastmod: Optional[str] = None

        # JWKS cache
        self._jwks_obj: Optional[dict] = None
        self._jwks_at: float = 0.0
        self._jwks_etag: Optional[str] = None
        self._jwks_lastmod: Optional[str] = None

        # accepted algs
        self._allowed_algs: Optional[Tuple[str, ...]] = (
            tuple(expected_alg_whitelist) if expected_alg_whitelist else None
        )

        self._lock = threading.RLock()

        # Pre-resolve discovery on init (best-effort)
        try:
            self._ensure_discovery_locked(force=False)
        except Exception:
            # non-fatal at construction; will retry on first verify()
            pass

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs = self._allowed_algs or (
            # Sensible defaults; may be narrowed by discovery later
            "RS256",
            "PS256",
            "ES256",
            "EdDSA",
        )
        fmts = ("JWT", "JWS")
        return {"formats": fmts, "algs": algs}

    async def mint(
        self,
        claims: Dict[str, Any],
        *,
        alg: str,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:  # pragma: no cover - mint not implemented
        raise NotImplementedError(
            "RemoteOIDCTokenService is verification-only (no mint)"
        )

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
        max_age_s: Optional[int] = None,  # optional OIDC 'max_age' enforcement
        nonce: Optional[str] = None,  # if you flow through /authorize with nonce
    ) -> Dict[str, Any]:
        """
        Verify a JWT/JWS against the configured OIDC issuer and remote JWKS.

        Checks performed:
          - JWS signature using remote JWKS (by 'kid' header).
          - 'iss' must equal configured issuer (or explicit 'issuer' arg if provided).
          - 'aud' validated if provided by caller.
          - 'exp','nbf','iat' validated with 'leeway_s'.
          - Optional 'nonce' and 'auth_time'/'max_age' checks if provided.
        """
        # Refresh caches if stale
        with self._lock:
            self._ensure_discovery_locked(force=False)
            self._ensure_jwks_locked(force=False)

            iss_expected = issuer or self._issuer

            # Choose allowed algorithms
            allowed = self._derive_allowed_algs_locked()

            # Build a key resolver that picks verification key from cached JWKS by kid
            jwks = self._jwks_obj or {"keys": []}

        def _resolve_key(header, payload):  # pragma: no cover - internal
            kid = header.get("kid")
            if header.get("alg") == "none":
                return (
                    None
                    if self._accept_unsigned
                    else jwt.InvalidAlgorithmError("Unsigned tokens are not accepted")
                )
            if not kid:
                return None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    kty = jwk.get("kty")
                    if kty == "RSA":
                        return algorithms.RSAAlgorithm.from_jwk(jwk)
                    if kty == "EC":
                        return algorithms.ECAlgorithm.from_jwk(jwk)
                    if kty == "OKP":
                        return algorithms.Ed25519Algorithm.from_jwk(jwk)
                    if kty == "oct":
                        return algorithms.HMACAlgorithm.from_jwk(jwk)
            return None

        options = {
            "verify_aud": audience is not None,
            "require": ["exp", "iat"],
        }

        header = jwt.get_unverified_header(token)
        key_obj = _resolve_key(header, None)
        claims = jwt.decode(
            token,
            key=key_obj,
            algorithms=list(allowed),
            audience=audience,
            issuer=iss_expected,
            leeway=leeway_s,
            options=options,
        )

        if nonce is not None:
            if claims.get("nonce") != nonce:
                raise jwt.InvalidTokenError("OIDC nonce mismatch")

        if max_age_s is not None:
            auth_time = claims.get("auth_time")
            now = int(_now())
            if isinstance(auth_time, int):
                if now > (auth_time + int(max_age_s) + int(leeway_s)):
                    raise jwt.ExpiredSignatureError("OIDC max_age exceeded")

        return claims

    async def jwks(self) -> dict:
        with self._lock:
            self._ensure_discovery_locked(force=False)
            self._ensure_jwks_locked(force=False)
            return dict(self._jwks_obj or {"keys": []})

    def refresh(self, *, force: bool = False) -> None:
        """
        Synchronous refresh of discovery + JWKS caches. Safe to call
        at process start or when you receive a rotation signal.
        """
        with self._lock:
            self._ensure_discovery_locked(force=force)
            self._ensure_jwks_locked(force=force)

    def _derive_allowed_algs_locked(self) -> Tuple[str, ...]:
        if self._allowed_algs:
            return self._allowed_algs
        algs = ()
        if isinstance(self._disc_obj, dict):
            vals = self._disc_obj.get(
                "id_token_signing_alg_values_supported"
            ) or self._disc_obj.get("token_endpoint_auth_signing_alg_values_supported")
            if isinstance(vals, list) and vals:
                algs = tuple(a for a in vals if isinstance(a, str))
        if not algs:
            algs = ("RS256", "PS256", "ES256", "EdDSA")
        return algs

    def _ensure_discovery_locked(self, *, force: bool) -> None:
        if self._jwks_url_config:
            if self._disc_obj is None:
                self._disc_obj = {"jwks_uri": self._jwks_url_config}
                self._disc_at = _now()
            return

        ttl_ok = (
            (not force)
            and self._disc_obj is not None
            and ((_now() - self._disc_at) < self._cache_ttl_s)
        )
        if ttl_ok:
            return

        url = urljoin(self._issuer + "/", ".well-known/openid-configuration")
        obj, etag, lastmod, not_modified = _http_get_json(
            url,
            timeout_s=self._timeout_s,
            user_agent=self._ua,
            etag=self._disc_etag,
            last_modified=self._disc_lastmod,
        )
        if not_modified and self._disc_obj is not None:
            self._disc_at = _now()
            return
        if not isinstance(obj, dict) or "jwks_uri" not in obj:
            raise RuntimeError(f"OIDC discovery did not return jwks_uri: {url}")
        self._disc_obj = obj
        self._disc_etag = etag
        self._disc_lastmod = lastmod
        self._disc_at = _now()

    def _ensure_jwks_locked(self, *, force: bool) -> None:
        ttl_ok = (
            (not force)
            and self._jwks_obj is not None
            and ((_now() - self._jwks_at) < self._cache_ttl_s)
        )
        if ttl_ok:
            return

        jwks_url = self._jwks_url_config
        if not jwks_url:
            if not self._disc_obj or "jwks_uri" not in self._disc_obj:
                self._ensure_discovery_locked(force=False)
            jwks_url = self._disc_obj.get("jwks_uri")  # type: ignore[assignment]
        if not jwks_url:
            raise RuntimeError("No JWKS URL available")

        obj, etag, lastmod, not_modified = _http_get_json(
            jwks_url,
            timeout_s=self._timeout_s,
            user_agent=self._ua,
            etag=self._jwks_etag,
            last_modified=self._jwks_lastmod,
        )
        if not_modified and self._jwks_obj is not None:
            self._jwks_at = _now()
            return
        if not isinstance(obj, dict) or "keys" not in obj:
            raise RuntimeError(
                f"JWKS fetch did not return an object with 'keys': {jwks_url}"
            )

        self._jwks_obj = obj
        self._jwks_etag = etag
        self._jwks_lastmod = lastmod
        self._jwks_at = _now()
