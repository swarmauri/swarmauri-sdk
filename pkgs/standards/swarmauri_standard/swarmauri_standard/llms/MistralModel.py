import asyncio
import json
from typing import AsyncIterator, Iterator, List, Literal, Dict
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


class MistralModel(LLMBase):
    """
    A model class for interfacing with the Mistral language model API.

    Provides methods for synchronous, asynchronous, and streaming conversation interactions
    with the Mistral language model API.

    Attributes:
        api_key (str): API key for authenticating with Mistral.
        allowed_models (List[str]): List of model names allowed for use.
        name (str): Default model name.
        type (Literal["MistralModel"]): Type identifier for the model.

    Provider resources: https://docs.mistral.ai/getting-started/models/
    """

    api_key: str
    allowed_models: List[str] = [
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest",
        "open-mistral-nemo",
        "codestral-latest",
        "open-codestral-mamba",
    ]
    name: str = "open-mixtral-8x7b"
    type: Literal["MistralModel"] = "MistralModel"
    _client: httpx.Client = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient = PrivateAttr(default=None)
    _BASE_URL: str = PrivateAttr(default="https://api.mistral.ai/v1/chat/completions")

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
        Format a list of message objects into dictionaries for the Mistral API.

        Args:
            messages (List[SubclassUnion[MessageBase]]): List of messages to format.

        Returns:
            List[Dict[str, str]]: Formatted list of message dictionaries.
        """
        message_properties = ["content", "role"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
            if message.role != "assistant"
        ]
        return formatted_messages

    def _prepare_usage_data(
        self,
        usage_data: Dict[str, float],
        prompt_time: float = 0,
        completion_time: float = 0,
    ) -> UsageData:
        """
        Prepare usage data by combining token counts and timing information.

        Args:
            usage_data: Raw usage data containing token counts.
            prompt_time (float): Time taken for prompt processing.
            completion_time (float): Time taken for response completion.

        Returns:
            UsageData: Processed usage data.
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
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> Conversation:
        """
        Generate a synchronous response for a conversation.

        Args:
            conversation (Conversation): The conversation to respond to.
            temperature (int, optional): Sampling temperature. Defaults to 0.7.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256.
            top_p (int, optional): Top-p sampling parameter. Defaults to 1.
            enable_json (bool, optional): If True, enables JSON responses. Defaults to False.
            safe_prompt (bool, optional): Enables safe prompt mode if True. Defaults to False.

        Returns:
            Conversation: Updated conversation with the model response.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "safe_prompt": safe_prompt,
        }

        if enable_json:
            payload["response_format"] = {"type": "json_object"}

        with DurationManager() as prompt_timer:
            response = self._client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

        response_data = response.json()
        message_content = response_data["choices"][0]["message"]["content"]

        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    async def apredict(
        self,
        conversation: Conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> Conversation:
        """
        Generate an asynchronous response for a conversation.

        Args:
            conversation (Conversation): The conversation to respond to.
            temperature (int, optional): Sampling temperature. Defaults to 0.7.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256.
            top_p (int, optional): Top-p sampling parameter. Defaults to 1.
            enable_json (bool, optional): Enables JSON responses. Defaults to False.
            safe_prompt (bool, optional): Enables safe prompt mode if True. Defaults to False.

        Returns:
            Conversation: Updated conversation with the model response.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "safe_prompt": safe_prompt,
        }

        if enable_json:
            payload["response_format"] = {"type": "json_object"}

        with DurationManager() as prompt_timer:
            response = await self._async_client.post(self._BASE_URL, json=payload)
            response.raise_for_status()

        response_data = response.json()

        message_content = response_data["choices"][0]["message"]["content"]

        usage_data = response_data.get("usage", {})

        usage = self._prepare_usage_data(usage_data, prompt_timer.duration)

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

        return conversation

    @retry_on_status_codes((429, 529), max_retries=1)
    def stream(
        self,
        conversation: Conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        safe_prompt: bool = False,
    ) -> Iterator[str]:
        """
        Stream response content iteratively.

        Args:
            conversation (Conversation): The conversation to respond to.
            temperature (int, optional): Sampling temperature. Defaults to 0.7.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256.
            top_p (int, optional): Top-p sampling parameter. Defaults to 1.
            safe_prompt (bool, optional): Enables safe prompt mode if True. Defaults to False.

        Yields:
            str: Chunks of response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "safe_prompt": safe_prompt,
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

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    @retry_on_status_codes((429, 529), max_retries=1)
    async def astream(
        self,
        conversation,
        temperature: int = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        safe_prompt: bool = False,
    ) -> AsyncIterator[str]:
        """
        Asynchronously stream response content.

        Args:
            conversation (Conversation): The conversation to respond to.
            temperature (int, optional): Sampling temperature. Defaults to 0.7.
            max_tokens (int, optional): Maximum tokens in response. Defaults to 256.
            top_p (int, optional): Top-p sampling parameter. Defaults to 1.
            safe_prompt (bool, optional): Enables safe prompt mode if True. Defaults to False.

        Yields:
            str: Chunks of response content.
        """
        formatted_messages = self._format_messages(conversation.history)

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "safe_prompt": safe_prompt,
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

        usage = self._prepare_usage_data(
            usage_data, prompt_timer.duration, completion_timer.duration
        )

        conversation.add_message(AgentMessage(content=message_content, usage=usage))

    def batch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
    ) -> List[Conversation]:
        """
        Synchronously processes multiple conversations and generates responses for each.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float, optional): Sampling temperature for response generation.
            max_tokens (int, optional): Maximum tokens for the response.
            top_p (int, optional): Nucleus sampling parameter.
            enable_json (bool, optional): If True, enables JSON output format.
            safe_prompt (bool, optional): If True, enables safe prompting.

        Returns:
            List[Conversation]: List of updated conversations with generated responses.
        """
        return [
            self.predict(
                conv,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                enable_json=enable_json,
                safe_prompt=safe_prompt,
            )
            for conv in conversations
        ]

    async def abatch(
        self,
        conversations: List[Conversation],
        temperature: float = 0.7,
        max_tokens: int = 256,
        top_p: int = 1,
        enable_json: bool = False,
        safe_prompt: bool = False,
        max_concurrent: int = 5,
    ) -> List[Conversation]:
        """
        Asynchronously processes multiple conversations with controlled concurrency.

        Args:
            conversations (List[Conversation]): List of conversations to process.
            temperature (float, optional): Sampling temperature for response generation.
            max_tokens (int, optional): Maximum tokens for the response.
            top_p (int, optional): Nucleus sampling parameter.
            enable_json (bool, optional): If True, enables JSON output format.
            safe_prompt (bool, optional): If True, enables safe prompting.
            max_concurrent (int, optional): Maximum number of concurrent tasks.

        Returns:
            List[Conversation]: List of updated conversations with generated responses.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_conversation(conv) -> Conversation:
            async with semaphore:
                return await self.apredict(
                    conv,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    enable_json=enable_json,
                    safe_prompt=safe_prompt,
                )

        tasks = [process_conversation(conv) for conv in conversations]
        return await asyncio.gather(*tasks)
