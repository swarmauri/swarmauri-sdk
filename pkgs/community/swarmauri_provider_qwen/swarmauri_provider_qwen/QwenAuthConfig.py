from typing import Literal, Optional
from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class QwenAuthConfig(ProviderAuthBase):
    api_key: Optional[SecretStr] = None
    type: Literal["QwenAuthConfig"] = "QwenAuthConfig"
