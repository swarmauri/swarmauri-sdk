from __future__ import annotations

from typing import Any, Literal, Mapping, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.auth_idp.IOAuth21Login import IOAuth21Login


class OAuth21LoginBase(IOAuth21Login, ComponentBase):
    """Base class for OAuth 2.1 user login flows."""

    resource: Optional[str] = Field(
        default=ResourceTypes.OAuth21Login.value, frozen=True
    )
    type: Literal["OAuth21LoginBase"] = "OAuth21LoginBase"

    async def auth_url(self) -> Mapping[str, str]:
        raise NotImplementedError("auth_url must be implemented by subclasses")

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        raise NotImplementedError(
            "exchange_and_identity must be implemented by subclasses"
        )
