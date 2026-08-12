"""Common provider endpoint settings."""

from typing import Literal

from pydantic import Field
from swarmauri_core.model_providers.IProviderEndpoint import IProviderEndpoint

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class ProviderEndpointBase(IProviderEndpoint, ComponentBase):
    base_url: str | None = None
    region: str | None = None
    resource: str = Field(
        default=ResourceTypes.MODEL_PROVIDER.value, frozen=True
    )
    type: Literal["ProviderEndpointBase"] = "ProviderEndpointBase"

    def resolve(self, capability: str) -> str:
        """Resolve any capability to the configured base URL by default."""
        if self.base_url is None:
            raise ValueError(
                f"No endpoint is configured for capability {capability!r}"
            )
        return self.base_url
