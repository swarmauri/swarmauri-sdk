import asyncio
from typing import List, Dict, Literal
from anthropic import AsyncAnthropic, Anthropic
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import UsageData
from swarmauri.utils.duration_manager import DurationManager


class AnthropicModel(LLMBase):
    """
    A class for integrating with the Anthropic API to facilitate interaction with various Claude models.
    This class supports synchronous and asynchronous prediction, streaming, and batch processing of conversations.

    Link to Allowed Models: https://docs.anthropic.com/en/docs/about-claude/models#model-names
    Link to API KEY: https://console.anthropic.com/settings/keys
    """

    api_key: str
    allowed_models: List[str] = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
    ]
    name: str = "claude-3-haiku-20240307"
    type: Literal["AnthropicModel"] = "AnthropicModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats messages by extracting necessary properties to prepare them for the model.

        Args:
            messages (List[SubclassUnion[MessageBase]]): The list of messages to format.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """

        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [
            message.model_dump(include=message_properties)
            for message in messages
            if message.role != "system"
        ]
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        """
        Extracts the system context from a list of messages if available.

        Args:
            messages (List[SubclassUnion[MessageBase]]): The list of messages to search through.

        Returns:
            str: The content of the system message if found; otherwise, None.
        """
        system_context = None
        for message in messages:
            if message.role == "system":
                system_context = message.content
        return system_context

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float,
        completion_time: float,
    ):
        """
        Prepares and extracts usage data along with timing information for prompt and completion.

        Args:
            usage_data (dict): The usage data from the model response.
            prompt_time (float): The duration of the prompt phase.
            completion_time (float): The duration of the completion phase.

        Returns:
            UsageData: A structured data object containing token counts and timing.
        """
        total_time = prompt_time + completion_time

        prompt_tokens = usage_data.get("input_tokens", 0)

        completion_tokens = usage_data.get("output_tokens", 0)

        total_token = prompt_tokens + completion_tokens

        usage = UsageData(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_token,
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    def predict(self, conversation: Conversation, temperature=0.7, max_tokens=256):
        """
        Generates a response synchronously based on the provided conversation context.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Returns:
            Conversation: The updated conversation with the new response appended.
        """
        client = Anthropic(api_key=self.api_key)

        # Get system_context from last message with system context in it
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        with DurationManager() as prompt_timer:
            if system_context:
                response = client.messages.create(system=system_context, **kwargs)
            else:
                response = client.messages.create(**kwargs)
        with DurationManager() as completion_timer:
            message_content = response.content[0].text

        usage_data = response.usage

        usage = self._prepare_usage_data(
            usage_data.model_dump(), prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    async def apredict(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ):
        """
        Asynchronously generates a response based on the provided conversation context.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Returns:
            Conversation: The updated conversation with the new response appended.
        """
        client = AsyncAnthropic(api_key=self.api_key)

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        with DurationManager() as prompt_timer:
            if system_context:
                response = await client.messages.create(system=system_context, **kwargs)
            else:
                response = await client.messages.create(**kwargs)

        with DurationManager() as completion_timer:
            message_content = response.content[0].text

        usage_data = response.usage

        usage = self._prepare_usage_data(
            usage_data.model_dump(),
            prompt_timer.duration,
            completion_timer.duration,
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    def stream(self, conversation: Conversation, temperature=0.7, max_tokens=256):
        """
        Streams the response in real-time for the given conversation.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Yields:
            str: Segments of the streamed response.
        """
        client = Anthropic(api_key=self.api_key)

        # Get system_context from last message with system context in it
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        collected_content = ""
        usage_data = {}

        with DurationManager() as prompt_timer:
            if system_context:
                stream = client.messages.create(system=system_context, **kwargs)
            else:
                stream = client.messages.create(**kwargs)

        with DurationManager() as completion_timer:
            for event in stream:
                if event.type == "content_block_delta" and event.delta.text:
                    collected_content += event.delta.text
                    yield event.delta.text
                if event.type == "message_start":
                    usage_data["input_tokens"] = event.message.usage.input_tokens
                if event.type == "message_delta":
                    usage_data["output_tokens"] = event.usage.output_tokens

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=collected_content, usage=usage))

    async def astream(
        self, conversation: Conversation, temperature=0.7, max_tokens=256
    ):
        """
        Asynchronously streams the response in real-time for the given conversation.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Yields:
            str: Segments of the streamed response.
        """
        async_client = AsyncAnthropic(api_key=self.api_key)

        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        kwargs = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        usage_data = {}
        collected_content = ""

        with DurationManager() as prompt_timer:
            if system_context:
                stream = await async_client.messages.create(
                    system=system_context, **kwargs
                )
            else:
                stream = await async_client.messages.create(**kwargs)

        with DurationManager() as completion_timer:
            async for event in stream:
                if event.type == "content_block_delta" and event.delta.text:
                    collected_content += event.delta.text
                    yield event.delta.text
                if event.type == "message_start":
                    usage_data["input_tokens"] = event.message.usage.input_tokens
                if event.type == "message_delta":
                    usage_data["output_tokens"] = event.usage.output_tokens

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
            completion_timer.duration,
        )

        conversation.add_message(AgentMessage(content=collected_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
    ) -> List:
        """
        Processes multiple conversations synchronously in a batch.

        Args:
            conversations (List[Conversation]): A list of conversation objects to process.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Returns:
            List[Conversation]: A list of updated conversations with responses appended.
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
        Processes multiple conversations asynchronously in parallel with a limit on concurrency.

        Args:
            conversations (List[Conversation]): A list of conversation objects to process.
            temperature (float, optional): The temperature for sampling. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.
            max_concurrent (int, optional): The maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List[Conversation]: A list of updated conversations with responses appended.
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
