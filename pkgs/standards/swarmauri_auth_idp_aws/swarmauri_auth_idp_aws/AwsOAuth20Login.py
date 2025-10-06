"""AWS Workforce OAuth 2.0 Authorization Code login."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from swarmauri_base.auth_idp import OAuth20LoginBase

from .AwsLoginMixin import AwsLoginMixin


class AwsOAuth20Login(AwsLoginMixin, OAuth20LoginBase):
    """Implement the AWS IAM Identity Center Workforce OAuth 2.0 flow."""

    type: Literal["AwsOAuth20Login"] = "AwsOAuth20Login"

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        return {"issuer": "aws-workforce", "tokens": tokens}
