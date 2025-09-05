import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type

import httpx
from pydantic import PrivateAttr, SecretStr
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
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "OpenAIToolModel")
class OpenAIToolModel(ToolLLMBase):
    """
    OpenAIToolModel provides an interface to interact with OpenAI's models for tool usage.

    This class supports synchronous and asynchronous predictions, streaming of responses,
    and batch processing. It communicates with the OpenAI API to manage conversations, format messages,
    and handle tool-related functions.

    Attributes:
        api_key (SecretStr): API key to authenticate with OpenAI API.
        allowed_models (List[str]): List of permissible model names.
        name (str): Default model name for predictions.
        type (Literal): Type identifier for the model.

    Provider resources: https://platform.openai.com/docs/guides/function-calling/which-models-support-function-calling
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        "gpt-5-2025-08-07",
        "gpt-5-mini-2025-08-07",
        "gpt-5-nano-2025-08-07",
        "gpt-4.1-2025-04-14",
        "gpt-oss-20b",
        "gpt-oss-120b",
        "gpt-4o-mini",
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-0125-preview",
        "gpt-4-0613",
        "gpt-3.5-turbo-0125",
    ]
    name: str = "gpt-4o-2024-05-13"

    type: Literal["OpenAIToolModel"] = "OpenAIToolModel"
    BASE_URL: str = "https://api.openai.com/v1/chat/completions"
    _headers: Dict[str, str] = PrivateAttr(default=None)

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
        if not self.name and self.allowed_models:
            self.name = self.allowed_models[0]

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Returns the schema converter class for OpenAI API.

        Returns:
            Type[SchemaConverterBase]: The OpenAISchemaConverter class.
        """
        return OpenAISchemaConverter

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        """
        Convert a dictionary of tools to the schema format required by OpenAI API.

        Args:
            tools (dict): A dictionary of tool objects.

        Returns:
            List[Dict[str, Any]]: A list of converted tool schemas.
        """
        converter = self.get_schema_converter()()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history messages for the OpenAI API.

        Args:
            messages (List[Type[MessageBase]]): List of message objects from the conversation history.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """
        message_properties = ["content", "role", "name", "tool_call_id", "tool_calls"]
        return [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "tool"
        ]

    def _process_tool_calls(self, tool_calls, toolkit, messages) -> List[Dict]:
        """
        Processes a list of tool calls and appends the results to the messages list.

        Args:
            tool_calls (list): A list of dictionaries representing tool calls. Each dictionary should contain
                               a "function" key with a nested dictionary that includes the "name" and "arguments"
                               of the function to be called, and an "id" key for the tool call identifier.
            toolkit (object): An object that provides access to tools via the `get_tool_by_name` method.
            messages (list): A list of message dictionaries to which the results of the tool calls will be appended.

        Returns:
            List[Dict]: The updated list of messages with the results of the tool calls appended.
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
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        multiturn: bool = True,
        temperature=0.7,
        max_tokens=1024,
    ) -> IConversation:
        """
        Makes a synchronous prediction using the OpenAI model.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            multiturn (bool): Whether to follow up a tool call with another LLM request.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum token limit.

        Returns:
            IConversation: Updated conversation with agent responses and tool calls.
        """
        formatted_messages = self._format_messages(conversation.history)
        logging.info(f"Formatted messages: {formatted_messages}")

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

        messages = formatted_messages.copy()
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

        # For multiturn and if there were tool calls, make a follow-up request
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.BASE_URL, headers=self._headers, json=payload
                )
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
            conversation (IConversation): Conversation instance with message history.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
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
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice or "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()
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

        # For multiturn and if there were tool calls, make a follow-up request
        if multiturn and tool_calls:
            payload["messages"] = messages
            payload.pop("tools", None)
            payload.pop("tool_choice", None)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.BASE_URL, headers=self._headers, json=payload
                )
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
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> Iterator[str]:
        """
        Streams response from OpenAI model in real-time.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
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

        # First request to handle tool calls
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()
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

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.BASE_URL, headers=self._headers, json=payload)
            response.raise_for_status()

        message_content = ""

        for line in response.iter_lines():
            # Handle bytes conversion if needed
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
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams response from OpenAI model.

        Parameters:
            conversation (IConversation): Conversation instance with message history.
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

        # First request to handle tool calls
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
            response.raise_for_status()
            tool_response = response.json()

        messages = formatted_messages.copy()
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

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.BASE_URL, headers=self._headers, json=payload
            )
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
        conversations: List[IConversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> List[IConversation]:
        """
        Synchronously processes multiple conversations and generates responses for each.

        Args:
            conversations (List[IConversation]): List of conversations to process.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.

        Returns:
            List[IConversation]: List of updated conversations with generated responses.
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
        conversations: List[IConversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        max_concurrent=5,
    ) -> List[IConversation]:
        """
        Asynchronously processes multiple conversations with controlled concurrency.

        Args:
            conversations (List[IConversation]): List of conversations to process.
            toolkit: Optional toolkit for tool conversion.
            tool_choice: Tool selection strategy.
            temperature (float): Sampling temperature for response diversity.
            max_tokens (int): Maximum tokens for each response.
            max_concurrent (int): Maximum number of concurrent tasks.

        Returns:
            List[IConversation]: List of updated conversations with generated responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> IConversation:
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
        Returns the list of allowed models for OpenAI API.

        Returns:
            List[str]: A list of allowed model names.
        """
        models_data = [
            "gpt-5-2025-08-07",
            "gpt-5-mini-2025-08-07",
            "gpt-5-nano-2025-08-07",
            "gpt-4.1-2025-04-14",
            "gpt-oss-20b",
            "gpt-oss-120b",
            "gpt-4o-mini",
            "gpt-4o-2024-05-13",
            "gpt-4o-2024-08-06",
            "gpt-4o-mini-2024-07-18",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview",
            "gpt-4",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4-0125-preview",
            "gpt-4-0613",
            "gpt-3.5-turbo-0125",
        ]
        return models_data
