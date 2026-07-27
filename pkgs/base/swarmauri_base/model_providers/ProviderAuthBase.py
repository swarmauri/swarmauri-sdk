"""Common provider authentication settings."""

from typing import Literal

from pydantic import Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase


class ProviderAuthBase(ComponentBase):
    api_key: SecretStr | None = Field(default=None, exclude=True)
    token: SecretStr | None = Field(default=None, exclude=True)
    type: Literal["ProviderAuthBase"] = "ProviderAuthBase"
