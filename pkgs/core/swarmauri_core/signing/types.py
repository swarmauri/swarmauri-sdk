from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Mapping as TypingMapping, Optional

# Local scalar aliases to avoid circular imports
KeyId = str
KeyVersion = int
Alg = str


@dataclass(frozen=True)
class Signature(Mapping[str, object]):
    """Universal signature record supporting attached and detached modes."""

    kid: Optional[KeyId]
    version: Optional[KeyVersion]
    format: str
    mode: str
    alg: Alg
    artifact: bytes
    hash_alg: Optional[str] = None
    cert_chain_der: Optional[Sequence[bytes]] = None
    headers: Optional[TypingMapping[str, Any]] = None
    meta: Optional[TypingMapping[str, Any]] = None
    ts: Optional[float] = None
    sig: Optional[bytes] = field(default=None, repr=False)
    chain: Optional[object] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.sig is None and self.mode == "detached":
            object.__setattr__(self, "sig", self.artifact)
        if self.chain is None and self.cert_chain_der:
            chain_value: object
            if len(self.cert_chain_der) == 1:
                chain_value = self.cert_chain_der[0]
            else:
                chain_value = tuple(self.cert_chain_der)
            object.__setattr__(self, "chain", chain_value)

    def __getitem__(self, k: str) -> object:  # type: ignore[override]
        return getattr(self, k)

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        return iter(
            (
                "kid",
                "version",
                "format",
                "mode",
                "alg",
                "artifact",
                "hash_alg",
                "cert_chain_der",
                "headers",
                "meta",
                "ts",
                "sig",
                "chain",
            )
        )

    def __len__(self) -> int:  # type: ignore[override]
        return 13


__all__ = ["Signature", "KeyId", "KeyVersion", "Alg"]
