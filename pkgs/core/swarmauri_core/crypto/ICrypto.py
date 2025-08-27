# swarmauri_core/crypto/ICrypto.py
"""
ICrypto: Single-recipient cryptography provider interface.

Scope
-----
- Symmetric AEAD over arbitrary plaintext using a DEK (encrypt/decrypt).
- Key wrap/unwrap of DEKs under KEKs (HSM/PKCS#11/OpenPGP/RSA-OAEP/etc).
- Public-key sealing/unsealing (sealed-box/PGP message/RSA-OAEP-seal).

Intentionally out of scope
--------------------------
- Multi-Recipient Encryption (MRE): use swarmauri_core.mre_crypto.IMreCrypto.
- Signing/verification (single or multi-signer): use signing plugins
  (e.g., swarmauri_core.signing.IEnvelopeSign).

Capability discovery
--------------------
Implementations advertise supported algorithms via ``supports()``, using
keys for any operation they handle.  Providers MAY separate advertise
algorithms by direction (e.g., ``encrypt`` vs ``decrypt``) when they only
support one side.

Example capability map::

  {
    "encrypt": ("AES-256-GCM", "XCHACHA20-POLY1305"),
    "decrypt": ("AES-256-GCM",),
    "wrap": ("AES-KW", "RSA-OAEP-SHA256", "OpenPGP"),
    "unwrap": ("AES-KW", "RSA-OAEP-SHA256", "OpenPGP"),
    "seal": ("OpenPGP-SEAL", "X25519-SEALEDBOX"),
    "unseal": ("OpenPGP-SEAL", "X25519-SEALEDBOX"),
  }

Notes
-----
- AEAD nonces must obey each algorithm's requirements (e.g., 12 bytes for AES-GCM).
- Providers MAY enforce ExportPolicy/KeyUse constraints carried in KeyRef.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

from .types import (
    AEADCiphertext,
    Alg,
    KeyRef,
    WrappedKey,
)


class ICrypto(ABC):
    @abstractmethod
    def supports(self) -> Dict[str, Iterable[Alg]]:
        """
        Return a capability map describing supported algorithms.

        Expected keys (all optional; omit if unsupported):
          - "encrypt" / "decrypt": AEAD algorithms for each direction
          - "wrap" / "unwrap": key-wrapping algorithms
          - "seal" / "unseal": sealed-box style algorithms

        Example::

            return {
                "encrypt": ("AES-256-GCM", "XCHACHA20-POLY1305"),
                "decrypt": ("AES-256-GCM",),
                "wrap": ("AES-KW", "RSA-OAEP-SHA256"),
                "unwrap": ("AES-KW", "RSA-OAEP-SHA256"),
                "seal": ("X25519-SEALEDBOX",),
                "unseal": ("X25519-SEALEDBOX",),
            }
        """
        ...

    # ────────────────────────── Symmetric AEAD ──────────────────────────

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
        """
        AEAD-encrypt 'pt' with the provided DEK 'key'.

        Parameters:
          key   : KeyRef for a data-encryption key (DEK) usable with 'alg'.
          pt    : plaintext bytes.
          alg   : AEAD algorithm identifier; if None, provider chooses a default.
          aad   : optional additional authenticated data; not encrypted, but bound.
          nonce : algorithm-specific nonce/IV; provider MAY generate if None.

        Returns:
          AEADCiphertext: (kid, version, alg, nonce, ct, tag[, aad])
        """
        ...

    @abstractmethod
    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        """
        AEAD-decrypt 'ct' with the DEK 'key'. If 'aad' is provided, it must
        match the value supplied during encryption.

        Raises on authentication failure.
        """
        ...

    # ─────────────────────────── Wrap / Unwrap ──────────────────────────

    @abstractmethod
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        """
        Protect a DEK under a KEK.

        Parameters:
          kek      : KeyRef for the key-encryption key (KEK).
          dek      : raw DEK bytes to wrap. If None, provider MAY generate a new DEK.
          wrap_alg : wrapping algorithm identifier; provider MAY default if None.
          nonce    : optional per-wrap nonce/IV (algorithm-specific).
          aad      : optional additional authenticated data bound to the wrap.

        Returns:
          WrappedKey: opaque blob + metadata to later recover the DEK.

        Notes:
          - Providers SHOULD honor ExportPolicy/KeyUse from both KEK and DEK KeyRefs.
          - Some HSM-backed providers may encode handles/labels rather than raw bytes.
        """
        ...

    @abstractmethod
    async def unwrap(
        self,
        kek: KeyRef,
        wrapped: WrappedKey,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        """
        Recover a DEK from 'wrapped' using KEK 'kek'.

        Parameters:
          aad : optional additional authenticated data to validate.

        Returns:
          bytes: the raw DEK.

        Notes:
          - HSM-backed providers may refuse export and instead return a handle;
            such providers SHOULD document their behavior or expose a separate
            decrypt() that accepts handles, not bytes.
        """
        ...

    # ─────────────────────────── Seal / Unseal ──────────────────────────

    @abstractmethod
    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        """
        Public-key 'sealed' encryption to 'recipient' without caller-managed DEKs.
        Example algs: "OpenPGP-SEAL", "X25519-SEALEDBOX", "RSA-OAEP-SHA256-SEAL".

        Returns:
          bytes: sealed ciphertext.

        Notes:
          - Sealed primitives typically do not bind external AAD. If you need
            authenticated metadata, prefer AEAD or wrap a CEK with AEAD outside.
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
        Decrypt 'sealed' bytes addressed to 'recipient_priv'.

        Returns:
          bytes: plaintext.

        Raises on authentication/decryption failure.
        """
        ...
