from __future__ import annotations

from typing import Literal

from pydantic import Field
from swarmauri_core.auth_idp.IOAuth21AppClient import IOAuth21AppClient

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class OAuth21AppClientBase(IOAuth21AppClient, ComponentBase):
    """Base class for OAuth 2.1 machine-to-machine token clients."""

    resource: str | None = Field(
        default=ResourceTypes.OAuth21AppClient.value, frozen=True
    )
    type: Literal["OAuth21AppClientBase"] = "OAuth21AppClientBase"

    async def access_token(self, scope: str | None = None) -> str:
        raise NotImplementedError(
            "access_token must be implemented by subclasses"
        )
