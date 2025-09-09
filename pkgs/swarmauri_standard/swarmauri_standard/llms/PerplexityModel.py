import asyncio
import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Optional, Type

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.messages.MessageBase import MessageBase

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.utils.duration_manager import DurationManager
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(LLMBase, "PerplexityModel")
class PerplexityModel(LLMBase):
    """
    Represents a language model interface for Perplexity API.

    Provides methods for synchronous and asynchronous predictions, streaming,
    and batch processing of conversations using the Perplexity language models.

    Attributes:
        api_key (SecretStr): API key for authenticating requests to the Perplexity API.
        allowed_models (List[str]): List of allowed model names that can be used.
        name (str): The default model name to use for predictions.
        type (Literal["PerplexityModel"]): The type identifier for this class.
        timeout (float): Timeout for API requests in seconds.

    Provider resources: https://docs.perplexity.ai/guides/model-cards
    Link to deprecated models: https://docs.perplexity.ai/changelog/changelog#model-deprecation-notice
    """

    api_key: SecretStr
    allowed_models: List[str] = [
        "sonar-reasoning-pro",
        "sonar-reasoning",
        "sonar-pro",
        "sonar",
    ]
    name: str = "sonar"
    type: Literal["PerplexityModel"] = "PerplexityModel"
    timeout: float = 600.0
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.perplexity.ai/chat/completions")

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Initialize the GroqAIAudio class with the provided data.

        Args:
            **data (Dict[str, Any]): Arbitrary keyword arguments containing initialization data.
        """
        super().__init__(**data)
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.api_key.get_secret_value()}"},
            base_url=self._BASE_URL,
            timeout=self.timeout,
        )
        self._async_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key.get_secret_value()}"},
            base_url=self._BASE_URL,
            timeout=self.timeout,
        )

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        """
        Formats the list of message objects for the API request.

        Args:
            messages (List[Type[MessageBase]]): A list of message objects.

        Returns:
            List[Dict[str, str]]: A list of formatted message dictionaries.
        """
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data: Dict[str, int],
        prompt_time: float = 0,
        completion_time: float = 0,
    ) -> UsageData:
        """
        Prepares usage data and calculates response timing.

        Args:
            usage_data (Dict[str, int]): The raw usage data from the API response.
            prompt_time (float): Time taken for the prompt processing.
            completion_time (float): Time taken for the completion processing.

        Returns:
            UsageData: A UsageData object containing token and timing information.
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
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> Conversation:
        """
        Makes a synchronous prediction request.

        Args:
            conversation (Conversation): The conversation object containing the history.
            temperature (float): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int): Maximum number of tokens for the response. Defaults to 256.
            top_p (Optional[float]): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int]): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (bool): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float]): Penalty for new tokens based on presence.
            frequency_penalty (Optional[float]): Penalty for new tokens based on frequency.

        Returns:
            Conversation: An updated Conversation object with the model's response.
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
            "authorization": f"Bearer {self.api_key.get_secret_value()}",
        }

        with DurationManager() as prompt_timer:
            response = self._client.post(self._BASE_URL, json=payload, headers=headers)
            response.raise_for_status()

        result = response.json()
        message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        if self.include_usage:
            usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> Conversation:
        """
        Makes an asynchronous prediction request.

        Args:
            conversation (Conversation): The conversation object containing the history.
            temperature (float): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int): Maximum number of tokens for the response. Defaults to 256.
            top_p (Optional[float]): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int]): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (bool): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float]): Penalty for new tokens based on presence.
            frequency_penalty (Optional[float]): Penalty for new tokens based on frequency.

        Returns:
            Conversation: An updated Conversation object with the model's response.
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
            "authorization": f"Bearer {self.api_key.get_secret_value()}",
        }

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(
                self._BASE_URL, json=payload, headers=headers
            )
            response.raise_for_status()

        result = response.json()

        message_content = result["choices"][0]["message"]["content"]

        usage_data = result.get("usage", {})

        if self.include_usage and usage_data:
            usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> Iterator[str]:
        """
        Synchronously streams the response for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing message history.
            temperature (float): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float]): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int]): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (bool): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float]): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float]): Penalty for repeating existing tokens. Defaults to None.

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
            "authorization": f"Bearer {self.api_key.get_secret_value()}",
        }

        with DurationManager() as prompt_timer:
            response = self._client.post(url, json=payload, headers=headers)
            response.raise_for_status()

        message_content = ""
        usage_data = {}

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
                    if chunk_data.get("usage"):
                        usage_data = chunk_data["usage"]

        if self.include_usage and usage_data:
            usage = self._prepare_usage_data(
                usage_data, prompt_timer.duration, completion_timer.duration
            )
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams the response for a given conversation.

        Args:
            conversation (Conversation): The conversation object containing message history.
            temperature (float): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float]): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int]): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (bool): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float]): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float]): Penalty for repeating existing tokens. Defaults to None.

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

        if self.include_usage and usage_data:
            usage = self._prepare_usage_data(
                usage_data, prompt_timer.duration, completion_timer.duration
            )
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
    ) -> List[Conversation]:
        """
        Processes a batch of conversations synchronously.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float]): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int]): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (bool): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float]): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float]): Penalty for repeating existing tokens. Defaults to None.

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
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: bool = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        max_concurrent: int = 5,  # Maximum concurrent tasks
    ) -> List[Conversation]:
        """
        Asynchronously processes a batch of conversations with a limit on concurrent tasks.

        Args:
            conversations (List[Conversation]): List of conversation objects.
            temperature (float): Sampling temperature for response generation. Defaults to 0.7.
            max_tokens (int): Maximum number of tokens in the generated response. Defaults to 256.
            top_p (Optional[float]): Nucleus sampling parameter. If specified, `top_k` should not be set.
            top_k (Optional[int]): Top-k sampling parameter. If specified, `top_p` should not be set.
            return_citations (bool): Whether to return citations in the response. Defaults to False.
            presence_penalty (Optional[float]): Penalty for introducing new topics. Defaults to None.
            frequency_penalty (Optional[float]): Penalty for repeating existing tokens. Defaults to None.
            max_concurrent (int): Maximum number of concurrent tasks. Defaults to 5.

        Returns:
            List[Conversation]: List of updated conversation objects after processing asynchronously.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv: Conversation) -> Conversation:
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

    def get_allowed_models(self) -> List[str]:
        """
        Queries the LLMProvider API endpoint to retrieve the list of allowed models.

        Returns:
            List[str]: List of allowed model names.
        """
        models_data = [
            "sonar-reasoning-pro",
            "sonar-reasoning",
            "sonar-pro",
            "sonar",
        ]
        return models_data
