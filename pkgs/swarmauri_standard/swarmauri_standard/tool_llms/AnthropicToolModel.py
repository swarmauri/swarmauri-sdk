import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type

import httpx
from pydantic import PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
<<<<<<< HEAD
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.conversations.IConversation import IConversation

from swarmauri_standard.conversations.Conversation import Conversation
=======

from swarmauri_core.conversations.IConversation import IConversation


>>>>>>> upstream/mono/dev
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.schema_converters.AnthropicSchemaConverter import (
    AnthropicSchemaConverter,
)
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(ToolLLMBase, "AnthropicToolModel")
class AnthropicToolModel(ToolLLMBase):
    """
    A model class for integrating with the Anthropic API to enable tool-assisted AI interactions.

    This class supports various functionalities, including synchronous and asynchronous message prediction,
    streaming responses, and batch processing of conversations. It utilizes Anthropic's schema and tool-conversion
    techniques to facilitate enhanced interactions involving tool usage within conversations.

    Attributes:
        api_key (str): The API key used for authenticating requests to the Anthropic API.
        allowed_models (List[str]): A list of allowed model versions that can be used.
        name (str): The default model name used for predictions.
        type (Literal): The type of the model, which is set to "AnthropicToolModel".

    Linked to Allowed Models: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    Link to API KEY: https://console.anthropic.com/settings/keys
    """

    BASE_URL: str = "https://api.anthropic.com/v1"
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()
    api_key: SecretStr
    allowed_models: List[str] = [
        "claude-3-7-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-5-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-7-sonnet-20250219,claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    name: str = "claude-3-sonnet-20240229"

    type: Literal["AnthropicToolModel"] = "AnthropicToolModel"

    def __init__(self, **data: dict[str, Any]):
        super().__init__(**data)
        self._headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key.get_secret_value(),
            "anthropic-version": "2023-06-01",
        }
        self._client = httpx.Client(
            headers=self._headers, base_url=self.BASE_URL, timeout=self.timeout
        )
        self._async_client = httpx.AsyncClient(
            headers=self._headers, base_url=self.BASE_URL, timeout=self.timeout
        )

        self.allowed_models = self.allowed_models or self.get_allowed_models()
        self.name = self.name or self.allowed_models[0]

    def get_schema_converter(self) -> Type[SchemaConverterBase]:
        """
        Returns the schema converter class for Anthropic API.

        Returns:
            Type[SchemaConverterBase]: The AnthropicSchemaConverter class.
        """
        return AnthropicSchemaConverter

    def _schema_convert_tools(
        self, tools: Dict[str, SubclassUnion[ToolBase]]
    ) -> List[Dict[str, Any]]:
        """
        Converts a toolkit's tools to the Anthropic-compatible schema format.

        Args:
            tools (Dict): A dictionary of tools to be converted.

        Returns:
            List[Dict[str, Any]]: A list of tool schemas converted to the Anthropic format.
        """
        schema_result = [
            AnthropicSchemaConverter().convert(tools[tool]) for tool in tools
        ]
        logging.info(schema_result)
        return schema_result

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats a list of messages to a schema that matches the Anthropic API's expectations.

        Args:
            messages (List[Type[MessageBase]]): The conversation history.

        Returns:
            List[Dict[str, str]]: A formatted list of message dictionaries.
        """
        message_properties = ["content", "role", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "assistant" and message.role != "tool"
        ]
        return formatted_messages

    def _process_tool_calls(
        self, tool_calls: List[Any], toolkit: Toolkit, messages: List[Type[MessageBase]]
    ) -> List[Type[MessageBase]]:
        """
        Processes tool calls from Anthropic API response and adds the results to messages.

        Args:
            tool_calls (List): The tool calls from Anthropic response.
            toolkit: The toolkit containing the tools to call.
            messages (List): The current list of messages.

        Returns:
            List[MessageBase]: Updated list of messages with tool responses.
        """
        if not tool_calls:
            return messages

        tool_messages = []
        for tool_call in tool_calls:
            if tool_call["type"] == "tool_use":
                func_name = tool_call["name"]
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call["input"]
                func_result = func_call(**func_args)

                # Create a function message for the tool response
                tool_message = FunctionMessage(
                    content=json.dumps(func_result),
                    name=func_name,
                    tool_call_id=tool_call["id"],
                )

                tool_messages.append(tool_message)

                # Also add to the messages list for API calls
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "content": json.dumps(func_result),
                                "tool_use_id": tool_call["id"],
                            }
                        ],
                    }
                )

        return messages, tool_messages

    def predict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Conversation:
        """
        Predicts the response based on the given conversation and optional toolkit.

        Args:
            conversation (IConversation): The current conversation object.
            toolkit: Optional toolkit object containing tools for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto' for automatic tool usage.
            multiturn (bool): Whether to process multiple turns in a single call.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): The maximum number of tokens in the response.

        Returns:
            IConversation: The updated conversation with the assistant's response.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice if toolkit and tool_choice else {"type": "auto"},
        }

        response = self._client.post("/messages", json=payload)
        response.raise_for_status()
        response_data = response.json()

        # Extract text content if available
        tool_text_response = None
        if response_data["content"] and response_data["content"][0]["type"] == "text":
            tool_text_response = response_data["content"][0]["text"]
            logging.info(f"tool_text_response: {tool_text_response}")

        # Process tool calls
        tool_calls = [c for c in response_data["content"] if c["type"] == "tool_use"]
        messages = formatted_messages.copy()

        messages.append(
            {
                "role": "assistant",
                "content": response_data["content"],
            }
        )

        messages, tool_messages = self._process_tool_calls(
            tool_calls, toolkit, messages
        )

        conversation.add_messages(tool_messages)

        # For multiturn, we need to make a follow-up request with the tool results
        if multiturn and tool_calls:
            # Create a new payload without tools
            followup_payload = {
                "model": self.name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            logging.info(f"messages: {messages}")

            followup_response = self._client.post("/messages", json=followup_payload)
            logging.info(f"response: {followup_response.json()}")

            followup_response.raise_for_status()
            followup_data = followup_response.json()

            if (
                followup_data["content"]
                and followup_data["content"][0]["type"] == "text"
            ):
                tool_text_response = followup_data["content"][0]["text"]

        # Create and add the agent message
        if tool_text_response:
            agent_message = AgentMessage(content=tool_text_response)
            conversation.add_message(agent_message)

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        multiturn: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> IConversation:
        """
        Asynchronous version of the `predict` method to handle concurrent processing of requests.

        Args:
            conversation (IConversation): The current conversation object.
            toolkit: Optional toolkit object containing tools for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto' for automatic tool usage.
            multiturn (bool): Whether to process multiple turns in a single call.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): The maximum number of tokens in the response.

        Returns:
            IConversation: The updated conversation with the assistant's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        logging.info(f"formatted_messages: {formatted_messages}")

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice if toolkit and tool_choice else {"type": "auto"},
        }

        response = await self._async_client.post("/messages", json=payload)
        response.raise_for_status()
        response_data = response.json()

        logging.info(f"tool_response: {response_data}")

        # Extract text content if available
        tool_text_response = None
        if response_data["content"] and response_data["content"][0]["type"] == "text":
            tool_text_response = response_data["content"][0]["text"]
            logging.info(f"tool_text_response: {tool_text_response}")

        # Process tool calls
        tool_calls = [c for c in response_data["content"] if c["type"] == "tool_use"]
        messages = formatted_messages.copy()
        messages.append(
            {
                "role": "assistant",
                "content": response_data["content"],
            }
        )

        messages, tool_messages = self._process_tool_calls(
            tool_calls, toolkit, messages
        )

        conversation.add_messages(tool_messages)

        # For multiturn, we need to make a follow-up request with the tool results
        if multiturn and tool_calls:
            # Create a new payload without tools
            followup_payload = {
                "model": self.name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            followup_response = await self._async_client.post(
                "/messages", json=followup_payload
            )
            followup_response.raise_for_status()
            followup_data = followup_response.json()

            if (
                followup_data["content"]
                and followup_data["content"][0]["type"] == "text"
            ):
                tool_text_response = followup_data["content"][0]["text"]

        # Create and add the agent message
        if tool_text_response:
            agent_message = AgentMessage(content=tool_text_response)
            conversation.add_message(agent_message)

        return conversation

    def stream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """
        Streams the response for a conversation in real-time, yielding text as it is received.

        Args:
            conversation (IConversation): The current conversation object.
            toolkit: Optional toolkit object for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto'.
            temperature (float): Controls randomness in the output.
            max_tokens (int): Maximum tokens in the response.

        Yields:
            Iterator[str]: Chunks of text received from the streaming response.
        """
        formatted_messages = self._format_messages(conversation.history)

        # First, handle any tool calls that might be needed
        tool_payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice if toolkit and tool_choice else {"type": "auto"},
        }

        response = self._client.post("/messages", json=tool_payload)
        response.raise_for_status()
        tool_response_data = response.json()

        tool_calls = [
            c for c in tool_response_data["content"] if c["type"] == "tool_use"
        ]
        messages = formatted_messages.copy()

        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": tool_response_data["content"],
                }
            )

            messages, tool_messages = self._process_tool_calls(
                tool_calls, toolkit, messages
            )
            conversation.add_messages(tool_messages)

        stream_payload = {
            "model": self.name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        message_content = ""

        with self._client.stream("POST", "/messages", json=stream_payload) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                line_text = line.decode("utf-8") if isinstance(line, bytes) else line

                if not line_text.startswith("data: "):
                    continue

                json_str = line_text.removeprefix("data: ").strip()
                if not json_str or json_str == "[DONE]":
                    continue

                try:
                    event = json.loads(json_str)

                    if event["type"] == "content_block_delta":
                        if "delta" in event and "text" in event["delta"].get(
                            "type", ""
                        ):
                            delta_text = event["delta"].get("text", "")
                            if delta_text:
                                message_content += delta_text
                                yield delta_text

                    elif event["type"] == "tool_use":
                        logging.info(f"Tool use event in stream: {event}")

                except json.JSONDecodeError as e:
                    logging.warning(
                        f"Error parsing stream event: {e}\nLine: {line_text}"
                    )

        if message_content:
            conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def astream(
        self,
        conversation: Conversation,
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response for a conversation, yielding text in real-time.

        Args:
            conversation (IConversation): The current conversation object.
            toolkit: Optional toolkit object for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto'.
            temperature (float): Controls randomness in the output.
            max_tokens (int): Maximum tokens in the response.

        Yields:
            AsyncIterator[str]: Chunks of text received from the streaming response.
        """
        formatted_messages = self._format_messages(conversation.history)

        tool_payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice if toolkit and tool_choice else {"type": "auto"},
        }

        response = await self._async_client.post("/messages", json=tool_payload)
        response.raise_for_status()
        tool_response_data = response.json()

        tool_calls = [
            c for c in tool_response_data["content"] if c["type"] == "tool_use"
        ]
        messages = formatted_messages.copy()

        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": tool_response_data["content"],
                }
            )

            messages, tool_messages = self._process_tool_calls(
                tool_calls, toolkit, messages
            )
            conversation.add_messages(tool_messages)

        stream_payload = {
            "model": self.name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        message_content = ""

        async with self._async_client.stream(
            "POST", "/messages", json=stream_payload
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line:
                    continue

                if not line.startswith("data: "):
                    continue

                json_str = line.removeprefix("data: ").strip()
                if not json_str or json_str == "[DONE]":
                    continue

                try:
                    event = json.loads(json_str)

                    if event["type"] == "content_block_delta":
                        if (
                            "delta" in event
                            and event["delta"].get("type") == "text_delta"
                        ):
                            delta_text = event["delta"].get("text", "")
                            if delta_text:
                                message_content += delta_text
                                yield delta_text

                except json.JSONDecodeError as e:
                    logging.warning(f"Error parsing stream event: {e}\nLine: {line}")

        if message_content:
            conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> List[IConversation]:
        """
        Processes a batch of conversations in a synchronous manner.

        Args:
            conversations (List[IConversation]): A list of conversation objects to process.
            toolkit: Optional toolkit object for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto' for automatic tool usage.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): The maximum number of tokens in the response.

        Returns:
            List[IConversation]: A list of conversation objects updated with the assistant's responses.
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
        toolkit: Toolkit,
        tool_choice: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_concurrent=5,
    ) -> List[IConversation]:
        """
        Processes a batch of conversations asynchronously with limited concurrency.

        Args:
            conversations (List[IConversation]): A list of conversation objects to process.
            toolkit: Optional toolkit object for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto' for automatic tool usage.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): The maximum number of tokens in the response.
            max_concurrent (int): The maximum number of concurrent processes allowed.

        Returns:
            List[IConversation]: A list of conversation objects updated with the assistant's responses.
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
        Returns the list of allowed models for Anthropic API.

        Returns:
            List[str]: A list of allowed model names.
        """
        allowed_models = [
            "claude-3-7-sonnet-latest",
            "claude-3-5-haiku-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-opus-latest",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
        return allowed_models
