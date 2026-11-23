from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping

from .types import PoPKind


class IPoPSigner(ABC):
    """Creates a proof-of-possession artefact for an HTTP request."""

    @property
    @abstractmethod
    def kind(self) -> PoPKind: ...

    @abstractmethod
    def header_name(self) -> str: ...

    @abstractmethod
    def sign_request(
        self,
        method: str,
        url: str,
        *,
        kid: bytes | None = None,
        jti: str | None = None,
        ath_b64u: str | None = None,
        extra_claims: Mapping[str, object] | None = None,
    ) -> str: ...
