from collections.abc import Mapping
from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class OpenAIAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    organization: str | None = None
    project: str | None = None
    type: Literal["OpenAIAuthConfig"] = "OpenAIAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        authorized = dict(headers)
        if self.api_key is not None:
            authorized["Authorization"] = (
                f"Bearer {self.api_key.get_secret_value()}"
            )
        if self.organization is not None:
            authorized["OpenAI-Organization"] = self.organization
        if self.project is not None:
            authorized["OpenAI-Project"] = self.project
        return authorized
