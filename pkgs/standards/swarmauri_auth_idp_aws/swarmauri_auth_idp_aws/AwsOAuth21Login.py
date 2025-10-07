"""AWS IAM Identity Center OAuth 2.1 Authorization Code login."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from swarmauri_base.auth_idp import OAuth21LoginBase

from .AwsLoginMixin import AwsLoginMixin, make_pkce_pair, sign_state


class AwsOAuth21Login(AwsLoginMixin, OAuth21LoginBase):
    """Implement the AWS IAM Identity Center OAuth 2.1 flow."""

    type: Literal["AwsOAuth21Login"] = "AwsOAuth21Login"

    async def auth_url(self) -> Mapping[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret(), {"verifier": verifier})
        url = (
            f"{self.authorization_endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256&prompt=consent"
        )
        return {"url": url, "state": state}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        return {"issuer": "aws-workforce", "tokens": tokens}
