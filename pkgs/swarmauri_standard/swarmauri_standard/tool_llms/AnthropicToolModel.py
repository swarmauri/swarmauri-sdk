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
from swarmauri_standard.schema_converters.AnthropicSchemaConverter import (
    AnthropicSchemaConverter,
)
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

    _BASE_URL: str = PrivateAttr("https://api.anthropic.com/v1")
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()

    api_key: SecretStr
    allowed_models: List[str] = []
    name: str = ""
    type: Literal["AnthropicToolModel"] = "AnthropicToolModel"

    timeout: float = 600.0

    def __init__(self, **data):
        super().__init__(**data)
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key.get_secret_value(),
            "anthropic-version": "2023-06-01",
        }
        self._client = httpx.Client(
            headers=headers, base_url=self._BASE_URL, timeout=self.timeout
        )
        self._async_client = httpx.AsyncClient(
            headers=headers, base_url=self._BASE_URL, timeout=self.timeout
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

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
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
            if message.role != "assistant"
        ]
        return formatted_messages

    def _process_tool_calls(self, tool_calls, toolkit, messages) -> List[MessageBase]:
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
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                        "tool_call_id": tool_call["id"],
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

        logging.info(f"tool_response: {response_data}")

        # Extract text content if available
        tool_text_response = None
        if response_data["content"] and response_data["content"][0]["type"] == "text":
            tool_text_response = response_data["content"][0]["text"]
            logging.info(f"tool_text_response: {tool_text_response}")

        # Process tool calls
        tool_calls = [c for c in response_data["content"] if c["type"] == "tool_use"]
        messages = formatted_messages.copy()
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

        # For multiturn, we need to make a follow-up request with the tool results
        if multiturn and tool_calls:
            # Create a new payload without tools
            followup_payload = {
                "model": self.name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            followup_response = self._client.post("/messages", json=followup_payload)
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
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        multiturn: bool = True,
        temperature=0.7,
        max_tokens=1024,
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
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> Iterator[str]:
        """
        Streams the response for a conversation in real-time, yielding text as it is received.

        Args:
            conversation (IConversation): The current conversation object.
            toolkit: Optional toolkit object for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto' for automatic tool usage.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): The maximum number of tokens in the response.

        Yields:
            Iterator[str]: Chunks of text received from the streaming response.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice if toolkit and tool_choice else {"type": "auto"},
            "stream": True,
        }

        message_content = ""
        tool_calls = []

        with self._client.stream("POST", "/messages", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        # Handle the case where line might be bytes or str
                        line_text = (
                            line if isinstance(line, str) else line.decode("utf-8")
                        )
                        if line_text.startswith("data: "):
                            line_text = line_text.removeprefix("data: ")

                        if not line_text or line_text == "[DONE]":
                            continue

                        event = json.loads(line_text)
                        if event["type"] == "content_block_delta":
                            if event["delta"]["type"] == "text":
                                delta = event["delta"]["text"]
                                message_content += delta
                                yield delta
                        elif event["type"] == "tool_use":
                            tool_calls.append(event)
                    except (json.JSONDecodeError, KeyError) as e:
                        logging.warning(f"Error parsing stream event: {e}")
                        continue

        # Process tool calls if any
        messages = formatted_messages.copy()
        self._process_tool_calls(tool_calls, toolkit, messages)

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

        # Add the final agent message
        agent_message = AgentMessage(content=message_content)
        conversation.add_message(agent_message)

        return conversation

    async def astream(
        self,
        conversation: IConversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response for a conversation, yielding text in real-time.

        Args:
            conversation (IConversation): The current conversation object.
            toolkit: Optional toolkit object for tool-based responses.
            tool_choice: Optional parameter to choose specific tools or set to 'auto' for automatic tool usage.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): The maximum number of tokens in the response.

        Yields:
            AsyncIterator[str]: Chunks of text received from the streaming response.
        """
        formatted_messages = self._format_messages(conversation.history)
        logging.info(formatted_messages)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": self._schema_convert_tools(toolkit.tools) if toolkit else None,
            "tool_choice": tool_choice if toolkit and tool_choice else {"type": "auto"},
            "stream": True,
        }

        collected_content = []
        tool_calls = []

        async with self._async_client.stream(
            "POST", "/messages", json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        # Handle the case where line might be bytes or str
                        line_text = (
                            line if isinstance(line, str) else line.decode("utf-8")
                        )
                        if line_text.startswith("data: "):
                            line_text = line_text.removeprefix("data: ")

                        if not line_text or line_text == "[DONE]":
                            continue

                        event = json.loads(line_text)
                        if event["type"] == "content_block_delta":
                            if event["delta"]["type"] == "text_delta":
                                collected_content.append(event["delta"]["text"])
                                yield event["delta"]["text"]
                            if event["delta"]["type"] == "input_json_delta":
                                collected_content.append(event["delta"]["partial_json"])
                                yield event["delta"]["partial_json"]
                        elif event["type"] == "tool_use":
                            tool_calls.append(event)
                    except (json.JSONDecodeError, KeyError) as e:
                        logging.warning(f"Error parsing stream event: {e}")
                        continue

        # Process tool calls if any
        messages = formatted_messages.copy()
        self._process_tool_calls(tool_calls, toolkit, messages)

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

        # Create the final agent message
        full_content = "".join(collected_content)
        agent_message = AgentMessage(content=full_content)
        conversation.add_message(agent_message)

    def batch(
        self,
        conversations: List[IConversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
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
        conversations: List[IConversation],
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
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
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229",
            "claude-3-5-sonnet-20240620",
        ]
        return allowed_models
