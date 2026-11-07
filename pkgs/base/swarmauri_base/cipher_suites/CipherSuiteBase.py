from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from pydantic import Field
from swarmauri_core.cipher_suites import (
    Alg,
    CipherOp,
    Features,
    ICipherSuite,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class CipherSuiteBase(ICipherSuite, ComponentBase):
    """Pydantic-enabled convenience base for cipher suite implementations."""

    resource: str = Field(
        default=ResourceTypes.CIPHER_SUITE.value, frozen=True
    )
    type: str = "CipherSuiteBase"

    def suite_id(self) -> str:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def supports(
        self,
    ) -> Mapping[
        CipherOp, Iterable[Alg]
    ]:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def default_alg(
        self, op: CipherOp, *, for_key: KeyRef | None = None
    ) -> Alg:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def normalize(
        self,
        *,
        op: CipherOp,
        alg: Alg | None = None,
        key: KeyRef | None = None,
        params: ParamMapping | None = None,
        dialect: str | None = None,
    ) -> NormalizedDescriptor:  # pragma: no cover - abstract placeholder
        raise NotImplementedError

    def policy(self) -> Mapping[str, Any]:
        """
        Return policy metadata describing enforcement rules for the suite.
        """

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
