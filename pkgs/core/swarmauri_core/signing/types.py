from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Iterator
from typing import Optional, Dict, Any

# Local scalar aliases to avoid circular imports
KeyId = str
KeyVersion = int
Alg = str


@dataclass(frozen=True)
class Signature(Mapping[str, object]):
    """Simple signature record used by signing providers."""

    kid: KeyId
    version: KeyVersion
    alg: Alg
    sig: bytes
    ts: Optional[int] = None
    chain: Optional[bytes] = None
    meta: Optional[Dict[str, Any]] = None

    def __getitem__(self, k: str) -> object:  # type: ignore[override]
        return getattr(self, k)

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        return iter(
            (
                "kid",
                "version",
                "alg",
                "sig",
                "ts",
                "chain",
                "meta",
            )
        )

    def __len__(self) -> int:  # type: ignore[override]
        return 7


__all__ = ["Signature", "KeyId", "KeyVersion", "Alg"]
