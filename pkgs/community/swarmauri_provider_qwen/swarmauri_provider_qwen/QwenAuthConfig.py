from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class QwenAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    type: Literal["QwenAuthConfig"] = "QwenAuthConfig"
