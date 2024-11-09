import json
from typing import List, Dict, Literal, AsyncIterator, Iterator
import openai
from openai import AsyncOpenAI
import asyncio
from pydantic import Field
from swarmauri_core.typing import SubclassUnion

from swarmauri.messages.base.MessageBase import MessageBase
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.llms.base.LLMBase import LLMBase


class DeepSeekModel(LLMBase):
    """
    A client class for interfacing with DeepSeek's language model for chat completions.

    This class provides methods for synchronous and asynchronous prediction, streaming, and batch processing.
    It handles message formatting, payload construction, and response parsing to seamlessly integrate
    with the DeepSeek API.

    Attributes:
        api_key (str): The API key for authenticating with DeepSeek.
        allowed_models (List[str]): List of models supported by DeepSeek, defaulting to ["deepseek-chat"].
        name (str): The model name, defaulting to "deepseek-chat".
        type (Literal): The class type for identifying the LLM, set to "DeepSeekModel".
        client (httpx.Client): The HTTP client for synchronous API requests.
        async_client (httpx.AsyncClient): The HTTP client for asynchronous API requests.

    Link to Allowed Models: https://platform.deepseek.com/api-docs/quick_start/pricing
    Link to API KEY: https://platform.deepseek.com/api_keys
    """

    api_key: str
    allowed_models: List[str] = ["deepseek-chat"]
    name: str = "deepseek-chat"
    type: Literal["DeepSeekModel"] = "DeepSeekModel"
    client: openai.OpenAI = Field(default=None, exclude=True)
    async_client: AsyncOpenAI = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.client = openai.OpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats a list of message objects into a list of dictionaries for API payload.

        Args:
            messages (List[SubclassUnion[MessageBase]]): The conversation history to format.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties) for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ):
        """
        Sends a synchronous request to the DeepSeek API to generate a chat response.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Returns:
            Updated conversation object with the generated response added.
        """
        formatted_messages = self._format_messages(conversation.history)

        response = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            top_p=top_p,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    async def apredict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ):
        """
        Sends an asynchronous request to the DeepSeek API to generate a chat response.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Returns:
            Updated conversation object with the generated response added.
        """
        formatted_messages = self._format_messages(conversation.history)

        response = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            top_p=top_p,
        )

        message_content = response.choices[0].message.content
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

    def stream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> Iterator[str]:
        """
        Streams the response token by token synchronously from the DeepSeek API.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Yields:
            str: Token of the response being streamed.
        """
        formatted_messages = self._format_messages(conversation.history)

        stream = self.client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=True,
            top_p=top_p,
        )

        collected_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    async def astream(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response token by token from the DeepSeek API.

        Args:
            conversation: The conversation object containing message history.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Yields:
            str: Token of the response being streamed.
        """
        formatted_messages = self._format_messages(conversation.history)

        stream = await self.async_client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            stream=True,
            top_p=top_p,
        )

        collected_content = []
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_content.append(content)
                yield content

        full_content = "".join(collected_content)
        conversation.add_message(AgentMessage(content=full_content))

    def batch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
    ) -> List:
        """
        Processes multiple conversations synchronously in a batch.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.

        Returns:
            List: List of updated conversation objects with responses added.
        """
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                top_p=top_p,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List,
        temperature=0.7,
        max_tokens=256,
        frequency_penalty=0,
        presence_penalty=0,
        stop="\n",
        top_p=1.0,
        max_concurrent=5,
    ) -> List:
        """
        Processes multiple conversations asynchronously in parallel, with concurrency control.

        Args:
            conversations (List): List of conversation objects.
            temperature (float): Sampling temperature for randomness in response.
            max_tokens (int): Maximum number of tokens in the response.
            frequency_penalty (float): Penalty for frequent tokens in the response.
            presence_penalty (float): Penalty for new topics in the response.
            stop (str): Token at which response generation should stop.
            top_p (float): Top-p sampling value for nucleus sampling.
            max_concurrent (int): Maximum number of concurrent tasks allowed.

        Returns:
            List: List of updated conversation objects with responses added.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv):
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop,
                    top_p=top_p,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
