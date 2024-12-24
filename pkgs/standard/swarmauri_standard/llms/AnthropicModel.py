import json
from typing import List, Dict, Literal, AsyncIterator, Iterator
import asyncio
import httpx
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri.utils.duration_manager import DurationManager
from swarmauri_base.llms.LLMBase import LLMBase


class AnthropicModel(LLMBase):
    """
    A class representing an integration with the Anthropic API to interact with the Claude model series.

    Attributes:
        api_key (str): The API key for accessing the Anthropic API.
        allowed_models (List[str]): List of models that can be used with this class.
        name (str): The default model name.
        type (Literal): Specifies the type of the model as "AnthropicModel".

    Link to Allowed Models: https://docs.anthropic.com/en/docs/about-claude/models#model-names
    Link to API KEY: https://console.anthropic.com/settings/keys
    """

    _BASE_URL: str = PrivateAttr("https://api.anthropic.com/v1")
    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()

    api_key: str
    allowed_models: List[str] = [
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-5-sonnet-20240620",
        "claude-2.1",
        "claude-2.0",
    ]
    name: str = "claude-3-haiku-20240307"
    type: Literal["AnthropicModel"] = "AnthropicModel"

    def __init__(self, **data):
        super().__init__(**data)
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        self._client = httpx.Client(
            headers=headers, base_url=self._BASE_URL, timeout=30
        )
        self._async_client = httpx.AsyncClient(
            headers=headers, base_url=self._BASE_URL, timeout=30
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats a list of message objects into a format suitable for the Anthropic API.

        Args:
            messages (List[SubclassUnion[MessageBase]]): A list of message objects from a conversation.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the 'content' and 'role' of each message,
                                  excluding system messages.
        """
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties)
            for message in messages
            if message.role != "system"
        ]
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        """
        Extracts the most recent system context from a list of messages.

        Args:
            messages (List[SubclassUnion[MessageBase]]): A list of message objects from a conversation.

        Returns:
            str: The content of the most recent system context if present, otherwise None.
        """
        # Iterate through messages in reverse to get the most recent system message
        for message in reversed(messages):
            if message.role == "system":
                return message.content
        return None

    def _prepare_usage_data(
        self,
        usage_data: Dict[str, int],
        prompt_time: float,
        completion_time: float,
    ) -> UsageData:
        """
        Prepares usage data for logging and tracking API usage metrics.

        Args:
            usage_data (Dict[str, int]): The raw usage data containing token counts.
            prompt_time (float): The duration of the prompt preparation phase.
            completion_time (float): The duration of the completion phase.

        Returns:
            UsageData: A data object encapsulating the usage information.
        """
        total_time = prompt_time + completion_time
        prompt_tokens = usage_data.get("input_tokens", 0)
        completion_tokens = usage_data.get("output_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens

        return UsageData(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ) -> Conversation:
        """
        Sends a prediction request to the Anthropic API and processes the response.

        Args:
            conversation (Conversation): The conversation object containing the history of messages.
            temperature (float, optional): The temperature setting for controlling response randomness.
            max_tokens (int, optional): The maximum number of tokens for the generated response.

        Returns:
            Conversation: The updated conversation object with the generated response added.
        """
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_context:
            payload["system"] = system_context

        with DurationManager() as prompt_timer:
            response = self._client.post("/messages", json=payload)
            response.raise_for_status()
            response_data = response.json()

        with DurationManager() as completion_timer:
            message_content = response_data["content"][0]["text"]

        usage_data = response_data["usage"]
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ) -> Iterator[str]:
        """
        Streams the response from the model in real-time.

        Args:
            conversation (Conversation): The conversation history and context.
            temperature (float, optional): Sampling temperature for the model.
            max_tokens (int, optional): Maximum number of tokens for the response.

        Yields:
            str: Incremental parts of the model's response as they are received.
        """
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if system_context:
            payload["system"] = system_context

        message_content = ""
        usage_data = {"input_tokens": 0, "output_tokens": 0}

        with DurationManager() as prompt_timer:
            with self._client.stream("POST", "/messages", json=payload) as response:
                response.raise_for_status()
                with DurationManager() as completion_timer:
                    for line in response.iter_lines():
                        if line:
                            try:
                                # Handle the case where line might be bytes or str
                                line_text = (
                                    line
                                    if isinstance(line, str)
                                    else line.decode("utf-8")
                                )
                                if line_text.startswith("data: "):
                                    line_text = line_text.removeprefix("data: ")

                                if not line_text or line_text == "[DONE]":
                                    continue

                                event = json.loads(line_text)
                                if event["type"] == "message_start":
                                    usage_data["input_tokens"] = event["message"][
                                        "usage"
                                    ]["input_tokens"]
                                elif event["type"] == "content_block_start":
                                    continue
                                elif event["type"] == "content_block_delta":
                                    delta = event["delta"]["text"]
                                    message_content += delta
                                    yield delta
                                elif event["type"] == "message_delta":
                                    if "usage" in event:
                                        usage_data["output_tokens"] = event["usage"][
                                            "output_tokens"
                                        ]
                                elif event["type"] == "message_stop":
                                    if (
                                        "message" in event
                                        and "usage" in event["message"]
                                    ):
                                        usage_data = event["message"]["usage"]
                            except (json.JSONDecodeError, KeyError) as e:
                                continue

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ) -> Conversation:
        """
        Asynchronously sends a request to the model for generating a prediction.

        Args:
            conversation (Conversation): The conversation history and context.
            temperature (float, optional): Sampling temperature for the model.
            max_tokens (int, optional): Maximum number of tokens for the response.

        Returns:
            Conversation: The updated conversation including the model's response.
        """
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_context:
            payload["system"] = system_context

        with DurationManager() as prompt_timer:
            response = await self._async_client.post("/messages", json=payload)
            response.raise_for_status()
            response_data = response.json()

        with DurationManager() as completion_timer:
            message_content = response_data["content"][0]["text"]

        usage_data = response_data["usage"]
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response from the model in real-time.

        Args:
            conversation (Conversation): The conversation history and context.
            temperature (float, optional): Sampling temperature for the model.
            max_tokens (int, optional): Maximum number of tokens for the response.

        Yields:
            str: Incremental parts of the model's response as they are received.
        """
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if system_context:
            payload["system"] = system_context

        message_content = ""
        usage_data = {"input_tokens": 0, "output_tokens": 0}

        with DurationManager() as prompt_timer:
            async with self._async_client.stream(
                "POST", "/messages", json=payload
            ) as response:
                response.raise_for_status()
                with DurationManager() as completion_timer:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                # Handle the case where line might be bytes or str
                                line_text = (
                                    line
                                    if isinstance(line, str)
                                    else line.decode("utf-8")
                                )
                                if line_text.startswith("data: "):
                                    line_text = line_text.removeprefix("data: ")

                                if not line_text or line_text == "[DONE]":
                                    continue

                                event = json.loads(line_text)
                                if event["type"] == "message_start":
                                    usage_data["input_tokens"] = event["message"][
                                        "usage"
                                    ]["input_tokens"]
                                elif event["type"] == "content_block_start":
                                    continue
                                elif event["type"] == "content_block_delta":
                                    delta = event["delta"]["text"]
                                    message_content += delta
                                    yield delta
                                elif event["type"] == "message_delta":
                                    if "usage" in event:
                                        usage_data["output_tokens"] = event["usage"][
                                            "output_tokens"
                                        ]
                                elif event["type"] == "message_stop":
                                    if (
                                        "message" in event
                                        and "usage" in event["message"]
                                    ):
                                        usage_data = event["message"]["usage"]
                            except (json.JSONDecodeError, KeyError) as e:
                                continue

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self, conversations: List[Conversation], temperature=0.7, max_tokens=256
    ) -> List:
        """
        Processes multiple conversations synchronously.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float, optional): Sampling temperature for the model.
            max_tokens (int, optional): Maximum number of tokens for the response.

        Returns:
            List[Conversation]: A list of updated conversations including the model's responses.
        """
        return [
            self.predict(conv, temperature=temperature, max_tokens=max_tokens)
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
        max_concurrent=5,
    ) -> List:
        """
        Processes multiple conversations asynchronously with controlled concurrency.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float, optional): Sampling temperature for the model.
            max_tokens (int, optional): Maximum number of tokens for the response.
            max_concurrent (int, optional): Maximum number of concurrent tasks.

        Returns:
            List[Conversation]: A list of updated conversations including the model's responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv, temperature=temperature, max_tokens=max_tokens
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
