"""Provide OpenRouter image-generation support."""

import asyncio
import base64
from typing import Any, Literal

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase

from ._internal.catalog import OpenRouterModelCatalog
from ._internal.common import compact
from ._internal.routing import OpenRouterProviderPreferences
from ._internal.transport import OpenRouterTransport


@ComponentBase.register_type(ImageGenBase, "OpenRouterImgGenModel")
class OpenRouterImgGenModel(ImageGenBase):
    """Generate images through OpenRouter's dedicated image API."""

    api_key: SecretStr = Field(exclude=True)
    name: str = "openai/gpt-image-1"
    type: Literal["OpenRouterImgGenModel"] = "OpenRouterImgGenModel"
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: str | None = None
    app_name: str | None = None
    timeout: float = 600.0
    provider: OpenRouterProviderPreferences | None = None
    allowed_models: list[str] = Field(default_factory=list)
    _transport: OpenRouterTransport = PrivateAttr()

    def __init__(self, **data: Any):
        super().__init__(**data)
        headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-OpenRouter-Title"] = self.app_name
        self._transport = OpenRouterTransport(
            self.base_url, headers, self.timeout
        )

    @property
    def catalog(self) -> OpenRouterModelCatalog:
        """Return an explicit live model-discovery client."""
        return OpenRouterModelCatalog(self._transport)

    def _decode_images(self, response: dict[str, Any]) -> list[bytes]:
        images: list[bytes] = []
        for item in response.get("data", []):
            encoded = item.get("b64_json") or item.get("b64")
            if encoded:
                images.append(base64.b64decode(encoded))
            elif item.get("url"):
                images.append(
                    self._transport.request("GET", item["url"]).content
                )
        return images

    def generate_image(
        self, prompt: str, **kwargs: Any
    ) -> bytes | list[bytes]:
        """Generate one or more images and return their bytes."""
        payload = compact(
            {
                "model": self.name,
                "prompt": prompt,
                "provider": self.provider.model_dump(exclude_none=True)
                if self.provider
                else None,
                **kwargs,
            }
        )
        images = self._decode_images(
            self._transport.request(
                "POST", "images/generations", json_data=payload
            ).json()
        )
        return images[0] if len(images) == 1 else images

    async def agenerate_image(
        self, prompt: str, **kwargs: Any
    ) -> bytes | list[bytes]:
        """Generate images without blocking the event loop."""
        return await asyncio.to_thread(self.generate_image, prompt, **kwargs)

    def batch_generate(
        self, prompts: list[str], **kwargs: Any
    ) -> list[bytes | list[bytes]]:
        """Generate images for prompts sequentially."""
        return [self.generate_image(prompt, **kwargs) for prompt in prompts]

    async def abatch_generate(
        self, prompts: list[str], max_concurrent: int = 5, **kwargs: Any
    ) -> list[bytes | list[bytes]]:
        """Generate images concurrently with a bounded fan-out."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(prompt: str) -> bytes | list[bytes]:
            async with semaphore:
                return await self.agenerate_image(prompt, **kwargs)

        return await asyncio.gather(*(run(prompt) for prompt in prompts))
