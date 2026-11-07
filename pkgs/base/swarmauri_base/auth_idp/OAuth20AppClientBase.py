from __future__ import annotations

from typing import Literal

from pydantic import Field
from swarmauri_core.auth_idp.IOAuth20AppClient import IOAuth20AppClient

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class OAuth20AppClientBase(IOAuth20AppClient, ComponentBase):
    """Base class for OAuth 2.0 machine-to-machine token clients."""

    resource: str | None = Field(
        default=ResourceTypes.OAuth20AppClient.value, frozen=True
    )
    type: Literal["OAuth20AppClientBase"] = "OAuth20AppClientBase"

    async def access_token(self, scope: str | None = None) -> str:
        raise NotImplementedError(
            "access_token must be implemented by subclasses"
        )
