from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderEndpointBase, "OpenAIEndpoints")
class OpenAIEndpoints(ProviderEndpointBase):
    base_url: str = "https://api.openai.com/v1"
    realtime_url: str = "wss://api.openai.com/v1/realtime"
    responses_websocket_url: str = "wss://api.openai.com/v1/responses"
    type: Literal["OpenAIEndpoints"] = "OpenAIEndpoints"

    def resolve(self, capability: str) -> str:
        endpoints = {
            "api": self.base_url,
            "realtime.connect": self.realtime_url,
            "responses.connect": self.responses_websocket_url,
        }
        try:
            return endpoints[capability]
        except KeyError as error:
            raise ValueError(
                f"OpenAI does not support capability {capability!r}"
            ) from error
