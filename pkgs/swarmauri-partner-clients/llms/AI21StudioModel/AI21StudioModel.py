from pydantic import Field
import asyncio
from typing import List, Literal, AsyncIterator, Iterator
import ai21
from ai21 import AsyncAI21Client
from ai21.models.chat import ChatMessage
from swarmauri.conversations.concrete import Conversation
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase
from swarmauri.messages.concrete.AgentMessage import UsageData
from swarmauri.utils.duration_manager import DurationManager


class AI21StudioModel(LLMBase):
    """
    A model class for interacting with the AI21 Studio's language models via HTTP API calls.

    This class supports synchronous and asynchronous methods for text generation, message streaming,
    and batch processing, allowing it to work with conversations and handle different text generation
    parameters such as temperature, max tokens, and more.

    Attributes:
        api_key (str): API key for authenticating with AI21 Studio's API.
        allowed_models (List[str]): List of model names allowed by the provider.
        name (str): Default model name to use.
        type (Literal): Specifies the model type, used for internal consistency.

    Provider resources: https://docs.ai21.com/reference/jamba-15-api-ref
    """

    api_key: str
    allowed_models: List[str] = [
        "jamba-1.5-large",
        "jamba-1.5-mini",
    ]
    name: str = "jamba-1.5-mini"
    type: Literal["AI21StudioModel"] = "AI21StudioModel"
    client: ai21.AI21Client = Field(default=None, exclude=True)
    async_client: AsyncAI21Client = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = ai21.AI21Client(api_key=self.api_key)
        self.async_client = AsyncAI21Client(api_key=self.api_key)

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[ChatMessage]:
        """
        Formats messages for API request payload.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of messages in the conversation.

        Returns:
            List[dict]: Formatted list of message dictionaries.
        """
        return [
            ChatMessage(content=message.content, role=message.role)
            for message in messages
        ]

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float = 0,
        completion_time: float = 0,
    ) -> UsageData:
        """
        Prepares usage data from the API response for tracking token usage and time.

        Args:
            usage_data (dict): Raw usage data from API response.
            prompt_time (float): Time taken for prompt processing.
            completion_time (float): Time taken for completion processing.

        Returns:
            UsageData: Structured usage data object.
        """
        total_time = prompt_time + completion_time

        usage = UsageData(
            prompt_tokens=usage_data.prompt_tokens,
            completion_tokens=usage_data.completion_tokens,
            total_tokens=usage_data.total_tokens,
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    def predict(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
    ) -> Conversation:
        """
        Synchronously generates a response for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Nucleus sampling parameter.
            stop (str): Stop sequence to halt generation.
            n (int): Number of completions to generate.

        Returns:
            Conversation: Updated conversation with generated message.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            response = self.client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                n=n,
            )

        message_content = response.choices[0].message.content

        usage_data = response.usage

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    async def apredict(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
    ) -> Conversation:
        """
        Asynchronously generates a response for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Nucleus sampling parameter.
            stop (str): Stop sequence to halt generation.
            n (int): Number of completions to generate.

        Returns:
            Conversation: Updated conversation with generated message.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            response = await self.async_client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                n=n,
            )

        message_content = response.choices[0].message.content

        usage_data = response.usage

        usage = self._prepare_usage_data(
            usage_data,
            prompt_timer.duration,
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    def stream(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
    ) -> Iterator[str]:
        """
        Synchronously streams responses for a conversation, yielding each chunk.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Nucleus sampling parameter.
            stop (str): Stop sequence to halt generation.

        Yields:
            Iterator[str]: Chunks of the response content as they are generated.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            stream = self.client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                stream=True,
            )

        collected_content = []
        usage_data = {}

        with DurationManager() as completion_timer:
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    yield content

                if hasattr(chunk, "usage") and chunk.usage is not None:
                    usage_data = chunk.usage

        full_content = "".join(collected_content)

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    async def astream(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams responses for a conversation, yielding each chunk.

        Args:
            conversation (Conversation): The conversation object containing the message history.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Nucleus sampling parameter.
            stop (str): Stop sequence to halt generation.

        Yields:
            AsyncIterator[str]: Chunks of the response content as they are generated.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            stream = await self.async_client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                stream=True,
            )

        collected_content = []
        usage_data = {}

        with DurationManager() as completion_timer:
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    yield content

                if hasattr(chunk, "usage") and chunk.usage is not None:
                    usage_data = chunk.usage

        full_content = "".join(collected_content)

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations synchronously, generating responses for each.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Nucleus sampling parameter.
            stop (str): Stop sequence to halt generation.
            n (int): Number of completions to generate per conversation.

        Returns:
            List[Conversation]: List of updated conversations.
        """
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                n=n,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
        top_p=1.0,
        stop="\n",
        n=1,
        max_concurrent=5,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations asynchronously, generating responses for each.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Nucleus sampling parameter.
            stop (str): Stop sequence to halt generation.
            n (int): Number of completions to generate per conversation.
            max_concurrent (int): Maximum number of concurrent requests.

        Returns:
            List[Conversation]: List of updated conversations.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stop=stop,
                    n=n,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
