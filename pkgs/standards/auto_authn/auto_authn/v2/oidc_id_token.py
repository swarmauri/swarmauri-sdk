"""Helpers for minting and verifying OIDC ID Tokens.

This module issues ID Tokens as JWTs signed with RS256 using the
``JWTTokenService`` infrastructure.  It stores the signing key on disk via
``FileKeyProvider`` similar to the Ed25519 helpers in :mod:`crypto` but backed by
an RSA key pair.  Only the minimal set of claims required by the OpenID Connect
Core specification are handled here.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import base64
import json
from hashlib import sha256
from datetime import timedelta
from functools import lru_cache
from typing import Any, Iterable, Mapping, Tuple

from .deps import (
    ExportPolicy,
    FileKeyProvider,
    JWAAlg,
    JWTTokenService,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)
from .errors import InvalidTokenError

# ---------------------------------------------------------------------------
# Signing key management
# ---------------------------------------------------------------------------

# Location of the RSA key identifier used for ID Token signing.
_RSA_KEY_PATH = pathlib.Path(
    os.getenv("JWT_RS256_KEY_PATH", "runtime_secrets/jwt_rs256.kid")
)


@lru_cache(maxsize=1)
def _provider() -> FileKeyProvider:
    """Return a cached ``FileKeyProvider`` rooted at the key directory."""
    return FileKeyProvider(_RSA_KEY_PATH.parent)


async def _ensure_key() -> Tuple[str, bytes, bytes]:
    """Ensure an RSA signing key exists and return ``(kid, priv, pub)``."""
    kp = _provider()
    if _RSA_KEY_PATH.exists():
        kid = _RSA_KEY_PATH.read_text().strip()
        ref = await kp.get_key(kid, include_secret=True)
    else:
        spec = KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.RSA_PSS_SHA256,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            label="jwt_rs256",
        )
        ref = await kp.create_key(spec)
        _RSA_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        _RSA_KEY_PATH.write_text(ref.kid)
    priv = ref.material or b""
    pub = ref.public or b""
    return ref.kid, priv, pub


@lru_cache(maxsize=1)
def _service() -> Tuple[JWTTokenService, str]:
    """Return a ``JWTTokenService`` bound to the RSA signing key."""
    kid, _, _ = asyncio.run(_ensure_key())
    svc = JWTTokenService(_provider())
    return svc, kid


# ---------------------------------------------------------------------------
# ID Token helpers
# ---------------------------------------------------------------------------


def _header_alg(token: str) -> str:
    try:
        header_segment = token.split(".")[0]
        padded = header_segment + "=" * (-len(header_segment) % 4)
        header = json.loads(base64.urlsafe_b64decode(padded).decode())
        return str(header.get("alg", "")).lower()
    except Exception:
        return ""


def oidc_hash(value: str) -> str:
    """Return the OIDC token hash for *value* per Core §3.3.2.11."""

    digest = sha256(value.encode("ascii")).digest()
    half = digest[: len(digest) // 2]
    return base64.urlsafe_b64encode(half).decode("ascii").rstrip("=")


def mint_id_token(
    *,
    sub: str,
    aud: Iterable[str] | str,
    nonce: str,
    issuer: str,
    ttl: timedelta = timedelta(minutes=5),
    **extra: Mapping[str, Any] | Any,
) -> str:
    """Mint an ID Token for *sub* and *aud* with the given *nonce*.

    The token is signed with RS256 and includes the standard claims required by
    OIDC: ``iss``, ``sub``, ``aud``, ``exp``, ``iat``, and ``nonce``.
    Additional claims may be supplied via ``extra``.
    """

    svc, kid = _service()
    claims: dict[str, Any] = {"nonce": nonce}
    if extra:
        claims.update(extra)  # type: ignore[arg-type]
    return asyncio.run(
        svc.mint(
            claims,
            alg=JWAAlg.RS256,
            kid=kid,
            lifetime_s=int(ttl.total_seconds()),
            issuer=issuer,
            subject=sub,
            audience=aud,
        )
    )


def verify_id_token(token: str, *, issuer: str, audience: Iterable[str] | str) -> dict:
    """Verify *token* and return its claims if valid."""
    if _header_alg(token) in {"", "none"}:
        raise InvalidTokenError("unsigned JWTs are not accepted")
    svc, _ = _service()
    return asyncio.run(svc.verify(token, issuer=issuer, audience=audience))


# Exported helpers for JWKS publication
rsa_key_provider = _provider
ensure_rsa_jwt_key = _ensure_key


async def rotate_rsa_jwt_key() -> str:
    """Create a new RSA signing key and update cached services."""
    kp = _provider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="jwt_rs256",
    )
    ref = await kp.create_key(spec)
    _RSA_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _RSA_KEY_PATH.write_text(ref.kid)
    _service.cache_clear()
    try:  # refresh discovery metadata if available
        from .rfc8414 import refresh_discovery_cache

        refresh_discovery_cache()
    except Exception:  # pragma: no cover - best effort
        pass
    return ref.kid


__all__ = [
    "mint_id_token",
    "verify_id_token",
    "oidc_hash",
    "rsa_key_provider",
    "ensure_rsa_jwt_key",
    "rotate_rsa_jwt_key",
]
