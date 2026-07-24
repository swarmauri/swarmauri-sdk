"""Provide OpenRouter vision-language model support."""

import asyncio
from typing import Any, Literal

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase

from ._internal.catalog import OpenRouterModelCatalog
from ._internal.common import add_assistant_response, compact, format_messages
from ._internal.routing import OpenRouterProviderPreferences
from ._internal.transport import OpenRouterTransport


@ComponentBase.register_type(VLMBase, "OpenRouterVLM")
class OpenRouterVLM(VLMBase):
    """Route image-aware conversations through OpenRouter."""

    api_key: SecretStr = Field(exclude=True)
    name: str = "openrouter/auto"
    type: Literal["OpenRouterVLM"] = "OpenRouterVLM"
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

    def _payload(self, conversation: Any, **kwargs: Any) -> dict[str, Any]:
        return compact(
            {
                "model": self.name,
                "messages": format_messages(conversation.history),
                "provider": self.provider.model_dump(exclude_none=True)
                if self.provider
                else None,
                **kwargs,
            }
        )

    def predict_vision(self, conversation: Any, **kwargs: Any) -> Any:
        """Generate a response to a multimodal conversation."""
        response = self._transport.request(
            "POST",
            "chat/completions",
            json_data=self._payload(conversation, **kwargs),
        )
        return add_assistant_response(conversation, response.json())

    async def apredict_vision(self, conversation: Any, **kwargs: Any) -> Any:
        """Generate a multimodal response asynchronously."""
        response = await self._transport.arequest(
            "POST",
            "chat/completions",
            json_data=self._payload(conversation, **kwargs),
        )
        return add_assistant_response(conversation, response.json())

    def batch(self, conversations: list[Any], **kwargs: Any) -> list[Any]:
        """Generate responses for multimodal conversations."""
        return [self.predict_vision(item, **kwargs) for item in conversations]

    async def abatch(
        self, conversations: list[Any], max_concurrent: int = 5, **kwargs: Any
    ) -> list[Any]:
        """Generate multimodal responses with bounded concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(item: Any) -> Any:
            async with semaphore:
                return await self.apredict_vision(item, **kwargs)

        return await asyncio.gather(*(run(item) for item in conversations))
