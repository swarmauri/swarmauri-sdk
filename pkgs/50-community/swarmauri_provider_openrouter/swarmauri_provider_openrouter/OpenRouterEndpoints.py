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

    def resolve(self, capability: str) -> str:
        paths = {
            "chat.completions": self.chat_completions_path,
            "models.list": self.models_path,
            "images.generate": self.image_generations_path,
        }
        try:
            path = paths[capability]
        except KeyError as error:
            raise ValueError(
                f"OpenRouter does not support capability {capability!r}"
            ) from error
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
