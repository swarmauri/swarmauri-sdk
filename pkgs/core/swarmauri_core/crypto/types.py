# swarmauri_core/crypto/types.py
"""
Canonical crypto/secret shared types.

This module aligns with the new ICrypto plugin interface:
- Enums: KeyType, KeyUse, KeyState, ExportPolicy
- Core records: KeySummary, KeyVersionInfo, KeyDescriptor, Page
- Operation IO: KeyRef, AEADCiphertext, WrappedKey
- Error taxonomy: KmsError and specific subclasses

Notes:
- Dataclasses are frozen (immutable-by-default).
- AEAD nonces/tags are bytes; we do minimal structural validation.
- Back-compat aliases preserved for gradual migration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple, Mapping, TYPE_CHECKING
import hashlib

from ..mre_crypto.types import RecipientInfo, MultiRecipientEnvelope

# -----------------------------
# Scalar aliases
# -----------------------------

KeyId = str
KeyVersion = int
Alg = str

if TYPE_CHECKING:  # pragma: no cover - typing aid
    from ..signing.types import Signature
else:  # pragma: no cover - runtime placeholder
    Signature = Mapping[str, object]


# -----------------------------
# Enums
# -----------------------------


class JWAAlg(str, Enum):
    """Registered JWA algorithm names from RFC 7518."""

    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"
    ES256K = "ES256K"
    EDDSA = "EdDSA"
    RSA_OAEP = "RSA-OAEP"
    RSA_OAEP_256 = "RSA-OAEP-256"
    ECDH_ES = "ECDH-ES"
    DIR = "dir"
    A128GCM = "A128GCM"
    A192GCM = "A192GCM"
    A256GCM = "A256GCM"


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
    ENCAPS = "encaps"
    DECAPS = "decaps"


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
    material: Optional[bytes | str] = None
    public: Optional[bytes | str] = None
    tags: Dict[str, str] | None = None
    fingerprint: Optional[str] = None

    def __post_init__(self) -> None:
        if self.fingerprint is None:
            data = self.public or self.material or self.kid.encode("utf-8")
            if isinstance(data, str):
                data = data.encode("utf-8")
            object.__setattr__(self, "fingerprint", hashlib.sha256(data).hexdigest())


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
class WrappedKey:
    """
    Result of wrapping a DEK with a KEK.
    - wrap_alg: e.g., "AES-KW" / "AES-KWP" / "RSA-OAEP"
    - nonce: optional for schemes that use IVs (not AES-KW)
    - tag: optional authentication tag for AEAD-based wrapping
    """

    kek_kid: KeyId
    kek_version: KeyVersion
    wrap_alg: Alg
    wrapped: bytes
    nonce: Optional[bytes] = None
    tag: Optional[bytes] = None


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
Ciphertext = AEADCiphertext  # old -> new
WrapResult = WrappedKey  # old -> new
MultiRecipient = MultiRecipientEnvelope  # old -> new


__all__ = [
    # scalars
    "KeyId",
    "KeyVersion",
    "Alg",
    # enums
    "JWAAlg",
    "KeyType",
    "KeyUse",
    "KeyState",
    "ExportPolicy",
    # key inventory
    "KeySummary",
    "KeyVersionInfo",
    "KeyDescriptor",
    "Page",
    # core refs & payloads
    "KeyRef",
    "AEADCiphertext",
    "Signature",
    "WrappedKey",
    "RecipientInfo",
    "MultiRecipientEnvelope",
    # errors
    "KmsError",
    "NotFound",
    "Disabled",
    "PermissionDenied",
    "UnsupportedAlgorithm",
    "InvalidState",
    "IntegrityError",
    # helpers
    "validate_aes_gcm_nonce",
    "validate_nonempty",
    # back-compat
    "Ciphertext",
    "WrapResult",
    "MultiRecipient",
]
