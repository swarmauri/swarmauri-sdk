import json
import logging
from typing import List, Dict, Any, Literal, AsyncIterator, Iterator, Optional, Union
import requests
import aiohttp
import asyncio
from pydantic import PrivateAttr
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage, contentItem
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.ShuttleAISchemaConverter import (
    ShuttleAISchemaConverter,
)


class ShuttleAIToolModel(LLMBase):
    api_key: str
    _client: Optional[requests.Session] = PrivateAttr(default=None)
    allowed_models: List[str] = [
        "claude-instant-1.1",
        "gemini-1.0-pro-latest",
        "gemini-1.5-pro-latest",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-4-1106-preview",
        "gpt-4-turbo-2024-04-09",
        "mistral-7b-instruct-v0.2",
        "shuttle-2-turbo",
        "wizardlm-2-8x22b",
    ]
    name: str = "shuttle-2-turbo"
    type: Literal["ShuttleAIToolModel"] = "ShuttleAIToolModel"
    resource: str = "LLM"

    def __init__(self, **data):
        super().__init__(**data)
        self._client = requests.Session()
        self._client.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def model_dump(self, **kwargs):
        dump = super().model_dump(**kwargs)
        return {k: v for k, v in dump.items() if k != "_client"}

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        if not tools:
            return []
        return [ShuttleAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _extract_text_content(self, content: Union[str, List[contentItem]]) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_contents = [
                item["text"]
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
                and "text" in item
            ]
            return " ".join(text_contents)
        return ""

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        formatted_messages = []
        role_mapping = {
            "human": "user",
            "agent": "assistant",
            "system": "system",
            "tool": "function",
        }

        for message in messages:
            message_dict = {}

            if hasattr(message, "content"):
                message_dict["content"] = self._extract_text_content(message.content)

            if hasattr(message, "role"):
                original_role = message.role.lower()
                message_dict["role"] = role_mapping.get(original_role, "user")

            for prop in ["name", "tool_call_id", "tool_calls"]:
                if hasattr(message, prop):
                    value = getattr(message, prop)
                    if value is not None:
                        message_dict[prop] = value

            formatted_messages.append(message_dict)

        return formatted_messages

    def _ensure_conversation_has_message(self, conversation):
        if not conversation.history:
            conversation.add_message(
                HumanMessage(content=[{"type": "text", "text": "Hello"}])
            )
        return conversation

    def _process_tool_calls(self, response, toolkit):
        tool_calls = response.get("tool_calls", [])
        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]
            func_call = toolkit.get_tool_by_name(func_name)
            func_args = json.loads(tool_call["function"]["arguments"])
            func_result = func_call(**func_args)
            func_message = FunctionMessage(
                content=func_result, name=func_name, tool_call_id=tool_call["id"]
            )
            conversation.add_message(func_message)
        return tool_calls

    def predict(
        self,
        conversation,
        toolkit=None,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
        internet=False,
        raw=False,
        image=None,
        citations=False,
        tone="precise",
    ):
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "tool_choice": tool_choice,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
        }

        if raw:
            payload["raw"] = True
        if internet:
            payload["internet"] = True
        if image is not None:
            payload["image"] = image
        if self.name in ["gpt-4-bing", "gpt-4-turbo-bing"]:
            payload["tone"] = tone
            if citations:
                payload["citations"] = True

        response = self._client.post(url, json=payload)
        response.raise_for_status()
        agent_response = response.json()

        tool_calls = self._process_tool_calls(
            agent_response["choices"][0]["message"], toolkit
        )

        if tool_calls:
            payload["messages"] = self._format_messages(conversation.history)
            response = self._client.post(url, json=payload)
            response.raise_for_status()
            agent_response = response.json()

        agent_message = AgentMessage(
            content=agent_response["choices"][0]["message"]["content"]
        )
        conversation.add_message(agent_message)
        return conversation

    def stream(
        self,
        conversation,
        toolkit=None,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
        internet=False,
        raw=False,
        image=None,
        citations=False,
        tone="precise",
    ) -> Iterator[str]:
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "tool_choice": tool_choice,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "stream": True,
        }

        if raw:
            payload["raw"] = True
        if internet:
            payload["internet"] = True
        if image is not None:
            payload["image"] = image
        if self.name in ["gpt-4-bing", "gpt-4-turbo-bing"]:
            payload["tone"] = tone
            if citations:
                payload["citations"] = True

        response = self._client.post(url, json=payload, stream=True)
        response.raise_for_status()

        full_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8").split("data: ", 1)[-1])
                    if (
                        chunk.get("choices")
                        and chunk["choices"][0].get("delta")
                        and chunk["choices"][0]["delta"].get("content")
                    ):
                        content = chunk["choices"][0]["delta"]["content"]
                        full_content += content
                        yield content
                except json.JSONDecodeError:
                    continue

        conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self,
        conversations: List,
        toolkit=None,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
        internet=False,
        raw=False,
        image=None,
        citations=False,
        tone="precise",
    ) -> List:
        return [
            self.predict(
                conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                internet=internet,
                raw=raw,
                image=image,
                citations=citations,
                tone=tone,
            )
            for conv in conversations
        ]

    async def apredict(
        self,
        conversation,
        toolkit=None,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
        internet=False,
        raw=False,
        image=None,
        citations=False,
        tone="precise",
    ):
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "tool_choice": tool_choice,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
        }

        if raw:
            payload["raw"] = True
        if internet:
            payload["internet"] = True
        if image is not None:
            payload["image"] = image
        if self.name in ["gpt-4-bing", "gpt-4-turbo-bing"]:
            payload["tone"] = tone
            if citations:
                payload["citations"] = True

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, headers=self._client.headers
            ) as response:
                response.raise_for_status()
                agent_response = await response.json()

        tool_calls = self._process_tool_calls(
            agent_response["choices"][0]["message"], toolkit
        )

        if tool_calls:
            payload["messages"] = self._format_messages(conversation.history)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers=self._client.headers
                ) as response:
                    response.raise_for_status()
                    agent_response = await response.json()

        agent_message = AgentMessage(
            content=agent_response["choices"][0]["message"]["content"]
        )
        conversation.add_message(agent_message)
        return conversation

    async def astream(
        self,
        conversation,
        toolkit=None,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
        internet=False,
        raw=False,
        image=None,
        citations=False,
        tone="precise",
    ) -> AsyncIterator[str]:
        conversation = self._ensure_conversation_has_message(conversation)
        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.shuttleai.app/v1/chat/completions"
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "tool_choice": tool_choice,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "stream": True,
        }

        if raw:
            payload["raw"] = True
        if internet:
            payload["internet"] = True
        if image is not None:
            payload["image"] = image
        if self.name in ["gpt-4-bing", "gpt-4-turbo-bing"]:
            payload["tone"] = tone
            if citations:
                payload["citations"] = True

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, headers=self._client.headers
            ) as response:
                response.raise_for_status()
                full_content = ""
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(
                                line.decode("utf-8").split("data: ", 1)[-1]
                            )
                            if (
                                chunk.get("choices")
                                and chunk["choices"][0].get("delta")
                                and chunk["choices"][0]["delta"].get("content")
                            ):
                                content = chunk["choices"][0]["delta"]["content"]
                                full_content += content
                                yield content
                        except json.JSONDecodeError:
                            continue
                    await asyncio.sleep(0)

        conversation.add_message(AgentMessage(content=full_content))

    async def abatch(
        self,
        conversations: List,
        toolkit=None,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
        internet=False,
        raw=False,
        image=None,
        citations=False,
        tone="precise",
        max_concurrent=5,
    ) -> List:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    internet=internet,
                    raw=raw,
                    image=image,
                    citations=citations,
                    tone=tone,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
