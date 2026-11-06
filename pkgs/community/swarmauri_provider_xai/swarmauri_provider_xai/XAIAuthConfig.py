from collections.abc import Mapping
from typing import Literal

from pydantic import Field, SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderAuthBase, "XAIAuthConfig")
class XAIAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = Field(default=None, exclude=True)
    type: Literal["XAIAuthConfig"] = "XAIAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        authorized = dict(headers)
        if self.api_key is None:
            raise ValueError("XAIProvider requires an api_key")
        authorized["Authorization"] = (
            f"Bearer {self.api_key.get_secret_value()}"
        )
        return authorized
