import asyncio

from groq import Groq, AsyncGroq
import json
from typing import List, Literal, Dict, Any, Optional
import logging

from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.GroqSchemaConverter import (
    GroqSchemaConverter,
)


class GroqToolModel(LLMBase):
    """
    Provider Documentation: https://console.groq.com/docs/tool-use#models
    """

    api_key: str
    allowed_models: List[str] = [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "llama3-groq-70b-8192-tool-use-preview",
        "llama3-groq-8b-8192-tool-use-preview",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        # parallel tool use not supported
        # "mixtral-8x7b-32768",
        # "gemma-7b-it",
        # "gemma2-9b-it",
    ]
    name: str = "llama3-groq-70b-8192-tool-use-preview"
    type: Literal["GroqToolModel"] = "GroqToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GroqSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ):
        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(tool_response)

        agent_message = AgentMessage(content=tool_response.choices[0].message.content)
        conversation.add_message(agent_message)

        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                func_message = FunctionMessage(
                    content=json.dumps(func_result),
                    name=func_name,
                    tool_call_id=tool_call.id,
                )
                conversation.add_message(func_message)

        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        logging.info(agent_response)
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
        formatted_messages = self._format_messages(conversation.history)

        client = AsyncGroq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = await client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(tool_response)

        agent_message = AgentMessage(content=tool_response.choices[0].message.content)
        conversation.add_message(agent_message)

        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                func_message = FunctionMessage(
                    content=json.dumps(func_result),
                    name=func_name,
                    tool_call_id=tool_call.id,
                )
                conversation.add_message(func_message)

        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        agent_response = await client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        logging.info(agent_response)
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
    ):
        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(tool_response)

        agent_message = AgentMessage(content=tool_response.choices[0].message.content)
        conversation.add_message(agent_message)

        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                func_message = FunctionMessage(
                    content=json.dumps(func_result),
                    name=func_name,
                    tool_call_id=tool_call.id,
                )
                conversation.add_message(func_message)

        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        message_content = ""

        for chunk in agent_response:
            if chunk.choices[0].delta.content:
                message_content += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

        conversation.add_message(AgentMessage(content=message_content))

    async def astream(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ):
        formatted_messages = self._format_messages(conversation.history)

        client = AsyncGroq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = await client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(tool_response)

        agent_message = AgentMessage(content=tool_response.choices[0].message.content)
        conversation.add_message(agent_message)

        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                func_message = FunctionMessage(
                    content=json.dumps(func_result),
                    name=func_name,
                    tool_call_id=tool_call.id,
                )
                conversation.add_message(func_message)

        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        agent_response = await client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        message_content = ""

        async for chunk in agent_response:
            if chunk.choices[0].delta.content:
                message_content += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> List:
        """Synchronously process multiple conversations"""
        if toolkit and not tool_choice:
            tool_choice = "auto"

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
        conversations: List[Conversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        max_concurrent=5,
    ) -> List:
        """Process multiple conversations in parallel with controlled concurrency"""
        if toolkit and not tool_choice:
            tool_choice = "auto"

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
