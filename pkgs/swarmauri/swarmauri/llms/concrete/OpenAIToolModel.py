import json
import logging
import asyncio
from typing import List, Literal, Dict, Any, Iterator, AsyncIterator
from openai import OpenAI, AsyncOpenAI
from pydantic import Field
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)


class OpenAIToolModel(LLMBase):
    """
    Provider resources: https://platform.openai.com/docs/guides/function-calling/which-models-support-function-calling
    """

    api_key: str
    allowed_models: List[str] = [
        "gpt-4o-2024-05-13",
        "gpt-4-turbo",
        "gpt-4o-mini",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-turbo-preview",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-4-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
    ]
    name: str = "gpt-3.5-turbo-0125"
    type: Literal["OpenAIToolModel"] = "OpenAIToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [OpenAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _process_tool_calls(self, tool_calls, toolkit, messages):
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)

                # Await the tool call in case it's asynchronous
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        return messages

    def predict(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ):
        client = OpenAI(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
        )

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        agent_response = client.chat.completions.create(
            model=self.name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        return conversation

    async def apredict(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ):
        """Asynchronous version of predict."""
        async_client = AsyncOpenAI(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = await async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
        )

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        agent_response = await async_client.chat.completions.create(
            model=self.name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        return conversation

    def stream(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> Iterator[str]:
        """Synchronously stream the response token by token"""
        client = OpenAI(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
        )

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        stream = client.chat.completions.create(
            model=self.name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        collected_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def astream(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> AsyncIterator[str]:
        """Asynchronously stream the response token by token."""
        async_client = AsyncOpenAI(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = await async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
        )

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        stream = await async_client.chat.completions.create(
            model=self.name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        collected_content = []
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self,
        conversations: List,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> List:
        """Synchronously process multiple conversations"""
        return [
            self.predict(
                conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        max_concurrent=5,
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    toolkit=toolkit,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
