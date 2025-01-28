import asyncio
from typing import List, Dict, Literal, AsyncIterator, Iterator
from pydantic import Field
import cohere
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class CohereModel(LLMBase):
    """
    A class representing a model interface for Cohere's language model APIs. This class provides synchronous
    and asynchronous methods for predictions, streaming responses, and batch processing of conversations.

    Attributes:
        api_key (str): The API key for authenticating with the Cohere service.
        allowed_models (List[str]): A list of allowed Cohere model names.
        name (str): The name of the model being used.
        type (Literal["CohereModel"]): The type identifier for this model class.
        client (cohere.ClientV2): The Cohere client used for API interactions.

    Link to Allowed Models: https://docs.cohere.com/docs/models
    Link to API Key: https://dashboard.cohere.com/api-keys
    """

    api_key: str
    allowed_models: List[str] = [
        "command-r-plus-08-2024",
        "command-r-plus-04-2024",
        "command-r-03-2024",
        "command-r-08-2024",
        "command-light",
        "command",
    ]
    name: str = "command"
    type: Literal["CohereModel"] = "CohereModel"
    client: cohere.ClientV2 = Field(default=None, exclude=True)

    def __init__(self, **data):
        """
        Initializes the CohereModel instance with the provided data and creates the Cohere client.

        Args:
            **data: Arbitrary keyword arguments containing configuration data.
        """
        super().__init__(**data)
        self.client = cohere.ClientV2(api_key=self.api_key)

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats a list of message objects into a structure that Cohere's API can interpret.

        Args:
            messages (List[SubclassUnion[MessageBase]]): A list of message objects to format.

        Returns:
            List[Dict[str, str]]: A list of dictionaries representing formatted messages.
        """
        formatted_messages = []
        for message in messages:
            role = message.role
            if role == "assistant":
                role = "assistant"
            formatted_messages.append({"role": role, "content": message.content})
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float,
        completion_time: float,
    ):
        """
        Prepares and extracts usage data including token counts and response timing information.

        Args:
            usage_data: The usage data returned by the Cohere API.
            prompt_time (float): Time taken for preparing the prompt.
            completion_time (float): Time taken for generating the completion.

        Returns:
            UsageData: An object containing structured usage data.
        """
        total_time = prompt_time + completion_time

        tokens_data = usage_data.tokens
        total_token = tokens_data.input_tokens + tokens_data.output_tokens

        usage = UsageData(
            prompt_tokens=tokens_data.input_tokens,
            completion_tokens=tokens_data.output_tokens,
            total_tokens=total_token,
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )
        return usage

    def predict(self, conversation, temperature=0.7, max_tokens=256):
        """
        Generates a response to a conversation synchronously.

        Args:
            conversation: The conversation object containing the current context and history.
            temperature (float, optional): Sampling temperature for randomness in the response. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Returns:
            conversation: The updated conversation object with the new message appended.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            response = self.client.chat(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        with DurationManager() as completion_timer:
            message_content = response.message.content[0].text

        usage_data = response.usage

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    async def apredict(self, conversation, temperature=0.7, max_tokens=256):
        """
        Generates a response to a conversation asynchronously.

        Args:
            conversation: The conversation object containing the current context and history.
            temperature (float, optional): Sampling temperature for randomness in the response. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Returns:
            conversation: The updated conversation object with the new message appended.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        with DurationManager() as completion_timer:
            message_content = response.message.content[0].text

        usage_data = response.usage

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    def stream(self, conversation, temperature=0.7, max_tokens=256) -> Iterator[str]:
        """
        Streams the response to a conversation synchronously in real-time.

        Args:
            conversation: The conversation object containing the current context and history.
            temperature (float, optional): Sampling temperature for randomness in the response. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Yields:
            str: Parts of the response as they are streamed.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            stream = self.client.chat_stream(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        usage_data = {}
        collected_content = []
        with DurationManager() as completion_timer:
            for chunk in stream:
                if chunk and chunk.type == "content-delta":
                    content = chunk.delta.message.content.text
                    collected_content.append(content)
                    yield content
                elif chunk and chunk.type == "message-end":
                    usage_data = chunk.delta.usage

        full_content = "".join(collected_content)
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    async def astream(
        self, conversation, temperature=0.7, max_tokens=256
    ) -> AsyncIterator[str]:
        """
        Streams the response to a conversation asynchronously in real-time.

        Args:
            conversation: The conversation object containing the current context and history.
            temperature (float, optional): Sampling temperature for randomness in the response. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the response. Defaults to 256.

        Yields:
            str: Parts of the response as they are streamed.
        """
        formatted_messages = self._format_messages(conversation.history)

        with DurationManager() as prompt_timer:
            stream = await asyncio.to_thread(
                self.client.chat_stream,
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        usage_data = {}
        collected_content = []
        with DurationManager() as completion_timer:
            for chunk in stream:
                if chunk and chunk.type == "content-delta":
                    content = chunk.delta.message.content.text
                    collected_content.append(content)
                    yield content

                elif chunk and chunk.type == "message-end":
                    usage_data = chunk.delta.usage
                await asyncio.sleep(0)  # Allow other tasks to run

        full_content = "".join(collected_content)
        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=full_content, usage=usage))

    def batch(self, conversations: List, temperature=0.7, max_tokens=256) -> List:
        """
        Processes multiple conversations synchronously in a batch.

        Args:
            conversations (List): A list of conversation objects.
            temperature (float, optional): Sampling temperature for randomness in the responses. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the responses. Defaults to 256.

        Returns:
            List: A list of updated conversation objects with new messages appended.
        """
        return [
            self.predict(conv, temperature=temperature, max_tokens=max_tokens)
            for conv in conversations
        ]

    async def abatch(
        self, conversations: List, temperature=0.7, max_tokens=256, max_concurrent=5
    ) -> List:
        """
        Processes multiple conversations asynchronously in a batch.

        Args:
            conversations (List): A list of conversation objects.
            temperature (float, optional): Sampling temperature for randomness in the responses. Defaults to 0.7.
            max_tokens (int, optional): The maximum number of tokens for the responses. Defaults to 256.
            max_concurrent (int, optional): The maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List: A list of updated conversation objects with new messages appended.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv, temperature=temperature, max_tokens=max_tokens
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
