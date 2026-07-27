from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)


class AmazonNovaEndpoints(ProviderEndpointBase):
    region: str = "us-east-1"
    service: str = "bedrock-runtime"
    type: Literal["AmazonNovaEndpoints"] = "AmazonNovaEndpoints"

    def runtime_url(self) -> str:
        return f"https://bedrock-runtime.{self.region}.amazonaws.com"
