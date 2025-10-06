from __future__ import annotations

from typing import Any, Literal, Mapping, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.auth_idp.IOIDC10Login import IOIDC10Login


class OIDC10LoginBase(IOIDC10Login, ComponentBase):
    """Base class for OpenID Connect 1.0 user login flows."""

    resource: Optional[str] = Field(
        default=ResourceTypes.OIDC10Login.value, frozen=True
    )
    type: Literal["OIDC10LoginBase"] = "OIDC10LoginBase"

    async def auth_url(self) -> Mapping[str, str]:
        raise NotImplementedError("auth_url must be implemented by subclasses")

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        raise NotImplementedError("exchange must be implemented by subclasses")
