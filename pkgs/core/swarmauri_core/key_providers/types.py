"""Key specification and related enums for key providers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..crypto.types import ExportPolicy, KeyUse


class KeyClass(str, Enum):
    """Key classification."""

    symmetric = "sym"
    asymmetric = "asym"
    opaque = "opaque"


class KeyAlg(str, Enum):
    """Supported key algorithms."""

    AES256_GCM = "AES256_GCM"
    ED25519 = "ED25519"
    X25519 = "X25519"
    HMAC_SHA256 = "HMAC_SHA256"
    RSA_OAEP_SHA256 = "RSA_OAEP_SHA256"
    RSA_PSS_SHA256 = "RSA_PSS_SHA256"
    ECDSA_P256_SHA256 = "ECDSA_P256_SHA256"


@dataclass(frozen=True)
class KeySpec:
    """Parameters for key creation or import."""

    klass: KeyClass
    alg: KeyAlg
    uses: tuple[KeyUse, ...]
    export_policy: ExportPolicy
    encoding: str | None = None
    private_format: str | None = None
    public_format: str | None = None
    encryption: str | None = None
    size_bits: int | None = None
    label: str | None = None
    tags: dict[str, str] | None = None


__all__ = [
    "KeyClass",
    "KeyAlg",
    "KeySpec",
    "ExportPolicy",
    "KeyUse",
]
