from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any
from typing import Mapping as TypingMapping

# Local scalar aliases to avoid circular imports
KeyId = str
KeyVersion = int
Alg = str


@dataclass(frozen=True)
class Signature(Mapping[str, object]):
    """Universal signature record supporting attached and detached modes."""

    kid: KeyId | None
    version: KeyVersion | None
    format: str
    mode: str
    alg: Alg
    artifact: bytes
    hash_alg: str | None = None
    cert_chain_der: Sequence[bytes] | None = None
    headers: TypingMapping[str, Any] | None = None
    meta: TypingMapping[str, Any] | None = None
    ts: float | None = None
    sig: bytes | None = field(default=None, repr=False)
    chain: object | None = field(default=None, repr=False)

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
