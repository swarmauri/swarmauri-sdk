from typing import Literal, Optional
from pydantic import Field, SecretStr
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase


class AmazonNovaAuthConfig(ProviderAuthBase):
    access_key_id: Optional[SecretStr] = Field(default=None, exclude=True)
    secret_access_key: Optional[SecretStr] = Field(default=None, exclude=True)
    session_token: Optional[SecretStr] = Field(default=None, exclude=True)
    profile: Optional[str] = None
    type: Literal["AmazonNovaAuthConfig"] = "AmazonNovaAuthConfig"
