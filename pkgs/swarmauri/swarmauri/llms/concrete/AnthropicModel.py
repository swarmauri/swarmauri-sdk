import asyncio
import json
import requests
from typing import List, Dict, Literal, AsyncGenerator, Generator
from swarmauri_core.typing import SubclassUnion
from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage, UsageData
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.utils.duration_manager import DurationManager
from swarmauri.llms.base.LLMBase import LLMBase


class AnthropicModel(LLMBase):
    """
    A class representing an integration with the Anthropic API to interact with the Claude model series.

    Attributes:
        api_key (str): The API key for accessing the Anthropic API.
        allowed_models (List[str]): List of models that can be used with this class.
        name (str): The default model name.
        type (Literal): Specifies the type of the model as "AnthropicModel".

    Provider resources: https://docs.anthropic.com/en/docs/about-claude/models#model-names
    Link to API KEY: https://console.anthropic.com/settings/keys
    """

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
        Extracts the system context from a list of messages.

        Args:
            messages (List[SubclassUnion[MessageBase]]): A list of message objects from a conversation.

        Returns:
            str: The content of the system context if present, otherwise None.
        """

        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

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
            UsageData: A data object encapsulating the prompt, completion, and total token counts,
                       along with the timing information.
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

    def predict(self, conversation: Conversation, temperature=0.7, max_tokens=256):
        """
        Sends a prediction request to the Anthropic API and processes the response.

        Args:
            conversation (Conversation): The conversation object containing the history of messages.
            temperature (float, optional): The temperature setting for controlling response randomness. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the generated response. Defaults to 256.

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
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
            )
            response_data = response.json()

        with DurationManager() as completion_timer:
            message_content = response_data["content"][0]["text"]

        usage_data = response_data["usage"]
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    def stream(self, conversation: Conversation, temperature=0.7, max_tokens=256):
        """
        Streams the response from the model in real-time.

        Args:
            conversation (Conversation): The conversation history and context.
            temperature (float, optional): Sampling temperature for the model. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens for the response. Defaults to 256.

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
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                stream=True,
            )

            with DurationManager() as completion_timer:
                for line in response.iter_lines():
                    if line:
                        try:
                            event = json.loads(
                                line.decode("utf-8").removeprefix("data: ")
                            )
                            if event["type"] == "message_start":
                                usage_data["input_tokens"] = event["message"]["usage"][
                                    "input_tokens"
                                ]
                            elif event["type"] == "content_block_start":
                                continue
                            elif event["type"] == "content_block_delta":
                                delta = event["delta"]["text"]
                                message_content += delta
                                yield delta  # Yield each token as it comes
                            elif event["type"] == "message_delta":
                                if "usage" in event:
                                    usage_data["output_tokens"] = event["usage"][
                                        "output_tokens"
                                    ]
                            elif event["type"] == "message_stop":
                                if "message" in event and "usage" in event["message"]:
                                    usage_data = event["message"]["usage"]
                        except json.JSONDecodeError:
                            continue
                        except KeyError:
                            continue

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    async def apredict(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ):
        """
        Asynchronously sends a request to the model for generating a prediction.

        Args:
            conversation (Conversation): The conversation history and context.
            temperature (float, optional): Sampling temperature for the model. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens for the response. Defaults to 256.

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
            response = await asyncio.to_thread(
                requests.post,
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
            )
            response_data = response.json()

        with DurationManager() as completion_timer:
            message_content = response_data["content"][0]["text"]

        usage_data = response_data["usage"]
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    async def astream(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ):
        """
        Asynchronously streams the response from the model in real-time.

        Args:
            conversation (Conversation): The conversation history and context.
            temperature (float, optional): Sampling temperature for the model. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens for the response. Defaults to 256.

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

        class AsyncLineIterator:
            def __init__(self, response):
                self.response = response
                self._iter = response.iter_lines()

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    line = await asyncio.to_thread(next, self._iter)
                    if line is None:
                        raise StopAsyncIteration
                    return line
                except StopIteration:
                    raise StopAsyncIteration

        with DurationManager() as prompt_timer:
            response = await asyncio.to_thread(
                requests.post,
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                stream=True,
            )

            with DurationManager() as completion_timer:
                async for line in AsyncLineIterator(response):
                    if line:
                        try:
                            event = json.loads(
                                line.decode("utf-8").removeprefix("data: ")
                            )
                            if event["type"] == "message_start":
                                usage_data["input_tokens"] = event["message"]["usage"][
                                    "input_tokens"
                                ]
                            elif event["type"] == "content_block_start":
                                continue
                            elif event["type"] == "content_block_delta":
                                delta = event["delta"]["text"]
                                message_content += delta
                                yield delta  # Yield each token as it comes
                            elif event["type"] == "message_delta":
                                if "usage" in event:
                                    usage_data["output_tokens"] = event["usage"][
                                        "output_tokens"
                                    ]
                            elif event["type"] == "message_stop":
                                if "message" in event and "usage" in event["message"]:
                                    usage_data = event["message"]["usage"]
                        except json.JSONDecodeError:
                            continue
                        except KeyError:
                            continue

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
    ) -> List:
        """
        Processes multiple conversations synchronously.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float, optional): Sampling temperature for the model. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens for the response. Defaults to 256.

        Returns:
            List[Conversation]: A list of updated conversations including the model's responses.
        """
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
            )
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
            temperature (float, optional): Sampling temperature for the model. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens for the response. Defaults to 256.
            max_concurrent (int, optional): Maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List[Conversation]: A list of updated conversations including the model's responses.
        """

        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
