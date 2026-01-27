"""GitLab OpenID Connect 1.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10LoginBase

from .GitLabOIDCLoginMixin import GitLabOIDCLoginMixin


@ComponentBase.register_type(OIDC10LoginBase, "GitLabOIDC10Login")
class GitLabOIDC10Login(GitLabOIDCLoginMixin, OIDC10LoginBase):
    """Implement OIDC 1.0 Authorization Code with PKCE for GitLab."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        result = await self._exchange_tokens(code, state)
        tokens = result["tokens"]
        claims = result["claims"]
        return {
            "issuer": "gitlab-oidc",
            "sub": claims["sub"],
            "email": claims.get("email"),
            "name": claims.get("name") or claims.get("preferred_username"),
            "raw": {"tokens": tokens, "claims": claims},
        }
