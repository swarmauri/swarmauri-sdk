from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderEndpointBase, "AmazonNovaEndpoints")
class AmazonNovaEndpoints(ProviderEndpointBase):
    region: str = "us-east-1"
    service: str = "bedrock-runtime"
    type: Literal["AmazonNovaEndpoints"] = "AmazonNovaEndpoints"

    def runtime_url(self) -> str:
        return f"https://bedrock-runtime.{self.region}.amazonaws.com"

    def resolve(self, capability: str) -> str:
        if capability not in {
            "bedrock.runtime",
            "live.connect",
            "model.invoke",
        }:
            raise ValueError(
                f"Amazon Nova does not support capability {capability!r}"
            )
        return self.runtime_url()
