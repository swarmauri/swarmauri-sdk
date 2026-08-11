from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)


class XAIEndpoints(ProviderEndpointBase):
    base_url: str = "https://api.x.ai/v1"
    chat_completions_path: str = "/chat/completions"
    models_path: str = "/language-models"
    websocket_url: str = "wss://api.x.ai/v1/realtime"
    type: Literal["XAIEndpoints"] = "XAIEndpoints"

    def resolve(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
