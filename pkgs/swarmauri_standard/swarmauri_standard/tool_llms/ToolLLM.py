import asyncio
import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Type

import httpx
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.conversations.IConversation import IConversation

from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)


@ComponentBase.register_type()
class ToolLLM(ToolLLMBase):
    def __init__(self, **data):
        """
        Initialize the OpenAIToolModel class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        self.allowed_models = self.allowed_models or self.get_allowed_models()

    def get_schema_converter(self) -> Type["SchemaConverterBase"]:
        return OpenAISchemaConverter()

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        converter = self.get_schema_converter()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        return [
            m.model_dump(include=message_properties, exclude_none=True)
            for m in messages
            if m.role != "tool"
        ]

    def _process_tool_calls(self, tool_calls, toolkit, messages) -> List[MessageBase]:
        """
        Processes a list of tool calls and appends the results to the messages list.

        Args:
            tool_calls (list): A list of dictionaries representing tool calls. Each dictionary should contain
                               a "function" key with a nested dictionary that includes the "name" and "arguments"
                               of the function to be called, and an "id" key for the tool call identifier.
            toolkit (object): An object that provides access to tools via the `get_tool_by_name` method.
            messages (list): A list of message dictionaries to which the results of the tool calls will be appended.

        Returns:
            List[MessageBase]: The updated list of messages with the results of the tool calls appended.
        """
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        return messages

    def predict(
        self,
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        multiturn: bool = True,
        temperature=0.7,
        max_tokens=1024,
    ) -> IConversation:
        """
        Makes a synchronous prediction using the Groq model.

        Parameters:
            conversation (IConversation): IConversation instance with message history.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            IConversation: Updated conversation with agent responses and tool calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Add tool messages to Conversation to enable Conversation hooks
        tool_messages = [
            FunctionMessage(
                tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
            )
            for m in messages
            if m["role"] == "tool"
        ]

        conversation.add_messages(tool_messages)

        if multiturn:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

            agent_response = response.json()

            agent_message = AgentMessage(
                content=agent_response["choices"][0]["message"]["content"]
            )
            conversation.add_message(agent_message)
        return conversation

    async def apredict(
        self,
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        multiturn: bool = True,
        temperature=0.7,
        max_tokens=1024,
    ) -> IConversation:
        """
        Makes an asynchronous prediction using the OpenAI model.

        Parameters:
            conversation (IConversation): IConversation instance with message history.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            IConversation: Updated conversation with agent responses and tool calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()
            tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])
        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        # Add tool messages to Conversation to enable Conversation hooks
        tool_messages = [
            FunctionMessage(
                tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
            )
            for m in messages
            if m["role"] == "tool"
        ]

        conversation.add_messages(tool_messages)

        if multiturn:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.BASE_URL, headers=self._headers, json=payload
                )
                response.raise_for_status()

            agent_response = response.json()

            agent_message = AgentMessage(
                content=agent_response["choices"][0]["message"]["content"]
            )
            conversation.add_message(agent_message)
        return conversation

    def stream(
        self,
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> Iterator[str]:
        """
        Streams response from OpenAI model in real-time.

        Parameters:
            conversation (IConversation): IConversation instance with message history.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            Iterator[str]: Streamed response content.
        """

        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice or "auto",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()

        tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()

        message_content = ""

        for line in response.iter_lines():
            json_str = line.replace("data: ", "")
            try:
                if json_str:
                    chunk = json.loads(json_str)
                    if chunk["choices"][0]["delta"]:
                        delta = chunk["choices"][0]["delta"]["content"]
                        message_content += delta
                        yield delta
            except json.JSONDecodeError:
                pass

        conversation.add_message(AgentMessage(content=message_content))

    async def astream(
        self,
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response from Groq model.

        Parameters:
            conversation (IConversation): IConversation instance with message history.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            AsyncIterator[str]: Streamed response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()

        tool_response = response.json()

        messages = [formatted_messages[-1], tool_response["choices"][0]["message"]]
        tool_calls = tool_response["choices"][0]["message"].get("tool_calls", [])

        messages = self._process_tool_calls(tool_calls, toolkit, messages)

        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            agent_response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            agent_response.raise_for_status()

        message_content = ""
        async for line in agent_response.aiter_lines():
            json_str = line.replace("data: ", "")
            try:
                if json_str:
                    chunk = json.loads(json_str)
                    if chunk["choices"][0]["delta"]:
                        delta = chunk["choices"][0]["delta"]["content"]
                        message_content += delta
                        yield delta
            except json.JSONDecodeError:
                pass
        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[IConversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> List[IConversation]:
        """
        Processes a batch of conversations and generates responses for each sequentially.

        Args:
            conversations (List[IConversation]): List of conversations to process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.

        Returns:
            List[IConversation]: List of updated conversations with model responses.
        """
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
        conversations: List[IConversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        max_concurrent=5,
    ) -> List[IConversation]:
        """
        Async method for processing a batch of conversations concurrently.

        Args:
            conversations (List[IConversation]): List of conversations to process.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            top_p (float): Cumulative probability for nucleus sampling.
            enable_json (bool): Whether to format the response as JSON.
            stop (Optional[List[str]]): List of stop sequences for response termination.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[IConversation]: List of updated conversations with model responses.
        """
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

    def get_allowed_models(self) -> List[str]:
        """
        Get the list of allowed models for the OpenAI API.

        Returns:
            List[str]: List of allowed models.
        """
        pass
