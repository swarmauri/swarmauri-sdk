"""Key specification and related enums for key providers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

from ..crypto.types import ExportPolicy, KeyUse


class KeyClass(str, Enum):
    """Key classification."""

    symmetric = "sym"
    asymmetric = "asym"


class KeyAlg(str, Enum):
    """Supported key algorithms."""

    AES256_GCM = "AES256_GCM"
    ED25519 = "ED25519"
    X25519 = "X25519"
    RSA_OAEP_SHA256 = "RSA_OAEP_SHA256"
    RSA_PSS_SHA256 = "RSA_PSS_SHA256"
    ECDSA_P256_SHA256 = "ECDSA_P256_SHA256"


@dataclass(frozen=True)
class KeySpec:
    """Parameters for key creation or import."""

    klass: KeyClass
    alg: KeyAlg
    uses: Tuple[KeyUse, ...]
    export_policy: ExportPolicy
    size_bits: Optional[int] = None
    label: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


__all__ = [
    "KeyClass",
    "KeyAlg",
    "KeySpec",
    "ExportPolicy",
    "KeyUse",
]