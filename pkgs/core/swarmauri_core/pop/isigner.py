from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping, Optional

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
        kid: Optional[bytes] = None,
        jti: Optional[str] = None,
        ath_b64u: Optional[str] = None,
        extra_claims: Mapping[str, object] | None = None,
    ) -> str: ...
