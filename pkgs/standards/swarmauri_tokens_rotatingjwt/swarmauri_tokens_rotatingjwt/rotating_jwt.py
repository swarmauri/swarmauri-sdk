"""Rotating JWT token service.

This module provides :class:`RotatingJWTTokenService`, a token issuer and
verifier that automatically rotates its signing key based on time or usage
thresholds. Older keys are retained for a configurable period so that tokens
minted with previous versions remain valid.

The implementation follows RFC 7515 (JWS), RFC 7517 (JWK), RFC 7518 (JWA) and
RFC 7519 (JWT).
"""

from __future__ import annotations

from typing import Dict, Iterable, Literal, Optional, Tuple
import base64
import time

import jwt
from jwt import algorithms

from abc import ABC

from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse
from swarmauri_core.crypto.types import JWAAlg


__all__ = ["RotatingJWTTokenService"]


def _now() -> int:
    """Return the current Unix timestamp.

    RETURNS (int): Seconds elapsed since the Unix epoch.
    """

    return int(time.time())


def _parse_kid_ver(header_kid: str) -> Tuple[str, int | None]:
    """Split ``kid.version`` into its components.

    header_kid (str): Value of the ``kid`` header, optionally suffixed by a
        version (e.g. ``"abc123.2"``).
    RETURNS (Tuple[str, int | None]): Base key identifier and version number
        if present.
    """

    if not header_kid:
        return "", None
    parts = header_kid.split(".")
    if len(parts) >= 2 and parts[-1].isdigit():
        return ".".join(parts[:-1]), int(parts[-1])
    return header_kid, None


def _b64u_to_bytes(s: str) -> bytes:
    """Decode a base64url-encoded string.

    s (str): Base64url-encoded data without padding.
    RETURNS (bytes): The decoded byte sequence.
    """

    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode(s + pad)


_SIGN_ALGS = {
    JWAAlg.RS256,
    JWAAlg.PS256,
    JWAAlg.ES256,
    JWAAlg.EDDSA,
    JWAAlg.HS256,
}


def _default_spec_for_alg(alg: JWAAlg, *, label: Optional[str] = None) -> KeySpec:
    """Choose a sensible :class:`KeySpec` for creating the initial signing key.

    alg (JWAAlg): Desired signing algorithm.
    label (str | None): Optional label for the created key.
    RETURNS (KeySpec): Specification describing the key to create.
    """
    if alg == JWAAlg.HS256:
        return KeySpec(
            klass=KeyClass.symmetric,
            alg=KeyAlg.AES256_GCM,
            size_bits=256,
            label=label or "hs256-signing",
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
        )
    if alg in {JWAAlg.RS256, JWAAlg.PS256}:
        return KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.RSA_PSS_SHA256,
            size_bits=3072,
            label=label or f"{alg}-signing",
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
        )
    if alg == JWAAlg.ES256:
        return KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.ECDSA_P256_SHA256,
            size_bits=None,
            label=label or "es256-signing",
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
        )
    if alg == JWAAlg.EDDSA:
        return KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.ED25519,
            size_bits=None,
            label=label or "eddsa-signing",
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
        )
    raise ValueError(f"Unsupported alg for default spec: {alg.value}")


class TokenServiceBase(ABC):
    """Minimal token service base class."""


