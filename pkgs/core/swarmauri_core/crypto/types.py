# swarmauri_core/crypto/types.py
"""
Canonical crypto/secret shared types.

This module aligns with the new ICrypto plugin interface:
- Enums: KeyType, KeyUse, KeyState, ExportPolicy
- Core records: KeySummary, KeyVersionInfo, KeyDescriptor, Page
- Operation IO: KeyRef, AEADCiphertext, Signature, WrappedKey,
                RecipientInfo, MultiRecipientEnvelope
- Error taxonomy: KmsError and specific subclasses

Notes:
- Dataclasses are frozen (immutable-by-default).
- AEAD nonces/tags are bytes; we do minimal structural validation.
- Back-compat aliases preserved for gradual migration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple, Iterable

# -----------------------------
# Scalar aliases
# -----------------------------

KeyId = str
KeyVersion = int
Alg = str


# -----------------------------
# Enums
# -----------------------------

class KeyType(str, Enum):
    SYMMETRIC = "symmetric"
    RSA = "rsa"
    EC = "ec"
    ED25519 = "ed25519"
    X25519 = "x25519"
    OPAQUE = "opaque"  # e.g., HSM handle only / non-extractable materials


class KeyUse(str, Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    WRAP = "wrap"
    UNWRAP = "unwrap"


class KeyState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    DESTROYED = "destroyed"


class ExportPolicy(str, Enum):
    NONE = "none"  # never export
    PUBLIC_ONLY = "public_only"  # export public/verification material
    SECRET_WHEN_ALLOWED = "secret_when_allowed"  # secret export gated by policy


# -----------------------------
# Key inventory & descriptors
# -----------------------------

@dataclass(frozen=True)
class KeySummary:
    kid: KeyId
    name: Optional[str]
    type: KeyType
    state: KeyState
    primary_version: KeyVersion
    uses: Tuple[KeyUse, ...]
    tags: Dict[str, str]


@dataclass(frozen=True)
class KeyVersionInfo:
    version: KeyVersion
    created_at: float  # epoch seconds
    state: KeyState
    thumbprint: Optional[str] = None


@dataclass(frozen=True)
class KeyDescriptor:
    kid: KeyId
    name: Optional[str]
    type: KeyType
    state: KeyState
    primary_version: KeyVersion
    uses: Tuple[KeyUse, ...]
    export_policy: ExportPolicy
    tags: Dict[str, str]
    versions: Tuple[KeyVersionInfo, ...]


@dataclass(frozen=True)
class Page:
    items: Tuple[KeySummary, ...]
    next_cursor: Optional[str] = None


# -----------------------------
# References & payload shapes
# -----------------------------

@dataclass(frozen=True)
class KeyRef:
    """
    General reference to a specific key version.
    - For software keys, 'material' and 'public' may carry raw bytes.
    - For HSM/non-extractable, leave 'material' None and use 'uri' and 'tags'
      to locate handles (slot, label, object id, etc).
    """
    kid: KeyId
    version: KeyVersion
    type: KeyType
    uses: Tuple[KeyUse, ...]
    export_policy: ExportPolicy
    uri: Optional[str] = None
    material: Optional[bytes] = None
    public: Optional[bytes] = None
    tags: Dict[str, str] | None = None


@dataclass(frozen=True)
class AEADCiphertext:
    """
    AEAD result with associated key identity.
    - alg: e.g., "AES-GCM"
    - nonce: MUST be correct size for 'alg' (e.g., 12 bytes for AES-GCM)
    - tag: For some libs (cryptography.AESGCM) tag is appended to ct; we still
      carry a 'tag' field to standardize shape. Set to b"" when not distinct.
    """
    kid: KeyId
    version: KeyVersion
    alg: Alg
    nonce: bytes
    ct: bytes
    tag: bytes
    aad: Optional[bytes] = None


@dataclass(frozen=True)
class Signature:
    kid: KeyId
    version: KeyVersion
    alg: Alg
    sig: bytes


@dataclass(frozen=True)
class WrappedKey:
    """
    Result of wrapping a DEK with a KEK.
    - wrap_alg: e.g., "AES-KW" / "AES-KWP" / "RSA-OAEP"
    - nonce: optional for schemes that use IVs (not AES-KW)
    """
    kek_kid: KeyId
    kek_version: KeyVersion
    wrap_alg: Alg
    wrapped: bytes
    nonce: Optional[bytes] = None


@dataclass(frozen=True)
class RecipientInfo:
    """
    Per-recipient header for multi-recipient envelopes.
    - wrap_alg: how the per-recipient material was produced (e.g., "X25519-SEALEDBOX",
                "RSA-OAEP", "UMBRAL-PRE")
    - wrapped_key: For sealed box, this MAY be the ciphertext directly if you
                   encode per-recipient; for KEM+AEAD schemes it's the CEK wrap.
    - nonce: optional per-recipient nonce (rare in sealed boxes)
    """
    kid: KeyId
    version: KeyVersion
    wrap_alg: Alg
    wrapped_key: bytes
    nonce: Optional[bytes] = None


@dataclass(frozen=True)
class MultiRecipientEnvelope:
    """
    A compact, transport-friendly container:
      - enc_alg: content encryption algorithm (e.g., "X25519-SEALEDBOX" or "AES-GCM")
      - (nonce, ct, tag): the common content ciphertext (or empty when the content
        is distributed per-recipient and not shared)
      - recipients: tuple of per-recipient infos
      - aad: optional associated data bound to the envelope (if supported by enc_alg)
    """
    enc_alg: Alg
    nonce: bytes
    ct: bytes
    tag: bytes
    recipients: Tuple[RecipientInfo, ...]
    aad: Optional[bytes] = None


# -----------------------------
# Errors
# -----------------------------

class KmsError(Exception):
    """Base class for KMS/crypto errors."""


class NotFound(KmsError):
    pass


class Disabled(KmsError):
    pass


class PermissionDenied(KmsError):
    pass


class UnsupportedAlgorithm(KmsError):
    pass


class InvalidState(KmsError):
    pass


class IntegrityError(KmsError):
    pass


# -----------------------------
# Minimal validators/helpers
# -----------------------------

def validate_aes_gcm_nonce(nonce: bytes) -> None:
    if len(nonce) != 12:
        raise IntegrityError("AES-GCM nonce must be 12 bytes")

def validate_nonempty(b: bytes, name: str) -> None:
    if not isinstance(b, (bytes, bytearray)) or len(b) == 0:
        raise IntegrityError(f"{name} must be non-empty bytes")


# -----------------------------
# Back-compat aliases (soft)
# -----------------------------
# If older code imported these names, keep them pointing to the new classes.
Ciphertext = AEADCiphertext              # old -> new
WrapResult = WrappedKey                  # old -> new
MultiRecipient = MultiRecipientEnvelope  # old -> new


__all__ = [
    # scalars
    "KeyId", "KeyVersion", "Alg",
    # enums
    "KeyType", "KeyUse", "KeyState", "ExportPolicy",
    # key inventory
    "KeySummary", "KeyVersionInfo", "KeyDescriptor", "Page",
    # core refs & payloads
    "KeyRef", "AEADCiphertext", "Signature", "WrappedKey",
    "RecipientInfo", "MultiRecipientEnvelope",
    # errors
    "KmsError", "NotFound", "Disabled", "PermissionDenied",
    "UnsupportedAlgorithm", "InvalidState", "IntegrityError",
    # helpers
    "validate_aes_gcm_nonce", "validate_nonempty",
    # back-compat
    "Ciphertext", "WrapResult", "MultiRecipient",
]
