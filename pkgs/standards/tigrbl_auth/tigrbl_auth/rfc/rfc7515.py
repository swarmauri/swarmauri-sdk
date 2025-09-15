"""RFC 7515 - JSON Web Signature (JWS) helpers via swarmauri plugins."""

from __future__ import annotations

from typing import Any, Final, Mapping

from ..deps import JWAAlg, JwsSignerVerifier

from ..runtime_cfg import settings

RFC7515_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7515"
_signer = JwsSignerVerifier()


async def sign_jws(payload: str, key: Mapping[str, Any]) -> str:
    """Return a JWS compact serialization of *payload* using *key*."""
    if not settings.enable_rfc7515:
        raise RuntimeError(f"RFC 7515 support disabled: {RFC7515_SPEC_URL}")
    alg = JWAAlg.HS256 if key.get("kty") == "oct" else JWAAlg.EDDSA
    return await _signer.sign_compact(payload=payload, alg=alg, key=key)


async def verify_jws(token: str, key: Mapping[str, Any]) -> str:
    """Verify *token* and return the decoded payload as a string."""
    if not settings.enable_rfc7515:
        raise RuntimeError(f"RFC 7515 support disabled: {RFC7515_SPEC_URL}")
    result = await _signer.verify_compact(token, jwks_resolver=lambda _k, _a: key)
    return result.payload.decode()


__all__ = ["sign_jws", "verify_jws", "RFC7515_SPEC_URL"]
