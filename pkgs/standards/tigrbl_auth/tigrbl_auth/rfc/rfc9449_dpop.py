"""Utilities for OAuth 2.0 Demonstrating Proof of Possession (DPoP)."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from typing import Any, Dict, Final
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import serialization
from swarmauri_signing_dpop import DpopSigner
from ..deps import JWAAlg

from ..runtime_cfg import settings

RFC9449_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9449"
_ALG = JWAAlg.EDDSA
_ALLOWED_SKEW = 300  # seconds
_signer = DpopSigner()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# ---------------------------------------------------------------------------
# JWK helpers
# ---------------------------------------------------------------------------


def jwk_from_public_key(public_key: bytes) -> Dict[str, str]:
    if public_key.startswith(b"-----BEGIN"):
        pub_obj = load_pem_public_key(public_key)
        public_key = pub_obj.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    x = _b64url(public_key)
    return {"kty": "OKP", "crv": "Ed25519", "x": x}


def jwk_thumbprint(jwk: Dict[str, str]) -> str:
    data = json.dumps({k: jwk[k] for k in sorted(jwk)}, separators=(",", ":")).encode()
    digest = hashlib.sha256(data).digest()
    return _b64url(digest)


# ---------------------------------------------------------------------------
# DPoP proof helpers
# ---------------------------------------------------------------------------


def create_proof(
    keyref: Any, method: str, url: str, *, enabled: bool | None = None
) -> str:
    """Create a DPoP proof for *method* and *url* using *keyref*.

    ``keyref`` is the :class:`~swarmauri_core.crypto.types.KeyRef` returned by a
    Swarmauri key provider such as :class:`~tigrbl_auth.deps.LocalKeyProvider` or
    ``InMemoryKeyProvider``. The private key material from the provider is
    passed to :class:`~swarmauri_signing_dpop.DpopSigner` for signing, avoiding
    direct usage of ``cryptography`` within this module.
    """

    if enabled is None:
        enabled = settings.enable_rfc9449
    if not enabled:
        return ""
    priv = keyref.material or b""
    if isinstance(priv, str):
        priv = priv.encode()
    sigs = asyncio.run(
        _signer.sign_bytes(
            {"kind": "pem", "priv": priv},
            b"",
            alg=_ALG.value,
            opts={"htm": method.upper(), "htu": url},
        )
    )
    return sigs[0]["sig"]


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
    # Decode header to derive JWK thumbprint for caller.
    parts = proof.split(".")
    if len(parts) != 3:
        raise ValueError(f"malformed DPoP proof: {RFC9449_SPEC_URL}")
    header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    jwk = header.get("jwk")
    if not jwk:
        raise ValueError(f"missing jwk in DPoP header: {RFC9449_SPEC_URL}")
    thumb = jwk_thumbprint(jwk)

    valid = asyncio.run(
        _signer.verify_bytes(
            b"",
            [{"sig": proof}],
            require={
                "htm": method.upper(),
                "htu": url,
                "algs": [_ALG.value],
                "max_skew_s": _ALLOWED_SKEW,
            },
        )
    )
    if not valid:
        raise ValueError(f"invalid DPoP proof: {RFC9449_SPEC_URL}")
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
