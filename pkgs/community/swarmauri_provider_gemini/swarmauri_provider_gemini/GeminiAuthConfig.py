from typing import Literal, Optional

from pydantic import SecretStr

from swarmauri_base.model_providers import ProviderAuthBase


class GeminiAuthConfig(ProviderAuthBase):
    api_key: Optional[SecretStr] = None
    vertex_project: Optional[str] = None
    vertex_location: Optional[str] = None
    type: Literal["GeminiAuthConfig"] = "GeminiAuthConfig"
