from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class OpenAIAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    organization: str | None = None
    project: str | None = None
    type: Literal["OpenAIAuthConfig"] = "OpenAIAuthConfig"
