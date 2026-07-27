from typing import Literal, Optional

from pydantic import SecretStr

from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class OpenAIAuthConfig(ProviderAuthBase):
    api_key: Optional[SecretStr] = None
    organization: Optional[str] = None
    project: Optional[str] = None
    type: Literal["OpenAIAuthConfig"] = "OpenAIAuthConfig"
