"""GitHub App installation client producing OAuth 2.1 compatible tokens."""

from __future__ import annotations

from typing import Optional

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21AppClientBase

from .GitHubAppClientMixin import GitHubAppClientMixin


@ComponentBase.register_type(OAuth21AppClientBase, "GitHubOAuth21AppClient")
class GitHubOAuth21AppClient(GitHubAppClientMixin, OAuth21AppClientBase):
    """Fetch GitHub App installation access tokens."""

    async def access_token(self, scope: Optional[str] = None) -> str:
        if scope:
            raise ValueError(
                "GitHub installation tokens do not support scope overrides"
            )
        return await self._cached_access_token()
