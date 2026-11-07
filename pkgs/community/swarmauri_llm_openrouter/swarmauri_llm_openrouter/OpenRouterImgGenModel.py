"""Provide OpenRouter image-generation support."""

import asyncio
import base64
from typing import Any, Literal

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_provider_openrouter import (
    OpenRouterModelCatalog,
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)

from ._client import (
    aclose_client,
    arequest,
    build_openrouter_client,
    close_client,
    request,
)
from ._internal.common import compact


@ComponentBase.register_type(ImageGenBase, "OpenRouterImgGenModel")
class OpenRouterImgGenModel(ImageGenBase):
    """Generate images through OpenRouter's dedicated image API."""

    api_key: SecretStr | None = Field(default=None, exclude=True)
    name: str = "openai/gpt-image-1"
    type: Literal["OpenRouterImgGenModel"] = "OpenRouterImgGenModel"
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: str | None = None
    app_name: str | None = None
    timeout: float = 600.0
    max_retries: int = Field(default=3, ge=1)
    routing: OpenRouterProviderPreferences | None = None
    allowed_models: list[str] = Field(default_factory=list)
    _provider: OpenRouterProvider = PrivateAttr()
    _http_client: IHttpClient = PrivateAttr()

    def __init__(
        self,
        *,
        provider: OpenRouterProvider
        | OpenRouterProviderPreferences
        | None = None,
        routing: OpenRouterProviderPreferences | None = None,
        http_client: IHttpClient | None = None,
        retry_policy: IHttpRetryPolicy | None = None,
        **data: Any,
    ) -> None:
        if isinstance(provider, OpenRouterProviderPreferences):
            routing = provider
            provider = None
        if routing is not None:
            data["routing"] = routing
        super().__init__(**data)
        self._provider = provider or OpenRouterProvider(
            api_key=self.api_key,
            base_url=self.base_url,
            site_url=self.site_url,
            app_name=self.app_name,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        if self._provider.api_key is None:
            raise ValueError(
                "api_key or an authenticated provider is required"
            )
        self.base_url = self._provider.base_url or self.base_url
        self._http_client = build_openrouter_client(
            provider=self._provider,
            http_client=http_client,
            retry_policy=retry_policy,
        )

    @property
    def catalog(self) -> OpenRouterModelCatalog:
        return self._provider.catalog

    def _decode_images(self, response: dict[str, Any]) -> list[bytes]:
        images: list[bytes] = []
        for item in response.get("data", []):
            encoded = item.get("b64_json") or item.get("b64")
            if encoded:
                images.append(base64.b64decode(encoded))
            elif item.get("url"):
                downloaded = self._http_client.request("GET", item["url"])
                downloaded.raise_for_status()
                images.append(downloaded.read())
        return images

    async def _adecode_images(self, response: dict[str, Any]) -> list[bytes]:
        images: list[bytes] = []
        for item in response.get("data", []):
            encoded = item.get("b64_json") or item.get("b64")
            if encoded:
                images.append(base64.b64decode(encoded))
            elif item.get("url"):
                downloaded = await self._http_client.arequest(
                    "GET", item["url"]
                )
                downloaded.raise_for_status()
                images.append(await downloaded.aread())
        return images

    def _payload(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return compact(
            {
                "model": self.name,
                "prompt": prompt,
                "provider": self.routing.model_dump(exclude_none=True)
                if self.routing
                else None,
                **kwargs,
            }
        )

    def generate_image(
        self, prompt: str, **kwargs: Any
    ) -> bytes | list[bytes]:
        response = request(
            self._provider,
            self._http_client,
            "images.generate",
            model=self.name,
            json_data=self._payload(prompt, **kwargs),
        )
        images = self._decode_images(response.json())
        return images[0] if len(images) == 1 else images

    async def agenerate_image(
        self, prompt: str, **kwargs: Any
    ) -> bytes | list[bytes]:
        response = await arequest(
            self._provider,
            self._http_client,
            "images.generate",
            model=self.name,
            json_data=self._payload(prompt, **kwargs),
        )
        images = await self._adecode_images(response.json())
        return images[0] if len(images) == 1 else images

    def batch_generate(
        self, prompts: list[str], **kwargs: Any
    ) -> list[bytes | list[bytes]]:
        return [self.generate_image(prompt, **kwargs) for prompt in prompts]

    async def abatch_generate(
        self, prompts: list[str], max_concurrent: int = 5, **kwargs: Any
    ) -> list[bytes | list[bytes]]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(prompt: str) -> bytes | list[bytes]:
            async with semaphore:
                return await self.agenerate_image(prompt, **kwargs)

        return await asyncio.gather(*(run(prompt) for prompt in prompts))

    def close(self) -> None:
        close_client(self._http_client)

    async def aclose(self) -> None:
        await aclose_client(self._http_client)
