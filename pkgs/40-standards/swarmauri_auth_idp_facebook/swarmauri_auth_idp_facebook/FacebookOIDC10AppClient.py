"""Facebook OIDC app client placeholder."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import ConfigDict
from swarmauri_base.auth_idp import OIDC10AppClientBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(OIDC10AppClientBase, "FacebookOIDC10AppClient")
class FacebookOIDC10AppClient(OIDC10AppClientBase):
    """Facebook does not support generic OIDC client credential grants."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["FacebookOIDC10AppClient"] = "FacebookOIDC10AppClient"

    async def access_token(self, scope: Optional[str] = None) -> str:
        raise NotImplementedError(
            "Facebook does not provide a client_credentials OIDC token flow"
        )


__all__ = ["FacebookOIDC10AppClient"]
