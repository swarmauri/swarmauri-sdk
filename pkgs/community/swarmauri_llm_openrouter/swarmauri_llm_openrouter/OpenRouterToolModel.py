"""Provide OpenRouter client-side tool-calling support."""

import asyncio
import json
from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal, Type

from pydantic import Field, PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.schema_converters.SchemaConverterBase import (
    SchemaConverterBase,
)
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)

from ._internal.catalog import OpenRouterModelCatalog
from ._internal.common import compact, delta_text, format_messages
from ._internal.routing import OpenRouterProviderPreferences
from ._internal.transport import OpenRouterTransport


@ComponentBase.register_type(ToolLLMBase, "OpenRouterToolModel")
class OpenRouterToolModel(ToolLLMBase):
    """Route Swarmauri toolkit calls through OpenRouter-compatible models."""

    api_key: SecretStr = Field(exclude=True)
    name: str = "openrouter/auto"
    type: Literal["OpenRouterToolModel"] = "OpenRouterToolModel"
    BASE_URL: str = "https://openrouter.ai/api/v1"
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: str | None = None
    app_name: str | None = None
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

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """Return the OpenAI-compatible tool schema converter."""
        return OpenAISchemaConverter

    def _schema_convert_tools(
        self, tools: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Convert tools with an instantiated schema converter."""
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
                "provider": self.provider.model_dump(exclude_none=True)
                if self.provider
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
        """Request, execute, and optionally complete client-side tool calls."""
        response = self._transport.request(
            "POST",
            "chat/completions",
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
            final_payload = compact(
                {
                    "model": self.name,
                    "messages": messages,
                    "provider": self.provider.model_dump(exclude_none=True)
                    if self.provider
                    else None,
                    **kwargs,
                }
            )
            final = self._transport.request(
                "POST", "chat/completions", json_data=final_payload
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
        """Execute the tool-calling workflow asynchronously."""
        response = await self._transport.arequest(
            "POST",
            "chat/completions",
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
            final = await self._transport.arequest(
                "POST",
                "chat/completions",
                json_data=compact(
                    {
                        "model": self.name,
                        "messages": messages,
                        "provider": self.provider.model_dump(exclude_none=True)
                        if self.provider
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
        """Resolve tools, then stream the final assistant response."""
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
                **kwargs,
            }
        )
        for event in self._transport.stream("chat/completions", payload):
            delta = delta_text(event)
            if delta:
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
        """Resolve tools, then stream the final response asynchronously."""
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
                **kwargs,
            }
        )
        async for event in self._transport.astream(
            "chat/completions", payload
        ):
            delta = delta_text(event)
            if delta:
                content.append(delta)
                yield delta
        conversation.add_message(AgentMessage(content="".join(content)))

    def batch(self, conversations: list[Any], **kwargs: Any) -> list[Any]:
        """Run tool workflows sequentially."""
        return [self.predict(item, **kwargs) for item in conversations]

    async def abatch(
        self, conversations: list[Any], max_concurrent: int = 5, **kwargs: Any
    ) -> list[Any]:
        """Run tool workflows with bounded concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run(item: Any) -> Any:
            async with semaphore:
                return await self.apredict(item, **kwargs)

        return await asyncio.gather(*(run(item) for item in conversations))
