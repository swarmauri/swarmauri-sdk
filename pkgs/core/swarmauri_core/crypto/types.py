"""Shared types for cryptography and secrets interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

KeyId = str
KeyVersion = int
Alg = str


class KeyType(str, Enum):
    SYMMETRIC = "symmetric"
    RSA = "rsa"
    EC = "ec"
    ED25519 = "ed25519"
    X25519 = "x25519"
    OPAQUE = "opaque"


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
    NONE = "none"
    PUBLIC_ONLY = "public_only"
    SECRET_WHEN_ALLOWED = "secret_when_allowed"


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
    created_at: float
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


@dataclass(frozen=True)
class KeyRef:
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
    kek_kid: KeyId
    kek_version: KeyVersion
    wrap_alg: Alg
    nonce: Optional[bytes]
    wrapped: bytes


@dataclass(frozen=True)
class RecipientInfo:
    kid: KeyId
    version: KeyVersion
    wrap_alg: Alg
    wrapped_key: bytes
    nonce: Optional[bytes] = None


@dataclass(frozen=True)
class MultiRecipientEnvelope:
    enc_alg: Alg
    nonce: bytes
    ct: bytes
    tag: bytes
    recipients: Tuple[RecipientInfo, ...]
    aad: Optional[bytes] = None


class KmsError(Exception):
    pass


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
