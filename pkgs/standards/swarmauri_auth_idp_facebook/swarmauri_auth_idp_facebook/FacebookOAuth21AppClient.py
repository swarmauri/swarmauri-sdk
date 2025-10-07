"""Facebook OAuth 2.1 client-credentials helper."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import ConfigDict, Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21AppClientBase

from .FacebookOAuth20AppClient import FacebookOAuth20AppClient


@ComponentBase.register_type(OAuth21AppClientBase, "FacebookOAuth21AppClient")
class FacebookOAuth21AppClient(OAuth21AppClientBase):
    """Reuse the OAuth 2.0 client credentials flow for OAuth 2.1 semantics."""

    model_config = ConfigDict(extra="forbid")

    graph_base: str = Field(default="https://graph.facebook.com")
    version: str = Field(default="v19.0")
    client_id: str
    client_secret: SecretStr

    type: Literal["FacebookOAuth21AppClient"] = "FacebookOAuth21AppClient"

    async def access_token(self, scope: Optional[str] = None) -> str:
        client = FacebookOAuth20AppClient(
            graph_base=self.graph_base,
            version=self.version,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        return await client.access_token(scope=scope)


__all__ = ["FacebookOAuth21AppClient"]
