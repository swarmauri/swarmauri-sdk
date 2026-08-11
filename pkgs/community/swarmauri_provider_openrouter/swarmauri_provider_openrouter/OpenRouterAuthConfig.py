from collections.abc import Mapping
from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class OpenRouterAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    site_url: str | None = None
    app_name: str | None = None
    type: Literal["OpenRouterAuthConfig"] = "OpenRouterAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        authorized = dict(headers)
        if self.api_key is not None:
            authorized["Authorization"] = (
                f"Bearer {self.api_key.get_secret_value()}"
            )
        if self.site_url:
            authorized["HTTP-Referer"] = self.site_url
        if self.app_name:
            authorized["X-OpenRouter-Title"] = self.app_name
        return authorized
