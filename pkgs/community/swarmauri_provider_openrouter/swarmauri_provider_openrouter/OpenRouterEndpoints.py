from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)


class OpenRouterEndpoints(ProviderEndpointBase):
    base_url: str = "https://openrouter.ai/api/v1"
    chat_completions_path: str = "/chat/completions"
    models_path: str = "/models"
    image_generations_path: str = "/images/generations"
    type: Literal["OpenRouterEndpoints"] = "OpenRouterEndpoints"

    def resolve(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
