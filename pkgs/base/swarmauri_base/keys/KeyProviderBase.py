from __future__ import annotations

from typing import Optional, Literal
import hashlib
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.keys.IKeyProvider import IKeyProvider


class KeyProviderBase(IKeyProvider, ComponentBase):
    """Base class for key providers within the Swarmauri ecosystem."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["KeyProviderBase"] = "KeyProviderBase"

    def _fingerprint(
        self,
        *,
        public: bytes | None = None,
        material: bytes | None = None,
        kid: str | None = None,
    ) -> str:
        data = public or material or (kid.encode("utf-8") if kid else b"")
        return hashlib.sha256(data).hexdigest()