class RotatingJWTTokenService(TokenServiceBase):
    """JWT issuer/verifier that rotates the signing key.

    Rotation can be triggered by elapsed time (``rotate_every_s``) or after a
    maximum number of minted tokens (``max_tokens_per_key``). Previous key
    versions are retained for a configurable window so that older tokens remain
    verifiable.
    """

    type: Literal["RotatingJWTTokenService"] = "RotatingJWTTokenService"

    def __init__(
        self,
        key_provider: IKeyProvider,
        *,
        alg: JWAAlg = JWAAlg.RS256,
        base_kid: Optional[str] = None,
        create_spec: Optional[KeySpec] = None,
        default_issuer: Optional[str] = None,
        rotate_every_s: Optional[int] = None,
        max_tokens_per_key: Optional[int] = None,
        previous_key_ttl_s: int = 86_400,
    ) -> None:
        """Create a rotating JWT token service.

        key_provider (IKeyProvider): Backend used to store and rotate keys.
        alg (JWAAlg): Signing algorithm for issued tokens.
        base_kid (str | None): Existing key identifier to bootstrap from.
        create_spec (KeySpec | None): Specification for creating the initial
            key if one does not already exist.
        default_issuer (str | None): Default ``iss`` claim for minted tokens.
        rotate_every_s (int | None): Seconds between automatic rotations.
        max_tokens_per_key (int | None): Maximum tokens minted before forcing
            rotation.
        previous_key_ttl_s (int): Time in seconds to retain previous keys for
            verification.
        RETURNS (None): This constructor does not return anything.
        """

        super().__init__()
        if alg not in _SIGN_ALGS:
            raise ValueError(f"Unsupported alg: {alg.value}")

        self._kp = key_provider
        self._alg = alg
        self._iss = default_issuer

        self._rotate_every_s = int(rotate_every_s) if rotate_every_s else None
        self._max_tokens = int(max_tokens_per_key) if max_tokens_per_key else None
        self._prev_ttl = int(previous_key_ttl_s)

        self._kid: str
        self._ver: int
        self._prev_versions: Dict[int, int] = {}
        self._mint_count = 0
        self._next_rotate_at: Optional[int] = None
        self._init_signing_key(base_kid, create_spec)

    # ------------------------------------------------------------------
    # ITokenService interface
    # ------------------------------------------------------------------
    def supports(self) -> Dict[str, Iterable[JWAAlg]]:
        """Return the token formats and algorithms supported.

        RETURNS (Dict[str, Iterable[JWAAlg]]): Mapping of supported formats and
        algorithms.
        """

        return {"formats": ("JWT", "JWS"), "algs": (self._alg,)}

    async def mint(
        self,
        claims: Dict[str, object],
        *,
        alg: JWAAlg,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, object]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        """Generate a signed JWT.

        claims (Dict[str, object]): Claims to include in the payload.
        alg (JWAAlg): Algorithm used for signing; must match the service
            configuration.
        kid (str | None): Override key identifier to sign with.
        key_version (int | None): Specific key version to sign with.
        headers (Dict[str, object] | None): Additional headers to include.
        lifetime_s (int | None): Lifetime of the token in seconds.
        issuer (str | None): Issuer claim to set for the token.
        subject (str | None): Subject claim to include.
        audience (str | list[str] | None): Audience claim for the token.
        scope (str | None): Optional scope value.
        RETURNS (str): Encoded JWT token.
        """

        if alg != self._alg:
            raise ValueError(
                f"This service is configured for alg={self._alg.value}, got {alg.value}"
            )

        await self._maybe_rotate()

        now = _now()
        payload = dict(claims)
        payload.setdefault("iat", now)
        payload.setdefault("nbf", now)
        if lifetime_s:
            payload.setdefault("exp", now + int(lifetime_s))
        if issuer or self._iss:
            payload.setdefault("iss", issuer or self._iss)
        if subject:
            payload.setdefault("sub", subject)
        if audience:
            payload.setdefault("aud", audience)
        if scope:
            payload.setdefault("scope", scope)

        hdr = dict(headers or {})
        hdr["alg"] = self._alg.value
        hdr["kid"] = f"{self._kid}.{self._ver}"

        ref = await self._kp.get_key(self._kid, self._ver, include_secret=True)
        if self._alg == JWAAlg.HS256:
            if ref.material is None:
                raise RuntimeError("HMAC secret is not exportable under current policy")
            key = ref.material
        else:
            key = ref.material
            if key is None:
                raise RuntimeError("Signing key is not exportable under current policy")

        token = jwt.encode(payload, key, algorithm=self._alg.value, headers=hdr)
        self._mint_count += 1
        return token

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, object]:
        """Validate a JWT and return its claims.

        token (str): Encoded JWT to verify.
        issuer (str | None): Expected issuer value.
        audience (str | list[str] | None): Expected audience claim.
        leeway_s (int): Allowable clock skew in seconds.
        RETURNS (Dict[str, object]): Verified claims payload.
        """

        try:
            header = jwt.get_unverified_header(token)
        except Exception as exc:  # pragma: no cover - propagating original error
            raise jwt.InvalidTokenError(f"Invalid JWS/JWT header: {exc}") from exc

        header_kid = header.get("kid")
        alg_val = header.get("alg")
        if not header_kid or alg_val is None:
            raise jwt.InvalidTokenError("Missing or unsupported kid/alg in header")
        try:
            alg = JWAAlg(alg_val)
        except ValueError as exc:
            raise jwt.InvalidTokenError(f"Unsupported alg: {alg_val}") from exc
        if alg not in _SIGN_ALGS:
            raise jwt.InvalidTokenError("Missing or unsupported kid/alg in header")

        kid, ver = _parse_kid_ver(header_kid)

        async def resolve_key() -> object | None:
            if alg == JWAAlg.HS256:
                ref = await self._kp.get_key(kid, ver, include_secret=True)
                return ref.material

            if ver is not None:
                try:
                    jwk = await self._kp.get_public_jwk(kid, ver)
                    return _jwk_to_key(jwk)
                except Exception:
                    pass

            jwks = await self._kp.jwks()
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == header_kid:
                    return _jwk_to_key(jwk)
            for jwk in jwks.get("keys", []):
                if isinstance(jwk.get("kid"), str) and jwk["kid"].startswith(kid + "."):
                    return _jwk_to_key(jwk)
            return None

        key_obj = await resolve_key()
        if key_obj is None:
            raise jwt.InvalidTokenError("Unable to resolve verification key")

        options = {"verify_aud": audience is not None}
        return jwt.decode(
            token,
            key=key_obj,
            algorithms=[alg.value],
            audience=audience,
            issuer=issuer or self._iss,
            leeway=leeway_s,
            options=options,
        )

    async def jwks(self) -> dict:
        """Return the JSON Web Key Set for verification.

        RETURNS (dict): JWKS containing current and previous public keys.
        """

        base = await self._kp.jwks()
        seen = {k.get("kid") for k in base.get("keys", []) if isinstance(k, dict)}
        keys = list(base.get("keys", []))

        current_kid = f"{self._kid}.{self._ver}"
        try:
            if current_kid not in seen:
                keys.append(await self._kp.get_public_jwk(self._kid, self._ver))
                seen.add(current_kid)
        except Exception:
            pass

        now = _now()
        expired = [v for v, until in self._prev_versions.items() if until <= now]
        for v in expired:
            self._prev_versions.pop(v, None)
        for v in self._prev_versions.keys():
            kidv = f"{self._kid}.{v}"
            if kidv in seen:
                continue
            try:
                keys.append(await self._kp.get_public_jwk(self._kid, v))
                seen.add(kidv)
            except Exception:
                continue

        return {"keys": keys}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _schedule_next_rotation(self) -> None:
        """Compute the timestamp for the next rotation.

        RETURNS (None): This method does not return anything.
        """

        self._mint_count = 0
        if self._rotate_every_s:
            self._next_rotate_at = _now() + self._rotate_every_s
        else:
            self._next_rotate_at = None

    async def _maybe_rotate(self) -> None:
        """Rotate the signing key if rotation conditions are met.

        RETURNS (None): This method does not return anything.
        """

        due_time = self._next_rotate_at is not None and _now() >= self._next_rotate_at
        due_count = (
            self._max_tokens is not None and self._mint_count >= self._max_tokens
        )
        if not (due_time or due_count):
            return

        self._prev_versions[self._ver] = _now() + self._prev_ttl
        ref = await self._kp.rotate_key(self._kid)
        self._kid = ref.kid
        self._ver = ref.version
        self._schedule_next_rotation()

    def _init_signing_key(
        self, base_kid: Optional[str], create_spec: Optional[KeySpec]
    ) -> None:
        """Initialize the signing key.

        base_kid (str | None): Existing key identifier to reuse.
        create_spec (KeySpec | None): Specification for creating a new key.
        RETURNS (None): This method does not return anything.
        """

        if base_kid:
            self._kid = base_kid
            self._ver = 1
        else:
            spec = create_spec or _default_spec_for_alg(self._alg, label="jwt-issuer")
            ref = _sync_run(self._kp.create_key(spec))
            self._kid = ref.kid
            self._ver = ref.version
        self._schedule_next_rotation()

    async def force_rotate(self) -> Tuple[str, int]:
        """Force immediate key rotation.

        RETURNS (Tuple[str, int]): New key identifier and version.
        """

        await self._maybe_rotate()
        self._prev_versions[self._ver] = _now() + self._prev_ttl
        ref = await self._kp.rotate_key(self._kid)
        self._kid, self._ver = ref.kid, ref.version
        self._schedule_next_rotation()
        return self._kid, self._ver

    @property
    def current_signing_key(self) -> Tuple[str, int, JWAAlg]:
        """Return the current key identifier, version and algorithm.

        RETURNS (Tuple[str, int, JWAAlg]): Details of the active signing key.
        """

        return self._kid, self._ver, self._alg


def _jwk_to_key(jwk: dict) -> object:
    """Convert a JWK dictionary to a cryptography key object.

    jwk (dict): JSON Web Key representation.
    RETURNS (object): Key object or ``None`` if unsupported.
    """

    kty = jwk.get("kty")
    if kty == "RSA":
        return algorithms.RSAAlgorithm.from_jwk(jwk)
    if kty == "EC":
        return algorithms.ECAlgorithm.from_jwk(jwk)
    if kty == "OKP" and jwk.get("crv") == "Ed25519":
        return algorithms.Ed25519Algorithm.from_jwk(jwk)
    if kty == "oct":
        k = jwk.get("k")
        if isinstance(k, str):
            return _b64u_to_bytes(k)
    return None


def _sync_run(coro):
    """Execute an async coroutine in a synchronous context.

    coro: Awaitable object to execute.
    RETURNS: Result produced by the coroutine.
    """

    try:
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
                asyncio.set_event_loop(loop)
        return asyncio.run(coro)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to initialize signing key: {exc}") from exc
