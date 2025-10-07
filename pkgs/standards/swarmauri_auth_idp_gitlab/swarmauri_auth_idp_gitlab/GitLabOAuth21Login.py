"""GitLab OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .GitLabOIDCLoginMixin import GitLabOIDCLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "GitLabOAuth21Login")
class GitLabOAuth21Login(GitLabOIDCLoginMixin, OAuth21LoginBase):
    """Implement the GitLab OAuth 2.1 Authorization Code flow via OIDC discovery."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        result = await self._exchange_tokens(code, state)
        tokens = result["tokens"]
        claims = result["claims"]
        return {
            "issuer": "gitlab-oauth21",
            "sub": claims["sub"],
            "email": claims.get("email"),
            "name": claims.get("name") or claims.get("preferred_username"),
            "raw": {"tokens": tokens, "claims": claims},
        }
