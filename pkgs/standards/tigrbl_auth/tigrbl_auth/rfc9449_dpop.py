"""Utilities for OAuth 2.0 Demonstrating Proof of Possession (DPoP)."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, Final
from uuid import uuid4

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from .deps import JWAAlg, JwsSignerVerifier

from .runtime_cfg import settings

RFC9449_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9449"
_ALG = JWAAlg.EDDSA
_ALLOWED_SKEW = 300  # seconds
_signer = JwsSignerVerifier()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# ---------------------------------------------------------------------------
# JWK helpers
# ---------------------------------------------------------------------------


def jwk_from_public_key(public_key: Ed25519PublicKey) -> Dict[str, str]:
    x = _b64url(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    return {"kty": "OKP", "crv": "Ed25519", "x": x}


def jwk_thumbprint(jwk: Dict[str, str]) -> str:
    data = json.dumps({k: jwk[k] for k in sorted(jwk)}, separators=(",", ":")).encode()
    digest = hashlib.sha256(data).digest()
    return _b64url(digest)


# ---------------------------------------------------------------------------
# DPoP proof helpers
# ---------------------------------------------------------------------------


def create_proof(
    private_pem: bytes, method: str, url: str, *, enabled: bool | None = None
) -> str:
    if enabled is None:
        enabled = settings.enable_rfc9449
    if not enabled:
        return ""
    sk = serialization.load_pem_private_key(private_pem, password=None)
    if not isinstance(sk, Ed25519PrivateKey):
        raise TypeError("private key must be Ed25519")
    jwk = jwk_from_public_key(sk.public_key())
    headers = {"typ": "dpop+jwt", "jwk": jwk}
    payload = {
        "htm": method.upper(),
        "htu": url,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "jti": str(uuid4()),
    }
    return asyncio.run(
        _signer.sign_compact(
            payload=payload,
            alg=_ALG,
            key={"kind": "cryptography_obj", "obj": sk},
            header_extra=headers,
        )
    )


def verify_proof(
    proof: str,
    method: str,
    url: str,
    *,
    jkt: str | None = None,
    enabled: bool | None = None,
) -> str:
    if enabled is None:
        enabled = settings.enable_rfc9449
    if not enabled:
        return ""
    parts = proof.split(".")
    if len(parts) != 3:
        raise ValueError(f"malformed DPoP proof: {RFC9449_SPEC_URL}")
    header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    jwk = header.get("jwk")
    if not jwk:
        raise ValueError(f"missing jwk in DPoP header: {RFC9449_SPEC_URL}")
    pub = base64.urlsafe_b64decode(jwk["x"] + "==")
    result = asyncio.run(_signer.verify_compact(proof, ed_pubkeys=[pub]))
    payload = json.loads(result.payload.decode())
    if payload.get("htm") != method.upper():
        raise ValueError(f"htm mismatch: {RFC9449_SPEC_URL}")
    if payload.get("htu") != url:
        raise ValueError(f"htu mismatch: {RFC9449_SPEC_URL}")
    now = int(time.time())
    iat = int(payload.get("iat", 0))
    if abs(now - iat) > _ALLOWED_SKEW:
        raise ValueError(f"iat out of range: {RFC9449_SPEC_URL}")
    thumb = jwk_thumbprint(jwk)
    if jkt and thumb != jkt:
        raise ValueError(f"jkt mismatch: {RFC9449_SPEC_URL}")
    return thumb


__all__ = [
    "RFC9449_SPEC_URL",
    "create_proof",
    "verify_proof",
    "jwk_from_public_key",
    "jwk_thumbprint",
]
