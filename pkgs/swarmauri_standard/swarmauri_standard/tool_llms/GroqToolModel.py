import asyncio
import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.conversations.IConversation import IConversation
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.GroqSchemaConverter import (
    GroqSchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "GroqToolModel")
class GroqToolModel(ToolLLMBase):
    """
    GroqToolModel provides an interface to interact with Groq's large language models for tool usage.

    This class supports synchronous and asynchronous predictions, streaming of responses,
    and batch processing. It communicates with the Groq API to manage conversations, format messages,
    and handle tool-related functions.

    Attributes:
        api_key (SecretStr): API key to authenticate with Groq API.
        allowed_models (List[str]): List of permissible model names.
        name (str): Default model name for predictions.
        type (Literal): Type identifier for the model.

    Provider Documentation: https://console.groq.com/docs/tool-use#models
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        "moonshotai/kimi-k2-instruct",
        "moonshotai/kimi-k2-instruct-0905",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
    name: str = ""
    type: Literal["GroqToolModel"] = "GroqToolModel"

    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Initialize the GroqToolModel class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        self._client = httpx.Client(
            headers=self._headers,
            timeout=self.timeout,
        )
        self._async_client = httpx.AsyncClient(
            headers=self._headers,
            timeout=self.timeout,
        )

        self.allowed_models = self.allowed_models or self.get_allowed_models()
        if not self.name and self.allowed_models:
            self.name = self.allowed_models[0]

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Returns the schema converter class for Groq API.

        Returns:
            Type[SchemaConverterBase]: The GroqSchemaConverter class.
        """
        return GroqSchemaConverter

    def _schema_convert_tools(self, tools: Dict[str, ToolBase]) -> List[Dict[str, Any]]:
        """
        Converts toolkit items to API-compatible schema format.

        Parameters:
            tools (Dict[str, ToolBase]): Dictionary of tools to be converted.

        Returns:
            List[Dict[str, Any]]: Formatted list of tool dictionaries.
        """
        converter = self.get_schema_converter()()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats messages for API compatibility.

        Parameters:
            messages (List[Type[MessageBase]]): List of message instances to format.

        Returns:
            List[Dict[str, str]]: List of formatted message dictionaries.
        """
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "tool"
        ]
        return formatted_messages

    def _process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        toolkit: Toolkit,
        messages: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Processes a list of tool calls and appends the results to the messages list.

        Args:
            tool_calls (List[Dict[str, Any]]): A list of dictionaries representing tool calls. Each dictionary should contain
                               a "function" key with a nested dictionary that includes the "name" and "arguments"
                               of the function to be called, and an "id" key for the tool call identifier.
            toolkit (Toolkit): An object that provides access to tools via the `get_tool_by_name` method.
            messages (List[Dict[str, Any]]): A list of message dictionaries to which the results of the tool calls will be appended.

        Returns:
            List[Dict[str, Any]]: The updated list of messages with the results of the tool calls appended.
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

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Conversation:
        """
        Makes a synchronous prediction using the Groq model.

        Parameters:
            conversation (Conversation): Conversation instance with message history.
            toolkit (Toolkit): Optional toolkit for tool conversion.
            tool_choice (Dict[str, Any]): Tool selection strategy.
            multiturn (bool): Whether to follow up a tool call with another LLM request.
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
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice or "auto",
        }

        response = self._client.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        tool_response = response.json()

        messages = formatted_messages.copy()

        # Add the assistant message
        if "choices" in tool_response and tool_response["choices"]:
            assistant_message = tool_response["choices"][0]["message"]
            messages.append(assistant_message)

            # Process tool calls if any
            tool_calls = assistant_message.get("tool_calls", [])
            messages = self._process_tool_calls(tool_calls, toolkit, messages)

            # Extract tool messages for the conversation
            tool_messages = [
                FunctionMessage(
                    tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
                )
                for m in messages
                if m.get("role") == "tool"
            ]

            # Add tool messages to conversation
            conversation.add_messages(tool_messages)

        # For multiturn, make a follow-up request with the tool results
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            response = self._client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            agent_response = response.json()

            if "choices" in agent_response and agent_response["choices"]:
                agent_message = AgentMessage(
                    content=agent_response["choices"][0]["message"]["content"]
                )
                conversation.add_message(agent_message)

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Conversation:
        """
        Makes an asynchronous prediction using the Groq model.

        Parameters:
            conversation (Conversation): Conversation instance with message history.
            toolkit (Toolkit): Optional toolkit for tool conversion.
            tool_choice (Dict[str, Any]): Tool selection strategy.
            multiturn (bool): Whether to follow up a tool call with another LLM request.
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
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as client:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()

        # Add the assistant message
        if "choices" in tool_response and tool_response["choices"]:
            assistant_message = tool_response["choices"][0]["message"]
            messages.append(assistant_message)

            # Process tool calls if any
            tool_calls = assistant_message.get("tool_calls", [])
            messages = self._process_tool_calls(tool_calls, toolkit, messages)

            # Extract tool messages for the conversation
            tool_messages = [
                FunctionMessage(
                    tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
                )
                for m in messages
                if m.get("role") == "tool"
            ]

            # Add tool messages to conversation
            conversation.add_messages(tool_messages)

        # For multiturn, make a follow-up request with the tool results
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            async with httpx.AsyncClient(
                headers=self._headers, timeout=self.timeout
            ) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                agent_response = response.json()

            if "choices" in agent_response and agent_response["choices"]:
                agent_message = AgentMessage(
                    content=agent_response["choices"][0]["message"]["content"]
                )
                conversation.add_message(agent_message)

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """
        Streams response from Groq model in real-time.

        Parameters:
            conversation (Conversation): Conversation instance with message history.
            toolkit (Toolkit): Optional toolkit for tool conversion.
            tool_choice (Dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            Iterator[str]: Streamed response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        # First, make a non-streaming request to handle tool calls
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice or "auto",
        }

        response = self._client.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        tool_response = response.json()

        messages = formatted_messages.copy()

        # Process tool calls if any
        if "choices" in tool_response and tool_response["choices"]:
            assistant_message = tool_response["choices"][0]["message"]
            messages.append(assistant_message)

            tool_calls = assistant_message.get("tool_calls", [])
            messages = self._process_tool_calls(tool_calls, toolkit, messages)

            # Extract tool messages for the conversation
            tool_messages = [
                FunctionMessage(
                    tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
                )
                for m in messages
                if m.get("role") == "tool"
            ]

            # Add tool messages to conversation
            conversation.add_messages(tool_messages)

        # Now make a streaming request for the final response
        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        response = self._client.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        message_content = ""

        for line in response.iter_lines():
            # Convert bytes to string if needed
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line

            if not line_str or line_str == "data: [DONE]":
                continue

            if line_str.startswith("data: "):
                json_str = line_str.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if (
                            "choices" in chunk
                            and chunk["choices"]
                            and "delta" in chunk["choices"][0]
                            and "content" in chunk["choices"][0]["delta"]
                        ):
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                except json.JSONDecodeError:
                    pass

        # Add the final agent message to the conversation
        conversation.add_message(AgentMessage(content=message_content))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response from Groq model.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
            toolkit (Toolkit): Optional toolkit for tool conversion.
            tool_choice (Dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Yields:
            AsyncIterator[str]: Streamed response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        # First, make a non-streaming request to handle tool calls
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else [],
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as client:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()

        # Process tool calls if any
        if "choices" in tool_response and tool_response["choices"]:
            assistant_message = tool_response["choices"][0]["message"]
            messages.append(assistant_message)

            tool_calls = assistant_message.get("tool_calls", [])
            messages = self._process_tool_calls(tool_calls, toolkit, messages)

            # Extract tool messages for the conversation
            tool_messages = [
                FunctionMessage(
                    tool_call_id=m["tool_call_id"], name=m["name"], content=m["content"]
                )
                for m in messages
                if m.get("role") == "tool"
            ]

            # Add tool messages to conversation
            conversation.add_messages(tool_messages)

        # Now make a streaming request for the final response
        payload["messages"] = messages
        payload["stream"] = True
        payload.pop("tools", None)
        payload.pop("tool_choice", None)

        message_content = ""

        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as client:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line or line == "data: [DONE]":
                    continue

                if line.startswith("data: "):
                    json_str = line.replace("data: ", "")
                    try:
                        if json_str:
                            chunk = json.loads(json_str)
                            if (
                                "choices" in chunk
                                and chunk["choices"]
                                and "delta" in chunk["choices"][0]
                                and "content" in chunk["choices"][0]["delta"]
                            ):
                                delta = chunk["choices"][0]["delta"]["content"]
                                message_content += delta
                                yield delta
                    except json.JSONDecodeError:
                        pass

        # Add the final agent message to the conversation
        conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> List[IConversation]:
        """
        Processes a batch of conversations sequentially.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            toolkit (Toolkit): Optional toolkit for tool conversion.
            tool_choice (Dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            List[Conversation]: List of updated conversations with responses.
        """
        results = []
        for conv in conversations:
            result = self.predict(
                conversation=conv,
                toolkit=toolkit,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            results.append(result)
        return results

    async def abatch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit = None,
        tool_choice: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations concurrently with limited concurrency.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            toolkit (Toolkit): Optional toolkit for tool conversion.
            tool_choice (Dict[str, Any]): Tool selection strategy.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[Conversation]: List of updated conversations with responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: Conversation) -> Conversation:
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
        Returns the list of allowed models for Groq API.

        Returns:
            List[str]: A list of allowed model names.
        """
        models_data = [
            "moonshotai/kimi-k2-instruct",
            "moonshotai/kimi-k2-instruct-0905",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]
        return models_data
