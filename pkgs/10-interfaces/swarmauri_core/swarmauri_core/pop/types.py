from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, Flag, auto
from typing import Mapping


class PoPKind(str, Enum):
    """Supported proof-of-possession scheme identifiers."""

    JWT_DPoP = "jwtpop"
    CWT = "cwtpop"
    X509 = "x509pop"


class BindType(str, Enum):
    """Confirmation thumbprint binding type."""

    JKT = "jkt"
    X5T_S256 = "x5t#S256"
    COSE_THUMB = "cose_thumb"


class Feature(Flag):
    """Feature flags advertised by a verifier implementation."""

    NONE = 0
    NONCE = auto()
    REPLAY = auto()
    ATH = auto()
    MTLS = auto()


@dataclass(frozen=True)
class HttpParts:
    """Normalized HTTP request attributes used for PoP verification."""

    method: str
    url: str
    headers: Mapping[str, str]


@dataclass(frozen=True)
class CnfBinding:
    """Confirmation binding requirement expressed by the access token."""

    bind_type: BindType
    value_b64u: str
