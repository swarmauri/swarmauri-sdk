"""Paramiko-backed crypto provider.

Implements the ICrypto contract using:
- AES-256-GCM for symmetric encrypt/decrypt
- RSA-OAEP(SHA-256) for wrapping the session key to many recipients

Notes
-----
- This provider expects RSA public keys in OpenSSH format via ``KeyRef.public``
- For unwrap, a PEM-encoded RSA private key is expected in ``KeyRef.material``
"""

from __future__ import annotations

import secrets
from typing import Any, Dict, Iterable, Literal, Optional
from enum import Enum

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from swarmauri_core.crypto.types import (
    AEADCiphertext,
    Alg,
    MultiRecipientEnvelope,
    RecipientInfo,
    UnsupportedAlgorithm,
    WrappedKey,
)
from swarmauri_core.crypto.types import KeyRef  # re-exported name used in ICrypto
from swarmauri_base.crypto.CryptoBase import CryptoBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(CryptoBase, "ParamikoCrypto")
class ParamikoCrypto(CryptoBase):
    """Concrete implementation of the ICrypto contract using AES-GCM and RSA-OAEP."""

    type: Literal["ParamikoCrypto"] = "ParamikoCrypto"

    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {
            "encrypt": ("AES-256-GCM",),
            "decrypt": ("AES-256-GCM",),
            "wrap": ("RSA-OAEP-SHA256",),
            "unwrap": ("RSA-OAEP-SHA256",),
            "sign": (),
            "verify": (),
        }

    # ────────────────────────── symmetric AEAD ──────────────────────────

    def _normalize_aead_alg(self, alg: Any) -> Alg:
        if isinstance(alg, Enum):
            alg = alg.value
        alg = alg or "AES-256-GCM"
        if alg == "AES256_GCM":
            alg = "AES-256-GCM"
        return alg

    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        alg = self._normalize_aead_alg(alg)
        if alg != "AES-256-GCM":
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {alg}")

        if key.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AEAD"
            )
        if len(key.material) not in (16, 24, 32):
            raise ValueError("KeyRef.material must be 16/24/32 bytes for AES-GCM")

        nonce = nonce or secrets.token_bytes(12)
        aead = AESGCM(key.material)
        ct_with_tag = aead.encrypt(nonce, pt, aad)
        # AESGCM appends a 16-byte tag to the ciphertext
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
        return AEADCiphertext(
            kid=key.kid,
            version=key.version,
            alg=alg,
            nonce=nonce,
            ct=ct,
            tag=tag,
            aad=aad,
        )

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        if self._normalize_aead_alg(ct.alg) != "AES-256-GCM":
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {ct.alg}")
        if key.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AEAD"
            )

        aead = AESGCM(key.material)
        blob = ct.ct + ct.tag
        return aead.decrypt(ct.nonce, blob, aad or ct.aad)

    # ────────────────── hybrid encrypt-for-many via RSA-OAEP ────────────

    async def encrypt_for_many(
        self,
        recipients: Iterable[KeyRef],
        pt: bytes,
        *,
        enc_alg: Optional[Alg] = None,
        recipient_wrap_alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> MultiRecipientEnvelope:
        enc_alg = self._normalize_aead_alg(enc_alg)
        if enc_alg != "AES-256-GCM":
            raise UnsupportedAlgorithm(f"Unsupported enc_alg: {enc_alg}")
        wrap_alg = recipient_wrap_alg or "RSA-OAEP-SHA256"
        if wrap_alg != "RSA-OAEP-SHA256":
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")

        k = secrets.token_bytes(32)  # 256-bit session key
        iv = nonce or secrets.token_bytes(12)
        aead = AESGCM(k)
        ct_with_tag = aead.encrypt(iv, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]

        recip_infos: list[RecipientInfo] = []
        for r in recipients:
            if r.public is None:
                raise ValueError(
                    "Recipient KeyRef.public must contain OpenSSH RSA public key bytes"
                )
            rsa_pub = serialization.load_ssh_public_key(r.public)
            enc_k = rsa_pub.encrypt(
                k,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            recip_infos.append(
                RecipientInfo(
                    kid=r.kid,
                    version=r.version,
                    wrap_alg=wrap_alg,
                    wrapped_key=enc_k,
                )
            )

        return MultiRecipientEnvelope(
            enc_alg=enc_alg,
            nonce=iv,
            ct=ct,
            tag=tag,
            recipients=tuple(recip_infos),
            aad=aad,
        )

    # ────────────────────────── raw RSA wrap/unwrap ─────────────────────

    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> WrappedKey:
        wrap_alg = wrap_alg or "RSA-OAEP-SHA256"
        if wrap_alg != "RSA-OAEP-SHA256":
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")
        if kek.public is None:
            raise ValueError("KeyRef.public must contain OpenSSH RSA public key bytes")

        rsa_pub = serialization.load_ssh_public_key(kek.public)
        dek = dek or secrets.token_bytes(32)
        wrapped = rsa_pub.encrypt(
            dek,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=wrap_alg,
            nonce=nonce,
            wrapped=wrapped,
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        if wrapped.wrap_alg != "RSA-OAEP-SHA256":
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrapped.wrap_alg}")
        if kek.material is None:
            raise ValueError(
                "KeyRef.material must contain PEM-encoded RSA private key bytes"
            )

        priv = serialization.load_pem_private_key(kek.material, password=None)
        return priv.decrypt(
            wrapped.wrapped,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    # ───────────────────────── signing (not supported) ──────────────────

    async def sign(
        self,
        key: KeyRef,
        msg: bytes,
        *,
        alg: Optional[Alg] = None,
    ):
        raise UnsupportedAlgorithm("sign not supported by ParamikoCrypto")

    async def verify(
        self,
        key: KeyRef,
        msg: bytes,
        sig,
    ) -> bool:
        raise UnsupportedAlgorithm("verify not supported by ParamikoCrypto")
