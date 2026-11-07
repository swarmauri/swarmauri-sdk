from collections.abc import Mapping
from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class GeminiAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    vertex_project: str | None = None
    vertex_location: str | None = None
    type: Literal["GeminiAuthConfig"] = "GeminiAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        authorized = dict(headers)
        if self.api_key is not None:
            authorized["x-goog-api-key"] = self.api_key.get_secret_value()
        return authorized
