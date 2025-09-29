"""Component base for proof-of-possession signers."""

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

from .PopSignerMixin import PopSignerMixin


@ComponentBase.register_model()
class PopSigningBase(PopSignerMixin, ComponentBase):
    """Component-backed base for PoP signers."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: str = "PopSigningBase"
    model_config = ConfigDict(arbitrary_types_allowed=True)
