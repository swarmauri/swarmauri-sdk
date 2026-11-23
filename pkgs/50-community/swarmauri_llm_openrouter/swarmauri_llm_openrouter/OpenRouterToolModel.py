"""Provide OpenRouter client-side tool-calling support."""

import asyncio
import builtins
import json
from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.schema_converters.SchemaConverterBase import (
    SchemaConverterBase,
)
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_provider_openrouter import (
    OpenRouterModelCatalog,
    OpenRouterProvider,
    OpenRouterProviderPreferences,
    OpenRouterToolSchemaConverter,
)
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.messages.FunctionMessage import FunctionMessage

from ._client import (
    aclose_client,
    arequest,
    astream_events,
    build_openrouter_client,
    close_client,
    request,
    stream_events,
)
from ._internal.common import compact, delta_text, format_messages


@ComponentBase.register_type(ToolLLMBase, "OpenRouterToolModel")
class OpenRouterToolModel(ToolLLMBase):
    """Route Swarmauri toolkit calls through OpenRouter-compatible models."""

    api_key: SecretStr | None = Field(default=None, exclude=True)
    name: str = "openrouter/auto"
    type: Literal["OpenRouterToolModel"] = "OpenRouterToolModel"
    BASE_URL: str = "https://openrouter.ai/api/v1"
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: str | None = None
    app_name: str | None = None
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

    def get_schema_converter(self) -> builtins.type[SchemaConverterBase]:
        return OpenRouterToolSchemaConverter

    def _schema_convert_tools(
        self, tools: dict[str, Any]
    ) -> list[dict[str, Any]]:
        converter = self.get_schema_converter()()
        return [converter.convert(tool) for tool in tools.values()]

    def _payload(
        self, conversation: Any, toolkit: Any, tool_choice: Any, **kwargs: Any
    ) -> dict[str, Any]:
        return compact(
            {
                "model": self.name,
                "messages": format_messages(conversation.history),
                "tools": self._schema_convert_tools(toolkit.tools)
                if toolkit
                else None,
                "tool_choice": tool_choice if toolkit else None,
                "provider": self.routing.model_dump(exclude_none=True)
                if self.routing
                else None,
                **kwargs,
            }
        )

    @staticmethod
    def _execute_tool_calls(
        conversation: Any, toolkit: Any, assistant: dict[str, Any]
    ) -> list[dict[str, Any]]:
        messages = format_messages(conversation.history)
        for tool_call in assistant.get("tool_calls") or []:
            function = tool_call["function"]
            result = toolkit.get_tool_by_name(function["name"])(
                **json.loads(function["arguments"])
            )
            function_message = FunctionMessage(
                tool_call_id=tool_call["id"],
                name=function["name"],
                content=json.dumps(result),
            )
            conversation.add_message(function_message)
            messages.append(
                function_message.model_dump(
                    include={"content", "role", "name", "tool_call_id"},
                    exclude_none=True,
                )
            )
        return messages

    def predict(
        self,
        conversation: Any,
        toolkit: Any = None,
        tool_choice: Any = "auto",
        multiturn: bool = True,
        **kwargs: Any,
    ) -> Any:
        response = request(
            self._provider,
            self._http_client,
            "chat.completions",
            model=self.name,
            json_data=self._payload(
                conversation, toolkit, tool_choice, **kwargs
            ),
        ).json()
        assistant = response["choices"][0]["message"]
        tool_calls = assistant.get("tool_calls") or []
        conversation.add_message(
            AgentMessage(
                content=assistant.get("content"),
                tool_calls=tool_calls or None,
                usage=UsageData.model_validate(response["usage"])
                if response.get("usage")
                else None,
            )
        )
        if multiturn and tool_calls:
            messages = self._execute_tool_calls(
                conversation, toolkit, assistant
            )
            final = request(
                self._provider,
                self._http_client,
                "chat.completions",
                model=self.name,
                json_data=compact(
                    {
                        "model": self.name,
                        "messages": messages,
                        "provider": self.routing.model_dump(exclude_none=True)
                        if self.routing
                        else None,
                        **kwargs,
                    }
                ),
            ).json()
            conversation.add_message(
                AgentMessage(
                    content=final["choices"][0]["message"].get("content")
                )
            )
        return conversation

    async def apredict(
        self,
        conversation: Any,
        toolkit: Any = None,
        tool_choice: Any = "auto",
        multiturn: bool = True,
        **kwargs: Any,
    ) -> Any:
        response = await arequest(
            self._provider,
            self._http_client,
            "chat.completions",
            model=self.name,
            json_data=self._payload(
                conversation, toolkit, tool_choice, **kwargs
            ),
        )
        assistant_response = response.json()
        assistant = assistant_response["choices"][0]["message"]
        tool_calls = assistant.get("tool_calls") or []
        conversation.add_message(
            AgentMessage(
                content=assistant.get("content"), tool_calls=tool_calls or None
            )
        )
        if multiturn and tool_calls:
            messages = self._execute_tool_calls(
                conversation, toolkit, assistant
            )
            final = await arequest(
                self._provider,
                self._http_client,
                "chat.completions",
                model=self.name,
                json_data=compact(
                    {
                        "model": self.name,
                        "messages": messages,
                        "provider": self.routing.model_dump(exclude_none=True)
                        if self.routing
                        else None,
                        **kwargs,
                    }
                ),
            )
            conversation.add_message(
                AgentMessage(
                    content=final.json()["choices"][0]["message"].get(
                        "content"
                    )
                )
            )
        return conversation

    def stream(
        self,
        conversation: Any,
        toolkit: Any = None,
        tool_choice: Any = "auto",
        **kwargs: Any,
    ) -> Iterator[str]:
        self.predict(
            conversation, toolkit, tool_choice, multiturn=False, **kwargs
        )
        assistant = conversation.get_last().model_dump(exclude_none=True)
        messages = self._execute_tool_calls(conversation, toolkit, assistant)
        content: list[str] = []
        payload = compact(
            {
                "model": self.name,
                "messages": messages,
                "stream": True,
                "provider": self.routing.model_dump(exclude_none=True)
                if self.routing
                else None,
                **kwargs,
            }
        )
        for event in stream_events(
            self._provider,
            self._http_client,
            "chat.completions",
            payload,
            model=self.name,
        ):
            if delta := delta_text(event):
                content.append(delta)
                yield delta
        conversation.add_message(AgentMessage(content="".join(content)))

    async def astream(
        self,
        conversation: Any,
        toolkit: Any = None,
        tool_choice: Any = "auto",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        await self.apredict(
            conversation, toolkit, tool_choice, multiturn=False, **kwargs
        )
        assistant = conversation.get_last().model_dump(exclude_none=True)
        messages = self._execute_tool_calls(conversation, toolkit, assistant)
        content: list[str] = []
        payload = compact(
            {
                "model": self.name,
                "messages": messages,
                "stream": True,
                "provider": self.routing.model_dump(exclude_none=True)
                if self.routing
                else None,
                **kwargs,
            }
        )
        async for event in astream_events(
            self._provider,
            self._http_client,
            "chat.completions",
            payload,
            model=self.name,
        ):
            if delta := delta_text(event):
                content.append(delta)
                yield delta
        conversation.add_message(AgentMessage(content="".join(content)))

    def batch(self, conversations: list[Any], **kwargs: Any) -> list[Any]:
        return [self.predict(item, **kwargs) for item in conversations]

    async def abatch(
        self, conversations: list[Any], max_concurrent: int = 5, **kwargs: Any
    ) -> list[Any]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(item: Any) -> Any:
            async with semaphore:
                return await self.apredict(item, **kwargs)

        return await asyncio.gather(*(run(item) for item in conversations))

    def close(self) -> None:
        close_client(self._http_client)

    async def aclose(self) -> None:
        await aclose_client(self._http_client)
