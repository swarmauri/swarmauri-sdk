from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Protocol

from .types import BindType, CnfBinding, Feature, HttpParts, PoPKind


class ReplayHooks(Protocol):
    """Protocol for replay-detection storage hooks."""

    def seen(self, scope: str, key: str) -> bool: ...

    def mark(self, scope: str, key: str, ttl_s: int) -> None: ...


class KeyResolver(Protocol):
    """Protocol for resolving verification keys by kid or binding."""

    def by_kid(self, kid: bytes) -> object | None: ...

    def by_thumb(self, bind: CnfBinding) -> object | None: ...


@dataclass(frozen=True)
class VerifyPolicy:
    """Runtime policy controls applied during PoP verification."""

    alg_allow: Iterable[str] = ()
    max_skew_s: int = 300
    require_ath: bool = False
    require_bind: Optional[BindType] = None
    htu_exact: bool = False


class PoPError(Exception):
    """Base class for PoP verification errors."""


class PoPParseError(PoPError):
    """Raised when a proof artefact cannot be parsed."""


class PoPBindingError(PoPError):
    """Raised when proof confirmation data does not match the access token."""


class PoPVerificationError(PoPError):
    """Raised when a proof fails semantic or cryptographic checks."""


class IPoPVerifier(ABC):
    """Scheme-specific verifier for request-bound proof-of-possession artefacts."""

    @property
    @abstractmethod
    def kind(self) -> PoPKind: ...

    @abstractmethod
    def features(self) -> Feature: ...

    @abstractmethod
    def algs(self) -> Iterable[str]: ...

    @abstractmethod
    async def verify_http(
        self,
        req: HttpParts,
        cnf: CnfBinding,
        *,
        policy: VerifyPolicy = VerifyPolicy(),
        replay: ReplayHooks | None = None,
        keys: KeyResolver | None = None,
        extras: Mapping[str, object] | None = None,
    ) -> None: ...
