from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class KeyAlg(str, Enum):
    """Enumeration of key algorithms supported by token services."""

    RSA_PSS_SHA256 = "RSA-PSS-SHA256"
    ECDSA_P256_SHA256 = "ECDSA-P256-SHA256"
    ED25519 = "ED25519"
    HMAC_SHA256 = "HMAC-SHA256"


@dataclass
class KeyRef:
    """Reference to a cryptographic key."""

    kid: str
    version: int
    material: Optional[bytes]
