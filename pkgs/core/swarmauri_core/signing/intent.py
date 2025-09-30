"""Intent specifications for signing and verification operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional

try:  # pragma: no cover - typing upgrade path
    from typing import Literal
except ImportError:  # pragma: no cover - Python <3.8 fallback (not expected)
    Literal = str  # type: ignore[misc,assignment]


Mode = Literal["detached", "attached"]
Format = Literal["jws", "cms", "openpgp", "pades"]


@dataclass(frozen=True)
class SignIntent:
    """Description of how a payload should be signed."""

    format: Format
    mode: Mode
    alg: str
    key_ref: Optional[str] = None
    key_id: Optional[str] = None
    hash_alg: str = "sha256"
    options: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class VerifyIntent:
    """Description of how a payload or artifact should be verified."""

    format: Format
    mode: Mode
    options: Mapping[str, object] = field(default_factory=dict)


__all__ = ["SignIntent", "VerifyIntent", "Mode", "Format"]
