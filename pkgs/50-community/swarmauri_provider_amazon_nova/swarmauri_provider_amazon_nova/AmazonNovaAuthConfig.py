from collections.abc import Mapping
from typing import Literal

from pydantic import Field, SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderAuthBase, "AmazonNovaAuthConfig")
class AmazonNovaAuthConfig(ProviderAuthBase):
    access_key_id: SecretStr | None = Field(default=None, exclude=True)
    secret_access_key: SecretStr | None = Field(default=None, exclude=True)
    session_token: SecretStr | None = Field(default=None, exclude=True)
    profile: str | None = None
    type: Literal["AmazonNovaAuthConfig"] = "AmazonNovaAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        """Preserve headers; the AWS transport applies request-aware SigV4."""
        return dict(headers)

    def sdk_credentials(self) -> dict[str, str]:
        if (self.access_key_id is None) != (self.secret_access_key is None):
            raise ValueError(
                "AWS access_key_id and secret_access_key must be "
                "provided together"
            )
        if self.access_key_id is None:
            return {}
        credentials = {
            "aws_access_key_id": self.access_key_id.get_secret_value(),
            "aws_secret_access_key": (
                self.secret_access_key.get_secret_value()
            ),
        }
        if self.session_token is not None:
            credentials["aws_session_token"] = (
                self.session_token.get_secret_value()
            )
        return credentials
