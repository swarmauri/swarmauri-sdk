"""Pydantic-enabled base class for cipher suite implementations."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

from pydantic import Field

from swarmauri_core.cipher_suites import ICipherSuite
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class CipherSuiteBase(ICipherSuite, ComponentBase):
    """Default NotImplemented stubs mirroring other Swarmauri base classes."""

    resource: str = Field(default=ResourceTypes.CIPHER_SUITE.value, frozen=True)
    type: str = "CipherSuiteBase"

    def suite_id(self) -> str:
        raise NotImplementedError

    def supports(self) -> Mapping[str, Iterable[Alg]]:
        raise NotImplementedError

    def normalize(
        self,
        *,
        op: str,
        alg: Optional[Alg] = None,
        key: Optional[KeyRef] = None,
        params: Optional[Mapping[str, object]] = None,
        dialect: Optional[str] = None,
    ) -> Mapping[str, object]:
        raise NotImplementedError

    def default_alg(self, op: str, *, for_key: Optional[KeyRef] = None) -> Alg:
        raise NotImplementedError

    def policy(self) -> Mapping[str, object]:
        return {}
