"""Common provider authentication settings."""

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, SecretStr
from swarmauri_core.model_providers.IProviderAuth import IProviderAuth

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class ProviderAuthBase(IProviderAuth, ComponentBase):
    api_key: SecretStr | None = Field(default=None, exclude=True)
    token: SecretStr | None = Field(default=None, exclude=True)
    resource: str = Field(
        default=ResourceTypes.MODEL_PROVIDER.value, frozen=True
    )
    type: Literal["ProviderAuthBase"] = "ProviderAuthBase"

    def apply(self, headers: Mapping[str, str]) -> Mapping[str, str]:
        """Return unchanged headers when a provider needs no header auth."""
        return dict(headers)
