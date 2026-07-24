"""Provide OpenRouter text and reasoning model support."""

import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Any, ClassVar, FrozenSet, Literal

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_standard.messages.AgentMessage import AgentMessage

from ._internal.catalog import OpenRouterModelCatalog
from ._internal.common import (
    add_assistant_response,
    compact,
    delta_text,
    format_messages,
)
from ._internal.routing import OpenRouterProviderPreferences
from ._internal.transport import OpenRouterTransport


@ComponentBase.register_type(LLMBase, "OpenRouterModel")
class OpenRouterModel(LLMBase):
    """Route text and reasoning conversations through OpenRouter."""

    api_key: SecretStr = Field(exclude=True)
    name: str = "openrouter/auto"
    type: Literal["OpenRouterModel"] = "OpenRouterModel"
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: str | None = None
    app_name: str | None = None
    provider: OpenRouterProviderPreferences | None = None
    allowed_models: list[str] = Field(default_factory=list)
    capabilities: ClassVar[FrozenSet[str]] = frozenset(
        {"predict", "apredict", "stream", "astream", "batch", "abatch"}
    )
    _transport: OpenRouterTransport = PrivateAttr()

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._transport = OpenRouterTransport(
            self.base_url, self._request_headers(), self.timeout
        )

    @property
    def catalog(self) -> OpenRouterModelCatalog:
        """Return an explicit live model-discovery client."""
        return OpenRouterModelCatalog(self._transport)

    def _request_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-OpenRouter-Title"] = self.app_name
        return headers

    def _payload(self, conversation: Any, **kwargs: Any) -> dict[str, Any]:
        payload = {
            "model": self.name,
            "messages": format_messages(conversation.history),
            "provider": self.provider.model_dump(exclude_none=True)
            if self.provider
            else None,
            **kwargs,
        }
        return compact(payload)

    def predict(self, conversation: Any, **kwargs: Any) -> Any:
        """Generate one response and append it to the conversation."""
        response = self._transport.request(
            "POST",
            "chat/completions",
            json_data=self._payload(conversation, **kwargs),
        )
        return add_assistant_response(conversation, response.json())

    async def apredict(self, conversation: Any, **kwargs: Any) -> Any:
        """Generate one response asynchronously."""
        response = await self._transport.arequest(
            "POST",
            "chat/completions",
            json_data=self._payload(conversation, **kwargs),
        )
        return add_assistant_response(conversation, response.json())

    def stream(self, conversation: Any, **kwargs: Any) -> Iterator[str]:
        """Stream response text and append the completed response."""
        content: list[str] = []
        payload = self._payload(conversation, stream=True, **kwargs)
        for event in self._transport.stream("chat/completions", payload):
            delta = delta_text(event)
            if delta:
                content.append(delta)
                yield delta
        conversation.add_message(AgentMessage(content="".join(content)))

    async def astream(
        self, conversation: Any, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream response text asynchronously."""
        content: list[str] = []
        payload = self._payload(conversation, stream=True, **kwargs)
        async for event in self._transport.astream(
            "chat/completions", payload
        ):
            delta = delta_text(event)
            if delta:
                content.append(delta)
                yield delta
        conversation.add_message(AgentMessage(content="".join(content)))

    def batch(self, conversations: list[Any], **kwargs: Any) -> list[Any]:
        """Generate responses for conversations sequentially."""
        return [self.predict(item, **kwargs) for item in conversations]

    async def abatch(
        self, conversations: list[Any], max_concurrent: int = 5, **kwargs: Any
    ) -> list[Any]:
        """Generate responses concurrently with a bounded fan-out."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(item: Any) -> Any:
            async with semaphore:
                return await self.apredict(item, **kwargs)

        return await asyncio.gather(*(run(item) for item in conversations))
