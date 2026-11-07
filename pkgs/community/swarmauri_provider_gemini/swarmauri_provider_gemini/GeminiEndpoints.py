from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)


class GeminiEndpoints(ProviderEndpointBase):
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    websocket_url: str = (
        "wss://generativelanguage.googleapis.com/ws/"
        "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
    )
    type: Literal["GeminiEndpoints"] = "GeminiEndpoints"

    def resolve(self, capability: str) -> str:
        endpoints = {
            "api": self.base_url,
            "live.connect": self.websocket_url,
        }
        try:
            return endpoints[capability]
        except KeyError as error:
            raise ValueError(
                f"Gemini does not support capability {capability!r}"
            ) from error
