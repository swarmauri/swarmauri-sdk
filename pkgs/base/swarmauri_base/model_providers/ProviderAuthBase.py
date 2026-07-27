"""Common provider authentication settings."""

from typing import Literal, Optional

from pydantic import Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase


class ProviderAuthBase(ComponentBase):
    api_key: Optional[SecretStr] = Field(default=None, exclude=True)
    token: Optional[SecretStr] = Field(default=None, exclude=True)
    type: Literal["ProviderAuthBase"] = "ProviderAuthBase"
