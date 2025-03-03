import asyncio
import json
from typing import AsyncIterator, Iterator
from typing import List, Dict, Literal, Any
import logging
from anthropic import AsyncAnthropic, Anthropic
from swarmauri.messages.concrete import FunctionMessage
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.schema_converters.concrete.AnthropicSchemaConverter import (
    AnthropicSchemaConverter,
)


class AnthropicToolModel(LLMBase):
    """
    A specialized LLM class for interacting with Anthropic's models, including tool use capabilities.

    This class facilitates model predictions, streaming, and batch processing with support for
    tools. It integrates with the Anthropic API for model interactions and handles both synchronous
    and asynchronous operations.

    Attributes:
        api_key (str): The API key for accessing Anthropic's services.
        allowed_models (List[str]): A list of supported Anthropic model names.
        name (str): The name of the default model used for predictions.
        type (Literal): Specifies the class type as "AnthropicToolModel".

    Linked to Allowed Models: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    Link to API KEY: https://console.anthropic.com/settings/keys
    """

    api_key: str
    allowed_models: List[str] = [
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        "claude-3-5-sonnet-20240620",
        "claude-3-sonnet-20240229",
    ]
    name: str = "claude-3-sonnet-20240229"
    type: Literal["AnthropicToolModel"] = "AnthropicToolModel"

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        """
        Converts a list of tools into a format compatible with Anthropic's API schema.

        Args:
            tools: A dictionary of tools to be converted.

        Returns:
            A list of dictionaries formatted for use with Anthropic's tool schema.
        """
        schema_result = [
            AnthropicSchemaConverter().convert(tools[tool]) for tool in tools
        ]
        logging.info(schema_result)
        return schema_result

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats a list of conversation messages for Anthropic's API.

        Args:
            messages: A list of message objects.

        Returns:
            A list of dictionaries with formatted message data.
        """
        message_properties = ["content", "role", "tool_call_id", "tool_calls"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "assistant"
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
        """
        Generates a prediction using Anthropic's model and handles tool interactions if necessary.

        Args:
            conversation: The conversation object containing the current conversation state.
            toolkit: An optional toolkit for tool usage in the conversation.
            tool_choice: Specifies the tool choice for the model (e.g., "auto").
            temperature: The temperature for sampling output (default is 0.7).
            max_tokens: The maximum number of tokens to generate (default is 1024).

        Returns:
            Updated conversation object with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)

        client = Anthropic(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = {"type": "auto"}

        tool_response = client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )

        logging.info(f"tool_response: {tool_response}")
        tool_text_response = None
        if tool_response.content[0].type == "text":
            tool_text_response = tool_response.content[0].text
            logging.info(f"tool_text_response: {tool_text_response}")

        for tool_call in tool_response.content:
            if tool_call.type == "tool_use":
                func_name = tool_call.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.input
                func_result = func_call(**func_args)

        if tool_text_response:
            agent_response = f"{tool_text_response} {func_result}"
        else:
            agent_response = f"{func_result}"

        agent_message = AgentMessage(content=agent_response)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

    async def apredict(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ):
        """
        Asynchronously generates a prediction using Anthropic's model and handles tool interactions if necessary.

        Args:
            conversation: The conversation object containing the current conversation state.
            toolkit: An optional toolkit for tool usage in the conversation.
            tool_choice: Specifies the tool choice for the model (e.g., "auto").
            temperature: The temperature for sampling output (default is 0.7).
            max_tokens: The maximum number of tokens to generate (default is 1024).

        Returns:
            Updated conversation object with the model's response.
        """
        async_client = AsyncAnthropic(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        logging.info(f"formatted_messages: {formatted_messages}")

        if toolkit and not tool_choice:
            tool_choice = {"type": "auto"}

        tool_response = await async_client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
        )

        logging.info(f"tools: {self._schema_convert_tools(toolkit.tools)}")

        logging.info(f"tool_response: {tool_response}")
        tool_text_response = None
        if tool_response.content[0].type == "text":
            tool_text_response = tool_response.content[0].text
            logging.info(f"tool_text_response: {tool_text_response}")

        func_result = None
        for tool_call in tool_response.content:
            if tool_call.type == "tool_use":
                func_name = tool_call.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.input
                func_result = func_call(**func_args)

        if tool_text_response:
            agent_response = f"{tool_text_response} {func_result}"
        else:
            agent_response = f"{func_result}"

        agent_message = AgentMessage(content=agent_response)
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
        """
        Streams model responses in real-time for interactive conversations.

        Args:
            conversation: The conversation object containing the current conversation state.
            toolkit: An optional toolkit for tool usage in the conversation.
            tool_choice: Specifies the tool choice for the model (e.g., "auto").
            temperature: The temperature for sampling output (default is 0.7).
            max_tokens: The maximum number of tokens to generate (default is 1024).

        Yields:
            Chunks of response text as they are received from the model.
        """
        client = Anthropic(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = {"type": "auto"}

        tool_response = client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
        )

        logging.info(f"tool_response: {tool_response}")
        tool_text_response = None
        if tool_response.content[0].type == "text":
            tool_text_response = tool_response.content[0].text
            logging.info(f"tool_text_response: {tool_text_response}")

        agent_message = AgentMessage(content=tool_text_response)
        conversation.add_message(agent_message)

        for tool_call in tool_response.content:
            if tool_call.type == "tool_use":
                func_name = tool_call.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.input
                func_result = func_call(**func_args)

                func_message = FunctionMessage(
                    content=json.dumps(func_result),
                    name=func_name,
                    tool_call_id=tool_call.id,
                )
                conversation.add_message(func_message)

        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        stream_response = client.messages.create(
            max_tokens=max_tokens,
            messages=formatted_messages,
            model=self.name,
            stream=True,
        )
        message_content = ""

        for chunk in stream_response:
            logging.info(chunk)
            if chunk.type == "content_block_delta":
                if chunk.delta.type == "text":
                    logging.info(chunk.delta.text)
                    message_content += chunk.delta.text
                    yield chunk.delta.text

        conversation.add_message(AgentMessage(content=message_content))

    async def astream(
        self,
        conversation,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams model responses in real-time for interactive conversations.

        Args:
            conversation: The conversation object containing the current conversation state.
            toolkit: An optional toolkit for tool usage in the conversation.
            tool_choice: Specifies the tool choice for the model (e.g., "auto").
            temperature: The temperature for sampling output (default is 0.7).
            max_tokens: The maximum number of tokens to generate (default is 1024).

        Yields:
            Chunks of response text or JSON as they are received from the model.
        """
        async_client = AsyncAnthropic(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        logging.info(formatted_messages)

        if toolkit and not tool_choice:
            tool_choice = {"type": "auto"}

        stream = await async_client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools) if toolkit else None,
            tool_choice=tool_choice,
            stream=True,
        )

        logging.info(f"tools: {self._schema_convert_tools(toolkit.tools)}")
        logging.info(f"message: {formatted_messages}")

        collected_content = []
        async for chunk in stream:
            logging.info(chunk)
            if chunk.type == "content_block_delta":
                if chunk.delta.type == "text_delta":
                    collected_content.append(chunk.delta.text)
                    yield chunk.delta.text
                if chunk.delta.type == "input_json_delta":
                    collected_content.append(chunk.delta.partial_json)
                    yield chunk.delta.partial_json

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
        """
        Processes a batch of conversations sequentially for model predictions.

        Args:
            conversations: A list of conversation objects.
            toolkit: An optional toolkit for tool usage in the conversation.
            tool_choice: Specifies the tool choice for the model (e.g., "auto").
            temperature: The temperature for sampling output (default is 0.7).
            max_tokens: The maximum number of tokens to generate (default is 1024).

        Returns:
            A list of updated conversation objects with model responses.
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
        conversations: List,
        toolkit=None,
        tool_choice=None,
        temperature=0.7,
        max_tokens=1024,
        max_concurrent=5,
    ) -> List:
        """
        Asynchronously processes a batch of conversations for model predictions with concurrency control.

        Args:
            conversations: A list of conversation objects.
            toolkit: An optional toolkit for tool usage in the conversation.
            tool_choice: Specifies the tool choice for the model (e.g., "auto").
            temperature: The temperature for sampling output (default is 0.7).
            max_tokens: The maximum number of tokens to generate (default is 1024).
            max_concurrent: The maximum number of concurrent requests (default is 5).

        Returns:
            A list of updated conversation objects with model responses.
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
