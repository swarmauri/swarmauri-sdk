import asyncio
import json
from typing import AsyncIterator, Iterator, List, Dict, Literal, Optional

import httpx
from pydantic import PrivateAttr
from swarmauri.utils.retry_decorator import retry_on_status_codes
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_base.llms.LLMBase import LLMBase

from swarmauri_standard.messages.AgentMessage import UsageData

from swarmauri.utils.duration_manager import DurationManager


class PerplexityModel(LLMBase):
    """
    Represents a language model interface for Perplexity API.

    Provides methods for synchronous and asynchronous predictions, streaming,
    and batch processing of conversations using the Perplexity language models.

    Attributes:
        api_key (str): API key for authenticating requests to the Perplexity API.
        allowed_models (List[str]): List of allowed model names that can be used.
        name (str): The default model name to use for predictions.
        type (Literal["PerplexityModel"]): The type identifier for this class.


    Provider resources: https://docs.perplexity.ai/guides/model-cards
    Link to deprecated models: https://docs.perplexity.ai/changelog/changelog#model-deprecation-notice
    """

    api_key: str
    allowed_models: List[str] = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-huge-128k-online",
        "llama-3.1-sonar-small-128k-chat",
        "llama-3.1-sonar-large-128k-chat",
        "llama-3.1-8b-instruct",
        "llama-3.1-70b-instruct",
    ]
    name: str = "llama-3.1-70b-instruct"
    type: Literal["PerplexityModel"] = "PerplexityModel"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.perplexity.ai/chat/completions")

    def __init__(self, **data):
        """
        Initialize the GroqAIAudio class with the provided data.

        Args:
            **data: Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )
        self._async_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            base_url=self._BASE_URL,
            timeout=30,
        )

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats the list of message objects for the API request.

        Args:
            messages: A list of message objects.

        Returns:
            A list of formatted message dictionaries.
        """
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data,
        prompt_time: float = 0,
        completion_time: float = 0,
    ) -> UsageData:
        """
        Prepares usage data and calculates response timing.

        Args:
            usage_data: The raw usage data from the API response.
            prompt_time: Time taken for the prompt processing.
            completion_time: Time taken for the completion processing.

        Returns:
            A UsageData object containing token and timing information.
        """

        total_time = prompt_time + completion_time

        usage = UsageData(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            prompt_time=prompt_time,
            completion_time=completion_time,
            total_time=total_time,
        )

        return usage

    @retry_on_status_codes((429, 529), max_retries=1)
    def predict(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> Conversation:
        """
        Makes a synchronous prediction request.

        Args:
            conversation: The conversation object containing the history.
            temperature: Sampling temperature for response generation.
            max_tokens: Maximum number of tokens for the response.
            top_p: Nucleus sampling parameter.
            top_k: Top-k sampling parameter.
            return_citations: Whether to return citations in the response.
            presence_penalty: Penalty for new tokens based on presence.
            frequency_penalty: Penalty for new tokens based on frequency.

        Returns:
            An updated Conversation object with the model's response.
        """

        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            response = self._client.post(self._BASE_URL, json=payload, headers=headers)
            response.raise_for_status()

        result = response.json()
        message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> Conversation:
        """
        Makes an asynchronous prediction request.

        Args:
            conversation: The conversation object containing the history.
            temperature: Sampling temperature for response generation.
            max_tokens: Maximum number of tokens for the response.
            top_p: Nucleus sampling parameter.
            top_k: Top-k sampling parameter.
            return_citations: Whether to return citations in the response.
            presence_penalty: Penalty for new tokens based on presence.
            frequency_penalty: Penalty for new tokens based on frequency.

        Returns:
            An updated Conversation object with the model's response.
        """

        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(
                self._BASE_URL, json=payload, headers=headers
            )
            response.raise_for_status()

        result = response.json()

        message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})
        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> Iterator[str]:
        """
        Synchronously streams the response for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing message history.
            temperature (float, optional): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float], optional): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int], optional): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (Optional[bool], optional): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float], optional): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float], optional): Penalty for repeating existing tokens. Defaults to None.

        Yields:
            str: Chunks of response content as the data is streamed.
        """
        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stream": True,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

        with DurationManager() as prompt_timer:
            response = self._client.post(url, json=payload, headers=headers)
            response.raise_for_status()

        message_content = ""

        with DurationManager() as completion_timer:
            for chunk in response.iter_lines():
                json_string = chunk.replace("data: ", "", 1)
                if json_string:
                    chunk_data = json.loads(json_string)
                    delta_content = (
                        chunk_data.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    message_content += delta_content
                    yield delta_content
                    if chunk_data["usage"]:
                        usage_data = chunk_data["usage"]

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing message history.
            temperature (float, optional): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float], optional): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int], optional): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (Optional[bool], optional): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float], optional): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float], optional): Penalty for repeating existing tokens. Defaults to None.

        Yields:
            str: Chunks of response content as the data is streamed asynchronously.
        """
        if top_p and top_k:
            raise ValueError("Do not set top_p and top_k")

        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stream": True,
        }

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

        message_content = ""
        usage_data = {}

        with DurationManager() as completion_timer:
            async for line in response.aiter_lines():
                json_string = line.replace("data: ", "", 1)
                if json_string:  # Ensure it's not empty
                    chunk_data = json.loads(json_string)
                    delta_content = (
                        chunk_data.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    message_content += delta_content
                    yield delta_content
                    usage_data = chunk_data.get("usage", usage_data)

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )
        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations synchronously.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float, optional): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float], optional): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int], optional): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (Optional[bool], optional): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float], optional): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float], optional): Penalty for repeating existing tokens. Defaults to None.

        Returns:
            List[Conversation]: List of updated conversation objects after processing.
        """
        return [
            self.predict(
                conversation=conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                return_citations=return_citations,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature=0.7,
        max_tokens=256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        max_concurrent: int = 5,  # Maximum concurrent tasks
    ) -> List[Conversation]:
        """
        Asynchronously processes a batch of conversations with a limit on concurrent tasks.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float, optional): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float], optional): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int], optional): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (Optional[bool], optional): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float], optional): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float], optional): Penalty for repeating existing tokens. Defaults to None.
            max_concurrent (int, optional): Maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List[Conversation]: List of updated conversation objects after processing asynchronously.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conversation=conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    return_citations=return_citations,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
