"""Base class for cryptography plugins."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class CryptoBase(ICrypto, ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["CryptoBase"] = "CryptoBase"
