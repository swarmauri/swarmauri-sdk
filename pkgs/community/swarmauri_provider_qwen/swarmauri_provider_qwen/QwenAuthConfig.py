from collections.abc import Mapping
from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class QwenAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    type: Literal["QwenAuthConfig"] = "QwenAuthConfig"

    def apply(self, headers: Mapping[str, str]) -> dict[str, str]:
        authorized = dict(headers)
        if self.api_key is not None:
            authorized["Authorization"] = (
                f"Bearer {self.api_key.get_secret_value()}"
            )
        return authorized
