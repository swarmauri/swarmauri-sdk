"""Abstract cipher suite contract for algorithm normalization and policy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Optional

from swarmauri_core.crypto.types import Alg, KeyRef

ParamMapping = Mapping[str, object]


class ICipherSuite(ABC):
    """Translate cryptographic operations into normalized descriptors.

    Cipher suites are responsible for:
    - Declaring algorithm support across the common crypto/signing operations.
    - Normalizing identifiers for different dialects (JWA, COSE, provider-specific).
    - Enforcing policy such as key length, allowed curves, or algorithm allow-lists.
    - Providing defaults for operations when the caller omits an explicit algorithm.
    """

    @abstractmethod
    def suite_id(self) -> str:
        """Return a stable identifier for the suite (e.g. ``"jwa"``)."""

    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[Alg]]:
        """Return supported algorithms grouped by operation."""

    @abstractmethod
    def normalize(
        self,
        *,
        op: str,
        alg: Optional[Alg] = None,
        key: Optional[KeyRef] = None,
        params: Optional[ParamMapping] = None,
        dialect: Optional[str] = None,
    ) -> Mapping[str, object]:
        """Produce a normalized descriptor for an operation.

        Implementations should raise :class:`ValueError` when the requested
        operation, algorithm, or parameters are not supported under the suite's
        policy.
        """

    @abstractmethod
    def default_alg(self, op: str, *, for_key: Optional[KeyRef] = None) -> Alg:
        """Return the default algorithm for ``op`` optionally scoped to ``for_key``."""

    @abstractmethod
    def policy(self) -> Mapping[str, object]:
        """Return policy metadata describing enforcement rules for the suite."""
