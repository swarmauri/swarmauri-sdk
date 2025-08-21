"""Interface for cryptography plugins.

Adds explicit sealing support.

Semantics
---------
- encrypt/decrypt:
    Symmetric AEAD over arbitrary plaintext using a DEK (e.g., AES-GCM).
- wrap/unwrap:
    Protects a DEK under a KEK (e.g., AES-KW, RSA-OAEP, OpenPGP).
- encrypt_for_many:
    Hybrid KEM+AEAD: one shared content ciphertext (nonce/ct/tag) plus
    per-recipient headers (wrapped CEK). Implementations may also support a
    sealed-style variant by setting an algorithm (e.g., "OpenPGP-SEAL" or
    "X25519-SEALEDBOX") and returning empty shared fields with per-recipient
    ciphertexts in RecipientInfo.wrapped_key.
- seal/unseal (NEW):
    Direct public-key encryption to a recipient's public key without caller-
    managed DEKs (e.g., OpenPGP message encryption, NaCl sealed box, RSA-OAEP
    of *plaintext*). No AAD is required or guaranteed by the primitive.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

from .types import (
    AEADCiphertext,
    Alg,
    KeyRef,
    MultiRecipientEnvelope,
    Signature,
    WrappedKey,
)


class ICrypto(ABC):
    @abstractmethod
    def supports(self) -> Dict[str, Iterable[Alg]]:
        """
        Returns capability map:
          {
            "encrypt": (algs...),
            "decrypt": (algs...),
            "wrap": (algs...),
            "unwrap": (algs...),
            "sign": (algs...),
            "verify": (algs...),
            "seal": (algs...),      # NEW (optional per provider)
            "unseal": (algs...),    # NEW (optional per provider)
            "for_many": (algs...),  # if you expose a distinct key (optional)
          }
        Implementations MAY omit keys they do not support.
        """
        ...

    # ────────────────────────── symmetric AEAD ──────────────────────────

    @abstractmethod
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        ...

    @abstractmethod
    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        ...

    # ───────────────────────── signing / verify ─────────────────────────

    @abstractmethod
    async def sign(
        self,
        key: KeyRef,
        msg: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> Signature:
        ...

    @abstractmethod
    async def verify(
        self,
        key: KeyRef,
        msg: bytes,
        sig: Signature,
    ) -> bool:
        ...

    # ───────────────────────── wrap / unwrap keys ───────────────────────

    @abstractmethod
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> WrappedKey:
        ...

    @abstractmethod
    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        ...

    # ───────────────── hybrid encrypt-for-many (KEM+AEAD or sealed) ─────

    @abstractmethod
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
        """
        KEM+AEAD mode:
          - Encrypt 'pt' once with a fresh CEK → (nonce, ct, tag)
          - For each recipient, wrap the CEK and emit RecipientInfo entries.

        Sealed-style mode (optional, algorithm-specific, e.g., "OpenPGP-SEAL",
        "X25519-SEALEDBOX"):
          - Produce per-recipient ciphertexts directly in RecipientInfo.wrapped_key
          - Return empty shared fields: nonce=b"", ct=b"", tag=b""
          - 'aad' is ignored unless the implementation explicitly binds it via
            an outer AEAD.
        """
        ...

    # ───────────────────────────── seal / unseal ────────────────────────
    # NEW: explicit sealed-box style single-recipient APIs

    @abstractmethod
    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        """
        Public-key encrypt 'pt' for 'recipient' using a sealing algorithm.
        Example algs: "OpenPGP-SEAL", "X25519-SEALEDBOX", "RSA-OAEP-SHA256-SEAL".
        Returns the sealed ciphertext bytes.
        """
        ...

    @abstractmethod
    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        """
        Decrypt a sealed ciphertext previously produced by 'seal'.
        'recipient_priv' must carry the private key material required by 'alg'.
        Returns the recovered plaintext bytes.
        """
        ...
