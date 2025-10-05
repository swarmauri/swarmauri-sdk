from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional, Sequence

from .types import (
    Alg,
    CipherOp,
    Features,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)


class ICipherSuite(ABC):
    """Resolution and policy contract for cipher suite descriptors."""

    @abstractmethod
    def suite_id(self) -> str:
        """Return the stable identifier for the suite."""

    @abstractmethod
    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        """Return the allow-list of algorithms grouped by operation."""

    @abstractmethod
    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        """Return the default algorithm for ``op`` under the current policy."""

    @abstractmethod
    def normalize(
        self,
        *,
        op: CipherOp,
        alg: Optional[Alg] = None,
        key: Optional[KeyRef] = None,
        params: Optional[ParamMapping] = None,
        dialect: Optional[str] = None,
    ) -> NormalizedDescriptor:
        """Return a normalized descriptor for the requested operation."""

    @abstractmethod
    def policy(self) -> Mapping[str, Any]:
        """Return the effective policy toggles for the suite."""

    @abstractmethod
    def features(self) -> Features:
        """Return descriptive metadata describing the suite capabilities."""

    def lint(self) -> Sequence[str]:
        """Return linter warnings about misconfiguration or policy conflicts."""

        issues: list[str] = []
        supported = self.supports()
        for op, allowed in supported.items():
            try:
                default = self.default_alg(op)
            except Exception as exc:  # pragma: no cover - defensive path
                issues.append(f"default_alg({op}) raised: {exc!r}")
                continue

            if default not in set(allowed):
                issues.append(
                    f"default_alg({op})={default} not in supports()[{op}]",
                )
        return issues
