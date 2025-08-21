from __future__ import annotations

import base64
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, Iterable, Literal, Mapping, Optional, Tuple

import jwt
from jwt import algorithms

JsonDict = Dict[str, Any]
JWKSFetcher = Callable[[], JsonDict]


def _b64u_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


class CachedJWKSVerifier:
    type: Literal["CachedJWKSVerifier"] = "CachedJWKSVerifier"

    def __init__(
        self,
        *,
        fetch: JWKSFetcher,
        ttl_s: int = 300,
        max_entries: int = 256,
        allowed_algs: Optional[Iterable[str]] = None,
        allowed_issuers: Optional[Iterable[str]] = None,
        user_agent: str = "CachedJWKSVerifier/1.0",
    ) -> None:
        if not callable(fetch):
            raise TypeError("fetch must be a callable returning a JWKS object")
        self._fetch = fetch
        self._ttl = int(ttl_s)
        self._max = int(max_entries)
        self._ua = user_agent

        self._lock = threading.RLock()
        self._jwks: JsonDict | None = None
        self._fetched_at: float = 0.0

        self._lru: OrderedDict[str, Any] = OrderedDict()
        self._by_family: Dict[Tuple[str, str], Tuple[str, ...]] = {}

        self._overrides: Dict[str, Any] = {}
        self._override_jwks: Dict[str, JsonDict] = {}

        self._allowed_algs = tuple(a for a in (allowed_algs or ()))
        self._allowed_issuers = tuple(i.rstrip("/") for i in (allowed_issuers or ()))

    def key_resolver(self) -> Callable[[JsonDict, JsonDict], Any]:
        def _resolver(header: JsonDict, payload: JsonDict) -> Any:
            alg = header.get("alg")
            if self._allowed_algs and alg not in self._allowed_algs:
                raise jwt.InvalidAlgorithmError(f"Algorithm {alg!r} not allowed")

            kid = header.get("kid")
            if kid:
                key = self._get_key_by_kid(kid)
                if key is not None:
                    return key

            kty = header.get("kty")
            crv = header.get("crv") or header.get("alg") or ""
            fam = (kty, crv)
            with self._lock:
                self._ensure_fresh_locked()
                candidates = self._by_family.get(fam, ())

            for cand_kid in candidates:
                key = self._get_key_by_kid(cand_kid)
                if key is not None:
                    return key

            if kty:
                with self._lock:
                    self._ensure_fresh_locked()
                    for jwk in self._jwks.get("keys", []):  # type: ignore[union-attr]
                        if jwk.get("kty") == kty:
                            obj = self._parse_and_admit(jwk)
                            if obj is not None:
                                return obj

            with self._lock:
                self._ensure_fresh_locked(force=True)
            if kid:
                key = self._get_key_by_kid(kid)
                if key is not None:
                    return key

            return None

        return _resolver

    def refresh(self, *, force: bool = False) -> None:
        with self._lock:
            self._ensure_fresh_locked(force=force)

    def inject_override_key(self, kid: str, key_obj: Any) -> None:
        with self._lock:
            self._overrides[kid] = key_obj
            self._lru.pop(kid, None)
            self._lru[kid] = key_obj
            self._trim_lru_locked()

    def inject_override_jwk(self, kid: str, jwk: JsonDict) -> None:
        with self._lock:
            self._override_jwks[kid] = jwk
            self._lru.pop(kid, None)

    def invalidate(self, kid: Optional[str] = None) -> None:
        with self._lock:
            if kid:
                self._lru.pop(kid, None)
                self._overrides.pop(kid, None)
                self._override_jwks.pop(kid, None)
            else:
                self._jwks = None
                self._fetched_at = 0.0
                self._lru.clear()
                self._by_family.clear()
                self._overrides.clear()
                self._override_jwks.clear()

    def verify(
        self,
        token: str,
        *,
        algorithms_whitelist: Iterable[str],
        audience: Optional[str | Iterable[str]] = None,
        issuer: Optional[str] = None,
        leeway_s: int = 60,
        options: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        iss = issuer
        if iss is None and self._allowed_issuers:
            iss = self._allowed_issuers[0]

        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        key = self.key_resolver()(header, payload)
        return jwt.decode(
            token,
            key=key,
            algorithms=list(algorithms_whitelist),
            audience=audience,
            issuer=iss,
            leeway=leeway_s,
            options={"verify_aud": audience is not None, **(options or {})},
        )

    def _get_key_by_kid(self, kid: str) -> Any | None:
        with self._lock:
            if kid in self._overrides:
                return self._overrides[kid]
            if kid in self._override_jwks:
                obj = self._parse_and_admit(self._override_jwks[kid])
                if obj is not None:
                    return obj

            obj = self._lru.get(kid)
            if obj is not None:
                self._lru.move_to_end(kid)
                return obj

            self._ensure_fresh_locked()
            for jwk in self._jwks.get("keys", []):  # type: ignore[union-attr]
                if jwk.get("kid") == kid:
                    return self._parse_and_admit(jwk)
        return None

    def _ensure_fresh_locked(self, *, force: bool = False) -> None:
        age = time.time() - self._fetched_at
        if (not force) and self._jwks is not None and age < self._ttl:
            return
        jwks = self._fetch()
        if (
            not isinstance(jwks, dict)
            or "keys" not in jwks
            or not isinstance(jwks["keys"], list)
        ):
            raise RuntimeError("JWKS fetcher returned an invalid JWKS object")
        self._jwks = jwks
        self._fetched_at = time.time()
        fam: Dict[Tuple[str, str], Tuple[str, ...]] = {}
        for jwk in jwks["keys"]:
            kty = jwk.get("kty")
            if not kty:
                continue
            crv_or_alg = jwk.get("crv") or jwk.get("alg") or ""
            kid = jwk.get("kid") or ""
            if kid:
                key = (kty, crv_or_alg)
                fam[key] = tuple((*fam.get(key, ()), kid))
        self._by_family = fam

    def _parse_and_admit(self, jwk: JsonDict) -> Any | None:
        kid = jwk.get("kid") or ""
        try:
            obj = self._parse_jwk(jwk)
        except Exception:
            return None
        if kid:
            self._lru[kid] = obj
            self._trim_lru_locked()
        return obj

    def _trim_lru_locked(self) -> None:
        while len(self._lru) > self._max:
            self._lru.popitem(last=False)

    @staticmethod
    def _parse_jwk(jwk: JsonDict) -> Any:
        kty = jwk.get("kty")
        if kty == "RSA":
            return algorithms.RSAAlgorithm.from_jwk(jwk)
        if kty == "EC":
            return algorithms.ECAlgorithm.from_jwk(jwk)
        if kty == "OKP":
            crv = jwk.get("crv")
            if crv == "Ed25519":
                return algorithms.Ed25519Algorithm.from_jwk(jwk)
            raise ValueError("Unsupported OKP curve for JWS verification")
        if kty == "oct":
            k = jwk.get("k")
            if not isinstance(k, str):
                raise ValueError("oct JWK must include 'k'")
            return _b64u_decode(k)
        raise ValueError(f"Unsupported JWK kty: {kty!r}")


__all__ = ["CachedJWKSVerifier"]
