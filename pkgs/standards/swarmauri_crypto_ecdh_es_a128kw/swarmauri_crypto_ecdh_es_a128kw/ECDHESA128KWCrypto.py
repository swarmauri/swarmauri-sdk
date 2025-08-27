"""ECDH-ES+A128KW key wrapping provider."""

from __future__ import annotations

import json
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Dict, Iterable, Optional, Literal

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap

from swarmauri_core.crypto.types import (
    Alg,
    KeyRef,
    WrappedKey,
    UnsupportedAlgorithm,
)
from swarmauri_base.crypto.CryptoBase import CryptoBase


_WRAP_ALG = "ECDH-ES+A128KW"
_AESKW_ALG_ID = b"A128KW"


def _b64url(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return urlsafe_b64decode(data + padding)


def _derive_kek(shared: bytes) -> bytes:
    otherinfo = (
        len(_AESKW_ALG_ID).to_bytes(4, "big")
        + _AESKW_ALG_ID
        + b"\x00\x00\x00\x00"  # apu
        + b"\x00\x00\x00\x00"  # apv
        + (128).to_bytes(4, "big")
        + b""  # suppPrivInfo
    )
    kdf = ConcatKDFHash(algorithm=hashes.SHA256(), length=16, otherinfo=otherinfo)
    return kdf.derive(shared)


class ECDHESA128KWCrypto(CryptoBase):
    """Crypto provider implementing ECDH-ES+A128KW wrapping."""

    type: Literal["ECDHESA128KWCrypto"] = "ECDHESA128KWCrypto"

    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {"wrap": (_WRAP_ALG,), "unwrap": (_WRAP_ALG,)}

    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        wrap_alg = (wrap_alg or _WRAP_ALG).upper()
        if wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")
        if kek.public is None:
            raise ValueError("KeyRef.public must contain recipient EC public key")
        recipient_pub = serialization.load_pem_public_key(kek.public)
        if not isinstance(recipient_pub, ec.EllipticCurvePublicKey):
            raise ValueError("Recipient key must be an EC public key")

        dek = dek or secrets.token_bytes(16)
        eph_priv = ec.generate_private_key(recipient_pub.curve)
        shared = eph_priv.exchange(ec.ECDH(), recipient_pub)
        kek_bytes = _derive_kek(shared)
        wrapped_key = aes_key_wrap(kek_bytes, dek)
        eph_pub_bytes = eph_priv.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        payload = {
            "epk": _b64url(eph_pub_bytes),
            "kw": _b64url(wrapped_key),
        }
        return WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=_WRAP_ALG,
            wrapped=json.dumps(payload).encode("utf-8"),
            nonce=None,
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        if wrapped.wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrapped.wrap_alg}")
        if kek.material is None:
            raise ValueError("KeyRef.material must contain recipient EC private key")
        priv = serialization.load_pem_private_key(kek.material, password=None)
        if not isinstance(priv, ec.EllipticCurvePrivateKey):
            raise ValueError("Recipient key must be an EC private key")

        payload = json.loads(wrapped.wrapped.decode("utf-8"))
        eph_pub_der = _b64url_decode(payload["epk"])
        wrapped_key = _b64url_decode(payload["kw"])
        eph_pub = serialization.load_der_public_key(eph_pub_der)
        if not isinstance(eph_pub, ec.EllipticCurvePublicKey):
            raise ValueError("Ephemeral key must be an EC public key")
        shared = priv.exchange(ec.ECDH(), eph_pub)
        kek_bytes = _derive_kek(shared)
        return aes_key_unwrap(kek_bytes, wrapped_key)


__all__ = ["ECDHESA128KWCrypto"]
