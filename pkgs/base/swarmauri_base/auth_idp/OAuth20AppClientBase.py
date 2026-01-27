from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.auth_idp.IOAuth20AppClient import IOAuth20AppClient


class OAuth20AppClientBase(IOAuth20AppClient, ComponentBase):
    """Base class for OAuth 2.0 machine-to-machine token clients."""

    resource: Optional[str] = Field(
        default=ResourceTypes.OAuth20AppClient.value, frozen=True
    )
    type: Literal["OAuth20AppClientBase"] = "OAuth20AppClientBase"

    async def access_token(self, scope: Optional[str] = None) -> str:
        raise NotImplementedError("access_token must be implemented by subclasses")
