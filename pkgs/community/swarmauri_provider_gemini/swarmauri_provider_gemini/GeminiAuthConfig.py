from typing import Literal

from pydantic import SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class GeminiAuthConfig(ProviderAuthBase):
    api_key: SecretStr | None = None
    vertex_project: str | None = None
    vertex_location: str | None = None
    type: Literal["GeminiAuthConfig"] = "GeminiAuthConfig"
