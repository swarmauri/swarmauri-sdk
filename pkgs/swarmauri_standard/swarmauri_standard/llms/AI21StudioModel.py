import asyncio
import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Literal, Type

import httpx
from pydantic import PrivateAttr, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.messages.MessageBase import MessageBase

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData
from swarmauri_standard.utils.duration_manager import DurationManager
from swarmauri_standard.utils.retry_decorator import retry_on_status_codes


@ComponentBase.register_type(LLMBase, "AI21StudioModel")
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

    api_key: SecretStr
    allowed_models: List[str] = ["jamba-1.5-large", "jamba-1.5-mini"]
    name: str = "jamba-1.5-large"
    type: Literal["AI21StudioModel"] = "AI21StudioModel"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(
        default="https://api.ai21.com/studio/v1/chat/completions"
    )

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Initializes the GroqToolModel instance, setting up headers for API requests.

        Parameters:
            **data: Arbitrary keyword arguments for initialization.
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

    def _format_messages(self, messages: List[Type["MessageBase"]]) -> List[dict]:
        """
        Formats messages for API request payload.

        Args:
            messages (List[Type[MessageBase]]): List of messages in the conversation.

        Returns:
            List[dict]: Formatted list of message dictionaries.
        """
        return [
            {"content": message.content, "role": message.role} for message in messages
        ]

    def _prepare_usage_data(
        self, usage_data, prompt_time: float = 0, completion_time: float = 0
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
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "n": n,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": [stop] if stop else [],
            "response_format": {"type": "text"},
        }

        with DurationManager() as prompt_timer:
            response = self._client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

        response_data = response.json()
        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        # Prepare usage data if tracking is enabled
        if self.include_usage and usage_data:
            usage = self._prepare_usage_data(usage_data, prompt_timer.duration)
            conversation.add_message(AgentMessage(content=message_content, usage=usage))
        else:
            conversation.add_message(AgentMessage(content=message_content))
        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
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
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "n": n,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": [stop] if stop else [],
            "response_format": {"type": "text"},
        }

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

        response_data = response.json()
        message_content = response_data["choices"][0]["message"]["content"]
        usage_data = response_data.get("usage", {})

        # Prepare usage data if tracking is enabled
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
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "n": 1,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": [stop] if stop else [],
            "response_format": {"type": "text"},
            "stream": True,
        }

        with DurationManager() as prompt_timer:
            response = self._client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

            usage_data = {}
            message_content = ""

        with DurationManager() as completion_timer:
            for line in response.iter_lines():
                json_str = line.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if (
                            chunk["choices"][0]["delta"]
                            and "content" in chunk["choices"][0]["delta"]
                        ):
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                        if "usage" in chunk:
                            usage_data = chunk.get("usage", {})
                except json.JSONDecodeError:
                    pass

        # Prepare usage data if tracking is enabled
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
        conversation,
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
        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "n": 1,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": [stop] if stop else [],
            "response_format": {"type": "text"},
            "stream": True,
        }

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

        usage_data = {}
        message_content = ""

        with DurationManager() as completion_timer:
            async for line in response.aiter_lines():
                json_str = line.replace("data: ", "")
                try:
                    if json_str:
                        chunk = json.loads(json_str)
                        if (
                            chunk["choices"][0]["delta"]
                            and "content" in chunk["choices"][0]["delta"]
                        ):
                            delta = chunk["choices"][0]["delta"]["content"]
                            message_content += delta
                            yield delta
                        if "usage" in chunk:
                            usage_data = chunk.get("usage", {})
                except json.JSONDecodeError:
                    pass

        # Prepare usage data if tracking is enabled
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
        conversations: List,
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

        async def process_conversation(conv) -> Conversation:
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

    def get_allowed_models(self) -> List[str]:
        """
        Queries the LLMProvider API endpoint to get the list of allowed models.

        Returns:
            List[str]: List of allowed model names.
        """
        return ["jamba-1.5-large", "jamba-1.5-mini"]
