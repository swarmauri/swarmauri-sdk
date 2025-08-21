from __future__ import annotations

import json
import time
import threading
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Tuple, Dict, Any, Literal
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import secrets

from pydantic import PrivateAttr

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, ExportPolicy, KeyUse
from swarmauri_core.crypto.types import KeyRef  # canonical KeyRef from your core types


def _now() -> float:
    return time.time()


@dataclass(frozen=True)
class _RemoteKeyRef(KeyRef):
    """
    Read-only KeyRef representing a remote (verification-only) public key discovered
    via JWKS. Secrets are never present (material=None).
    """

    pass


class RemoteJwksKeyProvider(KeyProviderBase):
    """
    Verification-only key provider backed by a remote JWKS.

    Features
    --------
    - Accepts either a direct JWKS URL or an OIDC issuer URL.
    - Resolves OIDC discovery: <issuer>/.well-known/openid-configuration → jwks_uri.
    - Caches the JWKS in-memory with TTL; thread-safe refresh with ETag/If-Modified-Since.
    - Exposes get_public_jwk() and jwks() to verifiers (e.g., JWTTokenService.verify()).
    - No key creation/rotation/destroy: strictly read-only (raises on those calls).
    - Provides random_bytes() and hkdf() for convenience (local ops).

    Constructor
    -----------
    RemoteJwksKeyProvider(
        jwks_url: Optional[str] = None,
        *,
        issuer: Optional[str] = None,
        cache_ttl_s: int = 300,
        request_timeout_s: int = 5,
        user_agent: str = "RemoteJwksKeyProvider/1.0",
    )

    Notes
    -----
    - If both `issuer` and `jwks_url` are provided, `jwks_url` wins.
    - KIDs may include version suffixes like "kid.version" to match your codebase.
    - This provider returns KeyRefs with public-only info; `material` is always None.
    """

    type: Literal["RemoteJwksKeyProvider"] = "RemoteJwksKeyProvider"

    _lock: threading.RLock = PrivateAttr(default_factory=threading.RLock)
    _jwks_obj: Dict[str, Any] | None = PrivateAttr(default=None)
    _jwks_fetched_at: float = PrivateAttr(default=0.0)
    _etag: Optional[str] = PrivateAttr(default=None)
    _last_modified: Optional[str] = PrivateAttr(default=None)
    _jwks_url: Optional[str] = PrivateAttr(default=None)
    _issuer: Optional[str] = PrivateAttr(default=None)
    _cache_ttl_s: int = PrivateAttr(default=300)
    _request_timeout_s: int = PrivateAttr(default=5)
    _ua: str = PrivateAttr(default="RemoteJwksKeyProvider/1.0")

    def __init__(
        self,
        jwks_url: Optional[str] = None,
        *,
        issuer: Optional[str] = None,
        cache_ttl_s: int = 300,
        request_timeout_s: int = 5,
        user_agent: str = "RemoteJwksKeyProvider/1.0",
    ) -> None:
        super().__init__()
        if not jwks_url and not issuer:
            raise ValueError("Provide either jwks_url or issuer")
        self._jwks_url = jwks_url
        self._issuer = issuer.rstrip("/") if issuer else None
        self._cache_ttl_s = int(cache_ttl_s)
        self._request_timeout_s = int(request_timeout_s)
        self._ua = user_agent

        # Resolve issuer → jwks_uri on init if needed (lazy fallback on first use if fails)
        if self._jwks_url is None and self._issuer:
            try:
                self._jwks_url = self._resolve_jwks_uri(self._issuer)
            except Exception:
                # Defer to first use; do not fail constructor for transient network issues
                pass

    # ───────────────────────── capabilities ─────────────────────────

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "class": ("asym",),
            "algs": ("RSA", "EC", "OKP", "oct"),  # JWKS kty families we may encounter
            "features": ("jwks", "verify_only", "refresh"),
        }

    # ───────────────────────── read/write lifecycle ─────────────────────────
    # Read-only provider: all mutation APIs raise.

    async def create_key(self, spec: KeySpec) -> KeyRef:
        raise NotImplementedError(
            "RemoteJwksKeyProvider is verification-only (no create_key)"
        )

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        raise NotImplementedError(
            "RemoteJwksKeyProvider is verification-only (no import_key)"
        )

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        raise NotImplementedError(
            "RemoteJwksKeyProvider is verification-only (no rotate_key)"
        )

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        raise NotImplementedError(
            "RemoteJwksKeyProvider is verification-only (no destroy_key)"
        )

    # ───────────────────────── getters / jwks ─────────────────────────

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        """
        Return a KeyRef for the given kid(.version) if present in JWKS.
        Secrets are never exported; material=None.
        """
        jwk = await self._find_jwk(kid, version)
        if jwk is None:
            raise KeyError(f"Unknown key id: {kid!r} (version={version!r})")

        # For compatibility with your KeyRef, we put the public JWK bytes into 'public'
        # (wire consumers typically use jwks() directly; this is mainly for parity).
        public_bytes = json.dumps(jwk, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
        parsed_kid, parsed_ver = self._split_kid_version(jwk.get("kid", ""))

        return _RemoteKeyRef(
            kid=parsed_kid or kid,
            version=parsed_ver or (version if version is not None else 1),
            type="OPAQUE",
            uses=(KeyUse.VERIFY,),  # verification only
            export_policy=ExportPolicy.PUBLIC_ONLY,
            public=public_bytes,
            material=None,
            tags={"kty": jwk.get("kty"), "alg": jwk.get("alg")},
        )

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        """
        Returns any discovered versions for the kid when keys are of the form 'kid.version'.
        If no version suffixes are found, returns (1,) when the base kid exists, else ().
        """
        keys = await self._get_jwks_keys()
        versions: set[int] = set()
        found_plain = False
        for jwk in keys:
            k = jwk.get("kid") or ""
            base, ver = self._split_kid_version(k)
            if base == kid:
                if ver is None:
                    found_plain = True
                else:
                    versions.add(ver)
        if versions:
            return tuple(sorted(versions))
        return (1,) if found_plain else tuple()

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        jwk = await self._find_jwk(kid, version)
        if jwk is None:
            raise KeyError(f"Unknown key id: {kid!r} (version={version!r})")
        return jwk

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        keys = await self._get_jwks_keys()
        if prefix_kids:
            keys = [k for k in keys if (k.get("kid") or "").startswith(prefix_kids)]
        return {"keys": keys}

    # ───────────────────────── material helpers ─────────────────────────

    async def random_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)

    # ───────────────────────── refresh / internals ─────────────────────────

    def refresh(self, *, force: bool = False) -> None:
        """
        Synchronous refresh of JWKS cache. Safe to call before latency-sensitive paths.
        """
        with self._lock:
            self._ensure_jwks_locked(force=force)

    async def _find_jwk(self, kid: str, version: Optional[int]) -> Optional[dict]:
        keys = await self._get_jwks_keys()
        # 1) Exact match by kid when version is provided -> "kid.version"
        if version is not None:
            target = f"{kid}.{version}"
            for jwk in keys:
                if jwk.get("kid") == target:
                    return jwk
        # 2) Exact match by kid as-is
        for jwk in keys:
            if jwk.get("kid") == kid:
                return jwk
        # 3) If version is None, try "kid.<any>" but prefer the highest numeric version
        if version is None:
            best = None
            best_ver = -1
            for jwk in keys:
                base, ver = self._split_kid_version(jwk.get("kid") or "")
                if base == kid and ver is not None and ver > best_ver:
                    best, best_ver = jwk, ver
            return best
        return None

    async def _get_jwks_keys(self) -> list[dict]:
        with self._lock:
            self._ensure_jwks_locked(force=False)
            keys = (self._jwks_obj or {}).get("keys", [])
            if not isinstance(keys, list):
                keys = []
            return keys

    def _ensure_jwks_locked(self, *, force: bool) -> None:
        # Resolve jwks_url if needed from issuer
        if self._jwks_url is None and self._issuer:
            try:
                self._jwks_url = self._resolve_jwks_uri(self._issuer)
            except Exception as e:
                if self._jwks_obj is None:
                    # First time and still nothing: bubble up
                    raise RuntimeError(
                        f"Unable to resolve jwks_uri from issuer {self._issuer!r}: {e}"
                    ) from e
                # Otherwise, keep old cache until TTL
        # Check TTL
        age = _now() - self._jwks_fetched_at
        if (not force) and self._jwks_obj is not None and age < self._cache_ttl_s:
            return
        # Fetch (with conditional headers if available)
        if not self._jwks_url:
            raise RuntimeError("No JWKS URL available to refresh")
        jwks, etag, lastmod, not_modified = self._fetch_json_conditional(
            self._jwks_url, self._etag, self._last_modified
        )
        if not_modified and self._jwks_obj is not None:
            # Just bump timestamp
            self._jwks_fetched_at = _now()
            return
        if not isinstance(jwks, dict) or "keys" not in jwks:
            raise RuntimeError(
                f"JWKS fetch did not return an object with 'keys': {self._jwks_url}"
            )
        # Update cache
        self._jwks_obj = jwks
        self._jwks_fetched_at = _now()
        self._etag = etag
        self._last_modified = lastmod

    def _resolve_jwks_uri(self, issuer: str) -> str:
        well_known = urljoin(issuer + "/", ".well-known/openid-configuration")
        obj, _, _, _ = self._fetch_json_conditional(well_known, None, None)
        if not isinstance(obj, dict) or "jwks_uri" not in obj:
            raise RuntimeError(f"OIDC discovery did not return jwks_uri: {well_known}")
        return obj["jwks_uri"]

    def _fetch_json_conditional(
        self,
        url: str,
        etag: Optional[str],
        last_modified: Optional[str],
    ) -> tuple[dict, Optional[str], Optional[str], bool]:
        """
        Minimal dependency HTTP GET with If-None-Match / If-Modified-Since.
        Returns: (json_obj, etag, last_modified, not_modified)
        """
        headers = {"User-Agent": self._ua, "Accept": "application/json"}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        req = Request(url, headers=headers, method="GET")
        try:
            with urlopen(req, timeout=self._request_timeout_s) as resp:
                status = getattr(resp, "status", 200)
                if status == 304 and self._jwks_obj is not None:
                    return {}, etag, last_modified, True
                data = resp.read()
                obj = json.loads(data.decode("utf-8"))
                new_etag = resp.headers.get("ETag") or etag
                new_last_mod = resp.headers.get("Last-Modified") or last_modified
                return obj, new_etag, new_last_mod, False
        except HTTPError as e:
            if e.code == 304 and self._jwks_obj is not None:
                return {}, etag, last_modified, True
            raise
        except URLError as e:
            # Keep existing cache if present; otherwise surface error
            if self._jwks_obj is not None:
                return self._jwks_obj, etag, last_modified, True
            raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    @staticmethod
    def _split_kid_version(k: str) -> tuple[str | None, int | None]:
        """
        Split "kid.version" → (kid, version). If no dot, return (kid, None).
        If version is non-integer, treat as None.
        """
        if not k:
            return None, None
        if "." not in k:
            return k, None
        base, _, ver = k.rpartition(".")
        try:
            return base, int(ver)
        except Exception:
            return base or k, None
