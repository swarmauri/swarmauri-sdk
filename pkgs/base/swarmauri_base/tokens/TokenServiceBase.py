from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.tokens import ITokenService


class TokenServiceBase(ITokenService, ComponentBase):
    """Base class for token services."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["TokenServiceBase"] = "TokenServiceBase"
