from __future__ import annotations

from typing import Optional, Literal
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.keys.IKeyProvider import IKeyProvider


class KeyProviderBase(IKeyProvider, ComponentBase):
    """Base class for key providers within the Swarmauri ecosystem."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["KeyProviderBase"] = "KeyProviderBase"
