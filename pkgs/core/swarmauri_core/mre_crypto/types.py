"""Types for Multi-Recipient Encryption (MRE)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

# Local scalar aliases to avoid circular imports
KeyId = str
KeyVersion = int
Alg = str

RecipientId = str


class MreMode(str, Enum):
    ENC_ONCE_HEADERS = "enc_once_headers"
    SEALED_PER_RECIPIENT = "sealed_per_recipient"
    SEALED_CEK_AEAD = "sealed_cek_aead"


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


__all__ = [
    "RecipientInfo",
    "MultiRecipientEnvelope",
    "RecipientId",
    "MreMode",
    "KeyId",
    "KeyVersion",
    "Alg",
]
