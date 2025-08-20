"""OpenPGP-backed crypto provider.

Implements the ICrypto contract using:
- AES-256-GCM for symmetric encrypt/decrypt
- OpenPGP public-key encryption for wrapping the session key to many recipients

Notes
-----
- For wrap/encrypt_for_many, ``KeyRef.public`` must contain an ASCII-armored
  OpenPGP public key (as produced by ``gpg --armor --export``)
- For unwrap, ``KeyRef.material`` must contain an ASCII-armored OpenPGP
  private key (as produced by ``gpg --armor --export-secret-keys``)
"""

from __future__ import annotations

import secrets
import tempfile
from typing import Any, Dict, Iterable, Literal, Optional
from enum import Enum

import gnupg
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


@ComponentBase.register_type(CryptoBase, "PGPCrypto")
class PGPCrypto(CryptoBase):
    """Concrete implementation of the ICrypto contract using AES-GCM and OpenPGP."""

    type: Literal["PGPCrypto"] = "PGPCrypto"

    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {
            "encrypt": ("AES-256-GCM",),
            "decrypt": ("AES-256-GCM",),
            "wrap": ("OpenPGP",),
            "unwrap": ("OpenPGP",),
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

    # ────────────────── hybrid encrypt-for-many via OpenPGP ────────────

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
        wrap_alg = recipient_wrap_alg or "OpenPGP"
        if wrap_alg != "OpenPGP":
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")

        k = secrets.token_bytes(32)  # 256-bit session key
        iv = nonce or secrets.token_bytes(12)
        aead = AESGCM(k)
        ct_with_tag = aead.encrypt(iv, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]

        recip_infos: list[RecipientInfo] = []

        # use an isolated temporary GPG home for each call to avoid polluting user keyrings
        with tempfile.TemporaryDirectory() as gpg_home:
            gpg = gnupg.GPG(gnupghome=gpg_home)
            for r in recipients:
                if r.public is None:
                    raise ValueError(
                        "Recipient KeyRef.public must contain ASCII-armored OpenPGP public key"
                    )
                import_result = gpg.import_keys(
                    r.public.decode() if isinstance(r.public, bytes) else r.public
                )
                if not import_result.fingerprints:
                    raise RuntimeError("Failed to import recipient OpenPGP public key")
                recipient_fp = import_result.fingerprints[0]

                enc = gpg.encrypt(k, recipient_fp, armor=False, always_trust=True)
                if not enc.ok:
                    raise RuntimeError(f"GPG encrypt failed: {enc.status}")

                recip_infos.append(
                    RecipientInfo(
                        kid=r.kid,
                        version=r.version,
                        wrap_alg=wrap_alg,
                        wrapped_key=bytes(enc.data),
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

    # ────────────────────────── raw OpenPGP wrap/unwrap ─────────────────

    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> WrappedKey:
        wrap_alg = wrap_alg or "OpenPGP"
        if wrap_alg != "OpenPGP":
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")
        if kek.public is None:
            raise ValueError(
                "KeyRef.public must contain ASCII-armored OpenPGP public key"
            )

        with tempfile.TemporaryDirectory() as gpg_home:
            gpg = gnupg.GPG(gnupghome=gpg_home)
            import_result = gpg.import_keys(
                kek.public.decode() if isinstance(kek.public, bytes) else kek.public
            )
            if not import_result.fingerprints:
                raise RuntimeError("Failed to import recipient OpenPGP public key")
            recipient_fp = import_result.fingerprints[0]

            dek = dek or secrets.token_bytes(32)
            enc = gpg.encrypt(dek, recipient_fp, armor=False, always_trust=True)
            if not enc.ok:
                raise RuntimeError(f"GPG encrypt failed: {enc.status}")

        return WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=wrap_alg,
            nonce=nonce,
            wrapped=bytes(enc.data),
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        if wrapped.wrap_alg != "OpenPGP":
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrapped.wrap_alg}")
        if kek.material is None:
            raise ValueError(
                "KeyRef.material must contain ASCII-armored OpenPGP private key"
            )

        passphrase = None
        if kek.tags and "passphrase" in kek.tags:
            passphrase = kek.tags["passphrase"]

        with tempfile.TemporaryDirectory() as gpg_home:
            gpg = gnupg.GPG(gnupghome=gpg_home)
            import_result = gpg.import_keys(
                kek.material.decode()
                if isinstance(kek.material, bytes)
                else kek.material
            )
            if not import_result.fingerprints:
                raise RuntimeError("Failed to import OpenPGP private key")

            dec = gpg.decrypt(wrapped.wrapped, passphrase=passphrase or "")
            if not dec.ok:
                raise RuntimeError(f"GPG decrypt failed: {dec.status}")

            return bytes(dec.data)

    # ───────────────────────── signing (not supported) ──────────────────

    async def sign(
        self,
        key: KeyRef,
        msg: bytes,
        *,
        alg: Optional[Alg] = None,
    ):
        raise UnsupportedAlgorithm("sign not supported by PGPCrypto")

    async def verify(
        self,
        key: KeyRef,
        msg: bytes,
        sig,
    ) -> bool:
        raise UnsupportedAlgorithm("verify not supported by PGPCrypto")
