"""OpenPGP-backed crypto provider with sealing support.

Implements the ICrypto contract using:
- AES-256-GCM for symmetric encrypt/decrypt (AEAD)
- OpenPGP public-key encryption for:
    • wrapping the session key to many recipients (KEM+AEAD mode)
    • sealing/unsealing (direct public-key encryption of plaintext) for one or many

Notes
-----
- For wrap/encrypt_for_many/seal, ``KeyRef.public`` must contain an ASCII-armored
  OpenPGP public key (as produced by ``gpg --armor --export``)
- For unwrap/unseal, ``KeyRef.material`` must contain an ASCII-armored OpenPGP
  private key (as produced by ``gpg --armor --export-secret-keys``)
- Sealed mode ("OpenPGP-SEAL") does not bind AAD and produces per-recipient
  ciphertexts (shared nonce/ct/tag are empty in MultiRecipientEnvelope).
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
    KeyRef,  # re-exported name used in ICrypto
)

from swarmauri_base.crypto.CryptoBase import CryptoBase
from swarmauri_base.ComponentBase import ComponentBase


_AEAD_DEFAULT = "AES-256-GCM"
_WRAP_ALG = "OpenPGP"
_SEAL_ALG = "OpenPGP-SEAL"


@ComponentBase.register_type(CryptoBase, "PGPCrypto")
class PGPCrypto(CryptoBase):
    """Concrete implementation of the ICrypto contract using AES-GCM and OpenPGP."""

    type: Literal["PGPCrypto"] = "PGPCrypto"

    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {
            "encrypt": (_AEAD_DEFAULT,),
            "decrypt": (_AEAD_DEFAULT,),
            "wrap": (_WRAP_ALG,),
            "unwrap": (_WRAP_ALG,),
            # Sealed-mode convenience
            "seal": (_SEAL_ALG,),
            "unseal": (_SEAL_ALG,),
            # encrypt_for_many supports both KEM+AEAD (AES-256-GCM + OpenPGP)
            # and sealed-style envelopes (OpenPGP-SEAL)
        }

    # ────────────────────────── symmetric AEAD ──────────────────────────

    def _normalize_aead_alg(self, alg: Any) -> Alg:
        if isinstance(alg, Enum):
            alg = alg.value
        alg = alg or _AEAD_DEFAULT
        if alg == "AES256_GCM":
            alg = _AEAD_DEFAULT
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
        if alg != _AEAD_DEFAULT:
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
        # AESGCM returns ciphertext||tag (16 bytes)
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
        if self._normalize_aead_alg(ct.alg) != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {ct.alg}")
        if key.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AEAD"
            )

        aead = AESGCM(key.material)
        blob = ct.ct + ct.tag
        return aead.decrypt(ct.nonce, blob, aad or ct.aad)

    # ─────────────────────────── sealing ───────────────────────────
    # (OpenPGP public-key encryption of plaintext; gpg handles hybrid internally)

    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = _SEAL_ALG,
    ) -> bytes:
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")
        if recipient.public is None:
            raise ValueError(
                "KeyRef.public must contain ASCII-armored OpenPGP public key"
            )

        with tempfile.TemporaryDirectory() as gpg_home:
            gpg = gnupg.GPG(gnupghome=gpg_home)
            import_result = gpg.import_keys(
                recipient.public.decode()
                if isinstance(recipient.public, bytes)
                else recipient.public
            )
            if not import_result.fingerprints:
                raise RuntimeError("Failed to import recipient OpenPGP public key")
            fp = import_result.fingerprints[0]

            enc = gpg.encrypt(pt, fp, armor=False, always_trust=True)
            if not enc.ok:
                raise RuntimeError(f"GPG encrypt (seal) failed: {enc.status}")
            return bytes(enc.data)

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = _SEAL_ALG,
    ) -> bytes:
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")
        if recipient_priv.material is None:
            raise ValueError(
                "KeyRef.material must contain ASCII-armored OpenPGP private key"
            )

        passphrase = None
        if recipient_priv.tags and "passphrase" in recipient_priv.tags:
            passphrase = recipient_priv.tags["passphrase"]

        with tempfile.TemporaryDirectory() as gpg_home:
            gpg = gnupg.GPG(gnupghome=gpg_home)
            import_result = gpg.import_keys(
                recipient_priv.material.decode()
                if isinstance(recipient_priv.material, bytes)
                else recipient_priv.material
            )
            if not import_result.fingerprints:
                raise RuntimeError("Failed to import OpenPGP private key")

            dec = gpg.decrypt(sealed, passphrase=passphrase or "")
            if not dec.ok:
                raise RuntimeError(f"GPG decrypt (unseal) failed: {dec.status}")
            return bytes(dec.data)

    # ─────────── hybrid encrypt-for-many via OpenPGP (KEM+AEAD) ───────────

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
        # 1) Sealed-style variant (per-recipient ciphertext; no shared ct/aad)
        if enc_alg == _SEAL_ALG:
            recip_infos: list[RecipientInfo] = []
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
                        raise RuntimeError(
                            "Failed to import recipient OpenPGP public key"
                        )
                    fp = import_result.fingerprints[0]

                    enc = gpg.encrypt(pt, fp, armor=False, always_trust=True)
                    if not enc.ok:
                        raise RuntimeError(
                            f"GPG encrypt (seal-for-many) failed: {enc.status}"
                        )

                    recip_infos.append(
                        RecipientInfo(
                            kid=r.kid,
                            version=r.version,
                            wrap_alg=_SEAL_ALG,
                            wrapped_key=bytes(enc.data),
                            nonce=None,
                        )
                    )

            # Shared fields empty for sealed variant
            return MultiRecipientEnvelope(
                enc_alg=_SEAL_ALG,
                nonce=b"",
                ct=b"",
                tag=b"",
                recipients=tuple(recip_infos),
                aad=None,  # AAD is not bound in OpenPGP-seal mode
            )

        # 2) Default KEM+AEAD path (shared AES-GCM ct + PGP-wrapped session key)
        enc_alg = self._normalize_aead_alg(enc_alg)
        if enc_alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported enc_alg: {enc_alg}")
        wrap_alg = recipient_wrap_alg or _WRAP_ALG
        if wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")

        k = secrets.token_bytes(32)  # 256-bit session key
        iv = nonce or secrets.token_bytes(12)
        aead = AESGCM(k)
        ct_with_tag = aead.encrypt(iv, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]

        recip_infos: list[RecipientInfo] = []
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
                fp = import_result.fingerprints[0]

                enc = gpg.encrypt(k, fp, armor=False, always_trust=True)
                if not enc.ok:
                    raise RuntimeError(f"GPG encrypt failed: {enc.status}")

                recip_infos.append(
                    RecipientInfo(
                        kid=r.kid,
                        version=r.version,
                        wrap_alg=wrap_alg,
                        wrapped_key=bytes(enc.data),
                        nonce=None,
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
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        wrap_alg = wrap_alg or _WRAP_ALG
        if wrap_alg != _WRAP_ALG:
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
        if wrapped.wrap_alg != _WRAP_ALG:
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
