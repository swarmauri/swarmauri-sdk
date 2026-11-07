from __future__ import annotations

from typing import Literal

from pydantic import Field
from swarmauri_core.auth_idp.IOIDC10AppClient import IOIDC10AppClient

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class OIDC10AppClientBase(IOIDC10AppClient, ComponentBase):
    """Base class for OpenID Connect 1.0 machine-to-machine token clients."""

    resource: str | None = Field(
        default=ResourceTypes.OIDC10AppClient.value, frozen=True
    )
    type: Literal["OIDC10AppClientBase"] = "OIDC10AppClientBase"

    async def access_token(self, scope: str | None = None) -> str:
        raise NotImplementedError(
            "access_token must be implemented by subclasses"
        )
