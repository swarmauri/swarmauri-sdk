"""Provide OpenRouter vision-language model support."""

import asyncio
from typing import Any, Literal

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vlms.VLMBase import VLMBase
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
from ._internal.common import add_assistant_response, compact, format_messages


@ComponentBase.register_type(VLMBase, "OpenRouterVLM")
class OpenRouterVLM(VLMBase):
    """Route image-aware conversations through OpenRouter."""

    api_key: SecretStr | None = Field(default=None, exclude=True)
    name: str = "openrouter/auto"
    type: Literal["OpenRouterVLM"] = "OpenRouterVLM"
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

    def refresh_catalog(self) -> list[dict[str, Any]]:
        response = request(self._provider, self._http_client, "models.list")
        return self.catalog.load_response(response.json())

    async def arefresh_catalog(self) -> list[dict[str, Any]]:
        response = await arequest(
            self._provider, self._http_client, "models.list"
        )
        return self.catalog.load_response(response.json())

    def _payload(self, conversation: Any, **kwargs: Any) -> dict[str, Any]:
        return compact(
            {
                "model": self.name,
                "messages": format_messages(conversation.history),
                "provider": self.routing.model_dump(exclude_none=True)
                if self.routing
                else None,
                **kwargs,
            }
        )

    def predict_vision(self, conversation: Any, **kwargs: Any) -> Any:
        response = request(
            self._provider,
            self._http_client,
            "chat.completions",
            model=self.name,
            json_data=self._payload(conversation, **kwargs),
        )
        return add_assistant_response(conversation, response.json())

    async def apredict_vision(self, conversation: Any, **kwargs: Any) -> Any:
        response = await arequest(
            self._provider,
            self._http_client,
            "chat.completions",
            model=self.name,
            json_data=self._payload(conversation, **kwargs),
        )
        return add_assistant_response(conversation, response.json())

    def batch(self, conversations: list[Any], **kwargs: Any) -> list[Any]:
        return [self.predict_vision(item, **kwargs) for item in conversations]

    async def abatch(
        self, conversations: list[Any], max_concurrent: int = 5, **kwargs: Any
    ) -> list[Any]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(item: Any) -> Any:
            async with semaphore:
                return await self.apredict_vision(item, **kwargs)

        return await asyncio.gather(*(run(item) for item in conversations))

    def close(self) -> None:
        close_client(self._http_client)

    async def aclose(self) -> None:
        await aclose_client(self._http_client)
