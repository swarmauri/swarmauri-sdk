from collections.abc import Mapping
from typing import Literal

from pydantic import Field, SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class AmazonNovaAuthConfig(ProviderAuthBase):
    access_key_id: SecretStr | None = Field(default=None, exclude=True)
    secret_access_key: SecretStr | None = Field(default=None, exclude=True)
    session_token: SecretStr | None = Field(default=None, exclude=True)
    profile: str | None = None
    type: Literal["AmazonNovaAuthConfig"] = "AmazonNovaAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        """Preserve headers; the AWS transport applies request-aware SigV4."""
        return dict(headers)
