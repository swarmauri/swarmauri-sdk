from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional, Sequence

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.cipher_suites import (
    Alg,
    CipherOp,
    Features,
    ICipherSuite,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)


@ComponentBase.register_model()
class CipherSuiteBase(ICipherSuite, ComponentBase):
    """Pydantic-enabled convenience base for cipher suite implementations."""

    resource: str = Field(default=ResourceTypes.CIPHER_SUITE.value, frozen=True)
    type: str = "CipherSuiteBase"

    def suite_id(self) -> str:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def supports(
        self,
    ) -> Mapping[CipherOp, Iterable[Alg]]:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def default_alg(
        self, op: CipherOp, *, for_key: Optional[KeyRef] = None
    ) -> Alg:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def normalize(
        self,
        *,
        op: CipherOp,
        alg: Optional[Alg] = None,
        key: Optional[KeyRef] = None,
        params: Optional[ParamMapping] = None,
        dialect: Optional[str] = None,
    ) -> NormalizedDescriptor:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def policy(self) -> Mapping[str, Any]:
        """Return policy metadata describing enforcement rules for the suite."""

        return {}

    def features(self) -> Features:
        """Return baseline metadata describing the suite capabilities."""

        return {
            "suite": self.suite_id(),
            "version": 1,
            "ops": {},
            "dialects": {},
            "constraints": {},
            "compliance": {},
        }

    def lint(self) -> Sequence[str]:
        """Delegate to :class:`ICipherSuite` lint implementation."""

        return super().lint()
