from typing import Literal, Optional
from pydantic import SecretStr
from swarmauri_base.model_providers import ProviderAuthBase


class XAIAuthConfig(ProviderAuthBase):
    api_key: Optional[SecretStr] = None
    type: Literal["XAIAuthConfig"] = "XAIAuthConfig"
