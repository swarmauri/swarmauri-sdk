from __future__ import annotations

from typing import Literal

from pydantic import Field
from swarmauri_core.tokens import ITokenService

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class TokenServiceBase(ITokenService, ComponentBase):
    """Base class for token services."""

    resource: str | None = Field(
        default=ResourceTypes.CRYPTO.value, frozen=True
    )
    type: Literal["TokenServiceBase"] = "TokenServiceBase"
